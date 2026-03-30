# 🐾 PawPal+

**PawPal+** is a Streamlit app that helps busy pet owners plan and manage daily care tasks for multiple pets. It uses a priority-aware scheduling engine to fit tasks into the owner's available time window, handles recurring care routines, and flags any scheduling conflicts before they become a problem.

---

## 📸 Demo

<a href="/course_images/ai110/pawpal1.png" target="_blank">
  <img src='/course_images/ai110/pawpal1.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

<a href="/course_images/ai110/pawpal-task.png" target="_blank">
  <img src='/course_images/ai110/pawpal-task.png' title='PawPal App - Tasks' width='' alt='PawPal App - Tasks' class='center-block' />
</a>

---

## Features

### Priority-based scheduling
Tasks are sorted high → medium → low priority before time slots are assigned. Within the same priority level, tasks with an earlier `preferred_time` are placed first. This guarantees that critical care needs — medication, feeding, walks — always claim a time slot before optional activities like grooming.

### Sorting by preferred time
`Scheduler.sort_by_time()` re-orders any task list by `preferred_time`, earliest first, using priority as a tiebreaker. The UI exposes this as a "Sort by: Preferred time" toggle so owners can view their tasks in the natural order of the day rather than the order they were entered.

### Filtering by pet and status
`Scheduler.filter_tasks(pet_name, completed)` returns a filtered slice of all tasks. Both parameters are optional and composable — filter by pet only, by completion status only, or both at once. The task table in the UI includes dropdowns for pet, status (Pending / Completed / All), and sort mode, all wired to this method.

### Daily recurrence
Tasks carry a `frequency` field (`"once"`, `"daily"`, `"weekly"`). When a recurring task is marked complete via `Scheduler.complete_task()`, `Task.next_occurrence()` automatically creates a fresh copy with `is_completed=False` and registers it back on the pet for the next scheduling cycle. One-time tasks that are completed are permanently excluded from future schedules.

### Conflict detection
`Scheduler.get_all_conflicts()` performs a pairwise scan of all scheduled tasks using the interval overlap condition `max(starts) < min(ends)`. It returns every overlapping pair with the overlap duration in minutes and whether the clash is within the same pet or across different pets. `warn_conflicts()` converts those results into plain warning strings — no exceptions raised, never crashes — so the UI only needs `if warnings:` to handle the result.

### Conflict warnings in the UI
If any conflicts are found after building the schedule, a red `st.error()` banner appears at the top of the results with a count, followed by individual `st.warning()` lines — one per conflict. Warnings appear *before* the schedule so the owner sees them immediately rather than after already reading the plan.

### Skipped task visibility
Tasks that cannot fit in the owner's available window are collected in `Scheduler.skipped_tasks` and displayed in the UI as a warning list after the schedule, so the owner knows what was left out and can adjust priorities or durations for the next run.

---

## System design

| Class | Responsibility |
|---|---|
| `Owner` | Stores the owner's name and daily availability window |
| `Pet` | Holds a pet's details and owns its task list |
| `Task` | Represents one care activity with priority, frequency, and timing hints |
| `ScheduledTask` | Wraps a placed `Task` with its assigned `start_time` and scheduling `reason` |
| `Scheduler` | Orchestrates all scheduling logic — sorting, filtering, slot assignment, conflict detection, and recurrence |

See [class_diagram.md](class_diagram.md) for the full Mermaid UML diagram.

---

## Smarter Scheduling

The scheduling engine goes beyond a basic greedy algorithm with four concrete improvements:

**Sort by time** — `sort_by_time()` orders tasks by `preferred_time` for display, independently of how the scheduler placed them.

**Filter by pet and status** — `filter_tasks()`, `filter_by_pet()`, and `filter_by_priority()` give the UI precise control over which tasks to show.

**Recurring task support** — `generate_recurring_tasks()` gates schedule eligibility by frequency, and `complete_task()` auto-spawns the next occurrence for daily and weekly tasks.

**Conflict detection** — `get_all_conflicts()` and `warn_conflicts()` surface overlapping time slots as human-readable warnings without crashing the program.

**Next-available-slot finder** — `find_next_slot(task)` scans every gap in the current schedule and returns the earliest opening wide enough to hold a task's duration. Unlike the greedy builder (which only appends to the tail), this is a true gap-scan: it checks the window before the first task, every gap between consecutive tasks, and the tail, returning the first fit or `None` if the day is fully packed. See [Algorithm detail](#find_next_slot-algorithm) below.

