# PawPal+ Project Reflection

## 1. System Design
Three core actions a user can perform:
- Setup tasks/routine for care per pet registered.
- Add/register pet.
- View daily schedule/plan.

**a. Initial design**

- Briefly describe your initial UML design.
**Answer:**
The design models a pet care scheduling system with four classes:

Pet — holds the animal's profile (species, age, special_needs, daily_needs) and exposes methods to check its care requirements. It drives what tasks need to exist.

Task — a dataclass representing a single care activity (feeding, medication, walks, etc.) with timing constraints and priority. Tasks originate from a Pet's needs.

Owner — tracks the person's time availability and time-of-day preferences. They use the Scheduler and ultimately perform the tasks.

Scheduler — the coordinator. It takes an Owner, Pet, and list of Tasks as inputs, then selects, orders, and allocates tasks into a feasible schedule based on the owner's availability.

The flow:

Pet's needs → Tasks → Scheduler organizes them → Owner performs them

The key design decision is that Scheduler doesn't own the domain objects — it receives them from outside, keeping the classes loosely coupled and independently testable.


- What classes did you include, and what responsibilities did you assign to each?
**Answer:** 
Owner
Manages the person's time and preferences. Responsible for tracking available minutes, time-of-day preferences, and consuming time as tasks are assigned.

Pet
Represents the animal's profile and care needs. Responsible for surfacing whether it needs medication, extra care, and producing a summary of its needs.

Task
Represents a single schedulable care activity. Responsible for knowing its own priority, whether it fits within a time window, and whether it can be scheduled given available time.

Scheduler
The coordinator of the whole system. Responsible for selecting which tasks to run, ordering them by priority, allocating them against the owner's available time, and producing a human-readable explanation of the plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

**Answer:**
Yes, five changes were made after reviewing the class skeleton against the UML:

1. **Added `Pet.generate_tasks()`** — The UML specifies a `Pet --> Task : requires` relationship but the skeleton had no code connecting them. This method was added so tasks originate from `daily_needs` and `special_needs` rather than always being created externally.

2. **Guarded `Owner.use_minutes()` against overdraft** — `use_minutes()` could be called without first checking `is_available()`, allowing `available_minutes` to go negative. A `ValueError` is now raised if the requested duration exceeds what remains.

3. **Enforced a consistent time format (`TIME_FORMAT = "%H:%M"`)** — `earliest_start`, `latest_end`, and `available_windows` all used raw strings with no enforced format. A module-level constant and a `Task._parse_time()` helper were added so all time comparisons use the same format and bad input fails fast.

4. **Kept `Task.is_required()` with a clarifying docstring** — The method is a wrapper around `self.required`, but it was retained for polymorphic access and documented so the intent is clear.

5. **Added `Scheduler.validate_schedule()`** — No method existed to verify a completed schedule stays within the owner's `available_minutes`. This method is called after `allocate_time()` and before the final schedule is returned.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**Answer:**
The scheduler considers three constraints:

1. **Time budget** — `Owner.available_minutes` is the hard outer limit. A task is only considered schedulable if `task.duration_minutes <= owner.remaining_availability()`. This is enforced in both `select_tasks()` and `allocate_time()`, and double-checked by `validate_schedule()`.

2. **Priority and required status** — `order_tasks()` sorts tasks so that required tasks always come before optional ones, and within each group by descending priority value (high → medium → low). This ensures the most critical care always gets scheduled before optional enrichment activities.

3. **Time windows** — Each task can specify an `earliest_start` and `latest_end`. `fits_in_window()` checks whether a task's constraints fall within a given availability window, and `sort_tasks_by_time()` orders tasks chronologically so that earlier-windowed tasks are attempted first.

The priority ordering was the most important decision because it maps directly to real pet-owner risk: a missed medication dose has consequences a missed play session does not. Time-budget enforcement is a close second — without it the schedule would be aspirational rather than realistic.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Answer:**
The scheduler uses a **greedy allocation strategy**: it walks the priority-sorted task list in order and grabs each task if time permits, stopping as soon as the budget is exhausted. It never backtracks or tries a different combination to fit more tasks.

The tradeoff is correctness vs. simplicity. A greedy approach can fail to find the optimal packing — for example, skipping one 30-minute optional task could allow three 10-minute tasks to fit instead. A proper knapsack algorithm would find that better solution.

This tradeoff is reasonable here for two reasons. First, pet care schedules are small: a household rarely has more than a dozen tasks per day, so the gap between greedy and optimal is typically just one or two low-priority tasks. Second, the required-first ordering means the greedy approach is essentially optimal for the tasks that actually matter — required, high-priority care is always scheduled, and only optional activities compete for leftover time where the packing inefficiency would appear.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**Answer:**
AI was used at every stage of the project, but in different roles depending on the task:

- **Design brainstorming** — early prompts like "suggest small algorithmic improvements for a pet-owner scheduling app" surfaced ideas (bin-packing, medication gap enforcement, age-based priority boost) that weren't in the original spec and shaped what got built.
- **Implementation** — specific, code-grounded prompts worked best: "implement a method that sorts Tasks by earliest_start using a lambda key" or "add conflict detection that returns warning strings rather than raising exceptions." These produced targeted code that fit directly into the existing class structure.
- **Docstring generation** — using the "Generate documentation" smart action on each new method produced Google-style `Args:` / `Returns:` docstrings consistently across the whole module without having to write them manually.
- **Refactoring and review** — asking "what is wrong with the current generate_schedule output when recurring tasks are added before it runs?" helped diagnose the demo ordering bug in `main.py` where extra task copies inflated the conflict list.

The most useful prompt pattern was always **specific + grounded in the actual code**: referencing the real method name, the real field name, and the real constraint produced answers that could be used directly. Vague prompts like "make the scheduler better" produced suggestions that required significant filtering.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

