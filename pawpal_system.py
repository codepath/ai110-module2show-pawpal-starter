"""Core implementation for the PawPal+ system, based on diagrams/uml_draft.mmd.

- Task: a single activity (description, time, frequency, completion status).
- Pet: pet details plus the list of tasks that belong to it.
- Owner: manages multiple pets and exposes all of their tasks together.
- Scheduler: the "brain" -- retrieves, organizes, and manages tasks across pets.
"""

from dataclasses import field


class Task:
    def __init__(
        self,
        description: str | None = None,
        time: str | None = None,
        frequency: str | None = None,
        completed: bool = False,
        info: dict | None = None,
        duration: int | None = None,
        priority: str | None = None,
    ):
        """Initialize a task with the provided details and status."""
        if info is not None or duration is not None or priority is not None:
            self.info = info if info is not None else {}
            self.description = self.info.get("title", self.info.get("description", description or ""))
            self.time = self.info.get("time", time or "")
            self.frequency = self.info.get("frequency", "once")
            self.completed = completed
            self.duration = duration if duration is not None else 0
            self.priority = priority.lower() if isinstance(priority, str) else "medium"
        else:
            self.description = description or ""
            self.time = time or ""
            self.frequency = frequency or "once"
            self.completed = completed
            self.info = {"title": self.description, "time": self.time, "frequency": self.frequency}
            self.duration = 0
            self.priority = "medium"

    def mark_complete(self):
        """Mark the task as completed."""
        self.completed = True

    def mark_incomplete(self):
        """Mark the task as incomplete."""
        self.completed = False

    def toggle_complete(self):
        """Toggle the completion state of the task."""
        self.completed = not self.completed

    def __str__(self):
        """Return a readable summary of the task."""
        status = "done" if self.completed else "pending"
        return f"{self.description} at {self.time} ({self.frequency}) - {status}"


class Pet:
    def __init__(self, name: str, weight: float, color: str, breed: str, tasks: list[Task] | None = None):
        """Initialize a pet with its core details and optional tasks."""
        self.name = name
        self.weight = weight
        self.color = color
        self.breed = breed
        self.tasks = tasks if tasks is not None else []

    def add_task(self, task: Task):
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from the pet's task list."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self):
        """Return the pet's list of tasks."""
        return self.tasks

    def get_pending_tasks(self):
        """Return the pet's incomplete tasks."""
        return [task for task in self.tasks if not task.completed]

    def snack_time(self):
        """Return the appropriate snack size for the pet."""
        if self.weight >= 7:
            return "Large snack"
        return "Small snack"

    def accommodations(self):
        """Return the housing needs for the pet."""
        if self.breed.lower() in {"golden retriever", "labrador", "german shepherd"}:
            return "Needs extra space and exercise"
        return "Standard home setup"

    def get_daily_needs(self):
        """Return the pet's daily care summary."""
        return {
            "name": self.name,
            "snack_time": self.snack_time(),
            "accommodations": self.accommodations(),
        }


class Owner:
    def __init__(self, info: dict, pets: list[Pet] | None = None, tasks: list[Task] | None = None):
        """Initialize an owner with profile information and optional pets and tasks."""
        self.info = info
        self.pets = pets if pets is not None else []
        self.tasks = tasks if tasks is not None else []

    def add_pet(self, pet: Pet):
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def add_pet_info(self, pet: Pet):
        """Add a pet to the owner's pet list using the same behavior as add_pet."""
        self.add_pet(pet)

    def remove_pet(self, pet: Pet):
        """Remove a pet from the owner's pet list."""
        if pet in self.pets:
            self.pets.remove(pet)

    def add_task(self, task: Task):
        """Add a task to the owner's standalone task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from the owner's standalone task list."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_all_tasks(self):
        """Return all tasks owned by the owner and their pets."""
        all_tasks = list(self.tasks)
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def update_preferences(self, preferences):
        """Update the owner's stored preferences."""
        self.info["preferences"] = preferences


class Scheduler:
    def __init__(self, owner: Owner | None = None, constraints: dict = None, priorities: dict = None):
        """Initialize a scheduler with an optional owner and planning preferences."""
        self.owner = owner
        self.constraints = constraints if constraints is not None else {}
        self.priorities = priorities if priorities is not None else {"daily": 3, "weekly": 2, "once": 1}
        self.tasks = []

    def get_all_tasks(self):
        """Return all tasks available to the scheduler."""
        if self.owner is None:
            return list(self.tasks)
        return self.owner.get_all_tasks()

    def get_tasks_by_pet(self, pet: Pet):
        """Return the tasks associated with a specific pet."""
        return pet.get_tasks()

    def get_pending_tasks(self):
        """Return all unfinished tasks from the scheduler's task list."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def sort_tasks(self, tasks: list[Task] | None = None):
        """Sort tasks by frequency and priority for planning."""
        task_list = tasks if tasks is not None else self.get_pending_tasks()
        return sorted(
            task_list,
            key=lambda task: (
                self.priorities.get(getattr(task, "frequency", "").lower(), 0),
                self.priority_rank(getattr(task, "priority", "medium")),
            ),
            reverse=True,
        )

    def daily_plan(self, constraint: dict | None = None):
        """Create a daily plan limited by the provided constraints."""
        constraint = constraint if constraint is not None else self.constraints
        plan = self.sort_tasks()
        max_tasks = constraint.get("max_tasks")
        if max_tasks is not None:
            plan = plan[:max_tasks]
        return plan

    def check_conflicts(self):
        """Find tasks that share the same time slot."""
        seen = {}
        conflicts = []
        for task in self.get_all_tasks():
            if task.time in seen:
                conflicts.append((seen[task.time], task))
            else:
                seen[task.time] = task
        return conflicts

    def explain_plan(self):
        """Return a human-readable summary of the current plan."""
        plan = self.daily_plan()
        if not plan:
            return "No pending tasks to schedule."
        lines = [f"- {task.description} ({task.frequency}) at {task.time}" for task in plan]
        return "Today's plan:\n" + "\n".join(lines)

    def priority_rank(self, priority: str):
        """Convert a priority label into a sortable rank."""
        rank_map = {"high": 3, "medium": 2, "low": 1}
        return rank_map.get(priority.lower(), 0)
