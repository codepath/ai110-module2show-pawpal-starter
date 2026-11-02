"""PawPal+ core classes (skeleton). Matches diagrams/uml_draft.mmd."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple


@dataclass
class Task:
    """Represents a single care activity."""

    description: str
    due_time: datetime
    duration_mins: int
    frequency: str = "Once"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass


@dataclass
class Pet:
    """Represents a pet profile."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass


@dataclass
class Owner:
    """Represents a pet owner."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass


@dataclass
class Scheduler:
    """Manages scheduling logic, conflict detection, and task retrieval."""

    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with the scheduler."""
        pass

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        """Return a list of (pet_name, task) tuples for every pet."""
        pass

    def get_upcoming_tasks(self) -> List[Tuple[str, Task]]:
        """Return incomplete tasks sorted by due time."""
        pass

    def check_conflicts(self, new_task: Task) -> bool:
        """Return True if new_task overlaps any existing task for any pet."""
        pass

    def generate_recurring_tasks(self) -> None:
        """Create the next instance of Daily/Weekly tasks."""
        pass