**Answer:**
When the conflict detection feature was first implemented, the AI wired `generate_schedule()` to call `conflict_warnings()` and print results to stdout. Running `main.py` showed the warnings printing twice — once from the explicit demo call and once from inside `generate_schedule()` — and the second pass also included extra tasks added by the recurring-task demo, producing false same-task-vs-itself conflicts.

The suggestion was not accepted as-is. The fix required two independent judgments: first, reordering the demos in `main.py` so the schedule ran before `complete_and_reschedule()` added new task copies; second, recognising that `generate_schedule()` printing warnings directly to stdout was the wrong layer — the UI (`app.py`) already calls `conflict_warnings()` and renders them with `st.error`/`st.warning`, so the stdout prints in `generate_schedule()` were redundant noise in the Streamlit context.

Verification was done by reading the terminal output line by line and tracing each warning back to the task pair that triggered it, then confirming after the fix that the demo section showed exactly the expected conflicts with no duplicates.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**Answer:**
The test suite in `tests/test_pawpal.py` covers the following behaviors:

- **`Task.mark_complete()`** — verifies that `completed` flips from `False` to `True`. This is the foundation of the status-filtering and recurring-task pipeline; if marking complete doesn't work, neither does anything that depends on it.
- **`Pet.add_task()`** — verifies that the task count on a pet increases and that `task.pet_name` is set to the pet's name. This is the entry point for every task in the system; a broken `add_task` would silently produce tasks with no pet association, breaking `filter_tasks` and `complete_and_reschedule`.
- **`Task.next_occurrence()` for daily, weekly, and weekdays recurrence** — verifies the exact `due_date` produced by each `timedelta` path, including the weekday skip logic when the base date falls on a Friday (expected: Monday, +3 days).
- **`Scheduler.order_tasks()`** — verifies that a required low-priority task sorts before an optional high-priority task, and that within the required group tasks are ordered high → medium → low.
- **`Scheduler.detect_conflicts()`** — verifies that two tasks with overlapping windows are flagged, tasks without windows are ignored, and two non-overlapping tasks produce an empty result.
- **`Scheduler.filter_tasks()`** — verifies pet-name filtering isolates only one pet's tasks, status filtering returns only pending or only completed tasks, and combined filtering works correctly.

These tests matter because they are the exact behaviors most likely to fail silently: wrong dates, wrong sort order, and wrong pet assignment all produce a schedule that looks plausible but is wrong.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

**Answer:**
Confidence is high for the happy path — the core scheduling pipeline (select → order → allocate → validate) and the four new algorithms (sort, filter, recurrence, conflict detection) all behave correctly on realistic inputs as demonstrated by `main.py` and the test suite.

Confidence is lower for the following edge cases, which would be tested next:

1. **`next_occurrence()` across month and year boundaries** — does `date(2024, 12, 31) + timedelta(days=1)` correctly produce `date(2025, 1, 1)`? Python's `date` handles this, but it's worth an explicit assertion.
2. **`filter_tasks()` with a pet name that doesn't exist** — currently returns an empty list; should verify it doesn't raise.
3. **`allocate_time()` when every task is exactly equal to `available_minutes`** — does the first task consume the full budget and leave zero for the rest?
4. **`detect_conflicts()` with tasks whose windows touch but don't overlap** — e.g., task A ends at `09:00` and task B starts at `09:00`. The condition `a_start < b_end AND b_start < a_end` should correctly treat this as non-overlapping (strict inequality), but a test would confirm it.
5. **`complete_and_reschedule()` when `pet_name` is `None`** — the pet lookup loop exits without attaching the new task; the function silently returns it without registering it anywhere.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**Answer:**
The part most worth being satisfied with is that the four new algorithms — sorting, filtering, recurring tasks, and conflict detection — all compose cleanly. `filter_tasks()` and `sort_tasks_by_time()` both accept a `list[Task]` and return a `list[Task]`, so they can be chained in any order without side effects. `complete_and_reschedule()` calls `next_occurrence()` internally and attaches the result to the right pet without the caller needing to know how. `conflict_warnings()` wraps `detect_conflicts()` without duplicating its logic.

That composability wasn't planned upfront — it emerged from keeping each method focused on one responsibility. The result is that `app.py` can call them in any combination depending on what the user has selected, and `main.py` can chain them for terminal output, and neither file contains any scheduling logic itself.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**Answer:**
Two things:

1. **Replace the greedy allocator with a knapsack approach.** The current `allocate_time()` can fail to pack tasks optimally when a large optional task blocks several smaller required ones. A simple 0/1 knapsack over the task list would guarantee no required task is skipped if it fits in the budget, even if a lower-priority task was allocated first.

2. **Decouple `generate_schedule()` from stdout.** Currently the method prints conflict warnings directly with `print()`, which is fine for the terminal demo but pollutes output when called from Streamlit. A cleaner design would return the warnings alongside the schedule — perhaps as a `ScheduleResult` dataclass with `schedule` and `warnings` fields — and let the caller decide how to display them.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

**Answer:**
The most important thing learned is that **AI is most useful when you already understand the problem well enough to evaluate its output.**

Early in the project, broad prompts ("make the scheduler smarter") produced suggestions that needed heavy filtering. Later, once the class structure was clear and the constraints were understood, narrow prompts ("implement conflict detection that returns warning strings and never raises") produced code that could go directly into the file with only minor adjustments.

The shift that made the difference was treating AI as a fast implementation partner rather than a designer. Design decisions — what constraints matter, what the right tradeoff is, where a warning belongs vs. an exception — require understanding the domain and the user. Those judgments came from reading the code, running it, and noticing when the output was wrong. AI accelerated the execution of those decisions but didn't replace the reasoning that produced them.
