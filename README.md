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

---

## Features

- **Add and manage pets** — register any number of pets (dog, cat, rabbit, etc.) with species, breed, and age.
- **Schedule tasks** — create one-time or recurring (daily / weekly) care tasks with a title, due date, and optional notes.
- **Schedule appointments** — log vet checkups, vaccinations, and grooming visits with provider and location details.
- **Sort by time** — the dashboard always displays tasks in chronological order, regardless of the order they were entered.
- **Filter by pet or status** — narrow the task list to a specific pet or to only pending / completed tasks.
- **Conflict warnings** — the scheduler detects when two tasks are booked at the same moment and displays a clear warning above the task table.
- **Recurring task auto-scheduling** — marking a daily or weekly task complete automatically creates the next occurrence using Python's `timedelta`.
- **Care summary per pet** — each pet card shows counts of incomplete, overdue, and upcoming appointment entries.
- **Reminder model** — `Reminder` objects link a scheduled notification to a specific task or appointment for future notification support.

---

## Smarter Scheduling

`pawpal_system.py` implements a `Scheduler` class with four algorithmic features:

| Feature | How it works |
|---|---|
| **Sort by time** | `sort_by_time()` uses `sorted()` with a `lambda t: t.due_date` key — O(n log n) on the `datetime` attribute. |
| **Filter tasks** | `filter_tasks()` accepts optional `pet_name` and `completed` flags; both can be applied at once. |
| **Recurring tasks** | `mark_task_complete()` uses `timedelta` to compute the next due date and appends a new `Task` to the pet automatically. |
| **Conflict detection** | `detect_conflicts()` flags exact `due_date` collisions and returns human-readable warning strings. |

**Run the terminal demo:**

```bash
python pawpal_demo.py
```

**Run the Streamlit UI:**

```bash
streamlit run app.py
```

---

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
  <img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

---

## Testing PawPal+

The automated test suite lives in `tests/test_pawpal.py` and covers 31 test cases across five categories:

| Category | What is tested |
|---|---|
| **Sorting** | Tasks returned in chronological order; multi-pet interleaving |
| **Recurrence** | Daily and weekly next-occurrence creation; one-time tasks produce no new task |
| **Conflict detection** | Same-time tasks flagged; different times pass; completed tasks excluded |
| **Filtering** | By pet name (case-insensitive), by status, composable filters |
| **Edge cases & model** | Empty pet, empty owner, overdue logic, appointment cancel/notes, reminder |

**Run the tests:**

```bash
python -m pytest
```

**Confidence level: ★★★★☆ (4/5)** — all 31 tests pass; UI layer not covered by pytest.
