# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

    I want a class Owner that is directly related to a class Pet, because an Owner can have one or more pets but a pet can only have one owner. Then I added a class task that handles all the tasks of each pet based on the owner. Lastly, I added a class Scheduler that creates a plan based on the owner, the pet, tasks assigned, priorities and then it explains the plan. In the UML Scheduler depends on  Owner and Pet to generate the plan. The class Owner has a composition relationship with the class Pet, that also has a composition relationship with the class Task.

- What classes did you include, and what responsibilities did you assign to each?

    Owner class -> holds owner's name, available time, and preferences. This class is responsible of managing the pets.

    Pet class -> holds pet's name, type of pet, and their age. This class is responsible of holding and managing the list of tasks.

    Task class -> reprsents a single care activity that holds name, duration in minutes, priority (1-3), and preffered time of day.

    Scheduler class -> takes an Owner and a Pet and filters tasks based on time constraints and preferences, sorts them by priority, generates a daily plan, and explains the reasoning behind it.


**b. Design changes**

- Did your design change during implementation? 

    Yes, significant changes were made during implementation.

- If yes, describe at least one change and why you made it.

    **Major Change: Task Status System**
    Initially, I used a simple `completed: bool` to track if tasks were done. During implementation, I discovered this was insufficient for real pet care scenarios. I redesigned it to use a 3-state `status` system with "pending", "in-progress", and "completed" states. This allows the tasks to be in an intermediate workflow state, providing better tracking and more realistic scheduling behavior.

    **Additional Changes:**
    - Expanded Task with unique `task_id` (UUID) for proper tracking
    - Implemented `filter_by_status()` and `filter_by_time_slot()` methods in Scheduler for analyzing constraints instead of just sorting

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

    The scheduler considers:
    1. **Time constraints**: Total available time (morning + afternoon split)
    2. **Priority levels**: 1-3 priority ordering (1=high, 3=low)
    3. **Time preferences**: Morning vs afternoon preferred time for each task
    4. **Feasibility**: Task duration must fit within available time
    5. **Recurring patterns**: Daily/weekly/monthly frequency
    6. **Status state**: Only includes pending/in-progress tasks in schedule (skips completed)

- How did you decide which constraints mattered most?

    Priority > Time Feasibility > Time Preference. AI suggested using weighted scoring, but I chose greedy algorithm with priority-first ordering since it's simpler and sufficient for a single pet per scheduler. High-priority tasks are scheduled first, then medium, then low—ensuring critical pet care (medications, feeding) never gets skipped.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

    **Tradeoff: Greedy Scheduling vs Optimal Scheduling**
    - Greedy approach: Sort by priority, add tasks in order until time runs out. Fast, simple, predictable.
    - Optimal approach: Use constraint satisfaction or branch-and-bound to find the best possible schedule. Slower, more complex.

- Why is that tradeoff reasonable for this scenario?

    For a single pet owner with ~10-20 daily tasks, greedy is perfectly reasonable. It runs instantly and produces intuitive schedules (high-priority tasks always get scheduled). Optimal would be overkill complexity. If the system scaled to 100 tasks across 10 pets, we'd reconsider.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

    AI was invaluable for:
    1. **Design iteration**: AI suggested the 3-state status system instead of boolean —> I accepted this.
    2. **Recurring task logic**: AI provided timedelta-based date calculation code that I refined.
    3. **Test generation**: AI drafted test templates; I adapted them for project-specific needs.
    4. **Code review**: AI identified edge cases (e.g., "What if a pet has no tasks?") that led to better validation.
    5. **UI enhancement**: AI suggested using st.warning for conflicts and st.success for completions.

