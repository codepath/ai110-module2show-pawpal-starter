# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

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

Terminal output from `python main.py` (CLI demo verifying backend logic):

```
=== PawPal+ CLI Demo ===

Owner : Jordan
Pets  : Mochi (Dog), Whiskers (Cat)

--------------------------------------------------------------
TODAY'S SCHEDULE  (Scheduler.todays_schedule - sorted by time)
--------------------------------------------------------------
  07:30  Mochi      Morning walk            [HIGH    ] daily   x
  08:00  Mochi      Morning feeding         [CRITICAL] daily   x
  08:30  Whiskers   Breakfast               [HIGH    ] daily   x
  13:00  Whiskers   Afternoon meds          [CRITICAL] daily   x
  17:00  Mochi      Training session        [MEDIUM  ] weekly  x
  18:00  Mochi      Evening walk            [HIGH    ] daily   x
  19:00  Whiskers   Evening feeding         [HIGH    ] daily   x
  20:00  Mochi      Evening medication      [CRITICAL] daily   x

--------------------------------------------------------------
CONFLICT CHECK  (Scheduler.detect_conflicts)
--------------------------------------------------------------
  No scheduling conflicts detected.

--------------------------------------------------------------
DEMO: Adding 'Vet call' at 20:00 for Mochi  (duplicate -> conflict)
--------------------------------------------------------------
  Warning: 'Vet call follow-up' and 'Evening medication' are both scheduled at 20:00 for Mochi.

--------------------------------------------------------------
FILTER: Incomplete tasks for Mochi  (filter_by_pet + filter_by_status)
--------------------------------------------------------------
  07:30  Mochi      Morning walk            [HIGH    ] daily   x
  08:00  Mochi      Morning feeding         [CRITICAL] daily   x
  17:00  Mochi      Training session        [MEDIUM  ] weekly  x
  18:00  Mochi      Evening walk            [HIGH    ] daily   x
  20:00  Mochi      Evening medication      [CRITICAL] daily   x
  20:00  Mochi      Vet call follow-up      [HIGH    ] once    x

--------------------------------------------------------------
DEMO: Mark 'Morning walk' done  (daily -> auto-reschedule)
--------------------------------------------------------------
  Done: 'Morning walk' marked complete.
  Next occurrence -> 2026-07-08 at 07:30  [daily]

--------------------------------------------------------------
COMPLETED TASKS  (filter_by_status completed=True)
--------------------------------------------------------------
  07:30  Mochi      Morning walk            [HIGH    ] daily   done

--------------------------------------------------------------
Demo complete. All backend methods verified.
--------------------------------------------------------------
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite (both files):
python -m pytest

# Run only the core class tests:
python -m pytest tests/test_pawpal.py -v
```

**What the tests cover:**
- `test_pawpal.py` (29 tests) — `Task.mark_complete()`, `Task.next_occurrence()`, `Pet.add_task()`, `Owner.get_all_tasks()`, `Scheduler.sort_by_time()`, `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()`, `Scheduler.detect_conflicts()`, `Scheduler.mark_task_complete()`, `Scheduler.todays_schedule()`
- `test_scheduler.py` (20 tests) — scoring algorithm, priority ordering, budget enforcement, frequency intervals (supplementary)

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1
collected 49 items

