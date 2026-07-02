# ADR-0001: Use uv for dependency and environment management

- **Status**: accepted
- **Date**: 2026-07-02
- **Deciders**: USER, Claude
- **PR**: `chore-uv-migration`

## Context and Problem Statement

The starter ships a bare `requirements.txt` (`streamlit>=1.30`, `pytest>=7.0`) with a manual venv workflow. We need reproducible installs locally and in CI, a lockfile, and separation of runtime vs development dependencies.

## Decision Drivers

- Reproducibility: identical environments locally and in CI (lockfile).
- Speed: CI installs should be fast and cacheable.
- Dev/runtime separation: pytest and tooling must not pollute runtime deps.
- Continuity: uv was adopted in module 1 and worked well; graders may still use pip.

## Considered Options

1. uv (`pyproject.toml` + `uv.lock`, dev dependency group)
2. Keep plain `requirements.txt` + venv + pip
3. Poetry

## Decision Outcome

Chosen option: **uv**, because it gives a lockfile, dependency groups, and hermetic Python management with the fastest installs, and matches the workflow rule "always uv, never bare python/pip" (`AGENTS.md` rule 2).

`requirements.txt` is kept, but as a **generated artifact** (`uv export --no-hashes -o requirements.txt`) so pip-based graders can still `pip install -r requirements.txt`.

### Consequences

- Positive: locked, reproducible env; `uv run` removes venv-activation mistakes; CI caching via `setup-uv`.
- Negative: two dependency files must not drift — mitigated by regenerating `requirements.txt` in any PR that touches dependencies.

## Pros and Cons of the Options

### uv

- Good: lockfile, dev groups, speed, `uv run` ergonomics, module-1 continuity.
- Bad: extra tool for graders unfamiliar with it (mitigated by pip fallback docs).

### Plain pip + requirements.txt

- Good: zero new tooling.
- Bad: no lockfile, no dev/runtime separation, manual venv activation errors.

### Poetry

- Good: lockfile and groups too.
- Bad: slower, heavier config, no advantage over uv here; breaks continuity.
