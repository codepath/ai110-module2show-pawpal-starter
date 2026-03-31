from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Pet — dataclass (pure data carrier, no complex init logic)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    pet_type: str                                          # e.g. "Dog", "Cat"
    owner: Owner = None                         # back-reference to Owner
    breed: str = ""
    age: int = 0
    weight: float = 0.0
    health_conditions: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    eating_habit: list[str] = field(default_factory=list)
    sleeping_time: list[tuple[datetime, datetime]] = field(default_factory=list)  # (start, end) pairs
    daily_sleep_hours: int = 0
    last_seen_doctor: Optional[date] = None


# ---------------------------------------------------------------------------
# Task — dataclass (data + a few state-transition methods)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    pet: Pet
    task_type: str                                        # grooming | feeding | vet_visit | walk | medication | other
    priority: str = "medium"                             # high | medium | low
    status: str = "pending"                              # pending | completed | overdue
    deadline: Optional[date] = None
    scheduled_time: Optional[datetime] = None
    duration: int = 30                                   # minutes
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def complete_task(self) -> None:
        """Mark this task as completed."""
        pass

    def delete_task(self) -> None:
        """Remove this task (caller is responsible for removing it from Owner's list)."""
        pass

    def mark_overdue(self) -> None:
        """Flip status to overdue when deadline has passed and task is still pending."""
        pass

    def reschedule(self, _new_time: datetime) -> None:
        """Update scheduled_time to new_time."""
        pass


# ---------------------------------------------------------------------------
# Owner — regular class (identity + owns pets/tasks/constraints)
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, email: str, scheduler: Scheduler) -> None:
        self.name: str = name
        self.email: str = email
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []
        self.constraints: list[str] = []                 # e.g. "work 9am-5pm weekdays"
        self.scheduler: Scheduler = scheduler    # assigned after Scheduler is created

    def add_pet(self, _pet: Pet) -> None:
        """Add a Pet to this owner's roster and set pet.owner back-reference."""
        pass

    def add_task(self, _task: Task) -> None:
        """Append a Task to this owner's master task list."""
        pass

    def add_constraint(self, _constraint: str) -> None:
        """Record a lifestyle constraint that blocks grooming time."""
        pass

    def display_constraints(self) -> None:
        """Print or return all current constraints for display in the UI."""
        pass

    def get_todays_tasks(self) -> list[Task]:
        """Return tasks whose scheduled_time or created_at falls on today's date."""
        pass

    def get_unfinished_tasks(self) -> list[Task]:
        """Return all tasks where status is not 'completed'."""
        pass


# ---------------------------------------------------------------------------
# Scheduler — regular class (the scheduling engine / constraint solver)
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner
        self.available_blocks: list[tuple[datetime, datetime]] = []   # owner's free windows
        self.blocked_times: list[tuple[datetime, datetime]] = []      # merged owner + pet constraints
        self.weekly_schedule: dict[date, list[Task]] = {}             # date → ordered task list

    def build_blocked_times(self) -> None:
        """
        Merge owner constraints + each pet's sleeping_time and eating windows
        into self.blocked_times so find_open_slot() knows what to avoid.
        """
        pass

    def find_open_slot(self, _task: Task) -> Optional[tuple[datetime, datetime]]:
        """
        Given a task's duration and priority, return the earliest (start, end)
        window that does not conflict with blocked_times.
        """
        pass

    def generate_daily_schedule(self, _target_date: date) -> None:
        """
        Sort pending tasks by priority + deadline, call find_open_slot() for
        each, and populate weekly_schedule[target_date].
        """
        pass

    def check_conflict(self, _time: datetime, _duration: int) -> bool:
        """Return True if the given time + duration overlaps any blocked window."""
        pass

    def get_schedule(self, _target_date: date) -> list[Task]:
        """Return the ordered task list for target_date from weekly_schedule."""
        pass
