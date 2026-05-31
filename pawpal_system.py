"""
PawPal+ Backend Logic Layer

Contains the core domain classes for pet care scheduling:
- Task: Individual care activity
- Pet: Pet entity with associated tasks
- Owner: Pet owner managing multiple pets
- Scheduler: Orchestrates daily plan generation
- ScheduleEntry: A scheduled task with time slot
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional

PRIORITY_LEVELS = {"low": 1, "medium":2, "high":3}
VALID_FREQUENCIES = {"daily", "weekly", "once"}


@dataclass
class Task:
    """Represents a single pet care activity."""

    id: str
    description: str
    duration_min: int
    priority: str = "medium"
    frequency: str = "daily"
    constraints: Dict[str, str] = field(default_factory=dict)
    is_complete: bool = False
    last_scheduled: Optional[date] = None

    def __post_init__(self) -> None:
        if not isinstance(self.duration_min, int) or isinstance(self.duration_min, bool):
            raise ValueError("duration_min must be an integer")
        if self.duration_min <= 0:
            raise ValueError("duration_min must be greater than zero")
        if self.priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {list(PRIORITY_LEVELS.keys())}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(VALID_FREQUENCIES)}")
    
    def is_due(self, today: date) -> bool:
        """Return True if this task should be scheduled on the given date."""
        if self.is_complete and self.frequency == "once":
            return False
        if self.last_scheduled is None:
            return True
        if self.frequency == "daily":
            return self.last_scheduled < today
        if self.frequency == "weekly":
            return (today - self.last_scheduled).days >= 7
        if self.frequency == "once":
            return not self.is_complete
        return True

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_complete = True

    def next_occurrence(self, new_id: str) -> Optional["Task"]:
        """
        Return a new Task instance for the next recurrence, or None if frequency is 'once'.

        The new task's last_scheduled is set so is_due() returns True on the correct future date:
          - daily:  due tomorrow  (last_scheduled = today)
          - weekly: due in 7 days (last_scheduled = today)
        """
        if self.frequency == "once":
            return None
        today = date.today()
        return Task(
            id=new_id,
            description=self.description,
            duration_min=self.duration_min,
            priority=self.priority,
            frequency=self.frequency,
            constraints=self.constraints.copy(),
            last_scheduled=today,
        )
    
    def priority_score(self) -> float:
        """Calculate a numeric score for prioritization."""
        base = PRIORITY_LEVELS.get(self.priority, 1)
        return base * 10.0 / self.duration_min
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary format."""
        return{
            "id" : self.id, 
            "description": self.description, 
            "duration_min": self.duration_min, 
            "priority": self.priority, 
            "frequency": self.frequency, 
            "constraints": self.constraints,
            "is_complete": self.is_complete
        }


@dataclass
class Pet:
    """Represents a pet with associated care tasks."""
    
    id: str
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)
    
    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID. Returns True if successful."""
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                self.tasks.pop(i)
                return True
        return False
    
    def edit_task(self, task_id: str, **updates) -> bool:
        """Edit a task's attributes. Returns True if successful."""
        for t in self.tasks:
            if t.id == task_id:
                for k, v in updates.items():
                    if hasattr(t, k):
                        setattr(t, k, v)
                return True
        return False
    
    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.is_complete]
    
    def get_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority (highest first)."""
        return sorted(self.get_pending_tasks(), key=lambda t: PRIORITY_LEVELS.get(t.priority, 1), reverse=True)


@dataclass
class Owner:
    """Represents a pet owner managing multiple pets."""
    
    id: str
    name: str
    available_time_min: int
    pets: List[Pet] = field(default_factory=list)
    global_preferences: Dict[str, str] = field(default_factory=dict)
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)
    
    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by ID. Returns True if successful."""
        for i, p in enumerate(self.pets):
            if p.id == pet_id:
                self.pets.pop(i)
                return True
        return False
    
    def get_all_tasks(self) -> List[Task]:
        """Return all pending tasks across all pets."""
        tasks: List[Task] = []
        for p in self.pets:
            tasks.extend(p.get_pending_tasks())
        return tasks
    
    def total_time_needed(self) -> int:
        """Calculate total minutes needed for all pending tasks."""
        return sum(t.duration_min for t in self.get_all_tasks())

    def filter_tasks(self, pet_id: str = None, status: str = None) -> List[Task]:
        """
        Return tasks filtered by pet and/or completion status.

        Args:
            pet_id: If provided, only return tasks for that pet.
            status: "pending" returns incomplete tasks; "complete" returns finished ones.
                    If omitted, all tasks are returned regardless of status.
        """
        pets = [p for p in self.pets if p.id == pet_id] if pet_id else self.pets
        tasks = [t for p in pets for t in p.tasks]
        if status == "pending":
            tasks = [t for t in tasks if not t.is_complete]
        elif status == "complete":
            tasks = [t for t in tasks if t.is_complete]
        return tasks


