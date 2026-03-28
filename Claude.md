# Claude Context
# To run program in streamlit: streamlit run app.py

## PawPal+ System Classes (as of March 28, 2026)

- **Task**: Represents a single activity for a pet. Fields: `description`, `time` (datetime), `frequency`, `completed` (bool). Methods: `mark_complete()`, `mark_incomplete()`.
- **Pet**: Stores pet details (name, species, breed, age) and a list of tasks. Methods: `add_task()`, `get_tasks()`.
- **Owner**: Manages multiple pets and aggregates all their tasks. Methods: `add_pet()`, `get_all_tasks()`.
- **Scheduler**: The "Brain" initialized with an Owner. Methods:
  - `get_all_tasks()` — all tasks across all pets.
  - `get_tasks_by_pet(pet)` — tasks for a specific Pet object.
  - `get_tasks_by_status(completed)` — filter by True/False completion.
  - `get_tasks_by_frequency(frequency)` — filter by frequency string.
  - `filter_by_pet_name(pet_name)` — filter by pet name string (case-insensitive).
  - `filter_tasks(completed, pet_name)` — combined filter; both args are optional.
  - `sort_by_time()` — returns all tasks sorted by `time` ascending; timeless tasks go last.
  - `complete_task(pet, task)` — marks task done and auto-creates next occurrence for `daily`/`weekly` tasks using `timedelta`.

**Goal:**
Keep the codebase focused on these four classes and their responsibilities. Avoid adding unrelated features or complexity.

---

## Algorithms Implemented (Phase 2)

- **Sorting** — `Scheduler.sort_by_time()` uses `sorted()` with a `lambda` key on `task.time`. Falls back to `datetime.max` for tasks with no time so they sort to the end.
- **Filtering** — `filter_by_pet_name()` and `filter_tasks()` allow filtering tasks by pet name, completion status, or both combined. Case-insensitive name matching.
- **Recurring Tasks** — `complete_task(pet, task)` marks a task complete then uses a `timedelta` delta map (`daily` → +1 day, `weekly` → +7 days) to auto-schedule the next occurrence on the same pet. `once` and `monthly` tasks are not rescheduled.
- **Imports** — `timedelta` is imported from `datetime` to support recurring task scheduling.

---

## Key Files

- **pawpal_system.py** — Core logic: all four classes with 1-line docstrings on every method.
- **app.py** — Streamlit UI fully wired to logic:
  - Imports `Owner`, `Pet`, `Task`, `Scheduler` from `pawpal_system.py`.
  - `st.session_state.owner` persists the `Owner` instance across reruns.
  - "Add Pet" button creates a `Pet` and calls `owner.add_pet()`.
  - "Add Task" button creates a `Task` and calls `pet.add_task()` on the selected pet.
  - "Generate Schedule" button uses `Scheduler.get_all_tasks()` and displays a table.
- **main.py** — Demo script: creates an Owner, two Pets, six Tasks added out of order, then demonstrates `sort_by_time()`, `filter_tasks()`, `filter_by_pet_name()`, and `complete_task()` with printed output.
- **tests/test_pawpal.py** — Two pytest tests: task completion (`mark_complete`) and task addition to a Pet.

---

## Conventions

- Use `st.session_state` for any persistent data in Streamlit (never re-create objects at the top of the script unconditionally).
- All UI actions delegate to class methods — no raw data manipulation in `app.py`.
- Tests live in `tests/test_pawpal.py` and are run with `python -m pytest`.
- Scheduling intelligence lives in `Scheduler` — `Task` and `Pet` stay simple data holders.

---

_This file is for context and alignment. Update as the system evolves._
