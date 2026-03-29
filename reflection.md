# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
	- My first UML version separated the data layer from the planning layer. I wanted clear entities (Owner, Pet, Task) and one scheduler class that turns those inputs into a practical day plan.

- What classes did you include, and what responsibilities did you assign to each?
	- I used four classes: Owner, Pet, Task, and Scheduler.
	- Owner stores top-level constraints and preferences (like available minutes per day and preferred schedule).
	- Pet keeps pet-specific info plus that pet's tasks.
	- Task models each care action (title, duration, priority, required/optional, timing fields, etc.).
	- Scheduler does the heavy lifting: gather tasks, rank/filter them, enforce constraints, and build a feasible schedule.

**b. Design changes**

- Did your design change during implementation?
	- Yes. Once I started implementing, I realized a few class interactions needed to be tighter.
- If yes, describe at least one change and why you made it.
	- Biggest change: I added task_id and switched removal/lookup from title-based to ID-based (remove_task(task_id) and get_task_by_id(task_id)). Titles can repeat, so ID-based handling is way safer.
	- I also added refresh_inputs() and a selection_reasons dictionary in the scheduler. That made data flow cleaner and gave me a reliable way to explain why a task was included or skipped.

### Phase 1 UML vs Final UML (Checklist)

- [x] **Task identity improved**: Added task_id and shifted task management from title-based lookup to ID-based lookup.
- [x] **Task lifecycle expanded**: Added completion + recurrence fields (is_completed, due_date, last_completed_on, last_completed_day, time, start_minute, description).
- [x] **Task behavior expanded**: Added mark_complete() and is_due_on_day() to support recurring scheduling.
- [x] **Pet-task linkage refined**: Updated remove_task(task_id) and added get_task_by_id(task_id).
- [x] **Owner-pet relationship made explicit**: Final model includes Owner managing multiple pets (add_pet, remove_pet, get_pet, get_pets, get_all_tasks).
- [x] **Scheduler state expanded**: Added selection_reasons, task_pet_lookup, schedule_date, and refresh flow via refresh_inputs().
- [x] **Time-aware scheduling added**: Added sort_by_time() and sort_tasks_by_time() for chronological and slot-based ordering.
- [x] **Filtering APIs added**: Added filter_tasks_by_pet_status() and alias filter_by().
- [x] **Conflict detection added**: Added detect_conflicts() and get_conflict_warnings() with owner-facing warning text.
- [x] **Recurring automation added**: Added mark_task_complete() logic in scheduler to auto-create next daily/weekly task instances.

This final UML now reflects how classes actually interact in pawpal_system.py: Owner owns many Pet, each Pet has many Task, and Scheduler orchestrates ranking, filtering, conflict checks, and schedule generation over those objects.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
	- I treat owner limits as hard constraints first (available minutes and max tasks). Then I check whether a task is even eligible (not already completed, due when needed, and usable timing info for ordering/conflict checks). After that, I rank using priority, required flag, and preferred time windows (morning/afternoon/evening/night/anytime). I also run overlap checks using start time + duration.
- How did you decide which constraints mattered most?
	- I used this order: feasibility -> obligation -> preference.
	- If feasibility breaks, the schedule is unrealistic.
	- If required/due tasks are ignored, care quality drops.
	- Preferences matter, but they are soft rules compared to required care.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
	- A clear tradeoff is conflict handling. Right now, if a task overlaps, I skip it for that run instead of trying to fully re-optimize the whole day.
- Why is that tradeoff reasonable for this scenario?
	- For this project, that tradeoff is acceptable. PawPal+ is meant to be quick, practical, and explainable for a busy owner. A simple, predictable planner with clear warnings was a better fit than a complicated optimizer.

---

## 3. AI Collaboration

**a. Most effective Copilot features**

- Which Copilot features were most effective for building your scheduler?
	- Iterative Copilot chat in VS Code helped the most. I could describe one rule at a time and get options quickly.
	- Inline suggestions were useful for smaller cleanup tasks (like simplifying condition blocks and quick refactors).
	- Chat was best for higher-level reasoning: ranking logic, recurrence behavior, and conflict strategy.
	- I also used it to generate edge-case ideas, then turned those into tests.

