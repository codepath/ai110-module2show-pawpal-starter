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

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