---

## `find_next_slot` algorithm

`Scheduler.find_next_slot(task)` answers: *"Given the schedule as it stands right now, where is the earliest opening I could slot this task in?"*

**Why it matters** — The greedy `build_schedule()` only ever appends. Once a schedule is built, there's no built-in way to ask "can I still fit a vet visit at 2 PM?" `find_next_slot` fills that gap, enabling a UI button like "Find me a slot" without rebuilding the whole schedule.

**Steps:**

1. Sort the existing `scheduled_tasks` by start time to get a clean ordered list of occupied intervals.
2. Build a list of **candidate start times** — the places a new task *could* begin:
   - `available_start` (the gap before the very first task)
   - The `end_time` of each scheduled task (immediately after each block)
3. For each candidate, compute the **wall** — the latest the new task can end before hitting the next occupied block (or `available_end` if no block follows).
4. Accept the first candidate where `candidate + task.duration ≤ wall` and `candidate + task.duration ≤ available_end`.
5. Return `None` if no candidate passes.

**Complexity** — O(n log n) for the sort + O(n) for the linear scan = O(n log n) overall, where n is the number of scheduled tasks.

```
Window:  |=====08:00============================================20:00=====|
Tasks:   |  Walk(30)  |     gap(30)    | Grooming(20) |       tail        |
                 ↑                ↑
         candidate 08:30      candidate 09:00 (after grooming)
         wall = 09:00         wall = 20:00

find_next_slot(20-min task) → 08:30  ✓ (fits in the 30-min gap)
find_next_slot(40-min task) → 09:00  ✓ (gap too small; tail fits)
```

---

## How Agent Mode was used

Claude Code's **Agent Mode** drove the entire implementation of `find_next_slot` through a multi-step agentic loop without manual intervention at each step:

1. **Codebase exploration** — An Explore subagent read every Python file and summarized the class structure, method signatures, and existing algorithm patterns. This gave the agent precise knowledge of how `_assign_time_slots` works before writing a single line of the new method.

2. **Algorithm design** — Using that context, the agent reasoned about what the greedy builder *can't* do (insert into gaps) and chose a gap-scan approach. It worked out the candidate/wall pairing on the `scheduled_tasks` list before touching any file.

3. **Implementation** — The agent wrote `find_next_slot` directly into [pawpal_system.py](pawpal_system.py) with a full docstring explaining each numbered step of the algorithm, matching the existing code style (same `datetime.combine` pattern, same `timedelta` arithmetic).

4. **Test generation** — The agent then wrote `TestFindNextSlot` in [tests/test_pawpal.py](tests/test_pawpal.py), covering six cases: empty schedule, single blocker, gap between two tasks, gap too small, fully packed window, and the exact-fit boundary. Each test has an inline comment explaining *why* that case matters.

5. **Verification** — The agent ran `pytest` autonomously and confirmed 39/39 passing before updating this README.

The entire flow — explore → design → implement → test → verify — ran without the user writing any code or switching tools.

---

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

### Run the CLI demo

```bash
py main.py
```

---

## Testing

### Run the test suite

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains **39 tests** across 8 test classes:

| Class | What it checks |
|---|---|
| `TestTask` | `mark_complete()`, priority flag, `fits_in_window()` boundary |
| `TestPet` | Adding/removing tasks, `pet_name` stamping |
| `TestOwner` | Available window tuple, total minutes calculation |
| `TestScheduledTask` | `end_time` computation, time range, display string format |
| `TestScheduler` | Pet registration, task flattening, schedule build order, skip-on-overflow |
| `TestSortingCorrectness` | Chronological order, `None` preferred_time sorts last, priority tiebreak |
| `TestRecurrenceLogic` | Daily task creates new occurrence, one-time task does not, completed tasks excluded from schedule, unique IDs across completions |
| `TestConflictDetection` | Exact same start time flagged, warning strings, normal schedule has zero conflicts, empty schedule is safe, overlap true/false boundary |
| `TestFindNextSlot` | Empty schedule, slot after blocker, gap between tasks, gap too small (continues scan), fully packed window returns None, exact-fit boundary |

### Confidence level

**★★★★☆ (4 / 5)**

The core scheduling contract — priority ordering, greedy slot assignment, recurring task lifecycle, and conflict detection — is fully covered and all 33 tests pass. One star is withheld because the Streamlit UI layer (`app.py`) has no automated tests; user-facing input handling and edge cases there are only verified manually.
