# PawPal+ Project Reflection

## 1. System Design
3 core actions users should be able to perform are:
    1. add pets
    2. add tasks
    3. edit tasks
    4. See all tasks for today

**a. Initial design**

- Briefly describe your initial UML design.
    I included owner repository, task, pet, and scheduler. Owner uses pet, pet uses task.
     
- What classes did you include, and what responsibilities did you assign to each?
    Owner: It has a repository and a class that describes itself. It is the top-level object (aggregate root), so saving it saves all system data including pets, tasks, and notes. It manages pets and acts as the single source of truth for the system.

    Pet:
    It represents an individual animal and acts as a container for tasks. A pet owns its tasks, meaning all care activities are scoped to a specific pet. It also stores notes and basic identifying information like name and species.

    Task:
    It represents a single care activity (e.g., feeding, walk, medication). It stores scheduling-related data like duration, priority, due time, and recurrence. It also holds notes and provides structure for what needs to be done for a pet.

    Scheduler:
    It is responsible for generating a daily plan from a list of tasks. It applies algorithmic logic such as sorting by priority, fitting tasks within available time, and detecting conflicts. It does not store data — it only processes it.

    OwnerRepository:
    It handles persistence of the system by saving and loading the Owner object to and from JSON. Since Owner is the aggregate root, this repository manages the entire application state in a single place.
![alt text](image.png)

**b. Design changes**

- Did your design change during implementation?
    I asked Claude to review pawpal_system.py and it mentioned that relationships between owner & scheudler is missing, also there isn't a method that filters but what's due today. Also there isn't a way to edit or remove tasks.
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    I decided to use local storage on your computer rather than trying to overcomplicate with a database.
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
