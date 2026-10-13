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

Output of `python pawpal_system.py` (a demo dog with a 90-minute budget, including a fixed 08:15 vet visit):

```
Daily plan for Mochi (dog):
  08:00–08:10 — Breakfast (10 min) [priority: high]
      why: high priority, fits in the 90-min budget; placed at the start of the morning as preferred
  08:15–08:45 — Vet visit (30 min) [priority: high]
      why: high priority, fits in the 90-min budget; fixed appointment at 08:15
  08:45–09:15 — Morning walk (30 min) [priority: high]
      why: high priority, fits in the 90-min budget; placed in the morning after earlier tasks finished
  12:00–12:15 — Brushing (15 min) [priority: low]
      why: low priority, fits in the 90-min budget; placed at the start of the afternoon as preferred
  17:00–17:05 — Heartworm meds (5 min) [priority: high]
      why: high priority, fits in the 90-min budget; placed at the start of the evening as preferred
  SKIPPED — Puzzle toy: needs 20 min but only 15 min left
  SKIPPED — Long hike: needs 60 min but only 0 min left
Total scheduled: 90 min
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage (needs `pip install pytest-cov` first):
pytest --cov
```

Sample test output:

```
collected 19 items

tests/test_pawpal_system.py::test_high_priority_chosen_over_low_when_time_is_short PASSED
tests/test_pawpal_system.py::test_plan_never_exceeds_time_budget PASSED
tests/test_pawpal_system.py::test_shorter_task_preferred_among_equal_priority PASSED
tests/test_pawpal_system.py::test_preferred_time_places_task_in_that_slot PASSED
tests/test_pawpal_system.py::test_tasks_do_not_overlap PASSED
tests/test_pawpal_system.py::test_empty_task_list_gives_empty_plan PASSED
tests/test_pawpal_system.py::test_every_scheduled_task_has_a_reason PASSED
tests/test_pawpal_system.py::test_invalid_task_values_are_rejected[kwargs0] PASSED
tests/test_pawpal_system.py::test_invalid_task_values_are_rejected[kwargs1] PASSED
tests/test_pawpal_system.py::test_invalid_task_values_are_rejected[kwargs2] PASSED
tests/test_pawpal_system.py::test_remove_task_by_title PASSED
tests/test_pawpal_system.py::test_overlapping_fixed_tasks_keep_higher_priority PASSED
tests/test_pawpal_system.py::test_fixed_task_conflict_tie_keeps_first_listed PASSED
tests/test_pawpal_system.py::test_flexible_task_pushed_after_fixed_task PASSED
tests/test_pawpal_system.py::test_no_items_overlap_with_mixed_fixed_and_flexible_tasks PASSED
tests/test_pawpal_system.py::test_invalid_fixed_time_is_rejected[kwargs0] PASSED
tests/test_pawpal_system.py::test_invalid_fixed_time_is_rejected[kwargs1] PASSED
tests/test_pawpal_system.py::test_invalid_fixed_time_is_rejected[kwargs2] PASSED
tests/test_pawpal_system.py::test_dropped_fixed_task_does_not_use_up_time_budget PASSED

============================= 19 passed in 0.08s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_importance` | Highest priority first; among equal priority, shorter tasks first so more of them fit. Chosen tasks are then laid out by preferred part of the day (morning 08:00, afternoon 12:00, evening 17:00). |
| Filtering | `Scheduler.select_tasks` | Greedily adds tasks in importance order until the owner's `available_minutes` runs out. Tasks that don't fit go to `DailyPlan.skipped` with a reason like "needs 60 min but only 10 min left". |
| Conflict handling | `Scheduler.build_plan`, `ScheduledItem.overlaps` | Tasks can have a `fixed_time` (e.g. a 09:00 vet visit). If two fixed tasks overlap, the higher priority one is kept (tie: the one listed first) and the other is skipped and recorded in `DailyPlan.conflicts`. Conflicts are resolved *before* the time budget, so a dropped task doesn't use up minutes. Flexible tasks are pushed past any fixed task they would overlap. |
| Recurring tasks | — | Not implemented. The scheduler plans a single day. |

## 📸 Demo Walkthrough

1. Start the app with `streamlit run app.py` and open the local URL it prints.
2. Under **Owner and Pet**, enter the owner name, how many minutes are available for pet care today, the pet's name, and its species.
3. Under **Tasks**, enter a task title, duration, and priority. Optionally choose a **Preferred time** (morning / afternoon / evening) *or* type a **Fixed time** in HH:MM for an appointment. Click **Add task**. Repeat for each task; the current list appears in a table (**Clear tasks** empties it).
4. Click **Generate schedule**. A green summary shows how many tasks were scheduled and how many minutes were used.
5. Read the plan table: each row has the time range, task, minutes, priority, and a **Why** column explaining the choice.
6. Below the table, yellow warnings list skipped tasks (not enough time, or lost a conflict) and red errors describe any fixed-time conflicts. A bad fixed time (e.g. `25:00`) shows an error instead of crashing.
7. Open **Plain-text plan** to see the same plan as text.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
