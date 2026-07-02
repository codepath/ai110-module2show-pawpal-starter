# PawPal+ Implementation Plan (v1)

> **Goal**: CodePath AI110 Project 2 at maximum score — 20/20 required + 10/10 stretch — using professional practices: trunk-based development with a single Graphite stack, uv, trunk.io, BDD/TDD with real end-to-end tests (no mocks), ADR governance, CI/CD, GitHub Project board, and docs updated in the same stack layer as the change they describe.
>
> **Deadline**: Monday, July 6, 2026, 9:59 AM GMT+3. Required points are locked in before any stretch work begins.

---

## Why this plan looks the way it does (module 1 post-mortem)

Module 1 scored 18/18 required but **2/10 stretch**. Every lost point was the same failure mode: _work done or half-done, but the rubric-specified evidence artifact missing at submission_ — an empty Model Comparison table, a missing README UI section, `logic_utils.py` left as `NotImplementedError` stubs, unmerged `fix-bug-*` branches. Infrastructure outran the deliverable.

This plan prevents that structurally:

1. **Rubric-first ordering.** PRs 1–16 secure all 20 required points. Stretch PRs only start after PR 16 is green.
2. **Evidence is part of the layer.** Every PR's Definition of Done lists the exact rubric evidence it must produce (README section, reflection answer, pasted real output). A layer without its evidence does not get submitted.
3. **No deferred work.** Nothing is "moved to a later milestone" once started. If a layer is descoped, its issue is closed as won't-do with a comment — never left silently open.
4. **Final audit gate.** PR 23 walks every rubric line and links the evidence. Any hole reopens work before submission.

## Core rules (see AGENTS.md for the full set)

- **gt only, uv only.** Never `git commit`/`git branch`; never bare `python`/`pip`.
- **Docs in-layer.** `reflection.md`, `ai_interactions.md`, `CHANGELOG.md`, `README.md` are updated in the same PR as the change they describe, in the **user's voice**, quoting actual prompts.
- **Real tests only.** pytest + pytest-bdd on real objects, Streamlit `AppTest` for UI, `subprocess` run of `main.py` for the CLI. No mocks, no fakes. One behavior per test, no loops/conditionals in test bodies, static `xfail` only (removed in the layer that fixes it).
- **Real output only.** Every "sample output" block in README is captured from an actual run, never hand-written.
- **Latest versions** for new deps; dev tools in the dev dependency group; existing pins untouched.
- **Every layer is releasable**: `uv run pytest` green, `trunk check` clean, no stubs above their skeleton layer, no scratch files.
- **UI-changing PRs** get before/after recordings (agent-recorded GIF, or the user records if agent recording fails).

## Target architecture

`pawpal_system.py` (logic layer — the only place business logic lives):

- `@dataclass Task` — `description: str`, `time: str` ("HH:MM"), `date: datetime.date`, `duration_minutes: int`, `frequency: str` ("once" | "daily" | "weekly"), `completed: bool = False`, `priority: str = "medium"` (added in PR 17). Methods: `mark_complete()`, `next_occurrence()` (returns the follow-up `Task` for recurring tasks, `None` otherwise).
- `@dataclass Pet` — `name`, `species`, `tasks: list[Task]`. Methods: `add_task()`, `list_tasks()`, `pending_tasks()`.
- `@dataclass Owner` — `name`, `pets: list[Pet]`. Methods: `add_pet()`, `get_pet(name)`.
- `class Scheduler` — constructed with an `Owner`; operates **across all pets**. Methods: `all_tasks() -> list[tuple[Pet, Task]]`, `sort_by_time()`, `filter_by_status()`, `filter_by_pet()`, `detect_conflicts()`, `complete_task()` (drives recurrence), and stretch: `sort_by_priority()` (PR 17), `find_next_available_slot()` (PR 18).
- Persistence (PR 19): `save_to_json(owner, path)` / `load_from_json(path)` using stdlib `json` + `dataclasses.asdict` — no serialization library.

`main.py` — CLI demo (rubric: 1 owner, 2 pets, 3+ tasks, scheduler in action, readable output). `app.py` — Streamlit UI backed by `st.session_state["owner"]`. `tests/` — `test_pawpal.py` (rubric artifact), `features/*.feature` + step defs, `test_app_ui.py` (AppTest), `test_demo_cli.py` (subprocess e2e).

