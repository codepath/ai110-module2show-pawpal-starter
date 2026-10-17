# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My intial UML design includes 4 classes such as owner, pet, task, and scheduler. Owner has attributes such as first name, last name, age, and pet type. Pet also has attributes like name, age, gender, and animal type. Task include walking, feeding, and taking pet to the vet, and these task go to the owner. For scheduler, the owner has a certain when he has to do these tasks. 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yea, my design change during implementation. In the UML diagram, I extended the task to include reoccurence class with attributes like daily and weekly. This is to add timing to the task.

I made a few more changes after reviewing the first version for missing relationships and logic bottlenecks:

- A `Task` now keeps a reference to its `Pet`, so a schedule that mixes several pets can still say which pet a task is for.
- The `Scheduler` does not store its own task list anymore. It reads everything through `owner.get_all_tasks()`, because a second copy of the tasks could drift out of sync with the pets' lists.
- I removed `Owner.pet_type`, since it duplicated `Pet.animal_type` and could not describe an owner with a dog and a cat.
- I replaced free-text task types with `TaskType` and `Recurrence` enums so a typo like "Walk" vs "walk" cannot break filtering.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers **time** (due time and duration, which together define a task's time range), **priority** (used to order tasks that start at the same time), **pet** (so it works across several pets), **completion status**, and **recurrence** (daily or weekly). I decided time mattered most, because the whole point of the app is a daily plan the owner can follow and the only thing that makes two tasks impossible to do together is overlapping time. Priority is deliberately a tie-breaker and not a hard rule, since a high-priority task shouldn't silently bump another. I did not build owner preferences or an available-hours limit, to keep the first version small.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler only *detects* conflicts and warns the owner; it does not automatically move or drop tasks to resolve them. `get_conflict_warnings()` finds overlapping tasks (using start time plus duration, not just identical start times) and returns readable messages, but it leaves the schedule unchanged. I also kept the conflict check simple: it compares every pair of pending tasks (`itertools.combinations`) instead of using a faster early-exit loop. When I reviewed it, the faster loop was about 12x quicker at 1,000 tasks but returned the same results, so I chose the shorter version that reuses `Task.overlaps()` and is easier to read.

This is reasonable for a pet owner because they have a few dozen tasks at most, so the speed difference is microseconds, while readability matters more. And only warning is safer than auto-resolving: the scheduler can't know whether a vet visit should beat a walk (priority alone doesn't capture that), so the owner makes the final call.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used the AI coding assistant for design brainstorming (turning my four-class idea into a UML diagram and then dataclass skeletons), for reviewing my own design (asking what relationships were missing and where the logic could bottleneck), for implementing the scheduler methods in small steps, for writing tests, and for connecting the backend to the Streamlit UI. The most helpful prompts were specific and built on what already existed, such as "Based on my skeletons in `pawpal_system.py`, how should the Scheduler retrieve all tasks from the Owner's pets?" and "what are the most important edge cases to test?". Asking for a review of my design before writing logic was especially useful, because it caught problems (like the duplicated task list) while they were still cheap to fix.

The features that helped most were having the assistant read and edit several files at once (the logic, the UML, the tests, `main.py` and `app.py` all had to stay in step), running the code and the tests itself so every change was checked straight away, and the Streamlit test runner, which let it confirm the UI behaved without me clicking through the app each time.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

There were a few moments where I did not take the first answer as it came:

- **Conflict detection:** the AI suggested a simpler version using `itertools.pairwise`, which only compares neighbouring tasks. I rejected that after checking it: it gave different results than my version, because a long task (a 2-hour vet visit) can overlap several later tasks, not just the next one. I kept comparing all pairs and used `itertools.combinations` instead, then confirmed it matched the earlier version on random data and added a test for the long-task case.
- **Recurring tasks:** the first version computed the next due date as the old due date plus one day. The project instructions said the new date should be "today + 1 day", and testing showed why that matters: a task that was due last week and finished today would have reappeared in the past. I changed it to count from the completion day and kept the original time of day.
- **A hidden bug:** while reviewing the code I noticed that completing a recurring task twice would create two copies of the next occurrence, so I made `mark_complete()` do nothing the second time and wrote a test for it.

I verified suggestions by running the tests, running `main.py` to see the real output, and comparing the old and new algorithms on the same data before choosing one.


---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 23 tests. They cover the basics (completing a task, adding a task to a pet), sorting (out-of-order input across several pets, ties broken by priority, completed tasks leaving the schedule, one-day views), filtering (by pet and status), recurrence (daily and weekly, month rollovers, copied details, no duplicates, counting from the completion day), conflict detection (same pet and different pets, back-to-back tasks, long tasks, tasks crossing midnight, tasks with no pet) and empty states (an owner with no pets, a pet with no tasks). They matter because the scheduler's value is that the owner can trust it: a wrong sort order, a missed overlap or a duplicated recurring task would quietly make the plan wrong.


**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident (4 out of 5) in the scheduling logic: all 23 tests pass and they include many edge cases. I'm less sure about the Streamlit UI, which I checked with a test runner but has no automated tests in the project. With more time I would test time zones and daylight-saving changes, a recurring task whose next occurrence overlaps another task, very large numbers of tasks, and invalid input in the UI (for example two pets with the same name, which would confuse the pet dropdown).


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with how the pieces fit together. The `Scheduler` has no data of its own, so there is one source of truth, and every feature (sorting, filtering, recurrence, conflict warnings) is a small method that I could test on its own. I'm also pleased that the same methods drive both the command-line demo and the Streamlit app, so I didn't write the logic twice.


**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would let the scheduler help resolve conflicts, for example by suggesting the next free time slot for a task that clashes, instead of only warning. I would also let owners schedule tasks on any date and not just today, add the owner and pet details (age, gender) to the UI, and add automated tests for the UI. Finally, I would add weekday-specific recurrence ("Monday, Wednesday, Friday").


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

**Working with AI tools: being the lead architect.** The AI is fast and capable, so it is easy to let it make the design decisions by default. What worked best was keeping those decisions for myself: I owned the structure (four classes, the `Scheduler` reading through the `Owner`, one source of truth) and the AI did the typing within it. Whenever I let it suggest something, I treated the suggestion as a proposal to be checked, not an answer, and the checks (tests, real output, comparing two versions) were what caught the problems. It also helped that I could ask the AI to review my design before building on it.

**Organizing the work.** I did most of this work in one long chat, not a separate chat for each phase, so I stayed organized through the files instead: the UML, the tests, the README and the commit history marked each phase, and each new request started from the code as it actually was and not from memory. If I did it again, I would start a fresh chat for each phase (design, implementation, testing, UI) so that each one begins with a clean, focused context and only the relevant files.

**Designing systems.** One source of truth beats keeping copies in sync. Several of my bugs and design problems (the duplicate task list, the redundant `pet_type`) were the same mistake in different forms.

