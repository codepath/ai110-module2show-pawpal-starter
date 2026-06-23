# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- I have 4 class, owner, pet, task, scheduler
- The owner, has all the descriptive information of the owner and their general availability
- The pet has all the descriptive information of the pet and some relevant functions, such as get_name(), get_species(), add_special_need(), get_spectial_needs()
- The task has the task_id, name, task_type, duration_minutes, and some functions like get_duration(), get_priority(), set_priority, get_task_type()



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

-The model wanted the owner to directly manage the pets. I chose not to do that since it wasn't directly relevant. 
-The scheduler is the central coordinator (connects owner+pet+tasks)
-4.5 also wanted to create a test file

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

It was constrained by everything being hard coded. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

-it has a greedly algorithmic tradeoff, picking the highest priority task first. 
-topoligcal stort: it sacrifices some optimization
-madatory first: may crowd out others

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
