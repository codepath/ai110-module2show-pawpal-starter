# PawPal+ — AI110 Applied AI System

PawPal+ helps a pet owner keep track of care tasks across multiple pets. The original Streamlit application let owners add pets and tasks, edit and complete tasks, find free time, and generate a daily plan. The AI110 extension answers general care questions from attributed local references and suggests new tasks for the owner's existing pets. The deterministic `Scheduler` decides whether suggested tasks fit the owner's time budget. AI suggestions never add, complete, delete, or save a task.

## AI110 features and scope

| Original application | AI extension |
| --- | --- |
| Owner, pets, tasks, recurrence, filters, conflict warnings, priority and time-budget plans | Multi-source local retrieval, structured Gemini answers with validated citations, and review-only care-task proposals |
| Explicit local JSON Save/Load | Observable planning trace and deterministic validation of proposed tasks using a copy of the owner |

Target users are individual pet owners planning routine care. The AI assistant is for general education and scheduling ideas, not veterinary diagnosis or treatment. The app runs without an API key; all original scheduling and storage controls continue to work.

### Technology and files

Python 3.10+, Streamlit, `google-genai`, pytest, Mermaid, and standard-library JSON make up the stack. `app.py` provides the UI; `pawpal_system.py` owns deterministic scheduling; `persistence.py` saves local data. `ai/retriever.py` ranks local text chunks; `ai/gemini_client.py` handles grounded answers; `ai/planner.py` builds validated, review-only proposals; `ai/knowledge/` contains attributed notes. The [architecture diagram](diagrams/architecture.mmd) separates AI and scheduling paths. [Model card](model_card.md), [AI interaction evidence](ai_interactions.md), and [reflection](reflection.md) document behavior and limits.

### Install and run

From the directory containing `app.py`:

