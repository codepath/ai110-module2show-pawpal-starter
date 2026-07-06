# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

- **Multi-pet management** — one owner can track many pets, each with its own task list.
- **Care tasks** — every task has a description, a time (`HH:MM`), a frequency (`once`/`daily`/`weekly`),
  a completion flag, and a due date.
- **Sorting by time** — the schedule is always returned in chronological order across *all* pets.
- **Filtering** — view tasks for a single pet, or only the completed / outstanding ones.
- **Conflict warnings** — if two tasks (even on different pets) share a time slot, the scheduler
  surfaces a warning instead of silently double-booking.
- **Daily / weekly recurrence** — completing a recurring task automatically schedules the next
  occurrence for the following day or week.
- **Streamlit UI** — add pets and tasks, see a live schedule table, and get conflict alerts, all
  backed by the same logic layer that the CLI and tests use.

## System architecture (UML)

The class design lives in [`diagrams/uml.mmd`](diagrams/uml.mmd) (Mermaid source).
`Owner 1→* Pet`, `Pet 1→* Task`, and `Scheduler 1→1 Owner`.

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

Actual terminal output from running `python main.py` (one owner, two pets, five tasks
added out of order — including two at 08:00 to trigger a conflict warning):

```text
====================================================
Today's Schedule for Jordan
  [ ] 08:00  Breakfast  (Biscuit) - daily
  [ ] 08:00  Feed cat  (Mochi) - daily
  [ ] 14:00  Vet appointment  (Biscuit) - once
  [ ] 18:00  Evening walk  (Biscuit) - daily
  [ ] 21:00  Night meds  (Mochi) - daily

Warnings:
  ! Conflict at 08:00: Biscuit's Breakfast, Mochi's Feed cat
====================================================

Biscuit's tasks only:
  - 18:00 Evening walk
  - 08:00 Breakfast
  - 14:00 Vet appointment

Completing Biscuit's Evening walk (daily)...
  -> Auto-created next occurrence for 2026-07-07

Remaining incomplete tasks (time-sorted):
  - 08:00 Breakfast [daily]
  - 08:00 Feed cat [daily]
  - 14:00 Vet appointment [once]
  - 18:00 Evening walk [daily]
  - 21:00 Night meds [daily]
```

## 🧪 Testing PawPal+

Run the full suite from the project root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`) covers both happy paths and edge cases:

- **Core:** `mark_complete()` flips task status; adding a task increases a pet's count.
- **Sorting:** tasks from all pets are returned in chronological order.
- **Filtering:** narrowing by pet name and by completion status.
- **Conflict detection:** two tasks at the same time (across different pets) raise one
  warning; unique times raise none.
- **Recurrence:** completing a daily task auto-creates the next day's task; a one-off
  task does not recur.
- **Edge cases:** a pet with no tasks yields an empty schedule without errors.

Sample output from a successful run:

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: ...\ai110-module2show-pawpal-starter
collected 9 items

tests\test_pawpal.py .........                                           [100%]

============================== 9 passed in 0.02s ==============================
```

**Confidence level:** ⭐⭐⭐⭐☆ (4/5) — all core behaviors and the main edge cases are
covered and passing; a future pass would add overlapping-duration conflicts (not just
exact time matches).

## 📐 Smarter Scheduling

Each algorithmic feature and the method that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts every pet's tasks chronologically using `sorted(key=lambda t: t.time)` on the `"HH:MM"` string. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Narrows tasks by pet name and/or completion status; either argument may be omitted. |
| Conflict handling | `Scheduler.detect_conflicts()` | Buckets tasks by time slot and returns a warning string for any slot with more than one task (across pets). Returns warnings rather than raising. |
| Recurring tasks | `Task.next_occurrence()` + `Scheduler.complete_task()` | On completion, a `daily`/`weekly` task auto-generates its next occurrence via `datetime.timedelta` and attaches it to the same pet. `once` tasks do not recur. |

## 📸 Demo Walkthrough

Launch the app:

```bash
python -m streamlit run app.py
```

**Main UI features / what a user can do**

- Set the **owner name** at the top.
- **Add a pet** (name + species) — the pet's tasks are tracked separately.
- **Add a care task** to any pet: description, time, and frequency (`once`/`daily`/`weekly`).
- View a **live schedule table** sorted by time across all pets, with a "Done" column.
- See **conflict warnings** whenever two tasks share a time slot.
- **Mark a task complete** — recurring tasks automatically roll to the next day/week.

**Example workflow**

1. Enter the owner name (e.g., *Jordan*).
2. Add a pet → *Biscuit (dog)*. Add a second pet → *Mochi (cat)*.
3. Add a task → *Breakfast, 08:00, daily* for Biscuit.
4. Add a task → *Feed cat, 08:00, daily* for Mochi.
5. View **Today's schedule**: both 08:00 tasks appear, sorted, and a
   ⚠️ **conflict warning** flags the 08:00 collision between the two pets.
6. Mark *Breakfast* complete → an `st.info` message confirms the next day's
   occurrence was created automatically.

**Key Scheduler behaviors shown:** time-sorting across pets, cross-pet conflict
detection, filtering by pet, and daily/weekly recurrence.

**Sample CLI output** (same logic layer, run via `python main.py`):

```text
====================================================
Today's Schedule for Jordan
  [ ] 08:00  Breakfast  (Biscuit) - daily
  [ ] 08:00  Feed cat  (Mochi) - daily
  [ ] 14:00  Vet appointment  (Biscuit) - once
  [ ] 18:00  Evening walk  (Biscuit) - daily
  [ ] 21:00  Night meds  (Mochi) - daily

Warnings:
  ! Conflict at 08:00: Biscuit's Breakfast, Mochi's Feed cat
====================================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
