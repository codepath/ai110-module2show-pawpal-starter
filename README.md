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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