```bash
python -m venv .venv
# PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The AI features need a Gemini API key in the `GEMINI_API_KEY` environment variable. Set it in your shell before starting Streamlit. Do not put the key in a file tracked by Git.

```powershell
$env:GEMINI_API_KEY = "your-key-here"
python -m streamlit run app.py
```

On macOS/Linux, use `export GEMINI_API_KEY="your-key-here"`. Without a key, the AI controls explain that configuration is missing; pet and schedule features still work. The model is `gemini-3.1-flash-lite`, with a 12-second SDK request timeout and one model call per submitted question or proposal. Provider availability and latency can vary.

### Try the app

1. Add a dog named Mochi and optionally create a few care tasks. Set **Available minutes** and generate a schedule.
2. Ask: “How should I plan dog exercise and fresh water on a warm day?” The answer should include local chunk IDs and links under **View cited knowledge sources** when Gemini returns a valid response.
3. Request: “Suggest a short dog exercise and water routine for Mochi on a warm day.” Review the proposed tasks, their budget results, cited sources, and **Planning steps**. Add any useful tasks yourself with **Add task**.
4. Try “quantum spaceship,” an empty question, or “My dog swallowed poison” to see knowledge and safety fallbacks.

The AI path is: user → Streamlit → request handler → local retriever → knowledge chunks → Gemini → validated answer and sources. The planning path also copies current owner data, validates each proposed task, and asks the existing Scheduler whether it fits today's shared budget. The scheduler's own plan and explicit JSON Save/Load remain separate.

### Guardrails and evaluation

Empty and overlong requests, obvious prompt-injection attempts, possible emergencies, and requests for diagnosis or dosage stop before Gemini. A request with no matching knowledge or no key gets an explicit fallback. Gemini errors and timeouts return a generic message without exposing exception text. The model receives only retrieved notes and relevant owner-provided planning context. JSON output must have cited IDs that match retrieved chunks; invalid citations, unsafe dosage text, and invalid proposed tasks are rejected. The source-term check and citation validation reduce risk but cannot prove that every generated sentence is medically or factually correct. Seek a veterinarian for health concerns.

Run the full suite and the separate deterministic AI evaluation harness:

```bash
python -m pytest -p no:cacheprovider
python -m ai.evaluate
```

The AI evaluation currently has **23 passing deterministic cases** using mocked model output. They cover relevant answers, empty and irrelevant input, absent key, injection, veterinary boundaries, API failures, citations, species retrieval, proposal validation, budget rejection, UI wiring, and no mutation. The earlier 150-case scheduler/UI suite and five initial retrieval tests are preserved. The full project suite passed **178 tests** on November 5, 2026 UTC using a fresh temporary directory. The [live comparison record](docs/ai_live_comparison.json) contains real calls: a direct model answer without local citations, a grounded answer citing `dog_care:0` and `dog_care:1`, and a planning run whose three proposals fit a 30-minute demo budget. The direct answer was capped at 200 output tokens and ended mid-sentence; this single example does not establish general model superiority. A fresh live run is optional: `python -m ai.compare` requires a key and writes a new comparison record only after the baseline and grounded calls succeed. On this Windows workspace, the older `.pytest_temp` directory was inaccessible to pytest cleanup; use the default temp location or a fresh `--basetemp` path if you see that setup error.

[Exact verification commands and outcomes](docs/ai_verification.md) distinguish mocked evaluation, full tests, app startup, Mermaid parsing, and live-model calls.

### Bonus features and limits

1. **Custom multi-source RAG:** local AVMA and ASPCA notes carry titles, URLs, and stable chunk IDs; ranking ignores common words and filters explicit dog/cat queries. The comparison record shows the observed baseline/RAG difference.
2. **Multi-step workflow:** request interpretation, retrieval, owner context inspection, Gemini proposal, task validation, Scheduler budget check, and a user-review trace. The live trace is in `docs/ai_live_comparison.json`.
3. **Model specialization:** fixed PawPal behavior, constrained JSON fields, citation checks, and care-plan limits are described in `model_card.md`.
4. **Automated evaluation:** `python -m ai.evaluate` runs 23 deterministic scenarios in `tests/test_ai_evaluation.py`; live-model observations are reported separately.

The knowledge base is intentionally small and can miss relevant questions. Keyword matching is weaker than semantic retrieval. The plan checks a shared minute budget; it does not reserve appointment times, check every interval conflict, or persist AI proposals. Local JSON storage is designed for one owner on a local machine. The UI should receive a manual browser and accessibility review before submission. For source details, see the notes in `ai/knowledge/` and the [AVMA warm-weather guide](https://avma.org/resources/pet-owners/petcare/warm-weather-pet-safety), [AVMA ownership guide](https://ebusiness.avma.org/files/productdownloads/Responsible-Pet-Ownership-EnglishColor.pdf), [ASPCA cat nutrition guide](https://www.aspca.org/pet-care/cat-care/cat-nutrition-tips), [ASPCA enrichment article](https://www.aspca.org/news/home-tips-keeping-your-pets-busy-and-engaged), and [ASPCA poisoning guidance](https://www.aspca.org/news/what-do-if-your-pet-poisoned).

## Historical Module 2 project documentation

**PawPal+** is a Streamlit app that helps an owner plan care tasks across multiple pets.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

The project follows a design-first workflow: UML, Python scheduling logic, and a connected Streamlit UI.

## Implementation Summary

### Architecture

The [final system architecture UML](diagrams/uml_final.mmd) shows the four classes, their attributes and methods, and their relationships. Owner manages pets, Pet contains tasks, and Scheduler uses their information without inheritance. The Streamlit UI calls these backend methods and keeps the objects in session state.

The original design is retained in [uml_draft.mmd](diagrams/uml_draft.mmd); [uml.mmd](diagrams/uml.mmd) mirrors the final diagram for graders looking at the default filename.

The logic layer in `pawpal_system.py` uses four classes. `Task` stores an activity's name, duration, priority, recurrence, last completion date, optional scheduled time, and optional due date. Its `completed` property reports whether completion has ever been recorded; `is_due(on_date)` checks whether the task is pending and its due date is absent or on/before that day. `Pet` manages its tasks, and `Owner` manages pets. `Owner.get_all_tasks()` returns `(pet, task)` pairs so tasks stay associated with their pets.

`Scheduler.generate_plan(owner, on_date=None)` retrieves all tasks through that Owner method, orders them by priority, and fits whole tasks into one shared time budget. The short-task preference breaks ties within a priority; otherwise, collection order is preserved. Tasks that do not fit or are not due are skipped with reasons, and the scheduler continues checking other tasks. One-time, daily, and weekly tasks are supported, and generating a plan does not mark tasks complete.

The plan is a dictionary with `selected`, `skipped`, `total_minutes`, and `remaining_minutes`. Each selected or skipped entry contains `pet`, `task`, and `reason`. The plan allocates a total time budget; it does not assign or enforce appointment times. Chronological sorting and conflict detection are separate methods, so the plan dictionary stays unchanged.

The backend has no Streamlit dependency. The app in `app.py` connects task entry, pending-task editing, sorting, filtering, completion, conflict warnings, schedule generation, and free-time search to the backend. Live objects stay in session state; explicit JSON Save/Load controls preserve data between runs. Adding pets or tasks, saving changed task details, completing tasks, loading data, or changing scheduling settings clears the saved plan so it can be regenerated. Run the app with `streamlit run app.py`.

Task inputs and owner scheduling settings are validated when created or updated through their methods. `main.py` demonstrates the system, and `tests/test_pawpal.py` checks completion, task addition, multi-pet scheduling through the Owner accessor, priorities, time limits, recurrence, and validation.

## Features

- Add multiple pets and create tasks for a selected pet with a duration, priority, optional scheduled `HH:MM` time, and optional due date.
- Generate today's plan across all pets using one time budget, priority ordering, and an optional preference for shorter tasks when priorities match. See selected tasks, skipped-task reasons, and time totals.
- Browse tasks automatically sorted by scheduled time, with untimed tasks last; filter by full pet name (ignoring case) and completion status.
- Choose `once`, `daily`, or `weekly` recurrence. Use **Complete today** buttons to record completion and automatically create the next daily or weekly occurrence.
- See readable warnings for pending tasks with identical start times on the same effective date, including tasks belonging to different pets. Warnings check all tasks regardless of the display filters.
- Edit a specific pending task in a form and save its title, duration, priority, recurrence, optional time, and due date together. Numbered labels distinguish tasks with matching names.
- Save and load pets, tasks, completion history, and owner settings as JSON between runs.
- Find the earliest available interval for an additional task, accounting for overlapping timed tasks across pets.
- Use validated inputs and 150 pytest cases: the original 97 backend tests, 19 frozen editor tests, and 34 bonus-feature tests. Task removal remains a backend method.

## Bonus rubric evidence

| Category | Implementation and evidence |
| --- | --- |
| Advanced algorithm via Agent Mode | `Scheduler.next_available_slot()` searches occupied intervals; the [Agent Workflow](ai_interactions.md#agent-workflow-sf7) records the request, files, completion, and corrections. |
| Data persistence | Versioned JSON `save_owner()` / `load_owner()` in `persistence.py`, Streamlit controls, and restart/failure tests. Workflow below. |
| Advanced scheduling | Priority/time-budget planning plus duration-aware free-slot search; actual CLI examples below. |
| Professional formatting | Streamlit tables, columns, forms, headings, emoji and status messages; specific APIs documented below. |
| Prompt comparison | [Structured Strategy A/B comparison](ai_interactions.md#prompt-comparison-sf11) and preserved evidence. The experiment remains a tie; A was selected for its form experience. |

## Saving and loading data

1. Add pets/tasks, submit pending-task edits with **Save changes**, and set your scheduling preferences.
2. At the bottom, click **Save data**. This writes `data/pawpal.json` relative to the project, using UTF-8 JSON. Saving again replaces the previous save.
3. Close and restart the app with `streamlit run app.py`. Click **Load saved data** to restore the saved owner, pets, tasks, and settings. Loading is explicit, not automatic.
4. Loading replaces the current session's data and discards unsaved changes and editor drafts. Generate the schedule again afterward. Save again after further changes you want to keep.

The save includes owner name, time budget and short-task preference; pet name/species/breed; and every task's title, duration, priority, recurrence, scheduled time, due date and completion date. Dates use ISO `YYYY-MM-DD`, absent values use JSON `null`, and schema version is `1`. Plans and widget state are recomputed rather than stored. Names need not be unique; pet/task order and associations survive loading.

Loading validates the entire document before replacing live data. Missing, malformed or unsupported saves show an error and leave the session intact. Saving validates before writing and replaces the file atomically using a temporary file in the same directory; a failed replacement preserves the previous save. The file must be on writable storage. This is single-owner local storage, shared by sessions on the same server; it has no accounts, locking, cloud backup, or merge support. The last successful save wins. Back up the JSON yourself if needed, and use persistent disk if deploying to a host whose local files are temporary. `/data/` is ignored by Git to keep personal pet data out of the repository.

Persistence files added/modified: `persistence.py` (standard-library `json`, `pathlib`, `tempfile`, `os` and dataclass serialization), `app.py` (Save/Load and state reset), `.gitignore` (private data), and `tests/test_bonus_features.py` (round trips, a separate-process load, validation, failed writes, and UI restoration). No additional package is required.

## Finding the next available slot

Under **Find a free time**, choose a date, minutes needed and a same-day window, then click **Find next available slot**. Times use 24-hour `HH:MM`; the window end may be `24:00`. Enter the suggestion and search date when adding or editing a task. The search treats existing timed tasks, including the task being edited, as reservations; it is intended to find room for an additional task and does not automatically move or reserve anything.

`Scheduler.next_available_slot()` collects all pets' pending timed intervals, sorts them by start and scans for the earliest gap of sufficient length. After an overlap, it moves the candidate start to the occupied interval's end. Nested and overlapping reservations are handled in the same scan. Touching endpoints are allowed. Completed and untimed tasks reserve no time. A dated task uses its due date; an undated task uses the search date. Earlier dated tasks can spill past midnight into the search day. Overdue appointments are not automatically moved to today, and future recurring occurrences are not invented. The window itself cannot cross midnight. Runtime is O(n log n), with O(n) additional space.

The existing priority/budget plan and identical-start warning keep their original behavior. This new search accounts for duration overlaps when suggesting free space, but it does not repair existing conflicts or make the generated priority plan enforce appointment times.

Actual output from `python main.py` after the existing demos:

```text
Next Available Slot Demo (09:00-11:00)
Reserved: Biscuit 09:00-09:30; Mochi 09:15-09:45 and 10:00-10:15
- 15 minutes: 09:45
- 20 minutes: 10:15
- 60 minutes: No available slot
```

## UI and output formatting

| Feature | Functions / library used |
| --- | --- |
| Pet, browse, selected-task and skipped-task tables with named columns | Streamlit `st.table()` in `app.py` |
| Grouped fields and batch editing | `st.columns()`, `st.form()`, `st.form_submit_button()` |
| Page hierarchy, guidance and paw emoji | `st.set_page_config()`, `st.title()`, `st.subheader()`, `st.markdown()`, `st.caption()`, `st.expander()`, `st.divider()` |
| Explicit validation, completion and storage feedback | `st.error()`, `st.warning()`, `st.success()`, `st.info()` |
| Numbered CLI plan, priority/status labels, time totals and skipped reasons | Python f-strings, `enumerate()` and `print()` in `main()` and `print_tasks()` in `main.py` |

The formatting uses the existing Streamlit dependency and Python standard library; no `tabulate` or terminal-color dependency is needed. Automated AppTest checks exercise the controls and output. Visual layout and keyboard accessibility have not received a manual browser review.

## Editing pending tasks

1. Add a pet and a task, then find **Edit a pending task** above **Browse tasks**.
2. Choose **Pending task to edit**. This selector includes pending tasks across all pets, regardless of browse filters; completed tasks cannot be edited.
3. Change the prefilled title, positive whole-minute duration, priority, recurrence (`once`, `daily`, or `weekly`), scheduled time, or due date. Use 24-hour `HH:MM` for the time. Clear the time or date to remove that optional value.
4. Click **Save changes** to submit the form. Switching to another task discards unsaved edits. Invalid submitted values show an error and leave the task unchanged.

A successful change keeps the same task and pet, updates the browse order and same-time warnings immediately, and clears the cached plan. Click **Generate schedule** again to use the edited details. An unchanged save retains the plan. Editing recurrence does not create another task; completing a daily or weekly task later creates its next occurrence through the existing completion workflow.

The editor uses Strategy A from the [prompt comparison](docs/prompt_comparison.md), selected for its form-based editing experience after the experiment ended in a tie.

## Getting started

### Setup

Use Python 3.10 or newer. Final checks used Python 3.13.7, Streamlit 1.60.0, and pytest 9.1.1; `requirements.txt` pins those tested package versions. Run these commands from the directory containing `app.py`:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run the terminal demo with `python main.py`. Its first demo creates an owner with two pets and four tasks. **Sample excerpt from an actual run:** the opening output is shown below; separate sorting/filtering, recurring-task, and conflict demos follow.

```text
Today's Schedule
Owner: Jordan | Available time: 40 min

