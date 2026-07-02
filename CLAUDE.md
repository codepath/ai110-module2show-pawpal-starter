# PawPal+ (AI110 Module 2)

Read `AGENTS.md` for the binding workflow rules (gt-only, uv-only, docs-in-layer, real tests, evidence integrity).

## Current Status

- Plan: `docs/plan.md` (v1) · Checklist: `docs/tasks.md` — update the checklist as PRs land.
- Goal: 20/20 required + 10/10 stretch. Deadline: 2026-07-06 09:59 GMT+3.

## Build Commands

- Setup: `uv sync`
- App: `uv run streamlit run app.py`
- Demo: `uv run python main.py`
- Tests: `uv run pytest` (coverage: `uv run pytest --cov`)
- Lint: `trunk check`

## Architecture

- `pawpal_system.py` — all logic: `Task`/`Pet`/`Owner` dataclasses + `Scheduler` (cross-pet algorithms). UI (`app.py`) and demo (`main.py`) only call this layer.
- Tests: `tests/test_pawpal.py` (rubric artifact), `tests/features/` + `step_defs/` (pytest-bdd), `tests/test_app_ui.py` (AppTest), `tests/test_demo_cli.py` (subprocess).
- Decisions: `docs/decisions/` (MADR ADRs).