**b. Suggestion I rejected or modified**

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
	- One Copilot suggestion was to auto-reschedule overlapping tasks into nearby free slots.
	- I chose not to make that the default because it made the logic much harder to explain and test.
	- I kept the cleaner approach: detect conflict, skip that task for this run, and show a clear reason/warning.

**c. Separate chat sessions by phase**

- How did using separate chat sessions for different phases help you stay organized?
	- Keeping separate Copilot chats for design, implementation, and testing honestly helped a lot.
	- In the design chat, I stayed focused on class boundaries and relationships.
	- In the implementation chat, I focused on behavior/debugging.
	- In the testing chat, I focused on edge cases and assertions.
	- That separation reduced context drift and made each decision easier to trace later.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
	- I tested task validation, pet task add/remove/get behavior, owner constraints and preferences, scheduler ranking/selection, chronological sorting, pet/status filtering, recurrence creation after completion, and conflict detection/warnings. I also covered edge cases like duplicate titles, due-date handling, and mixed completion states.
- Why were these tests important?
	- These tests matter because this app is all about trust in scheduling decisions. If ranking/filtering/recurrence breaks, the plan becomes unreliable. The tests gave me confidence that refactoring did not quietly break user-visible behavior.

**b. Confidence**

- How confident are you that your scheduler works correctly?
	- For the current scope, I am highly confident. The suite covers core model behavior, ranking/selection, recurrence, filtering, and conflict messaging, and all tests are passing.
- What edge cases would you test next if you had more time?
	- Next I would test boundary times (exact slot transitions), multiple pets with very similar windows, extremely tight time budgets with many required tasks, and long recurrence chains over many simulated days. I would also add more end-to-end day-plan tests, not just unit-level checks.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
	- I am most satisfied with the balance between usefulness and explainability. The app gives a practical schedule, but it also tells the user why tasks were selected or skipped.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
	- In another iteration, I would split ranking, feasibility filtering, and conflict handling into even clearer strategy components so each piece is easier to test and swap. I would also consider an optional "smart reschedule" mode, while keeping the current lightweight mode as default.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
	- Biggest takeaway: good system design is mostly about clear decisions, not just more features. AI helped me move faster, but I still had to set scope, choose tradeoffs, and verify behavior with tests.

**d. Lead architect lesson with AI**

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
	- I learned that being the "lead architect" means owning system boundaries and standards, not just accepting fast code suggestions. AI gave me lots of possible solutions, but I had to choose what fit the architecture, reject what added unnecessary complexity, and keep class responsibilities clean. In practice, tests became my final quality gate before I accepted any AI-assisted change.

---

## 6. Prompt Comparison (Multi-Model)

**a. Complex task used for comparison**

- What task did you compare across models?
	- I used weekly task rescheduling as the comparison task. The prompt was basically: after a weekly task is marked complete, generate the next instance with the correct due date, keep metadata consistent, avoid duplicate IDs, and keep the logic easy to test.

**b. Model outputs and quality**

- Which models did you compare?
	- I compared an OpenAI model response and a Claude response for the same scheduling prompt.
- Which one felt more modular or Pythonic, and why?
	- The OpenAI response felt more modular for this codebase because it naturally separated responsibilities into small helper methods, used clear naming, and matched the existing class structure better. It also suggested implementation steps that mapped cleanly to my current methods, so I did not have to rewrite my architecture to fit the answer.
	- The Claude response had good ideas too, especially around edge-case handling, but in my case it leaned toward broader rewrites and a slightly heavier structure than I needed. It was useful for stress-testing assumptions, but less plug-and-play for my existing design.

**c. Final decision and takeaway**

- What did you finally choose and what did you learn from comparing?
	- I ended up using the more modular OpenAI-style structure as the base, then borrowed a few edge-case checks inspired by the Claude output. Comparing both was useful because it reminded me that the "best" answer depends on fit with the current codebase, not just how sophisticated the raw idea sounds.