1. Mochi: Feeding (5 min) [high]
   High priority; fits the remaining time.
2. Biscuit: Morning walk (25 min) [high]
   High priority; fits the remaining time.
3. Mochi: Playtime (10 min) [medium]
   Medium priority; fits the remaining time.

Planned: 40 min | Remaining: 0 min

Skipped:
- Biscuit: Grooming - Needs 20 min; only 0 min remain.
```

## Testing PawPal+

Run the full pytest suite from the project directory:

```bash
python -m pytest

# Optional coverage report (requires pytest-cov):
pytest --cov
```

The tests cover chronological sorting (including minutes, tied times, and untimed tasks), filtering by pet and completion status, daily/weekly recurrence chains, and exact same-time conflict detection across pets and dates. They also check duplicate prevention by object identity, strict owner-setting validation, and rejected updates leaving settings unchanged. Edge cases include empty inputs, zero time budgets, invalid task details and times, completed tasks, repeated completion, leap days, and year changes.

The current suite contains the unchanged original 97 backend cases, 19 frozen UI acceptance cases in `tests/test_pending_task_editing.py`, and 34 additional cases in `tests/test_bonus_features.py`. The frozen UI cases exercise real backend objects through Streamlit AppTest: task selection, draft switching, atomic saves, identity preservation, optional-field clearing, plan invalidation, sorting, warnings, recurrence, stale submissions, and empty states. Bonus tests cover persistence across processes, corrupt data, atomic save failure, date and interval boundaries, exhaustive small interval comparisons, and UI Save/Load/free-slot flows. AppTest is not a visual browser review.

Run the suites separately or together without generating pytest cache files:

```bash
python -m pytest tests/test_pawpal.py -p no:cacheprovider
python -m pytest tests/test_pending_task_editing.py -p no:cacheprovider
python -m pytest tests/test_bonus_features.py -p no:cacheprovider
python -m pytest -p no:cacheprovider
```

Strategy A integration verification on October 11, 2026 passed all 97 backend cases, all 19 acceptance cases, and all 116 cases together. The CLI demo and syntax checks also passed. [Actual integration commands and output](docs/prompt_comparison/integration-verification.json) are recorded separately from the experiment's original runs.

The earlier submission-readiness run on October 11, 2026 passed all 116 then-existing tests, the CLI demo, syntax checks, and staged/unstaged diff checks. Historical pytest output excerpt:

```text
============================ 116 passed in 20.11s =============================
```

See the [historical audit](docs/submission_readiness.md) and [recorded verification output](docs/submission-verification.json). The subsequent bonus-feature run passed **150 tests in 12.88s**, including all original 116. Its results and limits are recorded separately in [bonus verification](docs/bonus_verification.md). Personal paths in public logs are replaced with labelled placeholders; test outcomes are unchanged.

Terminal output from the successful `python -m pytest` run for Phase 5 (historical 97-case run; the personal root path below is redacted):

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: <USER_HOME>\Downloads\ai110-module2show-pawpal-starter-main\ai110-module2show-pawpal-starter
plugins: anyio-4.12.1
collected 97 items

tests\test_pawpal.py ................................................... [ 52%]
..............................................                           [100%]

============================= 97 passed in 0.13s ==============================
```

