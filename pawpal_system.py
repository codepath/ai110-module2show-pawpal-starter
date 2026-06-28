"""PawPal+ system classes.

Skeleton generated from diagrams/uml.mmd: class names, attributes, and empty
method stubs. No logic yet — fill in the method bodies as you implement behavior.
"""

from __future__ import annotations

from datetime import date


class PetTask:
    """A single pet care task (walk, feeding, meds, grooming, etc.)."""

    # Single source of truth for priority ordering (higher = more urgent).
    PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3}

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        category: str = "general",
        recurring: bool = False,
    ) -> None:
        """Create a task, validating its priority and duration."""
        priority = priority.lower()
        if priority not in self.PRIORITY_WEIGHTS:
            raise ValueError(
                f"priority must be one of {list(self.PRIORITY_WEIGHTS)}, got {priority!r}"
            )
        if duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be positive, got {duration_minutes}")

        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low" | "medium" | "high"
        self.category = category
        self.recurring = recurring
        self.status = "pending"  # "pending" | "completed"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def priority_weight(self) -> int:
        """Return a sortable number for this task's priority (higher = more urgent)."""
        return self.PRIORITY_WEIGHTS[self.priority]

    def summary(self) -> str:
        """Return a short, human-readable description of the task."""
        recurring_note = ", recurring" if self.recurring else ""
        return (
            f"{self.title} ({self.category}) — {self.duration_minutes} min, "
            f"{self.priority} priority{recurring_note}"
        )


class Constraints:
    """The limits and preferences the scheduler must respect."""

    def __init__(
        self,
        available_minutes: int,
        preferred_start: str = "08:00",
        preferred_order: list[str] | None = None,
        skip_low_priority: bool = False,
    ) -> None:
        """Store the day's time budget and scheduling preferences."""
        self.available_minutes = available_minutes
        self.preferred_start = preferred_start
        self.preferred_order = preferred_order or []
        self.skip_low_priority = skip_low_priority

    def allows(self, task: PetTask, used_minutes: int) -> bool:
        """Return True if `task` may still be scheduled after `used_minutes` are spent."""
        if self.skip_low_priority and task.priority == "low":
            return False
        return task.duration_minutes <= self.remaining_minutes(used_minutes)

    def remaining_minutes(self, used_minutes: int) -> int:
        """Return how many minutes of the day's budget remain."""
        return max(0, self.available_minutes - used_minutes)


class DailyPlan:
    """A day's schedule plus the reasoning behind it.

    Also knows how to build itself: `DailyPlan.build(...)` sorts and filters tasks
    against the constraints and lays them out in sequential, non-overlapping slots.
    Each scheduled item is a (start_time, end_time, PetTask) tuple.
    """

    def __init__(self, day: date) -> None:
        """Create an empty plan for the given day."""
        self.day = day
        self.scheduled: list[tuple[str, str, PetTask]] = []
        self.skipped: list[PetTask] = []
        self.reasoning: str = ""

    @classmethod
    def build(cls, tasks: list[PetTask], constraints: Constraints, day: date) -> DailyPlan:
        """Build a plan: order tasks by priority/preference, keep those that fit."""
        plan = cls(day)
        clock = cls._to_minutes(constraints.preferred_start)
        used = 0
        for task in cls._sort(tasks, constraints):
            if not constraints.allows(task, used):
                continue
            start = cls._to_clock(clock)
            clock += task.duration_minutes
            used += task.duration_minutes
            plan.scheduled.append((start, cls._to_clock(clock), task))

        scheduled_ids = {id(task) for _, _, task in plan.scheduled}
        plan.skipped = [task for task in tasks if id(task) not in scheduled_ids]
        plan.reasoning = plan._build_reasoning(len(tasks), constraints)
        return plan

    def add(self, task: PetTask, start_time: str) -> None:
        """Append a task at `start_time`, computing its end from the task duration."""
        end_time = self._to_clock(self._to_minutes(start_time) + task.duration_minutes)
        self.scheduled.append((start_time, end_time, task))

    def total_minutes(self) -> int:
        """Return the total scheduled time across all entries."""
        return sum(task.duration_minutes for _, _, task in self.scheduled)

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        return self.reasoning

    # --- internal helpers -------------------------------------------------

    @staticmethod
    def _sort(tasks: list[PetTask], constraints: Constraints) -> list[PetTask]:
        """Order by priority (highest first), owner preference, then shortest."""
        order = constraints.preferred_order

        def preference_rank(task: PetTask) -> int:
            for index, key in enumerate(order):
                if key in (task.category, task.title):
                    return index
            return len(order)

        return sorted(
            tasks,
            key=lambda task: (
                -task.priority_weight(),
                preference_rank(task),
                task.duration_minutes,
            ),
        )

    def _build_reasoning(self, total: int, constraints: Constraints) -> str:
        """Compose the human-readable summary of what was scheduled vs. skipped."""
        note = " Low-priority tasks were skipped." if constraints.skip_low_priority else ""
        return (
            f"Scheduled {len(self.scheduled)} of {total} task(s) within "
            f"{constraints.available_minutes} min, ordered by priority then owner "
            f"preference.{note}"
        )

    @staticmethod
    def _to_minutes(clock: str) -> int:
        """Convert an "HH:MM" clock string to minutes since midnight."""
        hours, minutes = clock.split(":")
        return int(hours) * 60 + int(minutes)

    @staticmethod
    def _to_clock(total_minutes: int) -> str:
        """Convert minutes since midnight to an "HH:MM" clock string."""
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


class Pet:
    """A pet owned by an Owner, with its own list of care tasks."""

    def __init__(self, name: str, species: str) -> None:
        """Create a pet with the given name and species and no tasks yet."""
        self.name = name
        self.species = species
        self.tasks: list[PetTask] = []

    def add_task(self, task: PetTask) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove every task matching `title` from this pet."""
        self.tasks = [task for task in self.tasks if task.title != title]


class Owner:
    """A pet owner who manages multiple pets and builds their care plans."""

    def __init__(self, name: str, constraints: Constraints | None = None) -> None:
        """Create an owner with no pets and optional scheduling constraints."""
        self.name = name
        self.pets: list[Pet] = []
        self.constraints = constraints

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner, ignoring duplicates by name."""
        if self.get_pet(pet.name) is None:
            self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a pet (and its tasks) by name."""
        self.pets = [pet for pet in self.pets if pet.name != name]

    def get_pet(self, name: str) -> Pet | None:
        """Return the pet with the given name, or None if not found."""
        return next((pet for pet in self.pets if pet.name == name), None)

    def all_tasks(self) -> list[PetTask]:
        """Return every task across all of this owner's pets, flattened."""
        return [task for pet in self.pets for task in pet.tasks]

    def tasks_for(self, pet_name: str) -> list[PetTask]:
        """Return the tasks for one named pet (empty list if the pet is unknown)."""
        pet = self.get_pet(pet_name)
        return list(pet.tasks) if pet is not None else []

    def build_plan(self, day: date | None = None) -> DailyPlan:
        """Build a DailyPlan from all pets' tasks under this owner's constraints."""
        if self.constraints is None:
            raise ValueError("Owner has no constraints set; cannot build a plan.")
        return DailyPlan.build(self.all_tasks(), self.constraints, day or date.today())
