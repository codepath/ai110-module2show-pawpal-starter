"""PawPal+ core domain model.

Class skeleton generated from diagrams/uml.mmd. Method bodies are stubs to be
implemented as the scheduling logic is built out.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time


@dataclass
class Task:
    """A single care task for a pet, scheduled at a given time."""

    name: str
    time: time
    done: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        raise NotImplementedError

    def get_status(self) -> bool:
        """Return whether this task is complete."""
        raise NotImplementedError


@dataclass
class Schedule:
    """Holds and orders the tasks for a pet."""

    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule."""
        raise NotImplementedError

    def get_tasks_sorted(self) -> list[Task]:
        """Return the tasks ordered by their scheduled time."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet, with its own care schedule."""

    name: str
    breed: str
    schedule: Schedule = field(default_factory=Schedule)

    def set_name(self, name: str) -> None:
        """Rename the pet."""
        raise NotImplementedError

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's schedule."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's schedule."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        raise NotImplementedError

    def get_incomplete_tasks(self) -> list[Task]:
        """Return the tasks that are not yet done."""
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        raise NotImplementedError

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        raise NotImplementedError
