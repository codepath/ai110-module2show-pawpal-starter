# PawPal+ Project Reflection

## 1. System Design

**Three core actions a user can perform:**

1. **Add a pet** to their profile (name + species).
2. **Add a care task** to a specific pet (description, time of day, and how often it recurs).
3. **View today's schedule** across all their pets, sorted by time, with warnings when two tasks collide.

**a. Initial design**

I split the system into four classes, each with a single clear responsibility:

- **`Task`** — represents one care activity (a walk, feeding, medication, etc.). It holds a
  `description`, a `time` in `"HH:MM"` format, a `frequency` (`once` / `daily` / `weekly`), and a
  `completed` flag. It knows how to `mark_complete()` itself and how to produce its
  `next_occurrence()` for recurring tasks.
- **`Pet`** — stores a pet's `name` and `species` and owns a list of `Task` objects. It exposes
  `add_task()`, `list_tasks()`, and `task_count()`. It does *not* know anything about scheduling —
  it is just a container for that pet's tasks.
- **`Owner`** — the top-level entity. Holds the owner's `name` and a list of `Pet` objects, with
  `add_pet()` and `get_all_tasks()` (which flattens tasks across *every* pet so the scheduler can
  work system-wide, not one pet at a time).
- **`Scheduler`** — the "brain." It takes an `Owner` and organizes their tasks: `sort_by_time()`,
  `filter_tasks()` (by pet or completion status), `detect_conflicts()` (same-time collisions), and
  `complete_task()` (which also regenerates recurring tasks). Keeping this logic out of `Pet`/`Owner`
  means the data classes stay simple and all the algorithms live in one place.

**Relationships:** `Owner` **1→\*** `Pet` (an owner has many pets), `Pet` **1→\*** `Task` (a pet has
many tasks), and `Scheduler` **1→1** `Owner` (a scheduler operates on one owner's whole system).

**b. Design changes**

- **Added a `due_date` field to `Task`.** My first draft kept `Task` time-only (`"HH:MM"`), which was
  enough for sorting and conflict detection. But once I implemented recurring tasks, "mark a daily task
  complete and create the next one" had no meaning without a date to advance. I added
  `due_date` (defaults to today) so `Task.next_occurrence()` can compute the following day/week with
  `datetime.timedelta`. Conflict detection still compares only the `"HH:MM"` time, so this change
  didn't complicate that logic — it just made recurrence real.
- **Split responsibility for recurrence between `Task` and `Scheduler`.** `Task.next_occurrence()`
  builds the *next* task object, but it's `Scheduler.complete_task()` that marks the current task done
  and attaches the new occurrence back onto the correct pet. Keeping `Task` unaware of which `Pet`
  owns it preserved the clean one-directional ownership (Owner → Pet → Task) from my original design.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler's main organizing constraint is **time of day** — every task carries an `"HH:MM"`
time, and the schedule is always presented chronologically across all pets. On top of that it
tracks **completion status** (so finished tasks can be filtered out) and **frequency** (so daily
and weekly tasks regenerate themselves). I decided *time* mattered most because the core user need
is "what happens next, and when" — a pet owner reads their day top-to-bottom. Completion and
frequency came next because they're what keep the schedule honest over multiple days. I
deliberately left richer notions like task duration and numeric priority out of the first version
to keep the model small and the logic verifiable.

**b. Tradeoffs**

- **Conflict detection uses exact time matches, not overlapping durations.** Two tasks conflict
  only if they share the same `"HH:MM"` slot; an 08:00 task lasting 45 minutes does *not* flag a
  conflict with an 08:30 task. This is reasonable for the scenario because a pet owner's tasks are
  short, discrete events (a feeding, a pill) where "two things booked at once" is the realistic
  failure mode, and exact-match keeps the algorithm O(n) and trivial to reason about. Adding
  duration-based overlap would mean storing durations and doing interval math for a payoff most
  users wouldn't notice — a clear case of not over-engineering the first version.

---

## 3. AI Collaboration

**a. How you used AI**

I used an AI coding assistant in agent mode as a pair-programmer across the whole build: brainstorming
the four-class design, generating the Mermaid UML, scaffolding `pawpal_system.py`, writing the CLI
demo and the pytest suite, and wiring the Streamlit UI. The most useful prompts were **specific and
verifiable** — e.g., "sort tasks across all pets by their `HH:MM` time" or "when a daily task is
completed, create the next occurrence for the following day using `timedelta`." Vague prompts
("make the scheduler smart") produced sprawling code; narrow prompts tied to one method produced
code I could actually read and test. Working in separate phases (design → core → algorithms →
tests → UI) kept each conversation focused instead of ballooning.

**b. Judgment and verification**

- **A suggestion I modified:** my initial `Task` model was time-only, with no date. When I asked
  for recurring tasks, the straightforward path was "create a new task the next day" — but that has
  no meaning without a date field. Rather than bolt a fragile hack on, I **added a `due_date` field**
  to `Task` and let `next_occurrence()` advance it with `timedelta`, while keeping conflict detection
  time-only. I documented this in section 1b.
- **How I verified:** I didn't take generated code on faith. Every layer was exercised — I ran
  `main.py` and read the real terminal output, wrote a **9-test pytest suite** that all passes, and
  drove the Streamlit UI headlessly (add pet → add task → conflict warning → mark complete →
  recurrence) to confirm the wiring actually worked, not just that it compiled.

---

## 4. Testing and Verification

**a. What you tested**

The suite (`tests/test_pawpal.py`) covers: task completion flips status; adding a task increases a
pet's count; sorting returns tasks chronologically across pets; filtering by pet and by status;
conflict detection flags same-time tasks (and produces *no* warning when times are unique);
recurrence creates the next-day task for a daily task; a `once` task does not recur; and a pet with
no tasks produces an empty schedule without errors. These matter because they are exactly the
behaviors a user relies on — a scheduler that mis-sorts or silently double-books is worse than none.

**b. Confidence**

Confidence: **4/5**. All core behaviors and the main edge cases pass, and I verified the same logic
through the CLI, the tests, and the live UI. With more time I'd test **overlapping-duration**
conflicts (not just exact matches), **weekly** recurrence across a month boundary, and behavior when
many tasks share one slot.

---

## 5. Reflection

**a. What went well**

The clean separation between the logic layer (`pawpal_system.py`) and the UI (`app.py`) paid off
repeatedly: the exact same classes power the CLI demo, the tests, and the Streamlit app, so verifying
the "brain" once meant the UI just had to call it. The CLI-first workflow made bugs cheap to catch.

**b. What you would improve**

I'd add **task duration** and true interval-overlap conflict detection, plus **priority-based**
ordering so that when time is tight the important tasks win. I'd also add JSON persistence so pets
and tasks survive between runs.

**c. Key takeaway**

Being the "lead architect" with a powerful AI meant my leverage was in **design decisions and
verification**, not typing. The AI could generate any method in seconds, but *which* classes should
exist, where recurrence logic should live, and whether the output was actually correct were mine to
own. Small, testable prompts plus real verification beat one giant "build me everything" request
every time.
