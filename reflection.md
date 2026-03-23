# PawPal+ Project Reflection

## 1. System Design

### Actions to program

Three core actions:
- Add a pet
- Schedule a walk (task with date, time duration, and priority)
- See today's tasks

Extended
- Schedule medication (task with date, priority and without time duration)
- Explain what constraints informed today's tasks
- Edit tasks

### Object building blocks

#### Pet
Attributes
- name: str

#### Owner
Attributes
- name: str
- pets: list<Pet>
- preferences: dict (e.g. preference: value)

Methods
- add_pet(Pet) -> adds pet to pets

#### Task
Attributes
- name: str
- priority: str category
- start_time (optional): time 
- end_time (optional): time
- date: date
- assigned_pets: list<Pet>

Methods
- init(name, priority, date, start_time = None, end_time = None)
- get_duration() -> difference between start and end times

#### Schedule
Attributes
- tasks: list<Task>
- date: date (now)

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Initial design included a pet and owner class, as well as a task and schedule class. The pet will be associated with a set of tasks. An owner will have a

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
