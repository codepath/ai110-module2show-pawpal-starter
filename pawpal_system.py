"""PawPal+ logic layer: Task, Pet, Owner, and the cross-pet Scheduler."""

from __future__ import annotations

import json
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

# Sort rank per priority level (lower rank sorts first).
PRIORITY_RANK = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

# Waking-day window scanned by find_next_available_slot.
DAY_START = time(7, 0)
DAY_END = time(21, 0)


def _to_minutes(time_val: time | str) -> int:
    """Convert a datetime.time or 'HH:MM' string to minutes since midnight."""
    if isinstance(time_val, str):
        hours, minutes = map(int, time_val.split(":"))
        return hours * 60 + minutes
    return time_val.hour * 60 + time_val.minute


def _to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight to "HH:MM"."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


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
    priority: Priority | str = Priority.MEDIUM  # converts to Priority in __post_init__

    def __post_init__(self) -> None:
        """Coerce string inputs to datetime.time and StrEnum objects."""
        if isinstance(self.time, str):
            hours, minutes = map(int, self.time.split(":"))
            self.time = time(hours, minutes)
        if isinstance(self.frequency, str):
            self.frequency = Frequency(self.frequency)
        if isinstance(self.priority, str):
            self.priority = Priority(self.priority)

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

    def sort_by_priority(self) -> list[tuple[Pet, Task]]:
        """Return all pairs ordered by priority (high first), then by time."""
        return sorted(
            self.all_tasks(),
            key=lambda pair: (PRIORITY_RANK.get(pair[1].priority, 1), pair[1].time),
        )

    def filter_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
        """Return pairs whose task completion status matches."""
        return [
            (pet, task) for pet, task in self.all_tasks() if task.completed == completed
        ]

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Return pairs belonging to the named pet."""
        return [(pet, task) for pet, task in self.all_tasks() if pet.name == pet_name]

    def detect_conflicts(self) -> list[str]:
        """Return human-readable warnings for overlapping pending tasks.

        Two pending tasks conflict when their time blocks (start time plus
        duration) overlap on the same date — one caretaker can't do both.
        Back-to-back tasks (one ends exactly when the next starts) are fine.
        Warnings are advisory strings; nothing is raised or blocked.
        """
        pending = [(pet, task) for pet, task in self.all_tasks() if not task.completed]
        warnings = []
        for i, (pet_a, task_a) in enumerate(pending):
            for pet_b, task_b in pending[i + 1 :]:
                if task_a.date != task_b.date:
                    continue
                start_a = _to_minutes(task_a.time)
                start_b = _to_minutes(task_b.time)
                if (
                    start_a < start_b + task_b.duration_minutes
                    and start_b < start_a + task_a.duration_minutes
                ):
                    time_str = (
                        task_a.time.strftime("%H:%M")
                        if isinstance(task_a.time, time)
                        else task_a.time
                    )
                    warnings.append(
                        f"Conflict at {time_str} on {task_a.date}: "
                        f"{task_a.description} ({pet_a.name}) overlaps "
                        f"{task_b.description} ({pet_b.name})"
                    )
        return warnings

    def find_next_available_slot(
        self, duration_minutes: int, day: date | None = None
    ) -> str | None:
        """Earliest "HH:MM" where a task of this length fits with no overlap.

        Considers every pet's pending tasks on `day` (default today) as busy
        blocks and scans the DAY_START–DAY_END waking window. Returns None if
        no gap is large enough.
        """
        day = day or date.today()
        busy = sorted(
            (_to_minutes(task.time), _to_minutes(task.time) + task.duration_minutes)
            for _pet, task in self.all_tasks()
            if task.date == day and not task.completed
        )
        cursor = _to_minutes(DAY_START)
        for start, end in busy:
            limit = min(start, _to_minutes(DAY_END))
            if limit - cursor >= duration_minutes:
                return _to_hhmm(cursor)
            cursor = max(cursor, end)
            if cursor + duration_minutes > _to_minutes(DAY_END):
                break
        if _to_minutes(DAY_END) - cursor >= duration_minutes:
            return _to_hhmm(cursor)
        return None

    def complete_task(self, task: Task) -> Task | None:
        """Complete a task; if recurring, add and return its next occurrence."""
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is None:
            return None
        owning_pet = next((pet for pet in self.owner.pets if task in pet.tasks), None)
        if (
            owning_pet is None
        ):  # task detached from this household; nothing to reschedule
            return None
        owning_pet.add_task(follow_up)
        return follow_up

    def reschedule_task(
        self, task: Task, new_time: time | str, new_date: date
    ) -> list[str]:
        """Reschedule a task to a new time and date, returning any conflict warnings.

        Raises:
            ValueError: If the task is already completed.
        """
        if task.completed:
            raise ValueError("Cannot reschedule a completed task.")
        if isinstance(new_time, str):
            hours, minutes = map(int, new_time.split(":"))
            new_time = time(hours, minutes)
        task.time = new_time
        task.date = new_date
        return self.detect_conflicts()


class _PawPalEncoder(json.JSONEncoder):
    """Custom JSON encoder to serialize date and time objects."""

    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, time):
            return obj.strftime("%H:%M")
        return super().default(obj)


def save_to_json(owner: Owner, path: str) -> None:
    """Save owner, pets, and tasks data to a JSON file."""
    from dataclasses import asdict

    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(owner), f, cls=_PawPalEncoder, indent=2)


def load_from_json(path: str) -> Owner:
    """Load owner, pets, and tasks data from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    owner = Owner(name=data["name"])
    for pet_data in data.get("pets", []):
        pet = Pet(name=pet_data["name"], species=pet_data["species"])
        for task_data in pet_data.get("tasks", []):
            task = Task(
                description=task_data["description"],
                time=task_data["time"],
                date=(
                    date.fromisoformat(task_data["date"])
                    if isinstance(task_data["date"], str)
                    else task_data["date"]
                ),
                duration_minutes=task_data["duration_minutes"],
                frequency=task_data["frequency"],
                completed=task_data["completed"],
                priority=task_data.get("priority", "medium"),
            )
            pet.add_task(task)
        owner.add_pet(pet)
    return owner
