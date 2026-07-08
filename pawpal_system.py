"""Core implementation for the PawPal+ system, based on diagrams/uml_draft.mmd.

- Task: a single activity (description, time, frequency, completion status).
- Pet: pet details plus the list of tasks that belong to it.
- Owner: manages multiple pets and exposes all of their tasks together.
- Scheduler: the "brain" -- retrieves, organizes, and manages tasks across pets.
"""

from datetime import date, timedelta

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
        due_date: date | None = None,
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
            self.due_date = due_date if due_date is not None else self.info.get("due_date")
        else:
            self.description = description or ""
            self.time = time or ""
            self.frequency = frequency or "once"
            self.completed = completed
            self.info = {"title": self.description, "time": self.time, "frequency": self.frequency}
            self.duration = 0
            self.priority = "medium"
            self.due_date = due_date

        if self.due_date is None:
            self.due_date = date.today()

        self.info.setdefault("due_date", self.due_date)

    def _next_due_date(self):
        """Return the next due date for recurring tasks."""
        if self.frequency is None:
            return None

        frequency = self.frequency.lower()
        if frequency == "daily":
            return self.due_date + timedelta(days=1)
        if frequency == "weekly":
            return self.due_date + timedelta(days=7)
        return None

    def create_next_occurrence(self):
        """Create the next task instance for recurring schedules."""
        next_due_date = self._next_due_date()
        if next_due_date is None:
            return None

        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            completed=False,
            info={**self.info, "title": self.description, "time": self.time, "frequency": self.frequency},
            duration=self.duration,
            priority=self.priority,
            due_date=next_due_date,
        )

    def mark_complete(self):
        """Mark the task as completed and return the next occurrence if recurring."""
        self.completed = True
        return self.create_next_occurrence()

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
        """Return all tasks available to the scheduler.

        If an owner is attached, return the combined tasks from the owner and all pets.
        Otherwise return the scheduler's own standalone task list.
        """
        if self.owner is None:
            return list(self.tasks)
        return self.owner.get_all_tasks()

    def get_tasks_by_pet(self, pet: Pet):
        """Return the tasks associated with a specific pet.

        This helper exposes the pet's own task list for per-pet filtering or display.
        """
        return pet.get_tasks()

    def get_pending_tasks(self):
        """Return all unfinished tasks currently available to the scheduler.

        Pending tasks are those whose completed flag is False.
        """
        return [task for task in self.get_all_tasks() if not task.completed]

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None):
        """Return tasks matching the given completion status and/or pet name.

        If pet_name is provided, only tasks for that pet are returned.
        If completed is provided, tasks are filtered by their completion state.
        """
        if pet_name is not None:
            if self.owner is None:
                tasks = []
            else:
                tasks = [
                    task
                    for pet in self.owner.pets
                    if pet.name == pet_name
                    for task in pet.get_tasks()
                ]
        else:
            tasks = self.get_all_tasks()

        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]

        return tasks

    def sort_tasks(self, tasks: list[Task] | None = None):
        """Sort tasks by frequency and priority for planning.

        Higher-frequency tasks and higher-priority tasks are placed first to form a
        more urgent daily plan.
        """
        task_list = tasks if tasks is not None else self.get_pending_tasks()
        return sorted(
            task_list,
            key=lambda task: (
                self.priorities.get(getattr(task, "frequency", "").lower(), 0),
                self.priority_rank(getattr(task, "priority", "medium")),
            ),
            reverse=True,
        )

    def sort_by_time(self, tasks: list[Task] | None = None):
        """Sort tasks by their time attribute in ascending HH:MM order.

        Tasks with invalid or missing times are pushed to the end of the result.
        """
        task_list = tasks if tasks is not None else self.get_pending_tasks()
        return sorted(
            task_list,
            key=lambda task: self._time_sort_key(getattr(task, "time", "")),
        )

    def _time_sort_key(self, time_value: str):
        """Convert an HH:MM time string into a comparable tuple.

        Returns (hour, minute) or a sentinel value for missing/invalid times.
        """
        normalized_time = self._normalize_time(time_value)
        if normalized_time is None:
            return (24, 60)
        return normalized_time

    def daily_plan(self, constraint: dict | None = None):
        """Create a daily plan limited by the provided constraints.

        The plan is generated from pending tasks ordered by frequency and priority.
        If a max_tasks constraint is present, the returned list is truncated.
        """
        constraint = constraint if constraint is not None else self.constraints
        plan = self.sort_tasks()
        max_tasks = constraint.get("max_tasks")
        if max_tasks is not None:
            plan = plan[:max_tasks]
        return plan

    def _normalize_time(self, time_value: str):
        """Convert an HH:MM time string into a comparable tuple.

        Supports string-formatted times and numeric hour values. Raises on invalid formats.
        """
        if not time_value:
            return None

        if isinstance(time_value, (int, float)):
            return (int(time_value), 0)

        if not isinstance(time_value, str):
            raise ValueError("Task time must be a string")

        parts = time_value.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid time format: {time_value}")

        hour_text, minute_text = parts
        hour = int(hour_text)
        minute = int(minute_text)
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Invalid time values: {time_value}")

        return (hour, minute)

    def check_conflicts(self):
        """Find tasks sharing the same time slot across pets or within the same pet.

        Tasks are grouped by normalized time and any pair sharing the same slot is
        returned as a conflict tuple.
        """
        tasks_by_time = {}
        for task in self.get_all_tasks():
            try:
                normalized_time = self._normalize_time(getattr(task, "time", ""))
            except (TypeError, ValueError):
                continue

            if normalized_time is None:
                continue

            tasks_by_time.setdefault(normalized_time, []).append(task)

        conflicts = []
        for task_group in tasks_by_time.values():
            if len(task_group) < 2:
                continue

            for index, task in enumerate(task_group):
                for other_task in task_group[index + 1 :]:
                    conflicts.append((task, other_task))

        return conflicts

    def lightweight_conflict_check(self):
        """Return a warning message instead of raising when conflict checks fail.

        Validates task time formats first, then runs conflict detection. If any
        invalid times are found, a warning is returned rather than raising an exception.
        """
        try:
            tasks = self.get_all_tasks()
            for task in tasks:
                self._normalize_time(getattr(task, "time", ""))
        except (TypeError, ValueError):
            return "Warning: conflict check could not validate the schedule because one or more task times are invalid."

        try:
            conflicts = self.check_conflicts()
        except (TypeError, ValueError):
            return "Warning: conflict check could not validate the schedule because one or more task times are invalid."

        if conflicts:
            return f"Warning: possible scheduling conflict detected for {len(conflicts)} task pairing(s)."
        return "No scheduling conflicts detected."

    def explain_plan(self):
        """Return a human-readable summary of the current plan.

        Generates a text summary of the daily plan produced by the scheduler.
        """
        plan = self.daily_plan()
        if not plan:
            return "No pending tasks to schedule."
        lines = [f"- {task.description} ({task.frequency}) at {task.time}" for task in plan]
        return "Today's plan:\n" + "\n".join(lines)

    def priority_rank(self, priority: str):
        """Convert a priority label into a sortable rank.

        Higher numbers represent more urgent priority levels for task ordering.
        """
        rank_map = {"high": 3, "medium": 2, "low": 1}
        return rank_map.get(priority.lower(), 0)
