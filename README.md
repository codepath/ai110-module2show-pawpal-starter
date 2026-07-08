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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

Terminal Output:
Today's Schedule
Today's plan:
- Morning walk (daily) at 08:00
- Litter box cleaning (daily) at 09:00
- Vet checkup (once) at 10:00


## 🧪 Testing PawPal+

'''
Run the full test suite:
python3 -m pytest

Brief description of my tests:
My tests cover the core behavior of the PawPal system as they verify the main scheduling and task-management logic in my pet care app. 

Terminal Pytest Output:
========================================== test session starts ==========================================
platform darwin -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/gerardorivera/ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 20 items                                                                                      

test_pawpal_system.py ...........                                                                 [ 55%]
tests/test_pawpal.py .........                                                                    [100%]

========================================== 20 passed in 0.06s ===========================================

Confidence Level:
4 stars
'''



## 📐 Smarter Scheduling

The scheduler now supports a small set of planning behaviors that help turn a raw task list into a more useful daily plan.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting behavior | `Scheduler.sort_tasks()` | Orders pending tasks by frequency and priority so higher-urgency tasks are planned first. |
| Filtering behavior | `Scheduler.filter_tasks()` | Returns tasks based on completion status and/or pet name so the planner can focus on the right subset. |
| Conflict detection logic | `Scheduler.check_conflicts()` and `Scheduler.lightweight_conflict_check()` | Detects tasks that share the same time slot and returns a warning when conflicts or invalid times are found. |
| Recurring task logic | `Task._next_due_date()`, `Task.create_next_occurrence()`, and `Task.mark_complete()` | Handles recurring daily and weekly tasks by generating the next occurrence when a task is completed. |

## 📸 Demo Walkthrough

PawPal+ is designed as a simple, guided pet-care planning experience. In the Streamlit interface, a user can:

1. Enter an owner name and add one or more pets with basic details such as name, weight, color, and breed.
2. Create care tasks for each pet, including a title, time, frequency, priority, and duration.
3. Review all tasks in a sortable and filterable list, then generate a daily schedule from the pending items.
4. See conflict warnings when multiple tasks are assigned to the same time slot and adjust the plan accordingly.
5. Use the generated plan as a daily checklist for pet care routines.

Example workflow:

1. Add a pet such as "Mochi" and enter the pet's details.
2. Create a task like "Morning walk" for that pet, set the time to 08:00, and choose a daily frequency with high priority.
3. Add another task such as "Feeding" and generate the daily schedule.
4. Review the resulting plan, inspect the task list, and use the scheduler's conflict warnings to spot overlapping care times.

The scheduler demonstrates several behaviors during this flow:

- Sorting by priority and frequency to place the most urgent tasks first.
- Sorting by time to show tasks in chronological order.
- Filtering by pet name and completion status to focus on specific tasks.
- Conflict detection for overlapping time slots.
- Recurring task support for daily and weekly tasks that can generate future occurrences.

Sample CLI output from running the current demo script:

```text
Today's Schedule
Today's plan:
- Evening walk (daily) at 18:30
- Morning walk (daily) at 08:00
- Feeding (daily) at 07:30
- Litter box cleaning (daily) at 09:00
- Grooming (weekly) at 14:00
- Vet checkup (once) at 10:00
- Nail trimming (once) at 10:00

All Tasks Sorted by Time
- Feeding at 07:30 (daily) - pending
- Morning walk at 08:00 (daily) - pending
- Litter box cleaning at 09:00 (daily) - pending
- Vet checkup at 10:00 (once) - pending
- Nail trimming at 10:00 (once) - pending
- Grooming at 14:00 (weekly) - pending
- Evening walk at 18:30 (daily) - pending

Schedule Conflicts
- Vet checkup and Nail trimming both at 10:00
```

## Features

1. Priority-aware planning: Tasks are ranked by frequency and priority so the most urgent care items are surfaced first in the daily plan.
2. Sorting by time: Tasks can be ordered chronologically by their scheduled time, making it easier to review the day’s routine.
3. Conflict warnings: The scheduler detects tasks that share the same time slot and highlights potential scheduling conflicts.
4. Recurring task support: Daily and weekly tasks can generate the next occurrence when marked complete, supporting simple recurring schedules.
5. Pet and status filtering: Tasks can be filtered by pet name and completion status to focus on specific animals or pending work.
6. Flexible daily planning: The planner can generate a daily schedule and optionally limit the number of tasks included in the plan.