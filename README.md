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

## Smarter Scheduling

PawPal+ uses a priority-based scheduling engine to build daily care plans automatically. The `Scheduler` ranks tasks by priority (high, medium, low) and fits them into the owner's availability windows for each day. Tasks that don't fit are dropped rather than double-booked. The system also supports weekly and monthly recurring tasks, assigns them to specific days, and includes them alongside the daily schedule.

Key capabilities:

- **Priority ordering** — high-priority tasks (e.g. medication, walks) are scheduled first.
- **Constraint checking** — each task's duration is validated against the available window before placement.
- **Conflict detection** — overlapping time slots between tasks are identified and flagged.
- **Filtering** — tasks can be filtered by pet, completion status, or recurrence scope.
- **Rationale generation** — the scheduler produces a plain-text explanation of why the plan looks the way it does.

## Testing PawPal+

### Running the Tests

```bash
python3 -m pytest
```

### What the Tests Cover

The test suite (`tests/test_pawpal.py`) contains **12 tests** that verify core scheduling and task-management behaviors:

- **Task completion** — marking a task complete updates its status.
- **Adding tasks to a pet** — task count increases and the pet's name is automatically assigned to the task.
- **Sorting by time** — tasks are ordered by their scheduled time, with unscheduled tasks placed first.
- **Filtering by pet** — returns only tasks belonging to a specific pet (and an empty list when there is no match).
- **Filtering by completion status** — correctly separates completed from incomplete tasks.
- **Conflict detection** — identifies overlapping time slots between scheduled tasks, confirms non-overlapping tasks produce no conflicts, and skips unscheduled tasks.

### Confidence Level

**Confidence:** 

**4 / 5 stars; **All 12 tests pass and they cover the most critical scheduling behaviors (sorting, filtering, conflict detection, task lifecycle). A fifth star would require more robust coverage for edge cases for boundary time overlaps, the full `generate_schedule` workflow, and integration with the Streamlit UI.
