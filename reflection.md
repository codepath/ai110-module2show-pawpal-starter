# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Four classes, each with a single clear responsibility:

| Class | Responsibility |
|-------|---------------|
| `Task` | Holds one care activity: what, when, how long, how often, and whether it's done |
| `Pet` | Groups tasks under a named animal; owns `add_task` / `get_tasks` |
| `Owner` | Aggregates multiple pets; `get_all_tasks` flattens the tree into `(pet_name, Task)` pairs |
| `Scheduler` | Wraps an `Owner` and provides all algorithmic behavior: sorting, filtering, recurrence, conflict detection |

The data flow is strictly top-down: `Scheduler → Owner → [Pet] → [Task]`. No class reaches upward, which makes each layer independently testable.

`Task` and `Pet` are Python `@dataclass`es (immutable-friendly, zero-boilerplate). `Owner` and `Scheduler` are plain classes because they manage mutable state and behavior.

**b. Design changes**

Originally, `mark_task_complete` lived on `Task` itself. During implementation, I moved recurrence logic into `Scheduler.mark_task_complete` because generating the next task requires adding it to a `Pet`'s list — that cross-object mutation belongs in the coordinator (`Scheduler`), not the data object (`Task`). `Task.mark_complete()` was kept as a simple status flip.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:
- **Time** — tasks are sorted by `HH:MM` string (lexicographic sort is correct for zero-padded 24h time).
- **Due date** — `get_todays_schedule` only surfaces tasks due today or earlier; future tasks are hidden until relevant.
- **Completion status** — completed tasks are excluded from the active schedule.
- **Priority** — stored on each task and visible in the UI; not used for auto-reordering (by design — time is the primary axis for a daily schedule).

**b. Tradeoffs**

`detect_conflicts` checks for exact `HH:MM` matches only — it does not check whether two 30-minute tasks starting at 08:00 and 08:15 would overlap. This is a deliberate simplification: exact conflicts are unambiguous and always wrong (you can't be in two places at once), while duration-based overlap introduces grey areas (parallel tasks at home are fine). For a v1 scheduler, flagging exact collisions is the highest-signal check with the lowest implementation complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- **Architecture brainstorm**: Used Claude to pressure-test the four-class design — specifically asking whether `Scheduler` should be a standalone class or a method on `Owner`. Claude correctly argued for separation of concerns (Scheduler as a "strategy" object), which matched my intuition.
- **Algorithm review**: Asked Claude to suggest a Pythonic way to sort `HH:MM` strings. It confirmed that `sorted(..., key=lambda x: x[1].time)` works correctly for zero-padded 24-hour strings without needing `datetime.strptime`.
- **Test generation**: Used Claude to draft edge-case test names, then wrote the actual assertions manually.
- **UI explanation feature**: Claude is integrated live in `app.py` via the Anthropic API — it reads the generated schedule and explains the ordering in plain English to the pet owner.

**b. Judgment and verification**

Claude initially suggested using `datetime.strptime(task.time, "%H:%M")` as the sort key for "correctness." I kept the plain string comparison instead: for zero-padded `HH:MM` strings, lexicographic order is identical to chronological order, and avoiding the `strptime` call keeps the sort key simple and fast. I verified this by testing with edge values (`"00:00"`, `"09:00"`, `"10:00"`, `"23:59"`) — string sort produced the correct order in all cases.

---

## 4. Testing and Verification

**a. What you tested**

17 tests across 6 classes:

| Behavior | Why it matters |
|----------|---------------|
| `mark_complete` flips `completed` | Core state mutation — must be reliable |
| `add_task` increases count | Verifies tasks actually persist on the Pet |
| Sort returns chronological order | Wrong ordering would produce a useless schedule |
| `filter_tasks` by pet / status | Incorrect filtering would surface wrong data in UI |
| Daily/weekly recurrence creates next task with correct date | Recurrence is the main "smart" feature |
| `once` tasks don't recur | Prevents ghost tasks accumulating |
| Conflict detection fires on same time, silent on different times | Core correctness of conflict logic |
| Edge cases: no pets, no tasks, empty plan text | Prevents crashes on empty state |

**b. Confidence**

★★★★☆ (4/5) — all happy paths and key edge cases are covered. Next tests:
- Overlapping duration conflicts (08:00 + 30min vs 08:15)
- Tasks with due dates in the future are excluded from today's schedule
- Sorting stability when two tasks share the same time

---

## 5. Reflection

**a. What went well**

The separation of the logic layer (`pawpal_system.py`) from the UI (`app.py`) paid off immediately: all 17 tests ran without importing Streamlit, and the CLI demo (`main.py`) verified data flow before the UI was touched. Bugs in sorting and recurrence would have been painful to debug inside a running Streamlit app.

**b. What you would improve**

Persist state across app restarts (currently lost when the Streamlit process stops). A lightweight SQLite backend or JSON file would make the app genuinely useful. I'd also add duration-aware conflict detection and a visual timeline view using `st.plotly_chart`.

**c. Key takeaway**

AI tools are most valuable when you already have a clear design. Asking Claude to "build my scheduler" produces a mediocre monolith. Asking Claude to "review my Scheduler.detect_conflicts signature — is there a simpler return type?" produces focused, actionable feedback. The human's job is to own the architecture; AI's job is to accelerate implementation and surface blind spots.
