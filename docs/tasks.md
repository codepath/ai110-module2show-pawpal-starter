# PawPal+ Task Checklist

> Mirrors `docs/plan.md`. Every PR additionally satisfies the standing DoD:
> `uv run pytest` green · `trunk check` clean · CHANGELOG updated (scope vs main) · docs updated in-layer (user's voice) · no scratch files · issue linked via `Closes #N`.

## Phase A — Infrastructure

### PR 1 `chore-repo-hygiene`

- [x] `git rm --cached __pycache__/pawpal_system.cpython-314.pyc`
- [x] `.gitignore` += `temorary_resources/`, `.project/`, `.coverage`, `data.json`
- [x] `gt create` + verify clean `git status`

### PR 2 `docs-plan-and-guardrails`

- [x] Commit `docs/plan.md`, `docs/tasks.md`
- [x] `AGENTS.md` (guardrail rules) + `CLAUDE.md` pointer
- [x] `CHANGELOG.md` (Keep a Changelog, Unreleased)
- [x] ADR scaffold: `docs/decisions/README.md` + `template.md`

### PR 3 `chore-uv-migration`

- [x] `uv init` → pyproject (python ≥3.14)
- [x] `uv add "streamlit>=1.30"`; `uv add --dev pytest pytest-cov` (latest)
- [x] `requirements.txt` regenerated via `uv export --no-dev`
- [x] README setup: uv path + pip fallback
- [x] ADR-0001 use-uv

### PR 4 `chore-trunk-io`

- [x] Commit `.trunk/` config; enable fmt-pre-commit + check-pre-push actions
- [x] `trunk check --all` → fix everything
- [x] ADR-0002 use-trunk-io

### PR 5 `ci-github-actions`

- [x] `test.yml` (uv, cache, pytest) — `push: main` + unfiltered `pull_request`
- [x] `trunk-check.yml` — same triggers
- [x] README badges
- [x] Branch protection: require both checks (gh api)
- [x] ADR-0003 ci-pipeline
- [x] Verify checks actually run on stacked PRs

### PR 6 `chore-project-board`

- [x] Labels (category/phase/priority)
- [x] Project board + auto-add / closed→Done workflows
- [x] Issues for PRs 7–23, labeled, on board
- [x] `docs/project-management.md`

## Phase B — Design

### PR 7 `design-uml-draft`

- [x] `diagrams/uml.mmd`: 4 classes, attrs, methods, relationships
- [x] Diagram render-verified
- [x] reflection §1a (three core actions + initial design)

### PR 8 `feat-class-skeletons`

- [x] `pawpal_system.py` dataclass skeletons + docstring stubs (match UML 1:1)
- [x] Commit msg `chore: add class skeletons from UML`
- [x] AI skeleton review → reflection §1b

### PR 9 `test-bdd-framework`

- [x] `uv add --dev pytest-bdd`
- [x] `tests/` layout + `conftest.py`
- [x] ADR-0004 pytest-bdd + no-mocks e2e policy

## Phase C — Core (red → green inside each layer)

### PR 10 `feat-task-pet-owner`

- [x] Task (description, time, date, duration, frequency, completed, mark_complete, next_occurrence)
- [x] Pet (add_task, list_tasks, pending_tasks) · Owner (add_pet, get_pet)
- [x] `tests/test_pawpal.py`: completion test + task-count test
- [x] `features/task_management.feature` + steps

### PR 11 `feat-scheduler-core`

- [x] `Scheduler.all_tasks()` across pets (+ today view)
- [x] Cross-pet test (≥2 pets)
- [x] reflection §2a (constraints)

### PR 12 `feat-demo-cli`

- [x] `main.py`: 1 owner, 2 pets, 4 tasks, readable Today's Schedule
- [x] `tests/test_demo_cli.py` (subprocess e2e)
- [x] README Sample Output = captured run

### PR 13 `feat-sorting-filtering`

- [x] `sort_by_time`, `filter_by_status`, `filter_by_pet` + tests (cross-pet)
- [x] main.py: out-of-order tasks demoed sorted/filtered
- [x] README Smarter Scheduling rows (sorting, filtering) + refreshed output

### PR 14 `feat-recurring-tasks`

- [x] `complete_task()` recurrence (daily +1d, weekly +7d) + test
- [x] main.py demo + README row

### PR 15 `feat-conflict-detection`

- [x] `detect_conflicts()` warnings (cross-pet, non-crashing) + test
- [x] main.py conflict demo + README row + refreshed output
- [x] reflection §2b (tradeoff)

### PR 16 `feat-ui-integration`

- [x] app.py: session_state Owner, forms → real methods, sorted table, `st.warning` conflicts
- [x] `tests/test_app_ui.py` (AppTest e2e)
- [x] Before/after recording on PR
- [x] reflection §3a

**🔒 GATE: verify all 20 required points vs plan's Rubric → PR map**

## Phase D — Stretch

### PR 17 `feat-priority-scheduling` (+2)

- [x] Task.priority + `sort_by_priority()` (priority, then time) + tests
- [x] UI priority wired · README CLI output examples (captured)

### PR 18 `feat-next-available-slot` (+2)

- [x] `find_next_available_slot(duration)` + tests
- [x] ai_interactions.md **Agent Workflow** section (files, task, completed, corrections)
- [x] README feature row

### PR 19 `feat-persistence` (+2)

- [x] `save_to_json` / `load_from_json` (stdlib) + round-trip test (real file)
- [x] main.py + app.py sidebar hooks
- [x] README Persistence section (workflow + files modified)

### PR 20 `feat-output-formatting` (+2)

- [x] `uv add tabulate`; tabulate table + type emojis + status marks
- [x] README formatting docs (functions + libraries) + refreshed captured output

### PR 21 `docs-model-comparison` (+2)

- [x] Same rescheduling task → two models (Haiku 4.5 vs Fable 5; optional Gemini)
- [x] ai_interactions.md **Prompt Comparison** table fully filled + final decision

## Phase E — Finalization

### PR 22 `docs-final-polish`

- [x] `uml.mmd` matches final code; copy → `uml_final.mmd`
- [x] README: Features list, Demo Walkthrough steps, Testing (cmd, coverage summary, captured output, confidence ★)
- [x] reflection: §3b, §4a, §4b, §5a, §5b, §5c ALL answered
- [x] CHANGELOG release entry

### PR 23 `docs-rubric-audit`

- [ ] `docs/rubric-audit.md`: every rubric line → evidence link
- [ ] Instructions' submission checklist ticked
- [ ] Holes → `gt absorb` fixes into owning layer before submission