This run completed without Windows cache-permission errors; no fallback was needed. If cache permissions interfere with a later run, use `python -m pytest -p no:cacheprovider` to run the same tests without pytest's cache plugin.

**Confidence Level: 4/5 stars (★★★★☆).** The 150 tests provide coverage for the implemented behaviors. The exact-time warning does not report all duration overlaps; the separate free-slot search accounts for them when finding an available interval. Automated UI checks do not verify every browser interaction, visual layout, or accessibility concern. JSON storage is local and intended for one owner.

## Smarter Scheduling

These four features are implemented in `pawpal_system.py`, available in the Streamlit UI, and demonstrated in `main.py`:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Chronological sorting | `Scheduler.sort_tasks_by_time(task_pairs)` | Returns a new list ordered by scheduled `HH:MM` time (24-hour format). Untimed tasks go last, and ties keep their original order. This sorts by time of day, not due date. |
| Filtering | `Scheduler.filter_tasks(owner, pet_name=None, completed=None)` | Returns matching `(pet, task)` pairs. Pet names match exactly, ignoring case. Use `completed=True` for completed tasks, `False` for pending tasks, or `None` for either. Both filters can be combined. |
| Recurring tasks | `Pet.complete_task(task, on_date=None)` | Marks an owned task complete and automatically adds and returns its next pending occurrence: one day after completion for `daily`, seven days for `weekly`. The original stays completed; the new task keeps its care details and scheduled time. One-time tasks and repeated completion calls create no new occurrence. The completion date defaults to today. |
| Conflict detection | `Scheduler.detect_conflicts(task_pairs, on_date=None)` | Returns one readable warning per group of pending tasks with an identical starting time on the same effective date, including tasks across pets. Uses each task's due date, otherwise the planning date (default: today). Ignores completed and untimed tasks, returns `[]` when none conflict, and never changes tasks. |

