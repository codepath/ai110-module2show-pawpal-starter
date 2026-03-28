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

## Features

| Feature                       | Description                                                                                                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Add owners & pets**         | Create an owner profile and register multiple pets, each tracked independently.                                                                                     |
| **Task management**           | Add care tasks to any pet with a description, frequency, and optional scheduled time.                                                                               |
| **Sorting by time**           | The schedule is always displayed in chronological order (earliest first). Tasks without a scheduled time are sorted to the bottom automatically.                    |
| **Filtering**                 | Filter the schedule by pet name, by completion status (pending only), or both at once — without touching any other pet's data.                                      |
| **Conflict warnings**         | Before displaying the schedule, the app scans for tasks booked at the exact same time for the same pet and surfaces a clear warning banner for each conflict found. |
| **Daily & weekly recurrence** | Completing a `daily` or `weekly` task automatically schedules the next occurrence (+1 day or +7 days). One-time and monthly tasks are simply marked done.           |
| **Schedule metrics**          | A summary row shows total tasks, pending count, and completed count for the current filtered view.                                                                  |
| **Status indicators**         | Task completion is displayed as ✅ Done / ⏳ Pending throughout the UI instead of raw boolean values.                                                               |

---

## Smarter Scheduling

Phase 2 adds intelligent scheduling algorithms to the `Scheduler` class, making PawPal+ more useful and reliable for pet owners.

### Sorting

`sort_by_time()` returns all tasks across every pet ordered by scheduled time, earliest first. Tasks without a time are pushed to the end. Uses Python's `sorted()` with a `lambda` key on `task.time`, falling back to `datetime.max` for timeless tasks.

### Filtering

Two methods allow owners to quickly find the tasks they care about:

- `filter_by_pet_name(pet_name)` — returns all tasks for a specific pet by name (case-insensitive).
- `filter_tasks(completed, pet_name)` — a flexible combined filter; pass either or both arguments to narrow results by completion status, pet, or both at once.

### Recurring Tasks

`complete_task(pet, task)` marks a task done and automatically schedules the next occurrence for `daily` (+1 day) and `weekly` (+7 days) tasks using Python's `timedelta`. One-time (`once`) and `monthly` tasks are marked complete without generating a follow-up. This keeps the `Scheduler` as the "Brain" — `Task` and `Pet` stay simple.

### Conflict Detection

`detect_conflicts()` scans each pet's task list for tasks booked at the exact same time and returns plain-text warning messages. Conflicts are only flagged within the same pet's schedule. Returns an empty list when no conflicts exist — safe to iterate without any extra checks.

## Testing PawPal+

1. python -m pytest. Confidence Level ⭐️ ⭐️ ⭐️ ⭐️

The test cover
Creates a bare Task and verifies it starts as incomplete (completed=False). Calls mark_complete() and confirms the flag flips to True. Tests the most basic state change on a Task.

`test_task_addition_to_pet()`
Creates a Pet with no tasks, records the initial count, adds one Task, and asserts the count increased by exactly 1. Confirms add_task() actually appends to the pet's task list.

`test_sort_by_time_chronological_order()`
Adds four tasks to a pet out of order (evening first, then timeless, then morning, then afternoon). Calls sort_by_time() and asserts the returned list is in ascending time order — morning → afternoon → evening — and that the task with time=None lands at the very end.

`test_complete_daily_task_creates_next_occurrence()`
Creates a daily task with a specific datetime and calls complete_task(). Verifies three things: the original task is marked done, a second task was automatically created, and that new task has the same description/frequency but is scheduled exactly +1 day later and starts as incomplete.

`test_detect_conflicts_flags_duplicate_times()`
Gives a pet two tasks at the same time (10:00) and one at a different time (11:00). Calls detect_conflicts() and asserts exactly one warning is returned, and that warning message mentions both conflicting task names, the time "10:00", and the pet's name "Rex".

`test_detect_conflicts_no_false_positives()`
Gives a pet two tasks at different times and confirms detect_conflicts() returns an empty list — ensuring the method doesn't generate false alarms when there are no real conflicts.

## Demo


<a href="pawpal_screenshot.png" target="_blank"><img src='pawpal_screenshot.png'/>


![alt text](pawpal_screenshot.png)
