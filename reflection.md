# PawPal+ Project Reflection

## 1. System Design

Three core actions a user needs to perform with PawPal+:

1. **Add and manage pets** — enter a pet's name, species, breed, age, weight, and any medical conditions so the system knows who it's caring for.
2. **Schedule care tasks** — add tasks (walks, feedings, medication, grooming, etc.) with a specific time, priority level, and frequency (once/daily/weekly) so the app knows what needs to happen and when.
3. **View and act on today's schedule** — see all pending tasks for the day sorted by time, mark tasks complete, and have recurring tasks automatically rescheduled for the next occurrence.

---

**a. Initial design**

My initial UML had four classes: `Owner`, `Pet`, `Task`, and `Scheduler`. `Owner` manages multiple pets and exposes methods to aggregate their tasks. `Pet` holds profile info and a list of care tasks. `Task` stores what needs to happen, when (HH:MM time), how often (frequency), and tracks completion. `Scheduler` sits on top of the Owner and provides algorithmic methods — sorting, filtering, conflict detection, and recurring task management.

The relationships: Owner manages many Pets; Pet owns many Tasks; Scheduler reads from Owner. This maps directly to the UML in `diagrams/uml_draft.mmd`.

**b. Design changes**

Yes, a few things changed.

The biggest change was how I handled task ownership. Initially `Task` didn't know which pet it belonged to — I expected the caller to always have the pet context. But `Scheduler.detect_conflicts()` needs to compare tasks across all pets at once, so it needs to know which pet each task belongs to without re-fetching. Adding `pet_name: str` directly on `Task` solved this with minimal complexity.

I also removed a time-budget concept I drafted early on. My first pass had the scheduler filter tasks based on how many minutes an owner had available. Once I implemented `todays_schedule()`, I realized that concept doesn't belong in a time-based planner — if a task is scheduled at 8am, it goes in the plan regardless of budget. The budget idea was me confusing two different scheduling models. Removing it simplified everything.

The final diagram (see `diagrams/uml_final.mmd`) now accurately reflects the actual four classes in `pawpal_system.py` with all their methods.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three main constraints:

1. **Time budget** — the owner sets how many minutes they have. Tasks that would exceed the remaining budget get skipped.
2. **Task priority** — critical tasks (like medication) always score highest and get scheduled before lower-priority ones.
3. **How overdue a task is** — a task that's been skipped for longer gets a higher score, so chronic neglect can't happen even if the task has medium priority.

I decided priority mattered most because missing medication is genuinely dangerous, while skipping enrichment one day is fine. The overdue bonus exists so that low-priority tasks don't get pushed out forever — they slowly accumulate urgency until they get picked up.

**b. Tradeoffs**

The main tradeoff is the **greedy fill** approach. The scheduler just picks the highest-scoring task, checks if it fits in the remaining time, and moves on. It never looks ahead to see if a different combination of tasks would use the budget more efficiently.

This is reasonable for this scenario because pet owners aren't running a bin-packing optimization — they just want a clear, predictable list. A backtracking search would be harder to explain ("why did it skip this big task to fit three small ones?") and wouldn't meaningfully improve outcomes for a 2-hour daily budget. The tie-breaking rule (shorter tasks go first when scores are equal) gives a little efficiency improvement without the complexity.

---

## 3. AI Collaboration

**a. How I used AI**

I used Claude Code throughout this project. During the design phase I described the scenario and asked it to help me think through what classes made sense and where responsibilities should live. That conversation helped me land on separating the scheduler logic from the data models early.

For implementation, I let it write most of the code based on my design decisions — I described the scoring formula I wanted (priority × 20 + overdue hours × 1.5 + never-done bonus) and it implemented it. It also generated the Streamlit UI layout and the test suite. The most useful prompts were ones where I gave it a specific rule ("tasks that have never been done should get a +10 bonus on top of the overdue calculation") rather than open-ended ones like "write a scheduler."

**b. Judgment and verification**

One thing I didn't accept as-is was the time slot assignment for the `not_due` display. The AI initially proposed hiding not-due tasks entirely from the plan view. I pushed back on that because it felt like information the owner needed — if Mochi's evening walk is already done, I want to see that, not wonder why it's missing from the list. I asked it to add a collapsible "already handled" section and verify the `next_due_at()` calculation was correct before trusting it.

I also caught a test bug: one test for the multiple-daily frequency was using `datetime.now()` (8 AM) as a reference, but the scheduler internally uses midnight of the plan date. The test was passing sometimes and failing others depending on when it ran. Once I understood the bug, I fixed the test to anchor `last_done` relative to midnight explicitly.

---

## 4. Testing and Verification

**a. What I tested**

I wrote 15 tests covering the most important scheduling behaviors:

- Priority ordering (critical before optional)
- Overdue bonus (more overdue = higher score)
- Never-done bonus
- Budget enforcement (total minutes never exceeded)
- Task skipping when budget is full
- Critical tasks winning over filler even with a tight budget
- Inactive tasks not appearing
- Frequency intervals (multiple-daily, weekly) evaluated correctly
- Tie-breaking by duration (shorter task goes first when scores are equal)
- Reasoning strings are non-empty

These tests are important because the scheduler is the core of the app. If the priority ordering or budget enforcement breaks, the plan becomes useless — and bugs there are silent, you'd just get a bad plan with no error.

**b. Confidence**

I'm fairly confident in the scheduling logic for the cases I tested. Where I'm less confident is edge cases with multiple pets, tasks that span multiple days, and the slot assignment when many tasks compete for the same time window (e.g., three medications all wanting the morning slot). I'd test those next.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the scoring formula. It's simple enough to explain to a user ("your task scored higher because it's been overdue for 12 hours and it's high priority") but it actually produces sensible plans. The per-task reasoning text that surfaces in the UI directly comes from the score components, so there's no gap between what the algorithm does and what the user sees.

**b. What I would improve**

If I had another iteration, I'd add editable task details (right now you can only archive, not edit), and I'd let users manually reorder the generated plan. The greedy algorithm is opinionated — if it decides walk comes before grooming, there's no way to say "actually I want to groom first today." A drag-to-reorder on the plan output would make the app feel much more like a real assistant and less like a rigid output.

**c. Key takeaway**

The most important thing I learned is that AI works best as a collaborator, not a replacement for design thinking. When I described exactly what I wanted the scoring formula to do and why, the AI implemented it correctly on the first try. When I was vague ("make a smart scheduler"), the output was generic and needed a lot of rework. The clearer my mental model, the more useful the AI's help became — which means the design thinking still has to happen in my head first.