## Rubric → PR map

| Rubric item                                                                       | Pts | Delivered by                       |
| --------------------------------------------------------------------------------- | --- | ---------------------------------- |
| UML: 4 classes, .mmd source                                                       | 1   | PR 7 (draft), PR 22 (final)        |
| UML: attributes + methods per class                                               | 1   | PR 7, PR 22                        |
| UML: relationships (Owner→Pet→Task)                                               | 1   | PR 7, PR 22                        |
| UML: readable, matches final code                                                 | 1   | PR 22                              |
| Task class complete + `mark_complete`                                             | 1   | PR 10                              |
| Pet class + task management                                                       | 1   | PR 10                              |
| Owner class + pets management                                                     | 1   | PR 10                              |
| Scheduler works across multiple pets                                              | 1   | PR 11                              |
| ≥2 algorithmic features                                                           | 1   | PRs 13–15                          |
| Features correct + reproducible                                                   | 1   | PRs 13–15 (tests)                  |
| Features operate across multiple pets                                             | 1   | PRs 13–15 (tests assert cross-pet) |
| main.py: owner, 2 pets, 3+ tasks                                                  | 1   | PR 12                              |
| main.py uses Scheduler algorithm                                                  | 1   | PR 13                              |
| Readable output + pasted in README                                                | 1   | PR 12 (refreshed 13–15, 20)        |
| Test file exists, ≥1 passing test                                                 | 1   | PR 10                              |
| ≥2 meaningful passing tests                                                       | 2   | PRs 10–15                          |
| README: system, classes, algorithms                                               | 1   | PRs 12–15, 22                      |
| README: run/test instructions, pytest cmd, coverage summary, passing output block | 1   | PR 22                              |
| Reflection: AI influence, accepted/rejected, verification                         | 1   | PRs 7–16 in-layer, verified PR 22  |
| SF: 3rd algorithm + Agent Workflow section                                        | +2  | PR 18                              |
| SF: JSON persistence + README workflow                                            | +2  | PR 19                              |
| SF: advanced scheduling + README CLI output                                       | +2  | PR 17                              |
| SF: output formatting + README docs                                               | +2  | PR 20                              |
| SF: model/prompt comparison in ai_interactions.md                                 | +2  | PR 21                              |

## The stack

One Graphite stack, bottom → top. Branch names are final. Each PR body links its issue with `Closes #N` so the board auto-updates on merge.

### Phase A — Infrastructure (PRs 1–6)

**PR 1 `chore-repo-hygiene`** — Remove tracked `__pycache__/pawpal_system.cpython-314.pyc` (`git rm --cached`), extend `.gitignore` (`temorary_resources/`, `.project/`, `.coverage`, `data.json`). DoD: `git status` clean, no compiled files tracked.

**PR 2 `docs-plan-and-guardrails`** — Commit `docs/plan.md` (this file), `docs/tasks.md`, `AGENTS.md`, `CLAUDE.md` (pointer to AGENTS.md), `CHANGELOG.md` (Keep a Changelog), ADR scaffold: `docs/decisions/README.md` (index) + `docs/decisions/template.md` (MADR). DoD: ADR index renders, CHANGELOG has Unreleased section.

**PR 3 `chore-uv-migration`** — `uv init` (pyproject, `requires-python >=3.14`), `uv add "streamlit>=1.30"` (respect existing pin), `uv add --dev pytest pytest-cov` (latest), `uv sync`; regenerate `requirements.txt` via `uv export` (pip-compatible graders); README setup section gets uv + pip paths; **ADR-0001 use-uv**. DoD: `uv run streamlit --version` works, `uv run pytest` exits 5 (no tests yet is OK at this layer only).

**PR 4 `chore-trunk-io`** — Commit existing `.trunk/` config, enable `trunk-fmt-pre-commit` + `trunk-check-pre-push` actions, `trunk check --all` and fix all findings, **ADR-0002 use-trunk-io**. DoD: `trunk check --all` clean.

**PR 5 `ci-github-actions`** — `.github/workflows/test.yml` (setup-uv, cache, `uv sync`, `uv run pytest`) + `trunk-check.yml` (trunk-action). Triggers: `push: [main]` **and unfiltered `pull_request`** (stack-safe — module 1 lesson). README badges. Branch protection on main requiring both checks (via `gh api`). **ADR-0003 ci-pipeline**. DoD: both workflows green on the stack PRs.

