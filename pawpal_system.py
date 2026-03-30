"""PawPal+ system logic: Owner, Pet, Task, and Scheduler classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str  # "HH:MM" (24-hour)
    duration_minutes: int = 30
    priority: str = "medium"  # "low", "medium", or "high"
    frequency: str = "once"   # "once", "daily", or "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        return (
            f"[{status}] {self.time} | {self.description} "
            f"({self.duration_minutes}min, {self.priority}, {self.frequency})"
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Stores a pet's details and its list of tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def __str__(self) -> str:
        return f"{self.name} ({self.species})"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Manages one or more pets and provides access to all their tasks."""

    def __init__(self, name: str) -> None:
        """Initialize an Owner with a name and empty pet list."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's collection."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs across every owned pet."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet, task))
        return result

    def __str__(self) -> str:
        return f"Owner: {self.name} ({len(self.pets)} pet(s))"


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


class Scheduler:
    """The brain that retrieves, organizes, and manages tasks across pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with an Owner instance."""
        self.owner = owner

    # ---- retrieval ----

    def get_todays_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all incomplete tasks due today."""
        today = date.today()
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.due_date == today and not task.completed
        ]

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair regardless of date or status."""
        return self.owner.get_all_tasks()

    # ---- sorting ----

    def sort_by_time(self, tasks: list[tuple[Pet, Task]] | None = None) -> list[tuple[Pet, Task]]:
        """Sort tasks chronologically by their HH:MM time string."""
        if tasks is None:
            tasks = self.get_todays_tasks()
        return sorted(tasks, key=lambda x: x[1].time)

    def sort_by_priority(self, tasks: list[tuple[Pet, Task]] | None = None) -> list[tuple[Pet, Task]]:
        """Sort tasks by priority (high → medium → low), then by time."""
        if tasks is None:
            tasks = self.get_todays_tasks()
        return sorted(
            tasks,
            key=lambda x: (_PRIORITY_RANK.get(x[1].priority, 3), x[1].time),
        )

    # ---- filtering ----

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Return all tasks belonging to a specific pet."""
        return [
            (p, t)
            for p, t in self.owner.get_all_tasks()
            if p.name.lower() == pet_name.lower()
        ]

    def filter_by_status(self, completed: bool = False) -> list[tuple[Pet, Task]]:
        """Return tasks filtered by their completion status."""
        return [
            (p, t)
            for p, t in self.owner.get_all_tasks()
            if t.completed == completed
        ]

    # ---- recurrence ----

    def mark_task_complete(self, pet: Pet, task: Task) -> Task | None:
        """
        Mark a task complete and, if it recurs, create and attach the next occurrence.

        Returns the newly created Task for daily/weekly tasks, or None for one-time tasks.
        """
        task.mark_complete()

        if task.frequency == "daily":
            next_due = task.due_date + timedelta(days=1)
        elif task.frequency == "weekly":
            next_due = task.due_date + timedelta(weeks=1)
        else:
            return None

        new_task = Task(
            description=task.description,
            time=task.time,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            frequency=task.frequency,
            due_date=next_due,
        )
        pet.add_task(new_task)
        return new_task

    # ---- conflict detection ----

    def detect_conflicts(self) -> list[str]:
        """
        Detect scheduling conflicts (two tasks for the same pet at the same time/date).

        Returns a list of warning strings; empty list means no conflicts.
        """
        warnings: list[str] = []
        seen: dict[tuple, str] = {}

        for pet, task in self.owner.get_all_tasks():
            key = (pet.name, task.due_date, task.time)
            if key in seen:
                warnings.append(
                    f"⚠ Conflict: {pet.name} has two tasks at {task.time} "
                    f"on {task.due_date}: '{seen[key]}' and '{task.description}'"
                )
            else:
                seen[key] = task.description

        return warnings

    # ---- next available slot ----

    def get_next_available_slot(
        self, pet_name: str, target_date: date | None = None
    ) -> str:
        """
        Find the next free 30-minute time slot for a pet on a given date.

        Searches from 07:00 to 21:30 in 30-minute increments.
        Falls back to '22:00' if the whole day is blocked.
        """
        if target_date is None:
            target_date = date.today()

        occupied = {
            task.time
            for pet, task in self.owner.get_all_tasks()
            if pet.name.lower() == pet_name.lower() and task.due_date == target_date
        }

        for hour in range(7, 22):
            for minute in (0, 30):
                slot = f"{hour:02d}:{minute:02d}"
                if slot not in occupied:
                    return slot

        return "22:00"
