# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user must be able to perform:

1. Add a pet (with basic info) to their household.
2. Schedule a care task for a pet (what, when, how long, how often).
3. See "today's schedule" for all pets in one organized view.

For the initial UML (`diagrams/uml.mmd`) I settled on four classes with one responsibility each:

- **Task** — one care activity: description, time ("HH:MM"), date, duration, frequency, and completion status. It knows how to mark itself complete and produce its next occurrence if it recurs.
- **Pet** — identity (name, species) plus that pet's task list, with methods to add and list tasks. A pet owns its tasks; nothing else edits them directly.
- **Owner** — identity plus the pets, with methods to add and look up pets. The owner is the single entry point to all household data.
- **Scheduler** — the "brain". It holds no data of its own; it reads through the Owner and organizes tasks **across all pets**: today view, sorting, filtering, conflict detection, and completing tasks (which drives recurrence).

I asked Claude to draft the Mermaid diagram from this brainstorm and reviewed it for unnecessary complexity — the main thing I enforced was keeping Scheduler stateless (it references the Owner instead of duplicating task lists), so there is exactly one source of truth.

**b. Design changes**

Yes. Two key design decisions emerged during implementation:

1. **Scheduler methods return `(pet, task)` pairs instead of bare tasks.** A cross-pet schedule needs pet context for every row — a `Task` has no back-reference to its `Pet`. Returning pairs keeps `Task` simple (no circular references) while making every schedule view, filter, and conflict message pet-aware.
2. **Recurrence is split between `Task` and `Scheduler`.** `Task.next_occurrence()` handles pure "what would the follow-up be" logic, while `Scheduler.complete_task()` handles adding that follow-up to the right pet's task list — keeping concerns separated.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers, in the order I added them:

1. **Date** — only tasks due today appear in the daily view (`tasks_for_today`).
2. **Time of day** — tasks are ordered chronologically by their "HH:MM" time (`sort_by_time`).
3. **Completion status and pet** — views can be narrowed to pending/done tasks or to a single pet (`filter_by_status`, `filter_by_pet`).
4. **Collisions** — two tasks at the same time raise a warning (`detect_conflicts`), because a single human can't walk the dog and feed the cat simultaneously.
5. **Priority** (stretch) — high-priority tasks outrank earlier-but-lower-priority ones when I ask for a priority-ordered view.

I decided what mattered most by walking through the day of the busy owner in the scenario: the first question is "what do I do _today_ and in what order" (date + time), then "what's left" (status), then "am I double-booked" (conflicts). Priority came last because it only matters once the basics above already work.

**b. Tradeoffs**

`detect_conflicts()` uses interval overlap detection: two pending tasks conflict when their time blocks (start time through start + duration) overlap on the same date. Back-to-back tasks (one ends exactly when the next starts) are fine. The tradeoff:

- Conflicts are **purely advisory** — returned as a list of warning strings, never raising exceptions or blocking scheduling. The system warns but doesn't prevent double-booking.
- This design is deliberate: pet care tasks are flexible anchors, and the owner should decide whether to reschedule. A strict "reject conflicts" approach would make the scheduler rigid and frustrating.
- The advisory model also simplifies testing — tests verify the warnings appear without needing to handle exception flows.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude (Claude Code) as the executing engineer while I stayed the architect and reviewer:

- **Design brainstorming** — turning my brainstormed attributes/methods into the Mermaid UML, then reviewing the skeletons against it (see §1b for what that review changed).
- **Test-first implementation** — for every layer I had the AI write the failing behavior tests first, we confirmed they failed, then implemented to green. This kept "AI wrote plausible code" from ever being the acceptance bar.
- **Streamlit state investigation** — before wiring the UI I asked how `st.session_state` should hold my `Owner` so it survives reruns; the pattern we landed on (create once behind an `if "owner" not in st.session_state` guard, then always read from the vault) is exactly what `app.py` does.

The most helpful prompts were _constraint-rich_ ones: naming the exact files, the rule set (no mocks, one behavior per test, gt/uv only), and the acceptance evidence I expected. Vague prompts produced generic code I had to redo.

**b. Judgment and verification**

- One key verification point was the edge-case handling in `find_next_available_slot()`. The test `test_next_available_slot_respects_day_end_boundary_with_late_task` verifies that tasks scheduled after `DAY_END` (21:00) don't create false available slots — the algorithm correctly clamps gap-scanning to waking hours.
- I verified AI-generated scheduling logic by reviewing the algorithm step by step and ensuring comprehensive test coverage for boundary conditions: empty schedules, fully packed days, and tasks outside waking hours.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  I tested task CRUD functionality, chronological sorting across multiple pets, filtering by status and pet, recurring task rescheduling (+1 day for daily, +7 days for weekly), advisory collision warnings for overlapping times, priority-based sorting (high > medium > low, broken by time), waking-hours gap detection (empty day, busy blocks across pets, no available slot, late-night task boundaries), and JSON persistence round-trip. I also tested the Streamlit UI using `AppTest` (adding pets, tasks, rendering sorted tables, and validating saving/loading workflows).
- Why were these tests important?
  These tests were critical to verify that the core scheduler logic behaves correctly under complex scenarios (such as multi-pet conflict boundaries) and that persistence does not corrupt the datetime/date parsing. Using `AppTest` ensures that the UI integrates with the logic layer correctly without needing a manual browser test for every commit.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  I have high confidence. The test suite consists of 62 behavior-focused tests running on real objects with zero mocks. Every layer passes trunk linting and code formatting checks.
- What edge cases would you test next if you had more time?
  If I had more time, I would test DST boundary overlaps (e.g., tasks scheduled during daylight saving time shifts) and concurrency limits in persistence if multiple users saved or loaded the schedule at the same instant.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  I am most satisfied with the decision to write real, mock-free tests from the beginning. Implementing pytest-bdd and AppTest for Streamlit ensured that every single layer of the stack was fully functional and test-verified, preventing regressions and giving us high confidence.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  I would add multi-day scheduling views (e.g., a weekly overview), timezone-aware scheduling for owners who travel, and concurrent task limits per caretaker so the system can model households where more than one person shares responsibilities.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  Setting strict architecture boundaries (like making the Scheduler class stateless and keeping the Owner class the single entry point) makes collaborating with AI incredibly clean. When the AI has clear instructions and a solid architecture, it writes high-quality code that is easy to verify and integration-test.
