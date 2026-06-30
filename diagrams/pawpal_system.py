"""PawPal+ system skeleton.

Class stubs generated from diagrams/uml.mmd. No scheduling logic yet —
attributes and empty method bodies only. Fill these in incrementally.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single daily care item for a pet."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    done: bool = False

    def priority_rank(self) -> int:
        """Return a sortable integer for this task's priority (higher = more urgent)."""
        ...


@dataclass
class Pet:
    """An individual animal and the tasks that belong to it."""

    name: str
    species: str = "other"  # "dog" | "cat" | "other"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        ...

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet."""
        ...


@dataclass
class Owner:
    """The person who manages one or more pets."""

    name: str
    email: str = ""
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        ...

    def all_tasks(self) -> list[Task]:
        """Flatten and return every task across all of this owner's pets."""
        ...


@dataclass
class ScheduledItem:
    """A task placed into the daily plan, with its time slot and reasoning."""

    task: Task
    start_time: str  # e.g. "08:00"
    reason: str = ""


class Scheduler:
    """Builds an ordered daily plan from an owner's tasks under given constraints."""

    def build_plan(self, owner: Owner, available_minutes: int) -> list[ScheduledItem]:
        """Select, order, and time-slot tasks that fit within available_minutes."""
        ...

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by scheduling priority (e.g. priority, then duration)."""
        ...

    def explain(self, item: ScheduledItem) -> str:
        """Return a human-readable reason for why this item was scheduled as it was."""
        ...