@dataclass
class ScheduleEntry:
    """A task scheduled for a specific time slot."""
    
    task: Task
    pet: Pet
    start: datetime
    end: datetime


@dataclass
class Scheduler:
    """Orchestrates daily schedule generation based on tasks and constraints."""
    
    owner: Owner
    date: date = field(default_factory=date.today)
    schedule: List[ScheduleEntry] = field(default_factory=list)
    overflow_tasks: List[Task] = field(default_factory=list)
    
    def build_daily_plan(self, start_time: time = None) -> List[ScheduleEntry]:
        """
        Generate a daily plan for the owner.

        Returns a list of scheduled task entries.
        Populates self.overflow_tasks with tasks that didn't fit.
        """
        if start_time is None:
            start_time = time(8, 0)

        self.schedule = []
        self.overflow_tasks = []

        all_tasks = self.owner.get_all_tasks()
        eligible_tasks = self.apply_constraints(all_tasks)

        # Sort by priority (high to low), then shorter tasks first to maximize coverage
        eligible_tasks.sort(key=lambda t: (PRIORITY_LEVELS.get(t.priority, 1), -t.duration_min), reverse=True)

        remaining_minutes = self.owner.available_time_min
        current_dt = datetime.combine(self.date, start_time)

        for task in eligible_tasks:
            if task.duration_min <= remaining_minutes:
                pet = self._find_pet_for_task(task)
                entry = ScheduleEntry(task=task, pet=pet, start=current_dt, end=current_dt + timedelta(minutes=task.duration_min))
                self.schedule.append(entry)
                task.last_scheduled = self.date
                current_dt = entry.end
                remaining_minutes -= task.duration_min
            else:
                self.overflow_tasks.append(task)

        return self.schedule

    def _find_pet_for_task(self, task: Task) -> Optional[Pet]:
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet
        return None

    def apply_constraints(self, tasks: List[Task]) -> List[Task]:
        """Filter tasks based on recurrence rules. Tasks that don't fit the time budget go to overflow."""
        return [t for t in tasks if t.is_due(self.date)]

    def complete_task(self, task_id: str) -> Optional[Task]:
        """
        Mark a scheduled task complete and queue the next occurrence for recurring tasks.

        Returns the newly created Task if one was queued, or None for one-time tasks.
        """
        for entry in self.schedule:
            if entry.task.id == task_id:
                entry.task.mark_complete()
                pet = entry.pet
                if pet is None:
                    return None
                new_id = f"{task_id}_next"
                new_task = entry.task.next_occurrence(new_id)
                if new_task:
                    pet.add_task(new_task)
                return new_task
        return None

    def detect_conflicts(self) -> List[tuple]:
        """
        Return a list of (entry_a, entry_b) pairs whose time windows overlap.

        Under normal scheduling this list is empty, but catches conflicts if
        entries are added manually or out of order.
        """
        conflicts = []
        entries = self.schedule
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                a, b = entries[i], entries[j]
                if a.start < b.end and b.start < a.end:
                    conflicts.append((a, b))
        return conflicts

    def warn_conflicts(self) -> List[str]:
        """
        Return a list of human-readable warning strings for any overlapping schedule entries.

        Returns an empty list when the schedule is conflict-free.
        """
        warnings = []
        for a, b in self.detect_conflicts():
            pet_a = a.pet.name if a.pet else "unknown"
            pet_b = b.pet.name if b.pet else "unknown"
            warnings.append(
                f"WARNING: '{a.task.description}' ({pet_a}, "
                f"{a.start.strftime('%H:%M')}-{a.end.strftime('%H:%M')}) conflicts with "
                f"'{b.task.description}' ({pet_b}, "
                f"{b.start.strftime('%H:%M')}-{b.end.strftime('%H:%M')})"
            )
        return warnings

    def sort_by_time(self) -> List[ScheduleEntry]:
        """Return scheduled entries sorted by start time (earliest first)."""
        return sorted(self.schedule, key=lambda entry: entry.start)

    def explain_decision(self) -> str:
        """Generate a human-readable explanation of why tasks were scheduled."""
        lines = [f"Daily plan for owner {self.owner.name} on {self.date.isoformat()}:\n"]

        if not self.schedule and not self.overflow_tasks:
            return "No tasks scheduled. No pending tasks or all tasks exceed constraints."

        if self.schedule:
            lines.append("Included tasks:")
            for e in self.schedule:
                lines.append(
                    f" - {e.task.description} (pet: {e.pet.name if e.pet else 'unknown'}, priority: {e.task.priority}, "
                    f"{e.task.duration_min} min, {e.start.strftime('%H:%M')} - {e.end.strftime('%H:%M')})"
                )

        if self.overflow_tasks:
            lines.append("\nOverflow tasks:")
            for t in self.overflow_tasks:
                lines.append(f" - {t.description} (priority: {t.priority}, {t.duration_min} min)")

        lines.append("\nReasoning: Tasks are ordered by priority and duration, then placed until time budget is exhausted.")
        return "\n".join(lines)
