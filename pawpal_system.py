"""PawPal+ logic layer: Task, Pet, Owner, and the cross-pet Scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from enum import StrEnum


class Frequency(StrEnum):
    """Supported task repeat frequencies."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


class Priority(StrEnum):
    """Supported task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Days between occurrences for each recurring frequency.
RECURRENCE_DAYS = {Frequency.DAILY: 1, Frequency.WEEKLY: 7}


@dataclass
class Task:
    """One care activity for a pet (what, when, how long, how often)."""

    description: str
    time: time | str  # datetime.time (or string "HH:MM" converted in __post_init__)
    date: date
    duration_minutes: int = 15
    frequency: Frequency | str = (
        Frequency.ONCE
    )  # converts to Frequency in __post_init__
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return the follow-up Task for a recurring task, else None."""
        days = RECURRENCE_DAYS.get(self.frequency)
        if days is None:
            return None
        return replace(self, date=self.date + timedelta(days=days), completed=False)


@dataclass
class Pet:
    """A pet with identifying info and its list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def list_tasks(self) -> list[Task]:
        """Return all of this pet's tasks."""
        return list(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return this pet's not-yet-completed tasks."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """A pet owner managing multiple pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name, or None if absent."""
        return next((pet for pet in self.pets if pet.name == name), None)


class Scheduler:
    """The brain: retrieves and organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all pets."""
        return [(pet, task) for pet in self.owner.pets for task in pet.tasks]

    def tasks_for_today(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs due today."""
        today = date.today()
        return [(pet, task) for pet, task in self.all_tasks() if task.date == today]

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Return all pairs sorted chronologically by task time."""
        return sorted(self.all_tasks(), key=lambda pair: pair[1].time)

    def filter_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
        """Return pairs whose task completion status matches."""
        return [
            (pet, task) for pet, task in self.all_tasks() if task.completed == completed
        ]

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Return pairs belonging to the named pet."""
        return [(pet, task) for pet, task in self.all_tasks() if pet.name == pet_name]

    def detect_conflicts(self) -> list[str]:
        """Return human-readable warnings for same-time task collisions."""
        ...

    def complete_task(self, task: Task) -> Task | None:
        """Complete a task; if recurring, add and return its next occurrence."""
        ...
