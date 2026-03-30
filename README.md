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

## Smarter Scheduling

Beyond basic priority sorting, PawPal+ includes four algorithmic features:

| Feature | Method | How it works |
|---|---|---|
| **Sort by time** | `Scheduler.sort_by_time()` | Sorts scheduled items by `start_time` using a lambda key on zero-padded `"HH:MM"` strings, which compare correctly with Python's default string ordering. |
| **Filter tasks** | `Scheduler.filter_tasks(pet_name, completed)` | Returns a filtered view of the schedule by pet name and/or completion status. Both parameters are optional. |
| **Recurring tasks** | `Task.next_occurrence()` + `Scheduler.mark_complete()` | When a `daily` or `weekly` task is marked complete, `timedelta` calculates the next due date (`today + 1 day` or `today + 7 days`) and a fresh task is automatically appended to the pet's list. |
| **Conflict detection** | `Scheduler.detect_conflicts()` | Checks every pair of scheduled items for overlapping time intervals using the standard interval-overlap test: `A.start < B.end AND B.start < A.end`. Returns a list of human-readable warning strings instead of raising an exception. |

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

The suite contains **45 tests** across five categories:

| Category | What's covered |
|---|---|
| Task lifecycle | `complete()`, `reset()`, priority ordering, recurrence via `next_occurrence()` |
| Pet ownership | add/remove tasks, pending/completed filtering, species defaults |
| Owner aggregation | cross-pet task access, empty-owner edge cases |
| Scheduler algorithms | build, sort by time, filter by pet/status, mark-complete with recurrence |
| Conflict detection | overlapping slots flagged, adjacent slots not flagged, cross-pet conflicts |

**Confidence:** ★★★★☆ — all happy paths and most edge cases covered. Known gaps: midnight overflow in `_add_minutes`, Streamlit UI layer not tested.

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
