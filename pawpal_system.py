"""PawPal+ logic layer: Task, Pet, Owner, and the cross-pet Scheduler.

Skeletons translated from diagrams/uml.mmd; implementations land in the
feat-task-pet-owner and feat-scheduler-core layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


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
        ...

    def next_occurrence(self) -> Task | None:
        """Return the follow-up Task for a recurring task, else None."""
        ...


@dataclass
class Pet:
    """A pet with identifying info and its list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        ...

    def list_tasks(self) -> list[Task]:
        """Return all of this pet's tasks."""
        ...

    def pending_tasks(self) -> list[Task]:
        """Return this pet's not-yet-completed tasks."""
        ...


@dataclass
class Owner:
    """A pet owner managing multiple pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        ...

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name, or None if absent."""
        ...


class Scheduler:
    """The brain: retrieves and organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all pets."""
        ...

    def tasks_for_today(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs due today."""
        ...

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Return all pairs sorted chronologically by task time."""
        ...

    def filter_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
        """Return pairs whose task completion status matches."""
        ...

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Return pairs belonging to the named pet."""
        ...

    def detect_conflicts(self) -> list[str]:
        """Return human-readable warnings for same-time task collisions."""
        ...

    def complete_task(self, task: Task) -> Task | None:
        """Complete a task; if recurring, add and return its next occurrence."""
        ...
