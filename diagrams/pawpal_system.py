"""PawPal+ system skeleton.

Class stubs generated from diagrams/uml.mmd. No scheduling logic yet —
attributes and empty method bodies only. Fill these in incrementally.
"""

from dataclasses import dataclass, field

# Higher number = scheduled earlier. Unknown priorities fall to 0 (lowest).
_PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


def _to_minutes(hhmm: str) -> int:
    """Convert a "HH:MM" string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight back to a "HH:MM" string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    """A single daily care item for a pet."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    done: bool = False

    def priority_rank(self) -> int:
        """Return a sortable integer for this task's priority (higher = more urgent)."""
        # Unknown/typo priorities fall to 0 so a bad value degrades safely.
        return _PRIORITY_RANK.get(self.priority.lower(), 0)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.done = True


@dataclass
class Pet:
    """An individual animal and the tasks that belong to it."""

    name: str
    species: str = "other"  # "dog" | "cat" | "other"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """The person who manages one or more pets."""

    name: str
    email: str = ""
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flatten and return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledItem:
    """A task placed into the daily plan, with its time slot and reasoning."""

    task: Task
    pet_name: str  # which pet this task belongs to (preserved through scheduling)
    start_time: str  # e.g. "08:00"
    reason: str = ""


class Scheduler:
    """Builds an ordered daily plan from an owner's tasks under given constraints."""

    def build_plan(
        self, owner: Owner, available_minutes: int, day_start: str = "08:00"
    ) -> list[ScheduledItem]:
        """Build the daily plan: filter, sort, then assign time slots."""
        # Pair each task with its pet's name so the plan can show "for <pet>".
        pet_by_task = {
            id(task): pet.name for pet in owner.pets for task in pet.tasks
        }
        all_tasks = owner.all_tasks()

        candidates = self.sort_tasks(self.filter_tasks(all_tasks, available_minutes))

        plan: list[ScheduledItem] = []
        minutes_used = 0
        cursor = _to_minutes(day_start)
        for task in candidates:
            if minutes_used + task.duration_minutes > available_minutes:
                continue  # won't fit in the remaining budget; try the next one
            item = ScheduledItem(
                task=task,
                pet_name=pet_by_task[id(task)],
                start_time=_to_hhmm(cursor),
                reason=f"{task.priority} priority, fits remaining time",
            )
            plan.append(item)
            minutes_used += task.duration_minutes
            cursor += task.duration_minutes
        return plan

    def filter_tasks(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        """Drop tasks that are already done or that won't fit in available_minutes."""
        return [
            task
            for task in tasks
            if not task.done and task.duration_minutes <= available_minutes
        ]

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order by priority (high first), then shorter tasks first as a tie-break."""
        return sorted(
            tasks, key=lambda t: (-t.priority_rank(), t.duration_minutes)
        )

    def explain(self, item: ScheduledItem) -> str:
        """Return a human-readable reason for why this item was scheduled as it was."""
        return (
            f"{item.start_time} — {item.task.title} for {item.pet_name} "
            f"({item.task.duration_minutes} min) [{item.reason}]"
        )