# PawPal+ 🐾

**PawPal+** is a Streamlit app that helps a busy pet owner plan and keep track of pet care. Add your pets, schedule their walks, feedings and vet visits, and PawPal+ keeps everything in time order, repeats daily and weekly routines, and warns you when two tasks clash.

## Features

- **Multiple pets per owner:** one owner can have any number of pets, and each pet has its own tasks. The scheduler always looks at all of them together.
- **Sorting by time:** tasks are always shown in chronological order. When two tasks start at the same time, the higher-priority one comes first.
- **Filtering:** view tasks by pet, by status (to do or done), or by type (walk, feed, vet), alone or combined.
- **Daily schedule:** see only today's unfinished tasks, in time order, with the total minutes of care for the day.
- **Daily and weekly recurrence:** completing a repeating task automatically creates the next one. The new due date is counted from the day you complete it (daily = +1 day, weekly = +7 days) and keeps the same time of day, so a late walk never reappears in the past. Completing a task twice does not create duplicates.
- **Conflict warnings:** two tasks conflict when their time ranges overlap (start time plus duration), whether they belong to the same pet or different pets. Back-to-back tasks, like a walk ending at 8:30 and a vet visit starting at 8:30, are not conflicts. The app warns you instead of changing your schedule.
- **Check before you add:** when you add a task, the app tells you right away if it overlaps something already scheduled.
- **Tested:** 23 automated tests cover sorting, filtering, recurrence and conflict edge cases (see [Testing PawPal+](#-testing-pawpal)).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the command-line demo

```bash
python main.py
```

## How it works

The core logic lives in [pawpal_system.py](pawpal_system.py) and is built from four dataclasses. The final UML is in [diagrams/uml_final.mmd](diagrams/uml_final.mmd).

- **Task:** one care activity (walk, feed, vet) with a due time, duration, priority, optional recurrence and completion status. It can detect overlaps with another task, and completing a recurring task creates the next occurrence.
- **Pet:** stores pet details and its own list of tasks. `add_task()` links the task back to the pet.
- **Owner:** holds multiple pets. `get_all_tasks()` returns every pet's tasks combined.
- **Scheduler:** the "brain". It holds only an `Owner` and reads everything through `owner.get_all_tasks()`, so it works across all pets. It sorts, filters, builds the daily schedule, completes tasks and finds conflicts.

**How they fit together:** `Owner` → many `Pet` → many `Task`, with each `Task` pointing back to its `Pet`. The `Scheduler` stores no tasks of its own and derives its view from the owner each time, so there is a single source of truth. In the Streamlit app, the `Owner` is kept in `st.session_state` so your data survives each page refresh.

### Scheduler methods

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | By due time, then higher priority first |
| Filtering | `Scheduler.filter_tasks()` | By pet name, completion status and/or task type |
| Daily view | `Scheduler.get_daily_schedule()`, `get_pending_tasks()` | Incomplete tasks only |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.complete_task()` | Daily (+1 day) or weekly (+7 days) from completion day |
| Conflict handling | `Scheduler.find_conflicts()`, `conflicts_with()`, `get_conflict_warnings()` | Overlapping time ranges, same or different pets; warns, never raises |

### Limitations

- The scheduler warns about conflicts but does not resolve them. You decide what to move.
- Times have no time zones, and the app schedules tasks for today.

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The 23 tests in [test/test_pawpal.py](test/test_pawpal.py) cover the scheduling logic in `pawpal_system.py`:

- **Basics:** `mark_complete()` changes a task's status, and `Pet.add_task()` increases the pet's task count.
- **Sorting:** tasks come back in chronological order across multiple pets, even when added out of order. Tasks at the same time are ordered by priority. Completed tasks drop out, and the daily schedule only includes the requested day.
- **Filtering:** by pet name and by completion status, including an unknown pet and a pet with no tasks.
- **Recurring tasks:** completing a daily task creates one for the next day, and a weekly task one for the next week. Month rollovers work, details are copied, late completion counts from the completion day, and completing a task twice creates no duplicate.
- **Conflict detection:** overlapping and identical times are flagged for the same pet and for different pets. Back-to-back tasks, long tasks that cover several others, and tasks that span midnight are handled, and tasks with no pet still produce a warning without crashing.
- **Empty states:** an owner with no pets or tasks returns empty results instead of errors.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/viviany/Documents/Projects/AI110-Intro-to-AI/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 23 items

test/test_pawpal.py .......................                              [100%]

============================== 23 passed in 0.02s ==============================
```

**Confidence Level: ★★★★☆ (4/5)**

All 23 tests pass and they cover the main behaviors and many edge cases, so I'm confident in the scheduling logic. I'm not giving 5 stars because the Streamlit UI in `app.py` is not covered by automated tests, the scheduler only warns about conflicts and never resolves them, and times are naive (no time zones).

## 📸 Demo Walkthrough

### The app (`streamlit run app.py`)

The page has these sections, top to bottom:

1. **Owner:** edit the owner's first name.
2. **Pets:** enter a name and species, then click **Add pet**. Your pets are listed underneath.
3. **Tasks:** pick a pet, a task type (walk, feed, vet), a time, the length in minutes, a priority (1-3) and whether it repeats (none, daily or weekly), then click **Add task**. A green message confirms it, or a yellow warning tells you which existing task it overlaps. A **Mark complete** dropdown and button finish a task. For a repeating task, the message shows when the next one is scheduled.
4. **All tasks:** a table of every task in time order, with dropdowns to show one pet and/or only to-do or done tasks.
5. **Conflicts:** a yellow warning for each overlapping pair, or a green "No scheduling conflicts."
6. **Today's Schedule:** today's unfinished tasks in time order, with the total minutes of care.

### Example workflow

1. **Add a pet:** type "Rex", choose "dog", click **Add pet**. Add a second pet, "Mittens", the same way.
2. **Schedule tasks:** for Rex, add a 30-minute walk at 08:00 that repeats daily. For Mittens, add a 20-minute walk at 08:00.
3. **See the conflict:** the second task shows a warning that it overlaps Rex's walk, and the Conflicts section lists the pair. Both walks stay on the schedule.
4. **See the sorting:** add a feeding for Mittens at 07:00, then look at **All tasks**. It appears first, because tasks are sorted by time no matter what order you added them in.
5. **View today's schedule:** **Today's Schedule** lists what is left for the day.
6. **Complete a task:** choose Rex's walk and click **Mark complete**. It moves to "Done", and a new daily walk is scheduled for tomorrow at 08:00.

### Scheduler behaviors shown

- **Sorting:** tasks added out of order come back in chronological order, with the higher-priority task first when times match.
- **Filtering:** by pet and by status.
- **Conflict warnings:** one for the same pet (vet and feeding both at 14:00) and one across pets (the two 08:00 walks).
- **Recurrence:** completing Rex's daily walk marks it done and adds a new one for the next day (the last line of "Pending tasks" below).

### Command-line demo (`python main.py`)

`main.py` adds six tasks to two pets deliberately out of order, then prints each scheduler view:

```
As added (unsorted)
  14:00  vet   Rex      [todo]
  08:00  walk  Rex      [todo]
  14:00  feed  Rex      [todo]
  09:00  feed  Mittens  [todo]
  18:00  feed  Mittens  [todo]
  08:00  walk  Mittens  [todo]

Sorted by time
  08:00  walk  Rex      [todo]
  08:00  walk  Mittens  [todo]
  09:00  feed  Mittens  [todo]
  14:00  vet   Rex      [todo]
  14:00  feed  Rex      [todo]
  18:00  feed  Mittens  [todo]

Only Mittens
  08:00  walk  Mittens  [todo]
  09:00  feed  Mittens  [todo]
  18:00  feed  Mittens  [todo]

Conflict check
  Warning: walk (Sat 08:00-08:30) overlaps walk (08:00-08:20) for Rex and Mittens
  Warning: vet (Sat 14:00-15:00) overlaps feed (14:00-14:15) for Rex

Completed tasks
  08:00  walk  Rex      [done]

Pending tasks
  08:00  walk  Mittens  [todo]
  09:00  feed  Mittens  [todo]
  14:00  vet   Rex      [todo]
  14:00  feed  Rex      [todo]
  18:00  feed  Mittens  [todo]
  08:00  walk  Rex      [todo]

Today's schedule
  08:00  walk  Mittens  [todo]
  09:00  feed  Mittens  [todo]
  14:00  vet   Rex      [todo]
  14:00  feed  Rex      [todo]
  18:00  feed  Mittens  [todo]
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