Use `Owner.get_all_tasks()` to collect pairs for sorting or conflict detection. Use `Pet.complete_task()` for recurring tasks; `Task.mark_complete()` only records completion and does not create a next occurrence.

Conflict detection checks **identical start times on the same effective date only**, not overlapping durations. The effective date is the task's due date when set, otherwise the planning date (today in the UI). For example, 09:00–09:30 and 09:15–09:45 do not trigger a warning. It reports conflicts without deleting or rescheduling tasks and runs separately from `generate_plan()`.

### Python example

Run this from the project directory, where `pawpal_system.py` can be imported:

```python
from datetime import date
from pawpal_system import Owner, Pet, Scheduler, Task

day = date(2026, 10, 11)
dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
owner = Owner("Jordan", pets=[dog, cat])
scheduler = Scheduler()
grooming = Task("Grooming", 15, recurrence="weekly", scheduled_time="09:00")
feeding = Task("Feeding", 5, recurrence="daily", scheduled_time="09:00")
dog.add_task(grooming)
cat.add_task(Task("Playtime", 10, scheduled_time="18:00"))
cat.add_task(feeding)

pairs = scheduler.sort_tasks_by_time(owner.get_all_tasks())
print([task.name for pet, task in pairs])  # ['Grooming', 'Feeding', 'Playtime']
pending = scheduler.filter_tasks(owner, pet_name="MOCHI", completed=False)
print([task.name for pet, task in pending])  # ['Playtime', 'Feeding']
for warning in scheduler.detect_conflicts(pairs, on_date=day):
    print(warning)  # Warns about Biscuit's Grooming and Mochi's Feeding at 09:00.

next_feeding = cat.complete_task(feeding, on_date=day)
next_grooming = dog.complete_task(grooming, on_date=day)
print(next_feeding.due_date, next_grooming.due_date)  # 2026-10-12 2026-10-18
done = scheduler.filter_tasks(owner, completed=True)
print([task.name for pet, task in done])  # ['Grooming', 'Feeding']
print(scheduler.detect_conflicts(owner.get_all_tasks(), on_date=day))  # []
```

