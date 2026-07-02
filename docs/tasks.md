# PawPal+ Task Checklist

> Mirrors `docs/plan.md`. Every PR additionally satisfies the standing DoD:
> `uv run pytest` green · `trunk check` clean · CHANGELOG updated (scope vs main) · docs updated in-layer (user's voice) · no scratch files · issue linked via `Closes #N`.

## Phase A — Infrastructure

### PR 1 `chore-repo-hygiene`

- [ ] `git rm --cached __pycache__/pawpal_system.cpython-314.pyc`
- [ ] `.gitignore` += `temorary_resources/`, `.project/`, `.coverage`, `data.json`
- [ ] `gt create` + verify clean `git status`

### PR 2 `docs-plan-and-guardrails`

- [ ] Commit `docs/plan.md`, `docs/tasks.md`
- [ ] `AGENTS.md` (guardrail rules) + `CLAUDE.md` pointer
- [ ] `CHANGELOG.md` (Keep a Changelog, Unreleased)
- [ ] ADR scaffold: `docs/decisions/README.md` + `template.md`

### PR 3 `chore-uv-migration`

- [ ] `uv init` → pyproject (python ≥3.14)
- [ ] `uv add "streamlit>=1.30"`; `uv add --dev pytest pytest-cov` (latest)
- [ ] `requirements.txt` regenerated via `uv export --no-dev`
- [ ] README setup: uv path + pip fallback
- [ ] ADR-0001 use-uv

### PR 4 `chore-trunk-io`

- [ ] Commit `.trunk/` config; enable fmt-pre-commit + check-pre-push actions
- [ ] `trunk check --all` → fix everything
- [ ] ADR-0002 use-trunk-io

### PR 5 `ci-github-actions`

- [ ] `test.yml` (uv, cache, pytest) — `push: main` + unfiltered `pull_request`
- [ ] `trunk-check.yml` — same triggers
- [ ] README badges
- [ ] Branch protection: require both checks (gh api)
- [ ] ADR-0003 ci-pipeline
- [ ] Verify checks actually run on stacked PRs

### PR 6 `chore-project-board`

- [ ] Labels (category/phase/priority)
- [ ] Project board + auto-add / closed→Done workflows
- [ ] Issues for PRs 7–23, labeled, on board
- [ ] `docs/project-management.md`

## Phase B — Design

### PR 7 `design-uml-draft`

- [ ] `diagrams/uml.mmd`: 4 classes, attrs, methods, relationships
- [ ] Diagram render-verified
- [ ] reflection §1a (three core actions + initial design)

### PR 8 `feat-class-skeletons`

- [ ] `pawpal_system.py` dataclass skeletons + docstring stubs (match UML 1:1)
- [ ] Commit msg `chore: add class skeletons from UML`
- [ ] AI skeleton review → reflection §1b

### PR 9 `test-bdd-framework`

- [ ] `uv add --dev pytest-bdd`
- [ ] `tests/` layout + `conftest.py`
- [ ] ADR-0004 pytest-bdd + no-mocks e2e policy

## Phase C — Core (red → green inside each layer)

### PR 10 `feat-task-pet-owner`

- [ ] Task (description, time, date, duration, frequency, completed, mark_complete, next_occurrence)
- [ ] Pet (add_task, list_tasks, pending_tasks) · Owner (add_pet, get_pet)
- [ ] `tests/test_pawpal.py`: completion test + task-count test
- [ ] `features/task_management.feature` + steps

### PR 11 `feat-scheduler-core`

- [ ] `Scheduler.all_tasks()` across pets (+ today view)
- [ ] Cross-pet test (≥2 pets)
- [ ] reflection §2a (constraints)

### PR 12 `feat-demo-cli`

- [ ] `main.py`: 1 owner, 2 pets, 4 tasks, readable Today's Schedule
- [ ] `tests/test_demo_cli.py` (subprocess e2e)
- [ ] README Sample Output = captured run

### PR 13 `feat-sorting-filtering`

- [ ] `sort_by_time`, `filter_by_status`, `filter_by_pet` + tests (cross-pet)
- [ ] main.py: out-of-order tasks demoed sorted/filtered
- [ ] README Smarter Scheduling rows (sorting, filtering) + refreshed output

### PR 14 `feat-recurring-tasks`

- [ ] `complete_task()` recurrence (daily +1d, weekly +7d) + test
- [ ] main.py demo + README row

### PR 15 `feat-conflict-detection`

- [ ] `detect_conflicts()` warnings (cross-pet, non-crashing) + test
- [ ] main.py conflict demo + README row + refreshed output
- [ ] reflection §2b (tradeoff)

### PR 16 `feat-ui-integration`

- [ ] app.py: session_state Owner, forms → real methods, sorted table, `st.warning` conflicts
- [ ] `tests/test_app_ui.py` (AppTest e2e)
- [ ] Before/after recording on PR
- [ ] reflection §3a

**🔒 GATE: verify all 20 required points vs plan's Rubric → PR map**

## Phase D — Stretch

### PR 17 `feat-priority-scheduling` (+2)

- [ ] Task.priority + `sort_by_priority()` (priority, then time) + tests
- [ ] UI priority wired · README CLI output examples (captured)

### PR 18 `feat-next-available-slot` (+2)

- [ ] `find_next_available_slot(duration)` + tests
- [ ] ai_interactions.md **Agent Workflow** section (files, task, completed, corrections)
- [ ] README feature row

### PR 19 `feat-persistence` (+2)

- [ ] `save_to_json` / `load_from_json` (stdlib) + round-trip test (real file)
- [ ] main.py + app.py sidebar hooks
- [ ] README Persistence section (workflow + files modified)

### PR 20 `feat-output-formatting` (+2)

- [ ] `uv add tabulate`; tabulate table + type emojis + status marks
- [ ] README formatting docs (functions + libraries) + refreshed captured output

### PR 21 `docs-model-comparison` (+2)

- [ ] Same rescheduling task → two models (Haiku 4.5 vs Fable 5; optional Gemini)
- [ ] ai_interactions.md **Prompt Comparison** table fully filled + final decision

## Phase E — Finalization

### PR 22 `docs-final-polish`

- [ ] `uml.mmd` matches final code; copy → `uml_final.mmd`
- [ ] README: Features list, Demo Walkthrough steps, Testing (cmd, coverage summary, captured output, confidence ★)
- [ ] reflection: §3b, §4a, §4b, §5a, §5b, §5c ALL answered
- [ ] CHANGELOG release entry

### PR 23 `docs-rubric-audit`

- [ ] `docs/rubric-audit.md`: every rubric line → evidence link
- [ ] Instructions' submission checklist ticked
- [ ] Holes → `gt absorb` fixes into owning layer before submission