**PR 6 `chore-project-board`** — `gh label create` (category/phase/priority set), `gh project create` "PawPal+ (AI110 Module 2)" with auto-add + item-closed→Done workflows, one `gh issue create` per remaining PR (7–23) with labels, all added to the board; `docs/project-management.md` documents the scheme. DoD: board lists all issues; every later PR body carries `Closes #N`.

### Phase B — Design (PRs 7–9)

**PR 7 `design-uml-draft`** — Real `diagrams/uml.mmd` class diagram: 4 classes, attributes, methods, `Owner "1" --> "*" Pet`, `Pet "1" --> "*" Task`, `Scheduler --> Owner`. Reflection §1a (three core user actions + initial design, user's voice). DoD: diagram renders in Mermaid (verify via `npx -y @mermaid-js/mermaid-cli` or mermaid.live), reflection §1a non-empty.

**PR 8 `feat-class-skeletons`** — `pawpal_system.py` skeletons: dataclass fields + method stubs with 1-line docstrings (bodies `...`). Commit message: `chore: add class skeletons from UML`. AI reviews skeleton for missing relationships; reflection §1b documents any change made. DoD: `uv run python -c "import pawpal_system"` clean; skeletons match uml.mmd 1:1.

**PR 9 `test-bdd-framework`** — `uv add --dev pytest-bdd` (latest), `tests/` layout (`features/`, `step_defs/`, `conftest.py`), **ADR-0004 pytest-bdd + real-e2e-no-mocks testing policy**. DoD: `uv run pytest` collects (0 tests OK here), trunk clean.

### Phase C — Core implementation (PRs 10–16)

Red→green inside each layer: failing test first, then code.

**PR 10 `feat-task-pet-owner`** — Implement `Task`, `Pet`, `Owner` fully. Tests: `tests/test_pawpal.py` with the two rubric-named tests (mark_complete changes status; adding task increases pet task count) + `features/task_management.feature`. DoD: rubric rows "Task/Pet/Owner class" satisfied; tests green; docstrings on all methods.

**PR 11 `feat-scheduler-core`** — `Scheduler` with `all_tasks()` across pets + today view. Test asserts tasks from ≥2 pets are returned. Reflection §2a starts (constraints considered). DoD: cross-pet test green.

**PR 12 `feat-demo-cli`** — `main.py`: 1 owner, 2 pets, 4 tasks at different times, prints "Today's Schedule" readably. `tests/test_demo_cli.py` runs it via `subprocess` and asserts output. README "Sample Output" gets **captured** output. DoD: README block matches an actual run byte-for-byte.

**PR 13 `feat-sorting-filtering`** — `sort_by_time()` (key: HH:MM string), `filter_by_status()`, `filter_by_pet()`. main.py adds out-of-order tasks and demos both; README Smarter Scheduling rows filled with method names; sample output refreshed. Tests: chronological order across pets; filter correctness. DoD: rubric "≥2 algorithmic features" met with tests.

**PR 14 `feat-recurring-tasks`** — `Scheduler.complete_task()`: completing a daily/weekly task creates the next occurrence (`date + timedelta(days=1|7)`) on the same pet. Test: daily completion yields a task for tomorrow. main.py + README row updated. DoD: recurrence test green.

**PR 15 `feat-conflict-detection`** — `detect_conflicts()`: same-time tasks (across pets too) return warning strings, never raise. Test: two same-time tasks on different pets are flagged. main.py demos a conflict; README row + sample output refreshed. Reflection §2b (tradeoff: exact-time match vs duration overlap — resolved in PR 17's time awareness or documented as accepted). DoD: conflict test green, reflection §2b written.

**PR 16 `feat-ui-integration`** — `app.py` wired to logic layer: `Owner` in `st.session_state`, add-pet + add-task forms call real methods, schedule view uses `sort_by_time`, conflicts shown via `st.warning`, schedule via `st.table`. Tests: `tests/test_app_ui.py` with `AppTest` (add pet → add task → schedule appears sorted). **Before/after recording** attached to PR. Reflection §3a. DoD: AppTest suite green; recording on PR.

> **GATE: all 20 required points are now evidenced. Verify against the Rubric → PR map before proceeding.**

### Phase D — Stretch (PRs 17–21)

**PR 17 `feat-priority-scheduling`** (SF: advanced scheduling, +2) — `priority` on Task (low/medium/high), `sort_by_priority()` (priority desc, then time). UI select feeds it. Tests + README CLI output examples (captured). Reflection §2a extended.

**PR 18 `feat-next-available-slot`** (SF: 3rd algorithm via agent mode, +2) — `find_next_available_slot(duration_minutes)` scans the day across all pets' busy blocks. Tests. **ai_interactions.md "Agent Workflow" section** filled in user's voice: files modified, task given, what the agent completed, manual corrections. README feature row.

**PR 19 `feat-persistence`** (SF: persistence, +2) — `save_to_json`/`load_from_json` (stdlib json + `dataclasses.asdict`); main.py demos save+load; app.py sidebar save/load buttons. Test: round-trip through a real tmp file. README "Persistence" section: workflow + files modified.

**PR 20 `feat-output-formatting`** (SF: professional formatting, +2) — `uv add tabulate` (latest); main.py schedule as tabulate table + emoji per task type + ✅/⏳ status. README documents features, functions, and libraries; sample output refreshed (captured). test_demo_cli assertions updated.

**PR 21 `docs-model-comparison`** (SF: model comparison, +2) — Same task (weekly-task rescheduling logic) given to **two different models** (Claude Haiku 4.5 vs Claude Fable 5 via subagents; optionally + Gemini via Antigravity run by the user). ai_interactions.md "Prompt Comparison" table fully filled: model, prompt, useful output, flaws, final decision — user's voice, real transcripts.

### Phase E — Finalization (PRs 22–23)

**PR 22 `docs-final-polish`** — Update `diagrams/uml.mmd` to match final code exactly and save copy as `diagrams/uml_final.mmd` (instructions name both). README: Features list, Demo Walkthrough (numbered steps: add pet → schedule task → view sorted schedule → trigger conflict warning), Testing section with pytest command, coverage summary (`uv run pytest --cov`), **captured** passing output, Confidence Level (★1–5). Reflection: every remaining prompt answered — §3b, §4a, §4b, **§5a/b/c (module 1's blank sections)**. CHANGELOG release entry.

**PR 23 `docs-rubric-audit`** — `docs/rubric-audit.md`: every rubric line → evidence link (file + section/test name + PR). Submission checklist from the instructions (repo public, files present, multiple meaningful commits, reflection specific, pushed before deadline). Any hole found here reopens the owning layer via `gt absorb` — the audit does not paper over gaps.

## Pitfall register (module 1 → prevention here)

| Module 1 pitfall                                        | Prevention                                                                   |
| ------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Refactor/stubs deferred forever                         | No deferral rule; releasable-layer rule; PR 23 audit gate                    |
| Empty reflection/ai_interactions sections at submission | Docs-in-layer DoD per PR; PR 22 sweeps every prompt                          |
| README output hand-written, overstated reality          | Captured-output-only rule; subprocess CLI test keeps it honest               |
| CI skipped mid-stack PRs                                | Unfiltered `pull_request` trigger (PR 5)                                     |
| git/python used instead of gt/uv                        | AGENTS.md rules 1–2; every command in this plan is written gt/uv-first       |
| Wrong voice / fabricated prompts in logs                | User's-voice rule; quote real prompts only                                   |
| CHANGELOG logging intra-stack churn                     | Entries scoped vs main only                                                  |
| Scratch files committed                                 | Scratchpad only; trunk + review check                                        |
| Stack layers mixing concerns                            | One concern per PR as specced; `gt absorb` for fixups                        |
| Plan gutted in a "final pass"                           | Plan is committed and versioned; changes go through PRs                      |
| Submitted late                                          | Required core (PRs 1–16) targeted ≥48h before deadline; stretch is droppable |

## Execution loop (per PR)

```bash
gt create <branch-name> -m "<conventional commit>"   # after staging changes
uv run pytest                                        # green
trunk check                                          # clean
# DoD checklist from this plan verified, incl. docs-in-layer evidence
gt submit --no-interactive                           # PR with Closes #N in body
```

Fixups after review land via `gt absorb` into the owning layer, then `gt submit --stack`. The user reviews the full stack in Graphite at the end and merges bottom-up; merges close issues and move the board automatically.
