"""
Centralized logging + lightweight guardrails for PawPal+.

Every AI-facing call (RAG retrieval, agent steps, evaluator runs) should go
through `get_logger(__name__)` so a single `pawpal.log` file captures an audit
trail. The guardrail helpers short-circuit unsafe or ill-formed inputs before
they reach the LLM.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Optional

_LOG_PATH = Path(os.environ.get("PAWPAL_LOG_FILE", "pawpal.log"))
_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """Return a module logger wired to a shared file + console handler."""
    global _CONFIGURED
    if not _CONFIGURED:
        handlers: list[logging.Handler] = [logging.StreamHandler()]
        try:
            handlers.append(logging.FileHandler(_LOG_PATH, encoding="utf-8"))
        except OSError:
            # Read-only FS (e.g. some sandboxes) — console only is fine.
            pass
        logging.basicConfig(
            level=os.environ.get("PAWPAL_LOG_LEVEL", "INFO"),
            format=_FORMAT,
            handlers=handlers,
        )
        _CONFIGURED = True
    return logging.getLogger(name)


# ── Input guardrails ──────────────────────────────────────────────────────────
# These run *before* any user text reaches the LLM. They're intentionally
# small and deterministic — the goal is a first line of defense, not a full
# content moderation stack.

_MAX_INPUT_CHARS = 2000
_BLOCKLIST_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
    re.compile(r"system\s*prompt", re.I),
    re.compile(r"(?:api[_\s-]?key|secret|token)\s*[:=]", re.I),
]


class GuardrailError(ValueError):
    """Raised when user input fails a basic safety/shape check."""


def sanitize_user_text(text: Optional[str], *, label: str = "input") -> str:
    """
    Strip, length-check, and prompt-injection-screen a free-text field.

    Returns the cleaned string. Raises GuardrailError on violation so callers
    can surface a user-visible message instead of silently sending bad data
    to the model.
    """
    log = get_logger("pawpal.guardrails")
    if text is None:
        raise GuardrailError(f"{label} is required")
    cleaned = text.strip()
    if not cleaned:
        raise GuardrailError(f"{label} cannot be empty")
    if len(cleaned) > _MAX_INPUT_CHARS:
        log.warning("Rejected %s: over %d chars (%d)", label, _MAX_INPUT_CHARS, len(cleaned))
        raise GuardrailError(f"{label} is too long ({len(cleaned)} > {_MAX_INPUT_CHARS} chars)")
    for pattern in _BLOCKLIST_PATTERNS:
        if pattern.search(cleaned):
            log.warning("Guardrail blocked %s: matched %s", label, pattern.pattern)
            raise GuardrailError(
                f"{label} looks like a prompt-injection attempt and was rejected"
            )
    return cleaned