The last call returns no warnings because the original tasks are completed and their next occurrences have different due dates.

## Demo Walkthrough

1. After setup, run `streamlit run app.py` from the project directory and open the local URL shown in the terminal.
2. Enter the owner name **Jordan**. Add **Biscuit** as a dog and **Mochi** as a cat using **Add pet**.
3. Select **Task's pet**, enter each task below, and click **Add task** once for each row. Leave due dates blank or select today so these tasks are eligible for today's plan.

| Pet | Task title | Minutes | Priority | Scheduled time | Recurrence |
|-----|------------|---------|----------|----------------|------------|
| Biscuit | Morning walk | 25 | high | 07:30 | daily |
| Mochi | Feeding | 5 | high | 07:30 | daily |
| Mochi | Playtime | 10 | medium | 12:00 | once |
| Biscuit | Grooming | 20 | low | Leave blank | weekly |

4. In **Browse tasks**, confirm that 07:30 tasks appear before 12:00 and untimed Grooming appears last. Enter `mochi` in **Filter by pet name** and choose **Pending** to see Mochi's pending tasks. Clear the pet filter to show all pets again. Sorting is automatic; filters only change the task list.
5. Under **Build Schedule**, set **Available time (minutes)** to **40**, enable **Prefer shorter tasks when priorities match**, and click **Generate schedule**. Feeding, Morning walk, and Playtime fill the budget; Grooming is skipped with a reason. The generated plan follows priorities and the time budget, while the browse list follows scheduled times.
6. Review **Same-time conflicts**. A warning identifies Biscuit's Morning walk and Mochi's Feeding at 07:30 on the same effective date. It appears automatically, even before generating a plan or while filtering to one pet. Warnings do not reschedule tasks or remove them from the plan.
7. Expand **Complete a task** and click the **Complete today** button for Mochi's Feeding. A success message confirms completion and a new daily Feeding task due tomorrow. Choose **Completed** to see the original or **Pending** to see the new occurrence. Completing weekly Grooming would create its next occurrence seven days after completion. The saved plan is cleared; click **Generate schedule** again to update it. Future-dated occurrences are skipped until due.
