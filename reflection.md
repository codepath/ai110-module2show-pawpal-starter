# PawPal+ Project Reflection

## 1. System Design

- The user should be able to add their breed/pet
- The user should be able to schedule walks or other task throughout the day
- The user should be able to edit any task on the calendar for that day or any that are planned for the week.

**a. Initial design**

- Briefly describe your initial UML design: The initial design involves the app as the scheduler which will handle any conflicts in schedule, generate the schedule, constraints, owner and their pets. The scheduler will also house the plan for the owners.

- What classes did you include, and what responsibilities did you assign to each?
  : I have created an Owner class that weill be able to add their pets. I wanted to make sure that they would have the capability to create more than one pet profile. The pet class will consist of the name, species, breed, age and the list of tasks that we will define later. The owner will be able to edit the task under the pet profile, show tasks and add task. The Task class will have a description, title, category, duration, priority for the owner, scheduled time, frequncy, real-time status and any constraints. <-----> May place contraints with the Ownwer later.

Class Schedule will have a place to submit the date, pet, task and explanation.

**b. Design changes**


- Did your design change during implementation? Yes, I wanted to make sure that the functionality of the app was able to meet the requirements for the project but also implement what I would want as a user for myself. 
- If yes, describe at least one change and why you made it. I made sure that the app added a feature that included time management so that any disruptions in the planned time could be accounted for. 
In the latest revision, we added unique IDs to both Pet and Task classes to ensure reliable editing and referencing. We also improved type hints and method signatures for better clarity and maintainability, including specifying return types and using forward references. These changes strengthen relationships between objects and lay a more robust foundation for implementing scheduling and task management logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most? I wanted to value schedule conflicts so that the user could manage their time wisely. Everyone is extremely busy and need a way to always track time. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Exact time match vs. overlapping durations:**
The `detect_conflicts()` method only flags two tasks as a conflict when they are scheduled at the exact same `datetime` — for example, both at `17:00`. It does not account for task duration, so a 30-minute walk starting at `16:45` and a feeding task at `17:00` would not be flagged even though they realistically overlap.

This is a deliberate tradeoff. Tasks in the current system do not have a `duration` field, so there is no data available to calculate overlap. Building duration-aware conflict detection would require adding a new field to `Task`, updating every place tasks are created, and writing a more complex range-overlap check along the lines of `task_a.time + task_a.duration > task_b.time`. That added complexity is not justified at this stage of the project.

The exact-match approach is simple, reliable with the data we have, and still catches the most obvious scheduling mistakes — two things literally booked at the same moment. If task duration is added in a future phase, the detection logic in `Scheduler` can be upgraded without changing anything else in the system.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)? I used AI as a co-programmer to help plan, design and implement changes to the app. I also use AI to construct a simple but robust test suite to make sure that the app could handle edge cases. 
- What kinds of prompts or questions were most helpful? When using the prompt #codebase, it helped for the model to review the code and make sure that the direction of the app was following the flow. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is. It was attempting to add uncessary function for checking time conflicts. 
- How did you evaluate or verify what the AI suggested? I left the suggestion in the code ran a test on it and if it did not pass I would remove the implementation. The main thing to focus on when working with AI is using the correct context. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test? I tested the conflicts of time which seemed to be the most important. I manually added conflicts in the tasks to make sure that the app gave the user a message that would help them understand the conflict in time. 
- Why were these tests important? Time is always important to everyone. 

**b. Confidence**

- How confident are you that your scheduler works correctly? I am 100% confident that the app works due to the test suite and manual testing in the actual app.
- What edge cases would you test next if you had more time? We due to not having a data base it would be no reason to test if the user is the same person. If I was using postgres or sqlite I would test to make sure the same person was not able to create a profile. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with? I am satisfied with ho9w I was able to prompt and review the changes that I wanted to see. I was able to read the code even though python is not my first language. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign? I would want to add a data base and sign in page for each user. I would implement a sync with the user's favorite calendar to make sure they can keep up with their schedules daily.

- Would let the owner add pictures of their pets just in case they were lost to help with finding lost animals. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project? The importance of system design is where the field of software engineering is going. Even though I know that foundational skills in learning the languages are just as important. System design will allow engineers to create meaningful apps and implementation with co-pairing with AI. 