tests/test_pawpal.py::TestTask::test_mark_complete_changes_status PASSED
tests/test_pawpal.py::TestTask::test_mark_complete_is_idempotent PASSED
tests/test_pawpal.py::TestTask::test_next_occurrence_daily_adds_one_day PASSED
tests/test_pawpal.py::TestTask::test_next_occurrence_weekly_adds_seven_days PASSED
tests/test_pawpal.py::TestTask::test_next_occurrence_once_returns_none PASSED
tests/test_pawpal.py::TestTask::test_next_occurrence_inherits_all_fields PASSED
tests/test_pawpal.py::TestTask::test_new_occurrence_starts_incomplete PASSED
tests/test_pawpal.py::TestPet::test_add_task_increases_task_count PASSED
tests/test_pawpal.py::TestPet::test_get_tasks_returns_all_tasks PASSED
tests/test_pawpal.py::TestPet::test_pending_tasks_excludes_completed PASSED
tests/test_pawpal.py::TestOwner::test_add_pet_increases_pet_count PASSED
tests/test_pawpal.py::TestOwner::test_get_all_tasks_aggregates_across_pets PASSED
tests/test_pawpal.py::TestOwner::test_get_pet_by_name PASSED
tests/test_pawpal.py::TestOwner::test_get_pet_returns_none_for_unknown PASSED
tests/test_pawpal.py::TestScheduler::test_sort_by_time_returns_chronological_order PASSED
tests/test_pawpal.py::TestScheduler::test_filter_by_status_completed PASSED
tests/test_pawpal.py::TestScheduler::test_conflict_detection_flags_same_time_same_pet PASSED
tests/test_pawpal.py::TestScheduler::test_conflict_detection_ignores_different_pets PASSED
tests/test_pawpal.py::TestScheduler::test_conflict_detection_ignores_completed_tasks PASSED
tests/test_pawpal.py::TestScheduler::test_recurring_daily_task_creates_next_occurrence PASSED
tests/test_pawpal.py::TestScheduler::test_recurring_weekly_task_creates_next_occurrence PASSED
tests/test_pawpal.py::TestScheduler::test_once_task_creates_no_next_occurrence PASSED
tests/test_pawpal.py::TestScheduler::test_todays_schedule_returns_pending_tasks_for_today PASSED
tests/test_pawpal.py::TestScheduler::test_todays_schedule_is_sorted_by_time PASSED
... (49 total)

============================== 49 passed in 0.13s ==============================
```

**Confidence level: ★★★★☆ (4/5)**

Core behaviors are well-covered: completion status, recurrence, time-based sorting, conflict detection, and filtering all have dedicated tests with both happy-path and edge cases. One star held back because the UI layer (app.py Streamlit interactions) isn't covered by automated tests — those were verified manually.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by time | `Scheduler.sort_by_time(tasks)` | Uses Python `sorted()` with `lambda t: t.time` as key on "HH:MM" strings |
| Filter by status | `Scheduler.filter_by_status(completed, tasks)` | Returns tasks where `task.completed == completed` |
| Filter by pet | `Scheduler.filter_by_pet(pet_name)` | Case-insensitive match on `task.pet_name` |
| Conflict detection | `Scheduler.detect_conflicts(tasks)` | Flags two incomplete tasks for the same pet at the same HH:MM time |
| Recurring tasks | `Task.next_occurrence()` + `Scheduler.mark_task_complete(task)` | `mark_complete()` triggers `next_occurrence()`, auto-registered with the pet |
| Today's schedule | `Scheduler.todays_schedule(for_date)` | Filters to `due_date == today` and `completed == False`, then sorts by time |

## 📸 Demo Walkthrough

**Backend (CLI) — verify logic without the UI:**
```bash
python main.py
```
This runs `main.py`, which imports directly from `pawpal_system.py` and exercises every Scheduler method in the terminal. Output appears above in the Sample Output section.

**Frontend (Streamlit UI):**
```bash
streamlit run app.py
```

Example workflow:

1. **Enter your name** in the sidebar (persists across sessions via `Owner.save()`).
2. **Pet Setup tab** — add Mochi as a Dog, Shiba Inu, 3 years old. The owner object is stored in `st.session_state` so it survives page interactions without resetting.
3. **Manage Tasks tab** — click "＋ Add new task". Enter: name "Morning walk", time "07:30", priority "high", frequency "daily", duration 30 min. Click Add. Repeat for feeding, medication, etc.
4. **Today's Plan tab** — the app calls `Scheduler.todays_schedule(today)` to show all pending tasks sorted by time. If two tasks share the same time for the same pet, a yellow `st.warning` banner appears at the top of the plan.
5. **Mark done** — click **✓ Done** on a task. The app calls `Scheduler.mark_task_complete(task)`. For daily/weekly tasks, a green `st.success` banner confirms the next occurrence date. The plan immediately refreshes.
6. **Repeat daily** — recurring tasks auto-appear in tomorrow's plan. One-time tasks disappear after completion.

Key Scheduler behaviors visible in the UI:
- `sort_by_time()` — tasks always displayed in HH:MM ascending order
- `detect_conflicts()` — yellow warning banners for same-pet/same-time collisions
- `mark_task_complete()` — done button triggers recurrence and persists to disk
- `filter_by_pet()` — plan and task list scoped to the selected pet

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
