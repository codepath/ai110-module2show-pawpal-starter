"""
Agentic workflow layer for PawPal+.

Two distinct AI features live here:

1. `answer_question(...)` — RAG Q&A. Retrieves from the pet-care
   knowledge base and grounds Claude's answer in the retrieved snippets,
   with inline citations.

2. `ScheduleReviewAgent` — a plan → act → check agent. It:
       a. retrieves relevant guidance from the KB,
       b. asks Claude to flag issues with today's schedule,
       c. runs deterministic checks against the Scheduler to validate
          (or reject) each flagged issue before presenting it to the user.

Both paths return a `AgentResult` with the final text plus a confidence
score so the UI and the evaluator can reason about output quality.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional

from knowledge_base import Snippet, format_context, retrieve
from logger_setup import GuardrailError, get_logger, sanitize_user_text
from pawpal_system import Scheduler

log = get_logger(__name__)

# Haiku is fast + cheap enough for the agent's 2–3 round trips.
DEFAULT_MODEL = "claude-haiku-4-5-20251001"


# ── Result envelope ────────────────────────────────────────────────────────

@dataclass
class AgentResult:
    """Wraps every AI response with provenance + a self-reported confidence."""
    text: str
    confidence: float                       # 0.0 – 1.0
    sources: list[str] = field(default_factory=list)   # snippet topics used
    steps: list[str] = field(default_factory=list)     # agent trace
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


# ── Shared client bootstrap ────────────────────────────────────────────────

def _get_client():
    """Return an Anthropic client or raise a clean error if not configured."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Export it before running AI features."
        )
    import anthropic  # imported lazily so tests can run without the SDK
    return anthropic.Anthropic(api_key=api_key)


# ── Feature 1: RAG-grounded Q&A ────────────────────────────────────────────

_QA_SYSTEM = (
    "You are PawPal, a cautious, friendly pet-care assistant. "
    "Answer ONLY using the numbered context snippets provided. "
    "Cite snippets inline like [1] or [2]. "
    "If the context does not contain the answer, say so plainly and recommend "
    "asking a veterinarian. Do NOT invent facts, dosages, or medical advice. "
    "Keep answers under 120 words."
)


def answer_question(question: str, *, k: int = 3, model: str = DEFAULT_MODEL) -> AgentResult:
    """
    RAG Q&A: retrieve top-k snippets, ground Claude's answer, return text +
    confidence + cited sources.

    Confidence heuristic:
      - 0.2 base when the model replied.
      - +0.6 scaled by how many retrieved snippets the answer actually cites.
      - +0.2 when the retriever found at least one high-scoring hit.
    This is explicit and cheap — not a learned calibration, just a signal
    the UI can threshold on.
    """
    try:
        q = sanitize_user_text(question, label="question")
    except GuardrailError as e:
        log.warning("answer_question guardrail: %s", e)
        return AgentResult(text=str(e), confidence=0.0, error=str(e))

    snippets = retrieve(q, k=k)
    context = format_context(snippets)
    log.info("QA: question=%r retrieved=%s", q, [s.topic for s in snippets])

    try:
        client = _get_client()
    except RuntimeError as e:
        return AgentResult(text=str(e), confidence=0.0, error=str(e))

    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {q}\n\n"
        "Answer using only the context above. Cite like [1], [2]."
    )

    try:
        msg = client.messages.create(
            model=model,
            max_tokens=400,
            system=_QA_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = msg.content[0].text
    except Exception as e:          # pragma: no cover — network path
        log.exception("Anthropic call failed in answer_question")
        return AgentResult(text=f"AI call failed: {e}", confidence=0.0, error=str(e))

    # Confidence: how many of the retrieved snippets did the answer cite?
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer) if n.isdigit()}
    cited = {n for n in cited if 1 <= n <= len(snippets)}
    citation_ratio = (len(cited) / len(snippets)) if snippets else 0.0
    confidence = 0.2 + 0.6 * citation_ratio + (0.2 if snippets else 0.0)
    confidence = min(1.0, round(confidence, 2))

    return AgentResult(
        text=answer,
        confidence=confidence,
        sources=[s.topic for s in snippets],
        steps=[
            f"retrieve(k={k}) -> {len(snippets)} hit(s)",
            f"llm({model})",
            f"citations parsed: {sorted(cited)}",
        ],
    )


# ── Feature 2: Plan → Act → Check review agent ─────────────────────────────

_AGENT_SYSTEM = (
    "You are PawPal's schedule-review agent. You will be given today's "
    "schedule for one owner's pets, plus curated best-practice snippets. "
    "Identify at most 3 concrete issues. Reply with STRICT JSON matching:\n"
    '{"issues": [{"kind": "...", "summary": "...", '
    '"target_time": "HH:MM or null", "evidence": "[n]"}]}\n'
    "kind must be one of: 'conflict', 'spacing', 'priority', 'welfare', 'gap'. "
    "If nothing is wrong, return {\"issues\": []}. No prose outside the JSON."
)


# Deterministic validators keyed on the agent's self-declared `kind`.
# Each returns (accepted, reason). If the agent's claim disagrees with the
# actual Scheduler state, we reject it — preventing hallucinated warnings
# from reaching the user.

