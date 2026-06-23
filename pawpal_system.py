from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task — single activity belonging to a Pet
# ---------------------------------------------------------------------------

PRIORITY_ORDER: dict[str, int] = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    pet: Pet
    task_type: str                                              # grooming | feeding | vet_visit | walk | medication | other
    description: str = ""                                      # what the task involves
    frequency: str = "once"                                    # once | daily | weekly | monthly
    priority: str = "medium"                                   # high | medium | low
    status: str = "pending"                                    # pending | completed | overdue
    deadline: Optional[date] = None
    scheduled_time: Optional[datetime] = None
    duration: int = 30                                         # minutes
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def complete_task(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def delete_task(self, pet: Pet) -> None:
        """Remove this task from the pet's list and from the scheduler's weekly_schedule."""
        if self in pet.tasks:
            pet.tasks.remove(self)
        if pet.owner and pet.owner.scheduler and self.scheduled_time:
            day = self.scheduled_time.date()
            day_schedule = pet.owner.scheduler.weekly_schedule.get(day, [])
            if self in day_schedule:
                day_schedule.remove(self)

    def mark_overdue(self) -> None:
        """Flip status to overdue when deadline has passed and task is still pending."""
        if self.status == "pending" and self.deadline and self.deadline < date.today():
            self.status = "overdue"

    def reschedule(self, new_time: datetime) -> None:
        """Update scheduled_time to new_time."""
        self.scheduled_time = new_time

    def is_due_today(self) -> bool:
        """Return True if this task should appear on today's schedule based on frequency and status."""
        today = date.today()
        if self.frequency == "once":
            return self.status == "pending"
        last_completed = (
            self.scheduled_time.date() if self.scheduled_time and self.status == "completed"
            else None
        )
        if self.frequency == "daily":
            return last_completed != today
        if self.frequency == "weekly":
            return last_completed is None or (today - last_completed).days >= 7
        if self.frequency == "monthly":
            return last_completed is None or (today - last_completed).days >= 30
        return False


# ---------------------------------------------------------------------------
# Pet — stores pet details and owns its task list
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    pet_type: str                                               # e.g. "Dog", "Cat"
    owner: Optional[Owner] = None                              # set via Owner.add_pet()
    breed: str = ""
    age: int = 0
    weight: float = 0.0
    health_conditions: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    eating_habit: list[str] = field(default_factory=list)      # human-readable descriptions
    meal_times: list[tuple[datetime, datetime]] = field(default_factory=list)   # (start, end) for Scheduler
    sleeping_time: list[tuple[datetime, datetime]] = field(default_factory=list)
    daily_sleep_hours: int = 0
    last_seen_doctor: Optional[date] = None
    tasks: list[Task] = field(default_factory=list)            # this pet's task list

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's list."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks for this pet that are not yet completed."""
        return [t for t in self.tasks if t.status != "completed"]

    def get_todays_tasks(self) -> list[Task]:
        """Return tasks for this pet that are due today."""
        return [t for t in self.tasks if t.is_due_today()]


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and provides access to all their tasks
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, email: str) -> None:
        self.name: str = name
        self.email: str = email
        self.pets: list[Pet] = []
        self.constraints: list[str] = []
        self.scheduler: Optional[Scheduler] = None             # wired after Scheduler is created

    def set_scheduler(self, scheduler: Scheduler) -> None:
        """Attach a Scheduler to this owner. Call after both objects are constructed."""
        self.scheduler = scheduler

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet and wire the back-reference so pet.owner points to self."""
        self.pets.append(pet)
        pet.owner = self

    def add_task(self, task: Task) -> None:
        """Route a task to its pet's task list (tasks live on Pets, not Owner)."""
        task.pet.add_task(task)

    def add_constraint(self, constraint: str) -> None:
        """Record a lifestyle constraint string (e.g. 'work 9am-5pm weekdays')."""
        self.constraints.append(constraint)

    def display_constraints(self) -> list[str]:
        """Return all current constraints for display in the UI."""
        return self.constraints

    def get_todays_tasks(self) -> list[Task]:
        """Gather every pet's tasks that are due today into one flat list."""
        return [task for pet in self.pets for task in pet.get_todays_tasks()]

    def get_unfinished_tasks(self) -> list[Task]:
        """Gather every pet's pending/overdue tasks into one flat list."""
        return [task for pet in self.pets for task in pet.get_pending_tasks()]


# ---------------------------------------------------------------------------
# Scheduler — retrieves, organizes, and manages tasks across all pets
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner
        self.available_blocks: list[tuple[datetime, datetime]] = []    # owner's free windows
        self.blocked_times: list[tuple[datetime, datetime]] = []       # merged pet constraints
        self.weekly_schedule: dict[date, list[Task]] = {}              # derived view of owner.pets tasks

    def add_available_block(self, start: datetime, end: datetime) -> None:
        """Register a window when the owner is free for pet care."""
        self.available_blocks.append((start, end))

    def build_blocked_times(self) -> None:
        """Collect every pet's sleeping and meal intervals into blocked_times for conflict checking."""
        blocked: list[tuple[datetime, datetime]] = []
        for pet in self.owner.pets:
            blocked.extend(pet.sleeping_time)
            blocked.extend(pet.meal_times)
        self.blocked_times = blocked

    def check_conflict(self, start: datetime, duration: int) -> bool:
        """Return True if [start, start+duration) overlaps any blocked interval."""
        end = start + timedelta(minutes=duration)
        return any(
            start < block_end and end > block_start
            for block_start, block_end in self.blocked_times
        )

    def find_open_slot(
        self, task: Task, on_date: Optional[date] = None
    ) -> Optional[tuple[datetime, datetime]]:
        """Return the earliest free (start, end) window that fits the task's duration, or None."""
        blocks = self.available_blocks
        if on_date:
            blocks = [(s, e) for s, e in blocks if s.date() == on_date]

        for avail_start, avail_end in blocks:
            candidate = avail_start
            while candidate + timedelta(minutes=task.duration) <= avail_end:
                if not self.check_conflict(candidate, task.duration):
                    return (candidate, candidate + timedelta(minutes=task.duration))
                # jump past whichever blocked window contains candidate
                jumped = False
                for block_start, block_end in self.blocked_times:
                    if block_start <= candidate < block_end:
                        candidate = block_end
                        jumped = True
                        break
                if not jumped:
                    candidate += timedelta(minutes=15)
        return None

    def get_all_tasks(self) -> list[Task]:
        """Pull every task from every pet into one flat list."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def generate_daily_schedule(self, target_date: date) -> None:
        """Sort all due tasks by priority and deadline, slot each into a free window, and store in weekly_schedule."""
        self.build_blocked_times()

        due_tasks = [t for t in self.get_all_tasks() if t.is_due_today()]
        due_tasks.sort(key=lambda t: (
            PRIORITY_ORDER.get(t.priority, 1),
            t.deadline or date.max,
        ))

        scheduled: list[Task] = []
        for task in due_tasks:
            slot = self.find_open_slot(task, on_date=target_date)
            if slot:
                task.scheduled_time = slot[0]
                scheduled.append(task)
                self.blocked_times.append(slot)  # prevent later tasks overlapping

        self.weekly_schedule[target_date] = scheduled

    def get_schedule(self, target_date: date) -> list[Task]:
        """Return the ordered task list for target_date. Returns [] if not yet generated."""
        return self.weekly_schedule.get(target_date, [])
