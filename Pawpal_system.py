"""PawPal+ core classes. Matches diagrams/uml_draft.mmd."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
FREQUENCY_STEP = {"Daily": timedelta(days=1), "Weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """Represents a single care activity."""

    description: str
    due_time: datetime
    duration_mins: int
    priority: str = "medium"  # "low", "medium", or "high"
    frequency: str = "Once"  # "Once", "Daily", or "Weekly"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def end_time(self) -> datetime:
        """Return when this task finishes."""
        return self.due_time + timedelta(minutes=self.duration_mins)

    def overlaps(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps other's."""
        return self.due_time < other.end_time() and other.due_time < self.end_time()


@dataclass
class Pet:
    """Represents a pet profile."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """Represents a pet owner and their daily constraints."""

    name: str
    available_minutes: int = 120
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        """Return a list of (pet_name, task) tuples across all of this owner's pets."""
        return [(pet.name, task) for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledTask:
    """A task placed in the daily plan, with the reason it was chosen."""

    pet_name: str
    task: Task
    start_time: datetime
    reason: str


@dataclass
class Scheduler:
    """Manages scheduling logic, conflict detection, and task retrieval."""

    owner: Owner

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        """Return a list of (pet_name, task) tuples for every pet the owner has."""
        return self.owner.get_all_tasks()

    def get_upcoming_tasks(self) -> List[Tuple[str, Task]]:
        """Return incomplete tasks sorted by due time, then by priority."""
        pending = [(name, task) for name, task in self.get_all_tasks() if not task.is_completed]
        return sorted(pending, key=lambda item: (item[1].due_time, -self._priority(item[1])))

    def check_conflicts(self, new_task: Task) -> bool:
        """Return True if new_task overlaps any existing incomplete task for any pet."""
        return self._find_conflict(new_task, [task for _, task in self.get_upcoming_tasks()]) is not None

    def generate_recurring_tasks(self) -> List[Tuple[str, Task]]:
        """Create the next instance of each completed Daily/Weekly task and return the new tasks."""
        created = []
        for pet in self.owner.pets:
            for task in list(pet.tasks):
                step = FREQUENCY_STEP.get(task.frequency)
                if not task.is_completed or step is None:
                    continue
                next_due = task.due_time + step
                already_exists = any(
                    t.description == task.description and t.due_time == next_due for t in pet.tasks
                )
                if already_exists:
                    continue
                next_task = Task(
                    description=task.description,
                    due_time=next_due,
                    duration_mins=task.duration_mins,
                    priority=task.priority,
                    frequency=task.frequency,
                )
                pet.add_task(next_task)
                created.append((pet.name, next_task))
        return created

    def generate_plan(self) -> List[ScheduledTask]:
        """Pick tasks by priority that fit the owner's time without overlaps, returned in time order."""
        candidates = sorted(
            self.get_upcoming_tasks(),
            key=lambda item: (
                -self._priority(item[1]),
                not self._is_preferred(item[1]),
                item[1].due_time,
            ),
        )

        remaining = self.owner.available_minutes
        plan: List[ScheduledTask] = []
        for pet_name, task in candidates:
            if task.duration_mins > remaining:
                continue
            if self._find_conflict(task, [item.task for item in plan]) is not None:
                continue
            remaining -= task.duration_mins
            plan.append(ScheduledTask(pet_name, task, task.due_time, self._reason(task, remaining)))

        return sorted(plan, key=lambda item: item.start_time)

    def explain_plan(self, plan: List[ScheduledTask]) -> str:
        """Return a readable explanation of why each task was chosen and when."""
        if not plan:
            return f"No tasks fit into {self.owner.name}'s {self.owner.available_minutes} available minutes."

        used = sum(item.task.duration_mins for item in plan)
        lines = [f"Daily plan for {self.owner.name} ({used}/{self.owner.available_minutes} min used):"]
        for item in plan:
            lines.append(
                f"  {item.start_time:%H:%M} - {item.task.description} for {item.pet_name} "
                f"({item.task.duration_mins} min) [priority: {item.task.priority}]"
            )
            lines.append(f"      Why: {item.reason}")
        return "\n".join(lines)

    def _priority(self, task: Task) -> int:
        """Return a numeric rank for the task's priority (unknown values rank lowest)."""
        return PRIORITY_RANK.get(task.priority.lower(), 0)

    def _is_preferred(self, task: Task) -> bool:
        """Return True if the task description matches any of the owner's preferences."""
        description = task.description.lower()
        return any(pref.lower() in description for pref in self.owner.preferences)

    def _find_conflict(self, new_task: Task, existing: List[Task]) -> Optional[Task]:
        """Return the first task in existing that overlaps new_task, if any."""
        for task in existing:
            if task is not new_task and new_task.overlaps(task):
                return task
        return None

    def _reason(self, task: Task, remaining: int) -> str:
        """Build the explanation for why a task was added to the plan."""
        reason = f"{task.priority.capitalize()} priority"
        if self._is_preferred(task):
            reason += ", matches your preferences"
        return f"{reason}; fits in your time ({remaining} min left after this)."


if __name__ == "__main__":
    today = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    owner = Owner("Jordan", available_minutes=60, preferences=["walk"])
    luna = Pet("Luna", "Dog", 4)
    milo = Pet("Milo", "Cat", 2)
    owner.add_pet(luna)
    owner.add_pet(milo)

    luna.add_task(Task("Morning walk", today, 30, "high", "Daily"))
    luna.add_task(Task("Dinner", today.replace(hour=18), 10, "high", "Daily"))
    milo.add_task(Task("Brush fur", today.replace(hour=8, minute=15), 15, "medium", "Weekly"))
    milo.add_task(Task("Play time", today.replace(hour=12), 25, "low"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    print(scheduler.explain_plan(plan))