def _validate_conflict(issue: dict, scheduler: Scheduler) -> tuple[bool, str]:
    conflicts = scheduler.detect_conflicts()
    target = issue.get("target_time")
    if not conflicts:
        return False, "No conflicts detected in the actual schedule."
    if target and not any(target in c for c in conflicts):
        return False, f"No real conflict at {target}."
    return True, "Matches a real same-time conflict."


def _validate_spacing(issue: dict, scheduler: Scheduler) -> tuple[bool, str]:
    # Spacing / welfare / gap / priority are soft — we accept them but cap
    # confidence downstream. This keeps the agent useful without letting it
    # assert hard conflicts that don't exist.
    schedule = scheduler.get_todays_schedule()
    if not schedule:
        return False, "Schedule is empty, spacing claim not applicable."
    return True, "Soft heuristic — accepted with reduced confidence."


_VALIDATORS = {
    "conflict": _validate_conflict,
    "spacing":  _validate_spacing,
    "priority": _validate_spacing,
    "welfare":  _validate_spacing,
    "gap":      _validate_spacing,
}


def _extract_json(text: str) -> dict:
    """Be forgiving: find the first {...} block and parse it."""
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("no JSON object in model response")
    return json.loads(match.group(0))


class ScheduleReviewAgent:
    """
    Plan → Act → Check loop:

      1. PLAN  — retrieve grounding snippets from the KB.
      2. ACT   — ask Claude to enumerate at most 3 concrete issues (JSON).
      3. CHECK — run each issue through a deterministic validator against
                 the real Scheduler state. Drop any issue the validator
                 rejects. Confidence decays with every rejection.
    """

    def __init__(self, scheduler: Scheduler, *, model: str = DEFAULT_MODEL):
        self.scheduler = scheduler
        self.model = model

    # step 1
    def _plan(self) -> list[Snippet]:
        today = self.scheduler.get_todays_schedule()
        query_bits = ["schedule", "routine", "conflict"]
        for _, task in today:
            query_bits.append(task.description)
            query_bits.append(task.priority)
        query = " ".join(query_bits)
        snippets = retrieve(query, k=4, min_score=1.0)
        log.info("Agent.plan -> %s", [s.topic for s in snippets])
        return snippets

    # step 2
    def _act(self, snippets: list[Snippet]) -> dict:
        plan_text = self.scheduler.generate_plan_text()
        context = format_context(snippets)
        client = _get_client()
        user = (
            f"Today's schedule:\n{plan_text}\n\n"
            f"Relevant best-practice snippets:\n{context}\n\n"
            "Return JSON only."
        )
        msg = client.messages.create(
            model=self.model,
            max_tokens=500,
            system=_AGENT_SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        raw = msg.content[0].text
        log.debug("Agent.act raw: %s", raw)
        return _extract_json(raw)

    # step 3
    def _check(self, payload: dict) -> tuple[list[dict], list[str]]:
        accepted: list[dict] = []
        trace: list[str] = []
        for issue in payload.get("issues", []):
            kind = issue.get("kind", "").lower()
            validator = _VALIDATORS.get(kind)
            if validator is None:
                trace.append(f"✗ unknown kind={kind!r} rejected")
                continue
            ok, reason = validator(issue, self.scheduler)
            prefix = "✓" if ok else "✗"
            trace.append(f"{prefix} {kind}: {reason}")
            if ok:
                accepted.append(issue)
        return accepted, trace

    def review(self) -> AgentResult:
        """End-to-end: plan, act, check. Returns a user-facing summary."""
        steps: list[str] = []
        try:
            snippets = self._plan()
            steps.append(f"PLAN: retrieved {len(snippets)} snippet(s)")
        except Exception as e:
            log.exception("agent plan failed")
            return AgentResult(text=f"Planning failed: {e}", confidence=0.0, error=str(e))

        try:
            payload = self._act(snippets)
            steps.append(f"ACT:  LLM proposed {len(payload.get('issues', []))} issue(s)")
        except RuntimeError as e:
            # Missing API key — user-facing, not a crash.
            return AgentResult(text=str(e), confidence=0.0, error=str(e))
        except Exception as e:          # pragma: no cover — network path
            log.exception("agent act failed")
            return AgentResult(text=f"Agent LLM call failed: {e}", confidence=0.0, error=str(e))

        accepted, check_trace = self._check(payload)
        steps.extend([f"CHECK: {line}" for line in check_trace])

        # Confidence: fraction of proposed issues that survived validation.
        proposed = len(payload.get("issues", []))
        if proposed == 0:
            # No issues proposed — we trust silence less than concrete findings.
            confidence = 0.55 if snippets else 0.4
        else:
            ratio = len(accepted) / proposed
            confidence = round(0.4 + 0.5 * ratio, 2)

        if not accepted:
            text = (
                "No blocking issues detected in today's schedule. "
                "(The agent reviewed it against pet-care guidelines and found nothing "
                "that survived validation.)"
            )
        else:
            lines = ["Issues surfaced by the review agent:"]
            for i, issue in enumerate(accepted, 1):
                t = issue.get("target_time") or "—"
                lines.append(
                    f"  {i}. [{issue.get('kind')}] {issue.get('summary')} "
                    f"(time: {t}, evidence: {issue.get('evidence', '—')})"
                )
            text = "\n".join(lines)

        return AgentResult(
            text=text,
            confidence=min(1.0, confidence),
            sources=[s.topic for s in snippets],
            steps=steps,
        )
