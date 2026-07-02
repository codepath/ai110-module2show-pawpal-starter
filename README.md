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

## ✨ Features

- Pet and owner profile management (`Owner`, `Pet` classes)
- Priority-based schedule generation that fits tasks into a daily time budget (`Schedule.generate()`)
- Sorting tasks by scheduled time (`Schedule.sort_by_time()`)
- Filtering tasks by completion status and/or pet name (`Schedule.filter_tasks()`)
- Conflict detection for tasks scheduled at the exact same time (`Schedule.detect_conflicts()`)
- Recurring daily/weekly task logic that generates the next occurrence when a task is completed (`Task.mark_complete()`)
- A Streamlit UI for adding pets and tasks, generating a schedule, and viewing sorted results, filters, and conflict warnings (`app.py`)
- Multi-pet support with per-pet task isolation and active-pet scheduling (`app.py`, `Task.pet_name`)
- Mark complete with safe recurrence surfaced in the UI — clicking "Mark complete" marks a daily/weekly task done and appends the next occurrence automatically
- Task removal via "Remove" button (`Owner.remove_task()`)
- Pet profile display using `get_care_profile()` and `has_special_needs()`
- Priority tiebreaker scheduling based on owner's preferred time of day (`Schedule.generate()`)

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

```
=== Today's Schedule ===
Schedule for Luna on 2026-06-25 (Owner: Alex Rivera):
  08:00 — Morning Walk [Exercise] — 30 min [priority: high]
  08:30 — Feeding [Nutrition] — 10 min [priority: medium]
Total time used: 40 min

No tasks skipped.

Schedule for Mochi on 2026-06-25 (Owner: Alex Rivera):
  08:00 — Feeding [Nutrition] — 10 min [priority: medium]
  08:10 — Grooming [Hygiene] — 20 min [priority: low]
Total time used: 30 min

No tasks skipped.

=== Sorted by Time ===
Feeding: 08:00
Morning Walk: 14:00

=== filter_tasks: incomplete tasks on Luna's schedule ===
  Feeding (completed=False)

=== filter_tasks: completed tasks on Luna's schedule ===
  Morning Walk (completed=True)

=== filter_tasks: tasks for pet 'Luna' ===
  Morning Walk
  Feeding

=== filter_tasks: tasks for pet 'Mochi' (should be empty on Luna's schedule) ===
  []

=== Recurring Task: mark_complete() on Feeding ===
  Feeding | schedule_date: 2026-06-25 (completed=True)
  Feeding | schedule_date: 2026-06-26 (next occurrence)

=== Conflict Detection ===
  Conflict: 'Medication' and 'Dental Cleaning' both scheduled at 09:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
=============================== test session starts ===============================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/**********/Desktop/CodePath/ai110-module2show-pawpal-starter
configfile: pytest.ini
plugins: anyio-4.14.0, cov-7.1.0
collected 19 items

tests/test_pawpal.py .................                                      [100%]

=============================== 19 passed in 0.04s ================================
```

The 19 tests cover the core scheduling behaviors built into PawPal+, marking tasks as complete and verifying that daily/weekly recurring tasks correctly generate a next occurrence. They also validate schedule generation, making sure high-priority tasks are placed first and that tasks exceeding the available time budget get skipped. Beyond that, the suite checks that `sort_by_time()` returns slots in the right order, that `filter_tasks()` correctly narrows results by completion status or pet name, and that `detect_conflicts()` catches two tasks assigned to the same time slot.

Confidence Level: ⭐⭐⭐½ (3.5/5)

I'm fairly confident in this system, all 19 tests pass and they actually cover the behaviors that matter most, sorting, filtering, conflict detection, and recurrence. But I'm not giving it a full 5 stars because I know firsthand that passing tests don't catch everything. For example, earlier in this project, sort_by_time() quietly got changed to sort by the wrong field, and none of my tests caught it since I hadn't written tests for that method yet at the time, I only caught it because I happened to look closely at the terminal output and it didn't match what I expected. That experience made me trust my test suite more, but also made me realize that a green checkmark only means what I actually wrote tests for, not that the whole system is bulletproof.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature           | Method(s)                     | Notes                                                                                                                                                                                                                             |
| ----------------- | ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task sorting      | `Schedule.sort_by_time()`     | Returns a new list of slots sorted by `scheduled_time`, doesn't mutate `self.slots`. Tasks with no `scheduled_time` sort last.                                                                                                    |
| Filtering         | `Schedule.filter_tasks()`     | Filters by completed status and/or `pet_name`, combined with AND logic.                                                                                                                                                           |
| Conflict handling | `Schedule.detect_conflicts()` | Flags tasks with the exact same `scheduled_time` within one pet's schedule. Returns warning strings instead of raising errors. Only checks within a single pet's schedule, not across pets, does not check overlapping durations. |
| Recurring tasks   | `Task.mark_complete()`        | When a `"daily"` or `"weekly"` task is completed for the first time, returns a new `Task` instance scheduled one day/week later. Returns `None` for other frequencies or duplicate completions.                                   |

## 📸 Demo Walkthrough

The main page lays out all inputs in a single vertical flow, nothing hidden or gated.

