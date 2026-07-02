# Changelog

All notable changes to PawPal+ are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to trunk-based development: every entry describes a
change relative to `main`.

## [Unreleased]

### Added

- Implementation plan (`docs/plan.md`), task checklist (`docs/tasks.md`), agent
  guardrails (`AGENTS.md`, `CLAUDE.md`), this changelog, and the ADR scaffold
  (`docs/decisions/`).
- uv project setup: `pyproject.toml` (streamlit runtime dep; pytest + pytest-cov
  in the dev group), `uv.lock`, and pytest configuration (ADR-0001).
- trunk.io meta-linter config (`.trunk/`) with pre-commit format and pre-push
  check hooks enabled; repo-wide lint pass now clean (ADR-0002).
- CI: `Test` and `Trunk Check` workflows with stack-safe triggers, README
  badges, an AppTest boot smoke test, and branch protection on `main`
  (ADR-0003).

### Changed

- `requirements.txt` is now a generated artifact of `uv export` (pip fallback
  for graders); README setup instructions rewritten around `uv`.

### Removed

- Accidentally committed `__pycache__/pawpal_system.cpython-314.pyc`; local-only
  paths are now gitignored.
