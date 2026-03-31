# PawPal+ Project Reflection

## 1. System Design
- Let a user enter basic owner + pet info
    pet_desc, owner_name, pet_height, pet_weight, constraints, priorities(attributes)
    get method for each info
- Let a user add/edit tasks
    task(attributes)
    get and edit method for task
- Generate a daily schedule/plan based on constraints and priorities
    plan(attributes)
    get and edit method for plan
**a. Initial design**

- Briefly describe your initial UML design.
    My initial UML design focused on separating the app into a few clear classes with specific responsibilities. I included Owner to store the user’s name, constraints, and priorities, Pet to store the pet’s description and physical details, Task to represent care activities that could be viewed or edited, Plan to hold the daily schedule, and Scheduler to generate the plan by organizing tasks based on constraints and priorities. This design made the system easier to understand, update, and expand later.
- What classes did you include, and what responsibilities did you assign to each?
    My initial UML design used five main classes: Owner, Pet, Task, Plan, and Scheduler. Owner stored the user’s name, constraints, and priorities, while Pet stored basic pet details like description, height, and weight. Task represented care activities that could be added or edited, Plan stored the daily schedule, and Scheduler was responsible for organizing tasks into a plan based on the owner’s constraints and priorities.
**b. Design changes**

- Did your design change during implementation?
no change
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    My scheduler mainly considers the task's scheduled time, priority level, recurrence or due date, and category. It also uses simple tie-breakers so health-related tasks such as feeding or medication are placed ahead of less urgent activities, and shorter tasks can come first when the time and priority are otherwise similar. Owner constraints and priorities are stored in the plan, although the current version uses them more for context than for advanced optimization.
- How did you decide which constraints mattered most?
    I decided these constraints mattered most by thinking about what a real pet owner would need help with first: tasks that happen at a specific time and tasks related to the pet's health should not be missed. Because of that, time and urgency came before convenience, and then I used simple tie-breakers to keep the schedule readable and practical.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    One tradeoff my scheduler makes is that it only checks for exact time matches such as two tasks both being scheduled at 8:00. It does not yet calculate true duration overlap, so a 30-minute walk at 8:00 and a 15-minute feeding at 8:15 would not be flagged as a conflict.
- Why is that tradeoff reasonable for this scenario?
    That tradeoff is reasonable for this project because it keeps the logic lightweight, readable, and easy to test while still catching the most obvious conflicts a busy pet owner would care about. A more advanced overlap engine would be more powerful, but it would also add extra complexity that is probably unnecessary for a small scheduling app.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI for brainstorming, debugging, explaining the code, and give me some skeleton codes
- What kinds of prompts or questions were most helpful?
the most helpful prompts were to make a skeleton code, it gave me a direction on what to do.
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment where I did not accept the AI suggestion was when we did the testing code, I had to remove several testing cases because it was not aligning with the task
- How did you evaluate or verify what the AI suggested?
I verify what the AI suggested by doing sanity checks for most of them 
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
1. confirm task completion with mark_complete()
2. make sure task list grow when new task is added
3. make sure tasks are returned in chronological order and, for same time tasks, use priority, health category, and duration tie breakers.
4. confirms a completed daily/weekly task creates the next occurrence with right features
5. make sure that duplicate task are flagged
6. verifies that "once" tasks do not create duplicate

- Why were these tests important?
These test were important because they cover all bases of the website, catching edge cases like, recurrence, redunency, or simple things such as time ordering of the tasks are all important
**b. Confidence**

- How confident are you that your scheduler works correctly?
I am mostly confident that the code would work as intentdent.
- What edge cases would you test next if you had more time?
not sure, I added all edge cases that I want, maybe I could think more cases if I have more time
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I was most satisfied with the way I handle the streamlit code
**b. What you would improve**
- If you had another iteration, what would you improve or redesign?
I would make a calender like UI that the user would have a better time visualizing it.
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned that I can't just give the AI a big generic task and expect it to work, I need to split the work into multiple small task and then refined them later on