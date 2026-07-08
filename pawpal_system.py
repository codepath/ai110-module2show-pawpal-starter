"""PawPal+ core domain model.

Classes:
    Task      - a single care activity (description, time, frequency, status).
    Pet       - pet details plus its list of tasks.
    Owner     - manages multiple pets and access to all their tasks.
    Scheduler - the brain that retrieves, organizes, and manages tasks across pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time


@dataclass
class Task:
    """A single care activity: what to do, when, how often, and whether it's done."""

    name: str
    time: time
    frequency: str = "daily"
    done: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.done = True

    def get_status(self) -> bool:
        """Return whether this task is complete."""
        return self.done


@dataclass
class Pet:
    """Stores pet details and its list of care tasks."""

    name: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def set_name(self, name: str) -> None:
        """Rename the pet."""
        self.name = name

    def add_task(self, task: Task) -> None:
        """Add a task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet, ordered by time."""
        return sorted(self.tasks, key=lambda task: task.time)

    def get_incomplete_tasks(self) -> list[Task]:
        """Return the tasks that are not yet done."""
        return [task for task in self.get_tasks() if not task.done]


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        return self.pets

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


@dataclass
class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across an owner's pets."""

    owner: Owner

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all pets, ordered by time."""
        pairs = [(pet, task) for pet in self.owner.pets for task in pet.get_tasks()]
        return sorted(pairs, key=lambda pair: pair[1].time)

    def pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return the not-yet-done (pet, task) pairs, ordered by time."""
        return [(pet, task) for pet, task in self.all_tasks() if not task.done]

    def tasks_by_pet(self) -> dict[str, list[Task]]:
        """Group each pet's tasks (ordered by time) under the pet's name."""
        return {pet.name: pet.get_tasks() for pet in self.owner.pets}

    def build_daily_plan(self) -> list[tuple[Pet, Task]]:
        """Build today's plan: all pending tasks across pets, ordered by time."""
        return self.pending_tasks()

    def complete_task(self, task: Task) -> None:
        """Mark a task complete."""
        task.mark_complete()
