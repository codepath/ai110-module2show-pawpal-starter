# PawPal+ Project Reflection

## 1. System Design

**Three Core Actions**
- Track pet task
- Be able to take contraints from User
- Create a plan/schedule for the day based on contraints and criteria given

**a. Initial design**

- Briefly describe your initial UML design.
> I am creating a pet care app and I need an Owner Info class with Names and Pets and a Pet class with Information on the Pet like Name and Birthday and Animal  and the App will have classes that a Task abstract class with duration and ideal time and then that will have 2 child classes called Rigid Task and Static Task, one will have a Priority and an Ideal Time the other has a fixedTime and the app will generate a schedule to be made using these task.
- What classes did you include, and what responsibilities did you assign to each?
> Owner Info has data about the Owner
> Pet has Information about the Pet
> Task abstract class has Duration and IdealTime, shows the duration of the task and the idealtime it should be so how close it should be to it. 
> RigidTask contains Priority, to decide where in the schedule it should be 
> StaticTask contains FixedTime, this is a fixed time in the schedule 


**b. Design changes**

- Did your design change during implementation?
> Yes
- If yes, describe at least one change and why you made it.
> Create a relationship from pets to tasks and give task a name and description field and creating things like date variable instead of just time as the descrption of the instructiosn didn't specify these untill sort functions needed to be added.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    Priority,Preferences,and Time with 2 task  flexible task and static task, those that can be moved around and those that can only be at one time.
- How did you decide which constraints mattered most?
    Through Flexible and Static the user can decide what matters most.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
> There were no tradeoffs all algorthims are simple and appropriate for my project size and AI said nothing about tradeoffs

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
    AI was  very helpful at coming up with Task and test as coming up with the object task to test was very helpful as coming up with valid test and typing them takes time and is tedious.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    It implementing priority as Low Medium and High instead of a number.
- How did you evaluate or verify what the AI suggested?
    Running the App and Verifying it correctly

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    I test for static versus flexible task and how the app made them work and how warning works and how time changes work when similar times flexible events happen.
- Why were these tests important?
    Because it's helping  the work AI did.
**b. Confidence**

- How confident are you that your scheduler works correctly?
    10/10
- What edge cases would you test next if you had more time?
    Maybe testing if all 24 hours of the day were full what was the scheudler gonna do about that while moving times.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    The end product felt very satifying to see.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    The UI could be better.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    Testing yourself is important not just pytest.