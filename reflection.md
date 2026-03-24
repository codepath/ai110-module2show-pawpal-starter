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

#### Scheduler
Attributes
- tasks: list<Task>
- date: date (now)

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

UML diagram under ./UML, contains initial classes with their relationships, methods, and attributes.

Initial design included classes:
- pet: holds pet information and is assigned to task and owner
- owner: holds owner preferences and is associated with a set of pets
- task: holds task information and which pets they're related to. can be edited and can be aggregated in a schedule
- scheduler: holds a set of tasks for a given day to be displayed in the frontend

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Based on the README suggestions, I realized that it was asking for a Scheduler class so I changed that.

I also changed some relationships based on the README information. A pet has a list of tasks instead of a pet being assigned to a task. The owner provides access to their pets' tasks. The Scheduler is more broad and does CRUD on tasks across pets.

Regenerated the mermaid diagram and regenerated the structure for the pawpal_system.py file.

For each class, specific changes:

**Task**

Attributes
-name
+description: str
-end_time
-start_time
+scheduled_time: time
+frequency: str (once, weekly, daily, etc)
+completed: bool
+Optional(duration): timedelta

Methods
+mark_complete()
+reschedule(new_time)

**Pet**
Has tasks

Attributes
+species: str
+age: int
+tasks: list<Task>

Methods
+add_task(task) -> None
+remove_task(task) -> None
+get_tasks() -> list

**Owner**
Has pets

Methods
+get_all_tasks() -> list of tasks from owner's pets

**Scheduler**
Manages owners

Attributes
+owners: list<Owner>

Methods
+retrieve_tasks(date) -> list of all tasks for date across owners/pets
+organize_tasks(Optional(date)) -> sorted list of tasks chronologically across date or today's date
+detect_conflicts() -> list of all conflicts for tasks across all owners/pets
+assign_task_to_pet(task, pet) -> None

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
