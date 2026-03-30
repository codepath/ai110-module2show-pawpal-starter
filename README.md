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

PawPal+ goes beyond a simple task list with three scheduling improvements:

**Conflict detection** — `Scheduler.detect_conflicts()` checks every pair of scheduled tasks (same pet or different pets) for overlapping time slots. Rather than raising an exception, it returns plain-English warning strings so the UI can surface them without crashing. The algorithm sorts tasks by start time first, then uses an early-break inner loop to skip pairs that can't possibly overlap — keeping it fast even when called on every UI refresh.

**Priority-first scheduling** — `Scheduler.generate_schedule()` sorts tasks by priority before placing them in the time window, so high-priority tasks (feeding, medication) always get a slot before lower-priority ones. Tasks that don't fit are returned in a `dropped` list instead of being silently lost, and the UI warns the owner which ones were left out.

**Proactive daily warnings** — before the owner even clicks "Generate schedule," the app scans today's task list and warns whenever a single pet has multiple tasks due on the same day, giving the owner a heads-up about a busy day before committing to a schedule.

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
