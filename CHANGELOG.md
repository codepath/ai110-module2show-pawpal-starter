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
- Project tracking: labels, GitHub Project board with issues #1–#17 mapped to
  the planned PRs, documented in `docs/project-management.md`.
- UML class diagram draft (`diagrams/uml.mmd`): Task, Pet, Owner, Scheduler
  with attributes, methods, and relationships; reflection §1a documents the
  three core user actions and class responsibilities.
- `pawpal_system.py` class skeletons translated 1:1 from the UML (dataclasses,
  typed signatures, docstring stubs); reflection §1b records the design changes
  from the AI skeleton review.
- Test framework: pytest-bdd dev dependency, `tests/` layout (features,
  step_defs, shared real-object fixtures) and the no-mocks e2e testing policy
  (ADR-0004).
- Working `Task` (completion + recurrence-aware `next_occurrence`), `Pet`
  (add/list/pending tasks), and `Owner` (add/look-up pets) classes with the
  core behavior suite `tests/test_pawpal.py` and a Gherkin task-management
  feature.
- `Scheduler.all_tasks()` and `tasks_for_today()` operating across every pet
  in the household, with cross-pet tests; reflection §2a documents the
  constraint model.
- CLI demo `main.py` (one owner, two pets, four tasks, readable "Today's
  Schedule"), a subprocess end-to-end test, and the captured sample output in
  the README.
- Algorithms: `Scheduler.sort_by_time()`, `filter_by_status()`, and
  `filter_by_pet()` with cross-pet tests; demo shows sorted and filtered
  views and the README Smarter Scheduling table names the methods.
- Recurring tasks: `Scheduler.complete_task()` marks a task done and, for
  daily/weekly tasks, auto-schedules the next occurrence on the owning pet
  (tested for +1d, +7d, and one-off no-op; demoed in `main.py`).
- Conflict detection: `Scheduler.detect_conflicts()` returns advisory warnings
  for pending tasks sharing an exact date+time, across pets; reflection §2b
  documents the exact-match-vs-overlap tradeoff.
- Streamlit UI wired to the logic layer: session-state `Owner`, add-pet and
  add-task forms calling real methods, sorted schedule table with status
  filter, conflict warnings via `st.warning`, and task completion with
  recurring reschedule feedback — covered by five AppTest end-to-end tests.
- Priority-based scheduling (stretch): `Task.priority` (low/medium/high),
  `Scheduler.sort_by_priority()` (priority first, time tiebreak), a priority
  picker + "Order by" toggle in the UI, and a captured priority-view CLI
  example in the README.
- Next-available-slot finder (stretch, agent mode):
  `Scheduler.find_next_available_slot()` scans all pets' pending tasks as busy
  blocks in a 07:00–21:00 window; "Find a free slot" UI section, demo line,
  and the ai_interactions.md Agent Workflow write-up.
- JSON Persistence (stretch): `save_to_json()` and `load_from_json()` using stdlib json to save and restore household data; CLI demo, sidebar controls in the UI, and full unit/UI test coverage.
- Output formatting (stretch): `tabulate` library for aligned CLI tables,
  activity-type emojis (🦮 walks, 🥣 feeding, 💊 meds, 🩺 vet, 🐱 litter),
  and ✅/⏳ status icons; README documents the library, functions, and emoji
  mapping; sample output refreshed from real run.

### Changed

- `requirements.txt` is now a generated artifact of `uv export` (pip fallback
  for graders); README setup instructions rewritten around `uv`.

### Removed

- Accidentally committed `__pycache__/pawpal_system.cpython-314.pyc`; local-only
  paths are now gitignored.
