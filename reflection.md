# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My initial UML design incorporates the four main components as an individual class for my pet care app that checks each requirement on what it's supposed to accomplish, which is to be a smart pet care management system that helps owners keep their furry friends happy and healthy. 

- What classes did you include, and what responsibilities did you assign to each?
As stated earlier, I included four classes that individually represent each main component for the app. For instance, the responsibilities in the Pet class is updating its profile and getting what it needs on a daily schedule. Then, the Owner class has responsibilites for removing tasks, updating their pet's preferences, and receiving a summary of tasks in the form of a schedule. Next, the Task class contains responsibilities to set priorities and time durations of the tasks needed to be complete for their pet on a daily basis to keep them happy and healthy. Finally, the Scheduler class contains responsibilities for sorting tasks, checking conflicts, and providing explanation to the owner so that the pet's schedule accomodates with the owner's lifestyle for the schedule to work.


**b. Design changes**

- Did your design change during implementation?
Yes, my design did change during implementation. 

- If yes, describe at least one change and why you made it.
One change I made is adding the relationships between Scheduler and Task, and Scheduler and Pet. This change was very necessary because the Scheduler class can build a plan accordingly with adding tasks while following constraints based on a pet's information provided by the owner.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

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
