"""
PawPal System — logic layer
Class skeletons derived from the UML diagram in reflection.md.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


# ---------------------------------------------------------------------------
# Reminder
# ---------------------------------------------------------------------------

@dataclass
class Reminder:
    """A scheduled notification linking an Owner to a Task or Appointment."""

    owner_id: str
    message: str
    send_at: datetime
    task_id: Optional[str] = None    # set if this reminder is about a Task
    appt_id: Optional[str] = None    # set if this reminder is about an Appointment
    sent: bool = False
    reminder_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single care activity for a pet (feeding, walk, medication, etc.)."""

    title: str
    pet_id: str
    due_date: datetime
    description: str = ""
    recurrence: Optional[str] = None   # e.g. "daily", "weekly", None for one-time
    is_complete: bool = False
    completed_at: Optional[datetime] = None   # set when mark_complete() is called
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_complete(self) -> None:
        """Mark this task as done and record the completion timestamp."""
        self.is_complete = True
        self.completed_at = datetime.now()

    def reschedule(self, new_date: datetime) -> None:
        """Move the due date to new_date."""
        self.due_date = new_date

    def is_overdue(self) -> bool:
        """Return True if the task is past due and not yet complete."""
        return not self.is_complete and datetime.now() > self.due_date


# ---------------------------------------------------------------------------
# Appointment
# ---------------------------------------------------------------------------

@dataclass
class Appointment:
    """A scheduled visit to a vet, groomer, or other care provider."""

    pet_id: str
    appointment_type: str          # e.g. "vet checkup", "grooming", "vaccination"
    provider_name: str
    location: str
    date_time: datetime
    notes: str = ""
    cancelled: bool = False
    appt_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def reschedule(self, new_datetime: datetime) -> None:
        """Move the appointment to a new date and time."""
        self.date_time = new_datetime

    def cancel(self) -> None:
        """Mark this appointment as cancelled."""
        self.cancelled = True

    def add_notes(self, text: str) -> None:
        """Append text to the appointment notes."""
        self.notes = (self.notes + "\n" + text).strip()


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """An animal under an owner's care."""

    name: str
    species: str
    owner_id: str
    breed: str = ""
    age: float = 0.0
    pet_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tasks: List[Task] = field(default_factory=list)
    appointments: List[Appointment] = field(default_factory=list)
    # Private index for O(1) task lookup by ID; kept in sync by add_task / complete_task
    _task_index: dict = field(default_factory=dict, repr=False, compare=False)

    def add_task(self, task: Task) -> None:
        """Attach a new care task to this pet."""
        self.tasks.append(task)
        self._task_index[task.task_id] = task

    def complete_task(self, task_id: str) -> None:
        """Mark the task with the given ID as complete."""
        task = self._task_index.get(task_id)
        if task:
            task.mark_complete()

    def schedule_appointment(self, appointment: Appointment) -> None:
        """Add a vet or grooming appointment for this pet."""
        self.appointments.append(appointment)

    def get_care_summary(self) -> dict:
        """Return a summary of upcoming tasks and appointments."""
        now = datetime.now()
        return {
            "pet": self.name,
            "incomplete_tasks": [t for t in self.tasks if not t.is_complete],
            "overdue_tasks": [t for t in self.tasks if t.is_overdue()],
            "upcoming_appointments": [
                a for a in self.appointments
                if not a.cancelled and a.date_time >= now
            ],
        }


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """A person responsible for one or more pets."""

    name: str
    email: str
    phone: str = ""
    owner_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pets: List[Pet] = field(default_factory=list)
    reminders: List[Reminder] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove the pet with the given ID from this owner's list."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def list_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return list(self.pets)

    def get_upcoming_tasks(self) -> List[Task]:
        """Aggregate and return all incomplete tasks across every owned pet."""
        return [t for pet in self.pets for t in pet.tasks if not t.is_complete]

    def add_reminder(self, reminder: Reminder) -> None:
        """Attach a reminder (for a task or appointment) to this owner."""
        self.reminders.append(reminder)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

@dataclass
class Scheduler:
    """
    Scheduling utilities for a single Owner's task list.

    Provides sorting, filtering, recurring-task automation,
    and lightweight conflict detection.
    """

    owner: Owner

    def all_tasks(self) -> List[Task]:
        """Collect every task from every pet owned by this owner."""
        tasks: List[Task] = []
        for pet in self.owner.pets:
            tasks.extend(pet.tasks)
        return tasks

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Return tasks sorted by due_date ascending.

        Uses a lambda key on the datetime attribute so Python's
        built-in timsort does the work in O(n log n).
        """
        if tasks is None:
            tasks = self.all_tasks()
        return sorted(tasks, key=lambda t: t.due_date)

    def filter_tasks(
        self,
        tasks: Optional[List[Task]] = None,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """
        Filter tasks by pet name and/or completion status.

        pet_name: case-insensitive match against Pet.name
        completed: True → only done tasks; False → only pending tasks; None → all
        """
        if tasks is None:
            tasks = self.all_tasks()

        if pet_name is not None:
            pet_ids = {
                p.pet_id
                for p in self.owner.pets
                if p.name.lower() == pet_name.lower()
            }
            tasks = [t for t in tasks if t.pet_id in pet_ids]

        if completed is not None:
            tasks = [t for t in tasks if t.is_complete == completed]

        return tasks

    def mark_task_complete(self, task: Task, pet: Pet) -> Optional[Task]:
        """
        Mark a task complete and auto-schedule the next occurrence.

        For "daily" recurrence the next due date is completed_at + 1 day.
        For "weekly" recurrence the next due date is completed_at + 7 days.
        Returns the newly created Task, or None for one-time tasks.
        """
        task.mark_complete()

        if task.recurrence is None:
            return None

        if task.recurrence == "daily":
            next_due = task.completed_at + timedelta(days=1)
        elif task.recurrence == "weekly":
            next_due = task.completed_at + timedelta(weeks=1)
        else:
            return None

        next_task = Task(
            title=task.title,
            pet_id=task.pet_id,
            due_date=next_due,
            description=task.description,
            recurrence=task.recurrence,
        )
        pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """
        Return a list of warning strings for tasks scheduled at the same moment.

        Checks for exact due_date equality among incomplete tasks.
        Returns warnings rather than raising exceptions so callers can
        decide how to surface them.
        """
        if tasks is None:
            tasks = self.all_tasks()

        incomplete = [t for t in tasks if not t.is_complete]
        seen: dict[datetime, Task] = {}
        warnings: List[str] = []

        for task in incomplete:
            if task.due_date in seen:
                other = seen[task.due_date]
                warnings.append(
                    f"⚠ Conflict: '{task.title}' and '{other.title}' are both "
                    f"scheduled for {task.due_date.strftime('%Y-%m-%d %H:%M')}"
                )
            else:
                seen[task.due_date] = task

        return warnings
