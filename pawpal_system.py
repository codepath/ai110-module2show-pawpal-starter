"""
PawPal+ logic layer: Task, Pet, Owner, Scheduler.

Data flows: Owner -> [Pet] -> [Task]
Scheduler wraps Owner to sort, filter, detect conflicts, and handle recurrence.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """A single pet care activity."""
    description: str
    time: str           # "HH:MM" — used for sorting and conflict detection
    duration_minutes: int
    priority: str       # "low" | "medium" | "high"
    frequency: str = "once"   # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self):
        """Mark this task done."""
        self.completed = True


@dataclass
class Pet:
    """A pet with its own task list."""
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """Append task to this pet's list."""
        self.tasks.append(task)

    def get_tasks(self) -> list:
        """Return all tasks for this pet."""
        return self.tasks


@dataclass
class Owner:
    """An owner who manages one or more pets."""
    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Return (pet_name, task) pairs across all pets."""
        return [(pet.name, task) for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    """
    The scheduling brain.
    Retrieves tasks from the owner's pets and applies ordering,
    filtering, conflict detection, and recurrence logic.
    """

    def __init__(self, owner: Owner):
        self.owner = owner

    # ── Sorting ────────────────────────────────────────────────────────────────

    def sort_by_time(self, tasks_with_pet: Optional[list] = None) -> list:
        """Return tasks sorted chronologically by HH:MM time string."""
        if tasks_with_pet is None:
            tasks_with_pet = self.owner.get_all_tasks()
        return sorted(tasks_with_pet, key=lambda x: x[1].time)

    # ── Filtering ──────────────────────────────────────────────────────────────

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list:
        """
        Return tasks matching the given filters.
        Pass pet_name to restrict to one pet; pass completed to filter by status.
        """
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [(p, t) for p, t in tasks if p == pet_name]
        if completed is not None:
            tasks = [(p, t) for p, t in tasks if t.completed == completed]
        return tasks

    # ── Today's schedule ───────────────────────────────────────────────────────

    def get_todays_schedule(self) -> list:
        """Return sorted, incomplete tasks due today or earlier."""
        today = date.today()
        pending = [
            (p, t)
            for p, t in self.owner.get_all_tasks()
            if not t.completed and t.due_date <= today
        ]
        return self.sort_by_time(pending)

    # ── Recurrence ─────────────────────────────────────────────────────────────

    def mark_task_complete(self, pet_name: str, task: Task):
        """
        Mark task complete. For daily/weekly tasks, schedule the next occurrence.
        Tradeoff: only exact-day recurrence — no support for 'every 3 days' etc.
        """
        task.mark_complete()
        delta = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}.get(task.frequency)
        if delta is None:
            return
        next_task = Task(
            description=task.description,
            time=task.time,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            frequency=task.frequency,
            due_date=task.due_date + delta,
        )
        for pet in self.owner.pets:
            if pet.name == pet_name:
                pet.add_task(next_task)
                break

    # ── Conflict detection ─────────────────────────────────────────────────────

    def detect_conflicts(self) -> list[str]:
        """
        Detect tasks (across all pets) scheduled at the exact same HH:MM time.
        Returns a list of human-readable warning strings.
        Tradeoff: exact-time matches only — overlapping durations are not checked.
        """
        seen: dict[str, tuple[str, Task]] = {}
        conflicts: list[str] = []
        for pet_name, task in self.owner.get_all_tasks():
            if task.time in seen:
                prev_pet, prev_task = seen[task.time]
                conflicts.append(
                    f"Conflict at {task.time}: '{task.description}' ({pet_name}) "
                    f"clashes with '{prev_task.description}' ({prev_pet})"
                )
            else:
                seen[task.time] = (pet_name, task)
        return conflicts

    # ── Plain-text plan ────────────────────────────────────────────────────────

    def generate_plan_text(self) -> str:
        """Return a readable plain-text summary of today's schedule."""
        schedule = self.get_todays_schedule()
        if not schedule:
            return f"No pending tasks for {self.owner.name} today."

        priority_order = {"high": 0, "medium": 1, "low": 2}
        lines = [f"Today's Schedule — {self.owner.name}:"]
        lines.append("-" * 48)
        for pet_name, task in schedule:
            lines.append(
                f"  [ ] {task.time}  {pet_name}: {task.description}"
                f"  ({task.duration_minutes}min · {task.priority} · {task.frequency})"
            )
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("")
            lines.append("⚠ Conflicts detected:")
            for c in conflicts:
                lines.append(f"  {c}")
        return "\n".join(lines)
