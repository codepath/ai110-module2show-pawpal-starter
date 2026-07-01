"""PawPal+ system classes.

Skeleton generated from diagrams/uml.mmd: class names, attributes, and empty
method stubs. No logic yet — fill in the method bodies as you implement behavior.
"""

from __future__ import annotations

from datetime import date, timedelta


class PetTask:
    """A single pet care task (walk, feeding, meds, grooming, etc.)."""

    # Single source of truth for priority ordering (higher = more urgent).
    PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3}

    # Recurring cadence -> how many days until the next occurrence.
    FREQUENCY_DAYS = {"daily": 1, "weekly": 7}

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        category: str = "general",
        recurring: bool = False,
        time: str | None = None,
        frequency: str | None = None,
        due_date: date | None = None,
    ) -> None:
        """Create a task, validating its priority, duration, and frequency."""
        priority = priority.lower()
        if priority not in self.PRIORITY_WEIGHTS:
            raise ValueError(
                f"priority must be one of {list(self.PRIORITY_WEIGHTS)}, got {priority!r}"
            )
        if duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be positive, got {duration_minutes}")
        if frequency is not None and frequency not in self.FREQUENCY_DAYS:
            raise ValueError(
                f"frequency must be one of {list(self.FREQUENCY_DAYS)} or None, got {frequency!r}"
            )

        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low" | "medium" | "high"
        self.category = category
        self.frequency = frequency  # None | "daily" | "weekly"
        self.recurring = recurring or frequency is not None
        self.time = time  # preferred start as "HH:MM", or None if unscheduled
        self.due_date = due_date  # date this instance is due, or None
        self.status = "pending"  # "pending" | "completed"

    def mark_complete(self) -> PetTask | None:
        """Mark this task completed and, if recurring, return its next pending
        occurrence; returns None (no duplicate) if already completed."""
        if self.status == "completed":
            return None
        self.status = "completed"
        return self._next_occurrence()

    def _next_occurrence(self) -> PetTask | None:
        """Build the next pending instance of a recurring task (or None)."""
        if self.frequency is None:
            return None
        base_date = self.due_date or date.today()
        next_due = base_date + timedelta(days=self.FREQUENCY_DAYS[self.frequency])
        return PetTask(
            self.title,
            self.duration_minutes,
            self.priority,
            category=self.category,
            recurring=self.recurring,
            time=self.time,
            frequency=self.frequency,
            due_date=next_due,
        )

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

    @staticmethod
    def sort_by_time(tasks: list[PetTask]) -> list[PetTask]:
        """Return tasks sorted by their "HH:MM" `time`, earliest first, with
        untimed tasks (time is None) placed last."""
        return sorted(tasks, key=lambda task: (task.time is None, task.time))

    @staticmethod
    def detect_conflicts(pets: list[Pet]) -> list[str]:
        """Return non-raising warning strings for tasks sharing the same "HH:MM"
        `time`, noting whether each clash is within one pet or across pets."""
        by_time: dict[str, list[tuple[str, str]]] = {}
        for pet in pets:
            for task in pet.tasks:
                if task.time is None:
                    continue
                by_time.setdefault(task.time, []).append((pet.name, task.title))

        warnings: list[str] = []
        for time in sorted(by_time):
            entries = by_time[time]
            if len(entries) < 2:
                continue
            scope = "same pet" if len({name for name, _ in entries}) == 1 else "different pets"
            labels = ", ".join(f"{title} ({name})" for name, title in entries)
            warnings.append(f"Conflict at {time}: {labels} [{scope}]")
        return warnings

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

    def tasks_for(self, pet_name: str, status: str | None = None) -> list[PetTask]:
        """Return the tasks for one named pet (empty list if the pet is unknown).

        Pass `status` ("pending" or "completed") to keep only matching tasks.
        """
        pet = self.get_pet(pet_name)
        tasks = list(pet.tasks) if pet is not None else []
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        return tasks

    def tasks_by_status(self, status: str) -> list[PetTask]:
        """Return every task across all pets whose status matches `status`."""
        return [task for task in self.all_tasks() if task.status == status]

    def build_plan(self, day: date | None = None) -> DailyPlan:
        """Build a DailyPlan from all pets' tasks under this owner's constraints."""
        if self.constraints is None:
            raise ValueError("Owner has no constraints set; cannot build a plan.")
        return DailyPlan.build(self.all_tasks(), self.constraints, day or date.today())