**Owner section** — three fields at the top: "Owner name" (text), "Available minutes per day" (number, 15–600), and "Preferred time of day" (selectbox: morning / afternoon / evening). These update the live `Owner` object in session state on every render.

**Pet section** — five fields: "Pet name" (text), "Species" (selectbox: dog / cat / other), "Breed" (text), "Age" (number, 0–30), and "Special needs" (text area, one need per line). Clicking **Add Pet** instantiates a `Pet`, appends it to the `pets` list in session state, and immediately renders the pet's full profile via `pet.get_care_profile()` as an expandable JSON block. If the pet has any special needs, a yellow warning badge lists them; otherwise a green success toast confirms the save.

**Active pet selector** — once two or more pets exist, a selectbox labeled "Active pet" appears so you can switch context between registered pets. All subsequent task additions and schedule generation are scoped to whichever pet is selected here.

**Tasks section** — five inline columns: "Task title" (text), "Duration (minutes)" (number, 1–240), "Priority" (selectbox: low / medium / high), "Scheduled time" (text, placeholder `e.g. 08:00`), and "Preferred time of day" (selectbox: morning / afternoon / evening). Clicking **Add task** runs three validations in order: title must be non-empty, scheduled time must be non-empty, and scheduled time must match the `\d{2}:\d{2}` pattern — any failure shows a red error and rejects the entry.

**Current tasks table** — once at least one task exists, a table renders one row per task with eight columns: task name, scheduled time, duration, priority, completion status (✓ Done or Pending), a date label (Today / Tomorrow / month-day for anything further out), a **Mark complete** button, and a **Remove** button. Clicking **Mark complete** calls `task.mark_complete()`; if the task is recurring and not yet completed, the next occurrence is added to the owner's task list automatically and a success message shows the new date. Clicking **Remove** calls `owner.remove_task()` and reruns the page.

**Generate schedule** — the button at the bottom filters the owner's task list to only the active pet's tasks, constructs a `Schedule` for today, calls `schedule.generate()` against the owner's available-minutes budget, and then renders four sub-sections in sequence:

1. **Generated plan** — a success banner with `schedule.get_summary()` (and a warning for any skipped tasks).
2. **Sorted by Time** — a table produced by `schedule.sort_by_time()`, showing each task name and its scheduled time in chronological order.
3. **Conflict Warnings** — output of `schedule.detect_conflicts()`; tasks sharing the exact same `scheduled_time` are each flagged with a red error banner; a green banner confirms no conflicts when none exist.
4. **Filter by Status** — a radio button (All / Completed / Incomplete) feeds `schedule.filter_tasks(completed=...)` and renders the matching tasks as a table.

Everything on the page is scoped to the currently selected active pet; switching pets and regenerating produces an independent schedule for that pet.

**Example multi-pet workflow:**

1. Fill in the owner form — "Alex Rivera", 120 min/day, morning.
2. Add the first pet — "Luna", dog, Labrador, age 3, no special needs → profile card appears.
3. Add the second pet — "Mochi", cat, Domestic Shorthair, age 5, special needs: "kidney diet" → profile card appears with yellow warning badge.
4. With Luna selected as active pet, add two tasks: "Morning Walk" (30 min, high, 08:00, morning) and "Feeding" (10 min, medium, 08:30, morning).
5. Click **Generate schedule** — the plan for Luna appears, sorted view shows 08:00 then 08:30, no conflicts, filter radio lets you inspect completed vs. incomplete tasks.
6. Switch active pet to **Mochi** in the selector. Add Mochi's tasks: "Feeding" (10 min, medium, 08:00, morning) and "Medication" (5 min, high, 08:00, morning) — intentionally the same time to demonstrate conflict detection.
7. Click **Generate schedule** — the plan for Mochi appears; the Conflict Warnings section flags "Feeding" and "Medication" both at 08:00 in red. Luna's schedule is unaffected.
8. Mark a task complete on either pet to see the next recurring occurrence appended to the task list and the date label update accordingly.

```
=== Today's Schedule ===
Schedule for Luna on 2026-07-01 (Owner: Alex Rivera):
  08:00 — Morning Walk [Exercise] — 30 min [priority: high]
  08:30 — Feeding [Nutrition] — 10 min [priority: medium]
Total time used: 40 min

No tasks skipped.

Schedule for Mochi on 2026-07-01 (Owner: Alex Rivera):
  08:00 — Feeding [Nutrition] — 10 min [priority: medium]
  08:10 — Grooming [Hygiene] — 20 min [priority: low]
Total time used: 30 min

No tasks skipped.
=== Sorted by Time ===
Feeding: 08:00
Morning Walk: 14:00

=== filter_tasks: incomplete tasks on Luna's schedule ===
  Feeding (completed=False)

=== filter_tasks: completed tasks on Luna's schedule ===
  Morning Walk (completed=True)

=== filter_tasks: tasks for pet 'Luna' ===

=== filter_tasks: tasks for pet 'Mochi' (should be empty on Luna's schedule) ===
  []

=== Recurring Task: mark_complete() on Feeding ===
  Feeding | schedule_date: 2026-07-01 (completed=True)
  Feeding | schedule_date: 2026-07-02 (next occurrence)

=== Conflict Detection ===
  Conflict: 'Medication' and 'Dental Cleaning' both scheduled at 09:00
```

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
