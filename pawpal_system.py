"""PawPal+ logic layer: the core classes that model pets, tasks, and scheduling.

This module is UI-agnostic (no Streamlit here) so it can be driven from a CLI
demo (`main.py`), exercised by tests, or imported by the Streamlit app.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

VALID_FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """A single pet-care activity scheduled at a given HH:MM time."""

    description: str
    time: str  # 24-hour "HH:MM"
    frequency: str = "once"  # one of VALID_FREQUENCIES
    completed: bool = False
    due_date: str = field(default_factory=lambda: date.today().isoformat())

    def mark_complete(self) -> None:
        """Flip this task's status to completed."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy for the next day/week, or None if one-off."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        next_date = date.fromisoformat(self.due_date) + delta
        return Task(self.description, self.time, self.frequency, False, next_date.isoformat())


@dataclass
class Pet:
    """A pet that owns a list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return self.tasks

    def task_count(self) -> int:
        """How many tasks are assigned to this pet."""
        return len(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Flatten every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The 'brain': organizes tasks across ALL of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def _pet_task_pairs(self) -> list[tuple[Pet, Task]]:
        """Every (pet, task) pair across the owner's pets — keeps pet context for display."""
        return [(pet, task) for pet in self.owner.pets for task in pet.tasks]

    def sort_by_time(self, include_completed: bool = True) -> list[Task]:
        """Return all tasks across pets sorted chronologically by HH:MM time."""
        tasks = self.owner.get_all_tasks()
        if not include_completed:
            tasks = [t for t in tasks if not t.completed]
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Filter tasks by pet name and/or completion status (either may be omitted)."""
        results = []
        for pet, task in self._pet_task_pairs():
            if pet_name is not None and pet.name != pet_name:
                continue
            if completed is not None and task.completed != completed:
                continue
            results.append(task)
        return results

    def detect_conflicts(self) -> list[str]:
        """Return a warning string for each time slot holding more than one task."""
        by_time: dict[str, list[tuple[Pet, Task]]] = defaultdict(list)
        for pet, task in self._pet_task_pairs():
            by_time[task.time].append((pet, task))

        warnings = []
        for slot, items in sorted(by_time.items()):
            if len(items) > 1:
                names = ", ".join(f"{p.name}'s {t.description}" for p, t in items)
                warnings.append(f"Conflict at {slot}: {names}")
        return warnings

    def complete_task(self, task: Task) -> "Task | None":
        """Mark a task complete; if it recurs, add its next occurrence to the same pet."""
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            for pet in self.owner.pets:
                if task in pet.tasks:
                    pet.add_task(follow_up)
                    break
        return follow_up

    def todays_schedule(self, include_completed: bool = True) -> str:
        """Render a readable, time-sorted schedule across all pets, plus conflict warnings."""
        lines = [f"Today's Schedule for {self.owner.name}"]
        pairs = sorted(self._pet_task_pairs(), key=lambda pt: pt[1].time)
        if not include_completed:
            pairs = [(p, t) for p, t in pairs if not t.completed]

        if not pairs:
            lines.append("  (no tasks scheduled)")
        for pet, task in pairs:
            box = "[x]" if task.completed else "[ ]"
            lines.append(f"  {box} {task.time}  {task.description}  ({pet.name}) - {task.frequency}")

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("")
            lines.append("Warnings:")
            for warning in conflicts:
                lines.append(f"  ! {warning}")
        return "\n".join(lines)
