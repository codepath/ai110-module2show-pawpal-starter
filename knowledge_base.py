"""
Pet-care knowledge base with a tiny retrieval layer (RAG).

Why a hand-rolled retriever?
  - The corpus is small (~15 curated snippets) and we want zero extra
    dependencies — a TF-like scorer is plenty.
  - Retrieval is deterministic, so tests can assert exact ordering.

Each snippet has a `topic`, `tags` (helps keyword match), and `text` that
is eventually injected into the LLM prompt as grounding context.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from logger_setup import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class Snippet:
    topic: str
    tags: tuple[str, ...]
    text: str


# ── Curated pet-care corpus ────────────────────────────────────────────────
# Sources: ASPCA general guidance, AVMA wellness notes, AAHA nutrition.
# Kept intentionally short — these are grounding cues for the model,
# not a full veterinary reference.

_CORPUS: list[Snippet] = [
    Snippet(
        "dog-exercise",
        ("dog", "walk", "exercise", "energy", "morning"),
        "Adult dogs generally need 30–60 minutes of structured exercise per day, "
        "ideally split across two walks. Morning walks help burn overnight energy "
        "and reduce destructive behavior later in the day.",
    ),
    Snippet(
        "dog-feeding",
        ("dog", "feed", "feeding", "meal", "nutrition"),
        "Most adult dogs do best with two meals per day, spaced 8–12 hours apart. "
        "Avoid heavy exercise in the 60 minutes immediately after a large meal to "
        "reduce bloat risk, especially in deep-chested breeds.",
    ),
    Snippet(
        "cat-feeding",
        ("cat", "feed", "feeding", "meal", "nutrition"),
        "Cats are obligate carnivores and usually prefer several small meals "
        "throughout the day. Fresh water should always be available, ideally in "
        "a location separate from the food bowl.",
    ),
    Snippet(
        "cat-enrichment",
        ("cat", "play", "playtime", "enrichment", "indoor"),
        "Indoor cats need at least 15–20 minutes of interactive play per day to "
        "satisfy hunting instincts. Short bursts of play before meals mimic the "
        "natural hunt–eat–groom–sleep cycle.",
    ),
    Snippet(
        "medication-timing",
        ("medicine", "medication", "meds", "pill", "dose"),
        "Give daily medications at the same time each day (±1 hour is fine). "
        "Missed doses should generally be taken when remembered unless it's near "
        "the next scheduled dose — never double up without a vet's instruction.",
    ),
    Snippet(
        "grooming-cadence",
        ("groom", "grooming", "brush", "bath", "coat"),
        "Short-haired dogs and cats benefit from a weekly brush; long-haired "
        "breeds usually need brushing 2–3 times per week to prevent matting. "
        "Over-bathing strips natural oils — aim for no more than monthly unless "
        "a vet recommends otherwise.",
    ),
    Snippet(
        "walk-weather",
        ("walk", "weather", "heat", "cold", "pavement"),
        "Pavement above ~50°C (120°F) can burn paw pads — test with the back of "
        "your hand for 7 seconds. In hot weather, shift walks to early morning "
        "or late evening and always bring water.",
    ),
    Snippet(
        "puppy-schedule",
        ("puppy", "young", "training", "potty"),
        "Puppies under 6 months need potty breaks every 2–3 hours while awake, "
        "plus after meals, naps, and play. A consistent schedule accelerates "
        "house-training more than any single training technique.",
    ),
    Snippet(
        "senior-care",
        ("senior", "old", "elderly", "arthritis", "geriatric"),
        "Senior pets (7+ for large dogs, 10+ for cats) benefit from shorter but "
        "more frequent walks, joint-friendly surfaces, and twice-yearly vet "
        "checks. Watch for subtle signs of arthritis: stiffness after rest, "
        "reluctance on stairs, decreased grooming.",
    ),
    Snippet(
        "sleep-schedule",
        ("sleep", "rest", "night", "routine", "bedtime"),
        "Dogs sleep 12–14 hours per day; cats sleep 12–16. Scheduling the last "
        "walk or play session 1–2 hours before bedtime helps pets settle for "
        "the night and reduces nighttime waking.",
    ),
    Snippet(
        "conflict-resolution",
        ("conflict", "multi-pet", "household", "time", "overlap"),
        "When two pets need care at the same time, prioritize medical tasks "
        "(medication, wound care) first, then time-sensitive tasks (feeding, "
        "potty), then enrichment. Even a 10–15 minute offset can eliminate "
        "rushed, low-quality care.",
    ),
    Snippet(
        "hydration",
        ("water", "hydration", "drink", "thirst"),
        "A rough hydration target is about 30 ml of water per kilogram of body "
        "weight per day. Refresh bowls at least once daily — stale water is a "
        "common reason pets under-drink, especially cats.",
    ),
    Snippet(
        "vet-visits",
        ("vet", "checkup", "visit", "annual", "vaccine"),
        "Healthy adult pets should see a vet annually; seniors every six "
        "months. Bring a short list of behavioral or appetite changes — owners "
        "notice patterns a 20-minute exam cannot.",
    ),
    Snippet(
        "training-reinforcement",
        ("training", "reinforcement", "reward", "behavior", "treat"),
        "Positive reinforcement (food, praise, play) within 1–2 seconds of the "
        "behavior is far more effective than delayed rewards or punishment. "
        "Short 5-minute training sessions several times a day outperform one "
        "long session.",
    ),
    Snippet(
        "bird-routine",
        ("bird", "parrot", "cage", "out-of-cage"),
        "Companion birds need 2–4 hours of supervised out-of-cage time daily "
        "for mental stimulation. Rotate toys weekly and keep feeding times "
        "consistent — birds are highly routine-driven.",
    ),
]


# ── Retrieval ──────────────────────────────────────────────────────────────

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _score(query_tokens: Iterable[str], snippet: Snippet) -> float:
    """
    Simple relevance score: tag hits (weighted) + body token hits.
    Tag matches are weighted 3x because tags were hand-curated keywords.
    """
    q = set(query_tokens)
    if not q:
        return 0.0
    tag_hits = sum(1 for t in snippet.tags if t in q)
    body_tokens = set(_tokenize(snippet.text))
    body_hits = len(q & body_tokens)
    return 3.0 * tag_hits + body_hits


def retrieve(query: str, *, k: int = 3, min_score: float = 1.0) -> list[Snippet]:
    """
    Return the top-k snippets whose score clears `min_score`.

    `min_score` prevents the model from being fed unrelated context when the
    query doesn't match anything in the corpus — better to ground on nothing
    than on noise.
    """
    tokens = _tokenize(query)
    scored = [(_score(tokens, s), s) for s in _CORPUS]
    scored = [(score, s) for score, s in scored if score >= min_score]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = [s for _, s in scored[:k]]
    log.info("RAG retrieve(%r, k=%d) -> %d hit(s): %s",
             query, k, len(top), [s.topic for s in top])
    return top


def format_context(snippets: list[Snippet]) -> str:
    """Render retrieved snippets into a numbered block for prompt injection."""
    if not snippets:
        return "(no relevant guidance found in knowledge base)"
    parts = []
    for i, s in enumerate(snippets, start=1):
        parts.append(f"[{i}] {s.topic}: {s.text}")
    return "\n".join(parts)


def corpus_size() -> int:
    """Exposed for tests + the reliability dashboard."""
    return len(_CORPUS)


def all_topics() -> list[str]:
    return [s.topic for s in _CORPUS]
