"""PawPal+ system classes.

Skeleton generated from diagrams/uml.mmd: class names, attributes, and empty
method stubs. No logic yet — fill in the method bodies as you implement behavior.
"""

from __future__ import annotations

from datetime import date


class PetTask:
    """A single pet care task (walk, feeding, meds, grooming, etc.)."""

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        category: str = "general",
        recurring: bool = False,
    ) -> None:
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low" | "medium" | "high"
        self.category = category
        self.recurring = recurring

    def priority_weight(self) -> int:
        pass

    def summary(self) -> str:
        pass


class Constraints:
    """The limits and preferences the scheduler must respect."""

    def __init__(
        self,
        available_minutes: int,
        preferred_start: str = "08:00",
        preferred_order: list[str] | None = None,
        skip_low_priority: bool = False,
    ) -> None:
        self.available_minutes = available_minutes
        self.preferred_start = preferred_start
        self.preferred_order = preferred_order or []
        self.skip_low_priority = skip_low_priority

    def allows(self, task: PetTask, used_minutes: int) -> bool:
        pass

    def remaining_minutes(self, used_minutes: int) -> int:
        pass


class DailyPlan:
    """The generated schedule for a single day, plus the reasoning behind it."""

    def __init__(self, day: date) -> None:
        self.day = day
        self.scheduled: list = []  # ordered (start_time, PetTask) entries
        self.skipped: list[PetTask] = []
        self.reasoning: str = ""

    def add(self, task: PetTask, start_time: str) -> None:
        pass

    def total_minutes(self) -> int:
        pass

    def explain(self) -> str:
        pass


class Owner:
    """A pet owner: basic info, their tasks and constraints, and plan building."""

    def __init__(
        self,
        name: str,
        pet_name: str,
        species: str,
        constraints: Constraints | None = None,
    ) -> None:
        self.name = name
        self.pet_name = pet_name
        self.species = species
        self.tasks: list[PetTask] = []
        self.constraints = constraints

    def add_task(self, task: PetTask) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def build_plan(self) -> DailyPlan:
        pass
