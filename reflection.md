# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  - The UML diagram includes:
    - domain entities, these are "real world" entities/main actors, within our model this would be the **Owner** and **Pet**. The **Owner** is the primary user, they own **Pet**(s), and declare **AvailabilityWindows** and manage **Tasks**
    - Task model, Tasks has a type (**TaskType** enum), urgenecy (**Priorty** enum), and reccurence pattern (**ReccurenceScope** enum)
    - Schedule outputs, **DailySchedule** and **WeeklyMonthlyPlan** are two view of the generated schedule, with each holding a list of Tasks.
    - Schedule engine,**Scheduler** is the logic core; it takes the tasks and availability windows as inputs and produces  the schedule outputs
- What classes did you include, and what responsibilities did you assign to each?
  - Captilized and Bolded nouns within (a) are the classes, they can also be found in the pawpal_uml.md

**b. Design changes**

- Did your design change during implementation?
  - I decided to first outliine my functional and non-functional requirements prior to starting. Reading the writeup/readme left me with a good amount of room/ambiguity to refine what exactly I wanted. I first read the write up, and then practiced create FR and NFRs, I then went to claude and asked what FR and NFRs is it could extract, I then compared, refined and produced a final version of the FR and NFRs that I was able to create a UML diagram with. Using this process allowed me to process and solve ambiguities within my understanding of the project rather than in the middle of the implmenetation.
- If yes, describe at least one change and why you made it.
  - n/a

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
