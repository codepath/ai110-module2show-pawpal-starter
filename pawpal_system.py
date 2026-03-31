"""Core system classes for the PawPal+ pet care app.

This module provides a starter skeleton based on the UML design:
Owner, Pet, Task, Plan, and Scheduler.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """Represents a single pet-care activity."""

    title: str
    description: str = ""
    time: str = ""
    frequency: str = "once"
    priority: str = "medium"
    duration_minutes: int = 30
    category: str = "general"
    completed: bool = False
    last_completed_date: str = ""
    due_date: str = field(default_factory=lambda: date.today().isoformat())
    spawned_next_occurrence: bool = False

    def mark_complete(self, completed_on: Optional[str] = None) -> None:
        """Mark this task as completed and store when it was done."""
        self.completed = True
        self.last_completed_date = completed_on or date.today().isoformat()

    def create_next_occurrence(self, reference_date: Optional[date] = None) -> Optional["Task"]:
        """Create the next daily or weekly task instance.

        This keeps the completed task in the history while generating a fresh,
        incomplete copy with a new `due_date` based on `timedelta`.
        """
        if self.frequency not in {"daily", "weekly"}:
            return None

        if reference_date is None:
            reference_date = date.today()

        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        return Task(
            title=self.title,
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            priority=self.priority,
            duration_minutes=self.duration_minutes,
            category=self.category,
            due_date=(reference_date + delta).isoformat(),
        )

    def is_due_today(self, reference_date: Optional[date] = None) -> bool:
        """Return `True` when the task should appear in the current plan.

        Future-dated tasks are filtered out, completed one-time tasks stay hidden,
        and recurring tasks only reappear when their next scheduled date is due.
        """
        if reference_date is None:
            reference_date = date.today()

        try:
            scheduled_date = date.fromisoformat(self.due_date) if self.due_date else reference_date
        except ValueError:
            scheduled_date = reference_date

        if scheduled_date > reference_date:
            return False

        if not self.completed:
            return True

        if self.spawned_next_occurrence or self.frequency == "once":
            return False

        if not self.last_completed_date:
            return True

        try:
            last_done = date.fromisoformat(self.last_completed_date)
        except ValueError:
            return True

        if self.frequency == "daily":
            return last_done < reference_date
        if self.frequency == "weekly":
            return (reference_date - last_done) >= timedelta(weeks=1)
        if self.frequency == "monthly":
            return (last_done.year, last_done.month) != (reference_date.year, reference_date.month)
        return True

    def get_task_info(self) -> dict:
        """Return this task's details as a dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "priority": self.priority,
            "duration_minutes": self.duration_minutes,
            "category": self.category,
            "completed": self.completed,
            "last_completed_date": self.last_completed_date,
            "due_date": self.due_date,
        }

    def getTask(self) -> str:
        """Return the task title."""
        return self.title

    def edit_task(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        time: Optional[str] = None,
        frequency: Optional[str] = None,
        priority: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        category: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> None:
        """Update any provided task fields."""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if time is not None:
            self.time = time
        if frequency is not None:
            self.frequency = frequency
        if priority is not None:
            self.priority = priority
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if category is not None:
            self.category = category
        if due_date is not None:
            self.due_date = due_date

    def editTask(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        due_time: Optional[str] = None,
        priority: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        category: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> None:
        """Update the task using UML-style field names."""
        self.edit_task(
            title=name,
            description=description,
            time=due_time,
            priority=priority,
            duration_minutes=duration_minutes,
            category=category,
            due_date=due_date,
        )


@dataclass
class Pet:
    """Stores pet details and a list of associated tasks."""

    pet_name: str
    pet_desc: str = ""
    pet_height: float = 0.0
    pet_weight: float = 0.0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove tasks matching the given title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def getPetDesc(self) -> str:
        """Return the pet description or species."""
        return self.pet_desc

    def getPetHeight(self) -> float:
        """Return the pet height."""
        return self.pet_height

    def getPetWeight(self) -> float:
        """Return the pet weight."""
        return self.pet_weight


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    owner_name: str
    constraints: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.pet_name != pet_name]

    def get_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def getOwnerName(self) -> str:
        """Return the owner's name."""
        return self.owner_name

    def getConstraints(self) -> list[str]:
        """Return the owner's constraints."""
        return self.constraints

    def getPriorities(self) -> list[str]:
        """Return the owner's priorities."""
        return self.priorities

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs across every pet."""
        return [(pet, task) for pet in self.pets for task in pet.get_tasks()]


@dataclass
class Plan:
    """Represents the generated daily schedule or care plan."""

    date: str = field(default_factory=lambda: date.today().isoformat())
    tasks: list[Task] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    def get_plan(self) -> list[Task]:
        """Return the tasks in this plan."""
        return self.tasks

    def getPlan(self) -> list[Task]:
        """Return the tasks in this plan using the UML-style name."""
        return self.get_plan()

    def edit_plan(
        self,
        *,
        tasks: Optional[list[Task]] = None,
        constraints: Optional[list[str]] = None,
        priorities: Optional[list[str]] = None,
        conflicts: Optional[list[str]] = None,
    ) -> None:
        """Update the plan with any provided values."""
        if tasks is not None:
            self.tasks = tasks
        if constraints is not None:
            self.constraints = constraints
        if priorities is not None:
            self.priorities = priorities
        if conflicts is not None:
            self.conflicts = conflicts

    def editPlan(
        self,
        tasks: Optional[list[Task]] = None,
        constraints: Optional[list[str]] = None,
        priorities: Optional[list[str]] = None,
        conflicts: Optional[list[str]] = None,
    ) -> None:
        """Update the plan using the UML-style method name."""
        self.edit_plan(tasks=tasks, constraints=constraints, priorities=priorities, conflicts=conflicts)


class Scheduler:
    """The brain that retrieves, organizes, and manages tasks across pets."""

    PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}
    HEALTH_CATEGORIES = {"meds", "medication", "feeding", "vet", "health"}

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks for a single pet."""
        return pet.get_tasks()

    def get_all_tasks(self, owner: Owner) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs across every pet owned by the owner."""
        return owner.get_all_tasks()

    def get_pending_tasks(self, owner: Owner) -> list[tuple[Pet, Task]]:
        """Return only tasks that are due in the current planning window."""
        return [(pet, task) for pet, task in owner.get_all_tasks() if task.is_due_today()]

    def mark_task_complete(self, owner: Owner, pet_name: str, task_title: str) -> bool:
        """Mark a task complete and queue its next recurring occurrence.

        Returns `True` when a matching open task is found. For `daily` and
        `weekly` tasks, a new incomplete task is created instead of mutating the
        original completed record.
        """
        for pet in owner.get_pets():
            if pet.pet_name == pet_name:
                for task in pet.get_tasks():
                    if task.title == task_title and not task.completed:
                        task.mark_complete()
                        next_task = task.create_next_occurrence()
                        if next_task is not None:
                            task.spawned_next_occurrence = True
                            pet.add_task(next_task)
                        return True
        return False

    def is_health_related(self, task: Task) -> bool:
        """Return True for health- or feeding-related tasks that should win tie-breakers."""
        searchable_text = f"{task.title} {task.description} {task.category}".lower()
        return task.category.lower() in self.HEALTH_CATEGORIES or any(
            keyword in searchable_text for keyword in ("med", "pill", "feed", "vet", "health")
        )

    def task_sort_key(self, task: Task) -> tuple:
        """Build the multi-step sort key for the daily schedule.

        Tasks are ordered by time first, then by priority, health importance,
        shorter duration, and finally title for stable human-readable output.
        """
        return (
            task.time or "99:99",
            -self.PRIORITY_ORDER.get(task.priority.lower(), 0),
            -int(self.is_health_related(task)),
            task.duration_minutes,
            task.title.lower(),
        )

    def detect_conflicts(self, scheduled_items: list[tuple[Pet, Task]] | list[Task], owner: Optional[Owner] = None) -> list[str]:
        """Detect exact same-time conflicts and return warning messages.

        The strategy is intentionally lightweight: it groups tasks by matching
        `time` values and reports overlaps as readable warnings instead of
        crashing the program.
        """
        entries: list[tuple[str, Task]] = []

        if scheduled_items and isinstance(scheduled_items[0], tuple):
            entries = [(pet.pet_name, task) for pet, task in scheduled_items]
        else:
            pet_lookup = {}
            if owner is not None:
                pet_lookup = {id(task): pet.pet_name for pet, task in owner.get_all_tasks()}
            entries = [(pet_lookup.get(id(task), "Unknown pet"), task) for task in scheduled_items]

        tasks_by_time: dict[str, list[tuple[str, Task]]] = {}
        for pet_name, task in entries:
            if task.time:
                tasks_by_time.setdefault(task.time, []).append((pet_name, task))

        conflicts: list[str] = []
        for time_slot, overlapping_items in sorted(tasks_by_time.items()):
            if len(overlapping_items) > 1:
                ordered_items = sorted(overlapping_items, key=lambda item: self.task_sort_key(item[1]))
                summary = ", ".join(f"{pet_name}: {task.title}" for pet_name, task in ordered_items)
                conflicts.append(f"Warning: overlapping tasks at {time_slot} -> {summary}")
        return conflicts

    def get_conflict_warnings(self, owner: Owner) -> list[str]:
        """Return user-friendly conflict warnings for the owner's due tasks."""
        return self.detect_conflicts(self.get_pending_tasks(owner))

    def organize_by_time(self, owner: Owner) -> list[tuple[Pet, Task]]:
        """Return all due tasks sorted by scheduled time and smart tie-breakers."""
        pending = self.get_pending_tasks(owner)
        return sorted(pending, key=lambda pt: self.task_sort_key(pt[1]))

    def generatePlan(self, owner: Owner, pet: Pet, tasks: list[Task]) -> Plan:
        """Create a daily plan from the owner, pet, and task list."""
        del pet
        due_tasks = [task for task in tasks if task.is_due_today()]
        sorted_tasks = sorted(due_tasks, key=self.task_sort_key)
        conflicts = self.detect_conflicts(sorted_tasks, owner=owner)
        return Plan(
            tasks=sorted_tasks,
            constraints=owner.getConstraints(),
            priorities=owner.getPriorities(),
            conflicts=conflicts,
        )
