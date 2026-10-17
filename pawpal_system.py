from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from itertools import combinations
from typing import List


class TaskType(Enum):
    WALK = "walk"
    FEED = "feed"
    VET = "vet"


class Recurrence(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

    @property
    def interval(self) -> timedelta:
        """Time between occurrences of this recurrence."""
        return timedelta(days=1 if self is Recurrence.DAILY else 7)


# eq=False: tasks compare by identity, so two identical "feed" tasks stay distinct.
@dataclass(eq=False)
class Task:
    task_type: TaskType
    due_time: datetime
    pet: Pet | None = field(default=None, repr=False)  # set by Pet.add_task
    description: str = ""
    duration_minutes: int = 15
    priority: int = 1  # higher wins when tasks conflict
    recurrence: Recurrence | None = None
    completed: bool = False

    @property
    def end_time(self) -> datetime:
        """When the task finishes (due_time plus duration)."""
        return self.due_time + timedelta(minutes=self.duration_minutes)

    def mark_complete(self, today: date | None = None) -> Task | None:
        """Mark the task complete and, if it recurs, schedule the next occurrence.

        The next due date is counted from the completion day (not the old due date), so a
        late daily task reappears tomorrow instead of in the past. The time of day is kept.

        Args:
            today: Completion date; defaults to date.today(). Mainly for testing.

        Returns:
            The newly created next Task (also added to this task's pet), or None if the
            task does not recur or was already completed (so no duplicates are created).
        """
        if self.completed:  # already done: don't spawn a duplicate occurrence
            return None
        self.completed = True
        if self.recurrence is None:
            return None
        next_task = Task(
            task_type=self.task_type,
            due_time=datetime.combine(
                (today or date.today()) + self.recurrence.interval, self.due_time.time()
            ),
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
        )
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task

    def overlaps(self, other: Task) -> bool:
        """Check whether this task's time range intersects another's.

        Ranges are half-open, so back-to-back tasks (one ends exactly when the next
        starts) do not count as overlapping.

        Returns:
            True if the two tasks share any time.
        """
        return self.due_time < other.end_time and other.due_time < self.end_time


@dataclass
class Pet:
    name: str
    age: int
    gender: str
    animal_type: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach task to this pet and set task.pet."""
        task.pet = self
        if task not in self.tasks:
            self.tasks.append(task)


@dataclass
class Owner:
    first_name: str
    last_name: str
    age: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, ignoring duplicates."""
        if pet not in self.pets:
            self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """All tasks across all pets (derived, not stored)."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class Scheduler:
    """Builds schedules from owner.get_all_tasks(); stores no task list of its own."""

    owner: Owner

    @staticmethod
    def sort_by_time(tasks: List[Task]) -> List[Task]:
        """Return a new list of tasks ordered by due_time (earliest first).

        Tasks with the same due_time are ordered by priority, highest first. The input
        list is not modified.
        """
        return sorted(tasks, key=lambda t: (t.due_time, -t.priority))

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        task_type: TaskType | None = None,
    ) -> List[Task]:
        """Return the owner's tasks (across all pets) that match every given filter.

        Args:
            pet_name: Keep only tasks for the pet with this name.
            completed: True for finished tasks, False for pending ones.
            task_type: Keep only tasks of this TaskType.

        A filter left as None is ignored. Results are sorted with sort_by_time().
        """
        tasks = [
            t for t in self.owner.get_all_tasks()
            if (pet_name is None or (t.pet is not None and t.pet.name == pet_name))
            and (completed is None or t.completed == completed)
            and (task_type is None or t.task_type == task_type)
        ]
        return self.sort_by_time(tasks)

    def get_daily_schedule(self, day: date) -> List[Task]:
        """Return the incomplete tasks due on the given day, in time order.

        Args:
            day: The calendar date to build the schedule for.
        """
        return [t for t in self.filter_tasks(completed=False) if t.due_time.date() == day]

    def get_pending_tasks(self) -> List[Task]:
        """Return every incomplete task across all pets, soonest first (any day)."""
        return self.filter_tasks(completed=False)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete via Task.mark_complete().

        Returns:
            The next occurrence if the task recurs, otherwise None.
        """
        return task.mark_complete()

    def find_conflicts(self) -> List[tuple[Task, Task]]:
        """Find every pair of incomplete tasks whose time ranges overlap.

        Works across pets, so it catches clashes for one pet and between different pets.
        Checks all pairs (O(n^2)), which is fine for a typical owner's task count.

        Returns:
            A list of (earlier_task, later_task) tuples; empty if there are no conflicts.
        """
        # Compares every pair (not just neighbours): a long task can overlap several later ones.
        return [(a, b) for a, b in combinations(self.get_pending_tasks(), 2) if a.overlaps(b)]

    def conflicts_with(self, task: Task) -> List[Task]:
        """List the incomplete tasks that overlap the given task.

        Useful for checking a task before adding it. The task itself is excluded if it
        is already scheduled.
        """
        return [t for t in self.get_pending_tasks() if t is not task and t.overlaps(task)]

    def get_conflict_warnings(self) -> List[str]:
        """Describe each scheduling conflict as a readable warning message.

        Never raises: a task with no pet is reported as "unassigned", and the schedule is
        left unchanged (the owner decides how to resolve each conflict).

        Returns:
            One warning string per overlapping pair; empty if there are no conflicts.
        """
        warnings = []
        for a, b in self.find_conflicts():
            a_pet = a.pet.name if a.pet else "unassigned"
            b_pet = b.pet.name if b.pet else "unassigned"
            who = f"for {a_pet}" if a_pet == b_pet else f"for {a_pet} and {b_pet}"
            warnings.append(
                f"Warning: {a.task_type.value} ({a.due_time:%a %H:%M}-{a.end_time:%H:%M}) "
                f"overlaps {b.task_type.value} ({b.due_time:%H:%M}-{b.end_time:%H:%M}) {who}"
            )
        return warnings