- What kinds of prompts or questions were most helpful?

    Most helpful prompts:
    - "What edge cases should I test for a recurring task system?" → Led to TestTaskCompletion tests
    - "How should I structure the Scheduler to handle multiple filtering methods?" → Clear OOP guidance
    - "Why is my test failing?" → AI analyzed error, identified frequency validation bug
    - "Suggest Streamlit components for conflict warnings" → Practical UI/UX recommendations

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

    **Rejected: Sorting vs Filtering for Step 2**
    - AI initially suggested: "Implement sort_by_time() to sort tasks by HH:MM format" -> I found it a bit problematic since we handled it by minutes and preffered time which is strings.
    - Reality: The system uses minutes (0-480), not HH:MM
    - My decision: Implemented filter_by_status() and filter_by_time_slot() instead —> more useful for analyzing constraints
    - Verification: Wrote tests for both methods, verified they work with multi-pet scenarios

- How did you evaluate or verify what the AI suggested?

    I verified through:
    1. **Code inspection**: Does this match the data model?
    2. **Testing**: Run pytest; did the suggestion pass all tests?
    3. **Manual testing**: Load data in Streamlit, test UI flows
    4. **Domain knowledge**: Does this make sense for pet owners?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

    Tested 34 behaviors across 11 test classes:
    1. Task status transitions (pending→in-progress→completed)
    2. Invalid status rejection (raises ValueError)
    3. Recurring task next-occurrence creation
    4. Task addition and ordering
    5. Task validation (duration, priority, status)
    6. Duplicate pet prevention
    7. Task feasibility (does duration fit available time?)
    8. Owner time slot assignments
    9. Conflict detection (morning/afternoon overflow)
    10. Priority sorting
    11. Filtering by status (pending/in-progress/completed)
    12. Filtering by time slot (morning/afternoon/flexible)
    13. Multi-pet filtering validation

- Why were these tests important?

    Testing ensures:
    - Data integrity (no invalid tasks, statuses, configurations)
    - Algorithmic correctness (conflicts detected, priorities honored)
    - Recurring automation (no infinite loops, proper date calculation)
    - UI safety (filtering won't crash on edge cases)
    - User confidence (34 passing tests = reliable system)

**b. Confidence**

- How confident are you that your scheduler works correctly?

    **Confidence Level: 5/5 stars**
    - All 34 tests pass consistently
    - Tested both happy paths and edge cases
    - Multi-pet scenarios validated
    - No known bugs or crashes
    - Manual Streamlit testing confirms UI works end-to-end

- What edge cases would you test next if you had more time?

    1. **Very short time slots**: What if owner has only 15 minutes total? (Scheduler should handle gracefully)
    2. **All high-priority tasks overflow**: Conflict detection message could be more granular
    3. **Timezone edge cases**: What if due_date crosses midnight? (Currently not handled)
    4. **Large datasets**: Performance with 500+ tasks (scalability testing)
    5. **Concurrent updates**: What if multiple pets are updated simultaneously? (Thread safety)

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

    **Most satisfied: The 3-state task status system + recurring automation**
        It's elegant, simple, and solves real problems. The auto-generation of next occurrences is intuitive for users. Testing validated it works in all scenarios. Streamlit UI displays it beautifully with status dropdowns

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

    1. **Conflict resolution strategy**: Instead of just flagging conflicts, suggest which low-priority tasks to skip
    2. **Task templates**: Pre-built recurring tasks (e.g., "Daily Dog Walk", "Weekly Vet Checkup")
    3. **Persistent storage**: Save schedules and pets to database (currently session-only in Streamlit)


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    
    AI excels at suggesting implementations, generating test templates, and catching syntax errors. But I had to:
    - Understand the problem (pet care) to reject suggestions that didn't fit
    - Test AI suggestions before trusting them
    - Make intentional design choices (greedy vs optimal, filtering vs sorting)
    - Verify correctness through rigorous testing
    
    The best results came when I treated AI as a brainstorming partner, not an oracle. I asked good questions, evaluated suggestions critically, and made decisions aligned with project requirements and system constraints. This project taught me that being the "lead architect" means using AI effectively while keeping human judgment in the driver's seat.
