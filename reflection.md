# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial design (proposed with Claude Code, then written up in `diagrams/uml.mmd`) had six classes:

- **`Task`**: one care activity. Holds its title, duration, priority (low/medium/high), and an optional preferred part of the day (morning/afternoon/evening). It validates its own values, so a bad priority or a zero-minute task raises an error right away.
- **`Pet`**: a pet's name, species, and list of tasks, with `add_task` / `remove_task`.
- **`Owner`**: the owner's name, how many minutes they have for pet care today, when their day starts, and their pets.
- **`Scheduler`**: the decision-maker. It picks which tasks fit in the time budget and decides when each one happens.
- **`DailyPlan`**: the result: scheduled items, skipped tasks with reasons, total minutes, and an `explain()` method that prints the plan as text.
- **`ScheduledItem`**: one task placed at a start time, plus the reason it was chosen.

I kept the data classes (`Task`, `Pet`, `Owner`) separate from the logic (`Scheduler`) and the output (`DailyPlan`), so the Streamlit UI only has to build objects, call `build_plan()`, and display the result.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. When I added conflict handling, I added a `fixed_time` field to `Task` for appointments that must happen at an exact time (like a vet visit). Before that, the scheduler laid every task out back-to-back, so overlaps were impossible and there was nothing to handle. I also added a `conflicts` list to `DailyPlan` and an `overlaps()` method to `ScheduledItem`. A task can't have both a fixed time and a preferred time, because the two would contradict each other.

The order of steps inside `build_plan` also changed. At first the scheduler applied the time budget first and resolved fixed-time conflicts second. That meant a task that lost a conflict still used up minutes. I moved conflict resolution before the budget step so those minutes stay available.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers:

1. **Fixed times**: an appointment must happen at its exact time. If two overlap, the higher-priority one wins.
2. **Time budget**: the total scheduled minutes can never exceed the owner's available minutes.
3. **Priority**: high-priority tasks are chosen before medium and low ones.
4. **Duration**: among tasks with the same priority, shorter tasks go first so more of them fit.
5. **Preferred time of day**: morning tasks start from 08:00, afternoon from 12:00, evening from 17:00.

I ranked them by what would hurt the pet or owner most if ignored. A missed vet appointment or a missed dose of meds matters more than when a play session happens. So fixed times and priority decide *what* gets done, and preferences only decide *when*.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler picks tasks **greedily**: it walks through the tasks in priority order and takes each one if it still fits. It never goes back to check whether a different combination would use the time better. For example, with 60 minutes free, a 50-minute high-priority task gets picked even if two medium tasks of 30 minutes each would have filled the hour exactly.

That's reasonable here because the owner cares most about the important tasks getting done, not about filling every minute. Greedy selection is also easy to explain ("it was high priority and it fit"), which matters because the app has to explain its choices. A smarter search would be harder to explain and isn't needed for a handful of daily pet tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude Code as an agent for most of the build. It set up the environment, proposed the class design, wrote `pawpal_system.py` and the tests, connected the scheduler to `app.py`, and tested the app in a browser. I also used it to run a prompt comparison for conflict handling (see `ai_interactions.md`): the same model got a vague one-line prompt and a detailed spec, each in a separate copy of the project.

The most helpful prompts were specific ones that said exactly what behavior I wanted and which tests to write. The detailed conflict-handling prompt produced code I could check line by line against my requirements.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I didn't accept either conflict-handling version as-is. The detailed-prompt version (B) was easier to review, but it let a task that lost a conflict still use up time budget. The vague-prompt version (A) handled that better, but it changed files I hadn't asked about and was twice as much code. I chose B as the base and had A's fix merged in.

To verify, I had a test added for exactly that case (`test_dropped_fixed_task_does_not_use_up_time_budget`). It fails on B's original code and passes on the merged version, which shows the fix actually changes behavior. I also ran the full test suite (19 passing) and ran the app with two overlapping appointments to check that the conflict message appeared.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The 19 tests in `tests/test_pawpal_system.py` cover:

- High priority beats low priority when time is short.
- The plan never goes over the time budget.
- Shorter tasks win ties between tasks with the same priority.
- Preferred times are respected (an evening task starts at 17:00).
- No two scheduled tasks overlap, with or without fixed-time tasks.
- Overlapping fixed tasks: the higher priority one is kept, and ties go to the one listed first.
- Flexible tasks are pushed past fixed tasks they would overlap.
- A task that loses a conflict doesn't use up time budget.
- Invalid input is rejected (bad priority, zero duration, bad time strings, fixed + preferred together).
- An empty task list gives an empty plan, and every scheduled task has a reason.

These matter because they're the promises the app makes to the owner: important things get done, the plan fits their day, and nothing is double-booked.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident about the behaviors listed above, since each has a test. One limit is that the AI wrote both the code and most of the tests, so the tests check the rules it chose. They don't prove those rules are the right ones for a real owner.

Edge cases I would test next:

- A task that *wins* a conflict but is then dropped because time runs out. Right now the task it beat stays dropped too, even though the time slot is free.
- Tasks that run past midnight, or a fixed time earlier than the owner's day start.
- A single-digit hour like `"8:00"`, which the time check currently accepts.
- Two pets sharing the same owner's time budget (the scheduler only plans one pet).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with how the app explains itself. Every scheduled task has a "Why" (for example, "high priority, fits in the 90-min budget; fixed appointment at 08:15"), and every skipped task says exactly why it was left out ("needs 60 min but only 10 min left"). A pet owner doesn't have to trust a black box; they can see the reasoning and disagree with it.

I'm also happy with the conflict handling, because I didn't just take the first version. Comparing two prompts, picking one, and merging in the better idea from the other produced a result that was better than either one alone, and I have a test that proves the difference.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

- **Recurring tasks.** Real pet care repeats: feeding twice a day, meds every day, grooming once a week. Right now the owner has to re-enter everything for each day. I'd add a frequency to `Task` (daily / weekly) and have the scheduler pick the tasks that are due.
- **Multiple pets.** `Owner` can hold several pets, but `Scheduler` only plans one at a time, so two pets don't share the owner's time budget. I'd schedule all of an owner's pets together.
- **Fix the conflict-winner edge case.** If a fixed task wins a conflict but is then dropped because time runs out, the task it beat should get its slot back.
- **Saving tasks.** Tasks disappear when the app restarts. Saving them to a file would make the app usable day to day.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Being specific with AI pays off, but being specific isn't the same as being right. The detailed prompt gave me code I could review against my own requirements, which the vague prompt didn't. But one of my requirements (letting a dropped task keep using time) was actually the weaker design, and the AI followed it anyway. The AI can build what I describe very quickly, so the hard part, and my job, is deciding what *should* be built and checking the result with tests and by running the app myself.
