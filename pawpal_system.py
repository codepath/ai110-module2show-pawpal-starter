from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict
from enum import Enum


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def from_any(cls, value) -> "Priority":
        """Accept a Priority instance or a string like 'high' / 'HIGH'."""
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).lower())
        except ValueError:
            raise ValueError(f"Invalid priority {value!r}. Choose from: low, medium, high.")


# ---------------------------------------------------------------------------
# TimeWindow — reusable availability block
# ---------------------------------------------------------------------------

@dataclass
class TimeWindow:
    """A contiguous block of time within a single day."""
    start: time
    end: time

    def duration_minutes(self) -> int:
        """Return the length of this window in whole minutes."""
        dummy = date(2000, 1, 1)
        delta = datetime.combine(dummy, self.end) - datetime.combine(dummy, self.start)
        return int(delta.total_seconds() // 60)

    def contains(self, t: time) -> bool:
        """Return True if *t* falls within this window (inclusive)."""
        return self.start <= t <= self.end


# ---------------------------------------------------------------------------
# Task — a single pet-care activity
# ---------------------------------------------------------------------------

class Task:
    """
    Represents a single pet-care activity.

    Attributes
    ----------
    title           : Short name shown in the schedule.
    description     : Longer explanation of what the task involves.
    duration_minutes: How long the task takes (the "time" component).
    priority        : HIGH / MEDIUM / LOW — drives scheduling order.
    recurrence      : Frequency string, e.g. "daily", "weekly", "Mon/Wed/Fri".
                      None means one-off.
    completed       : Whether this task has been marked done today.
    earliest_start  : Earliest wall-clock time the task may begin.
    latest_end      : Deadline by which the task must finish.
    notes           : Any free-form extra info.
    required_pet_id : Pin this task to one specific pet (optional).
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        duration_minutes: int = 10,
        priority: Priority | str = Priority.MEDIUM,
        recurrence: Optional[str] = None,
        earliest_start: Optional[time] = None,
        latest_end: Optional[time] = None,
        notes: Optional[str] = None,
        required_pet_id: Optional[uuid.UUID] = None,
    ):
        self.id: uuid.UUID = uuid.uuid4()
        self.title = title
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = Priority.from_any(priority)
        self.recurrence = recurrence
        self.completed: bool = False
        self.earliest_start = earliest_start
        self.latest_end = latest_end
        self.notes = notes
        self.required_pet_id = required_pet_id
        self.next_due: Optional[date] = None   # set when a recurring task is completed

    # -- Status helpers ------------------------------------------------------

    def complete(self, today: Optional[date] = None) -> None:
        """Mark this task done and calculate the next due date for recurring tasks."""
        self.completed = True
        if self.recurrence and today:
            rec = self.recurrence.lower().strip()
            if rec == "daily":
                self.next_due = today + timedelta(days=1)
            elif rec == "weekly":
                self.next_due = today + timedelta(weeks=1)

    def reset(self) -> None:
        """Clear completion so the task can be scheduled again (e.g. next day)."""
        self.completed = False

    def is_recurring(self) -> bool:
        """Return True if the task repeats on a schedule."""
        return bool(self.recurrence)

    def spawn_next_occurrence(self) -> Optional["Task"]:
        """Return a fresh copy of this task reset for its next due date, or None if not recurring."""
        if not self.recurrence or not self.next_due:
            return None
        new_task = Task(
            title=self.title,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
            earliest_start=self.earliest_start,
            latest_end=self.latest_end,
            notes=self.notes,
            required_pet_id=self.required_pet_id,
        )
        new_task.next_due = self.next_due
        return new_task

    # -- Validation ----------------------------------------------------------

    def validate(self) -> bool:
        """Return False if the task has settings that make it unschedulable."""
        if self.duration_minutes <= 0:
            return False
        if self.earliest_start and self.latest_end and self.earliest_start >= self.latest_end:
            return False
        return True

    # -- Serialisation -------------------------------------------------------

    def to_dict(self) -> Dict:
        """Serialize this task to a JSON-compatible dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority.value,
            "recurrence": self.recurrence,
            "completed": self.completed,
            "next_due": self.next_due.isoformat() if self.next_due else None,
            "earliest_start": str(self.earliest_start) if self.earliest_start else None,
            "latest_end": str(self.latest_end) if self.latest_end else None,
            "notes": self.notes,
            "required_pet_id": str(self.required_pet_id) if self.required_pet_id else None,
        }

    def __repr__(self) -> str:
        """Return a compact string representation for debugging."""
        status = "done" if self.completed else "pending"
        return f"Task({self.title!r}, {self.priority.value}, {self.duration_minutes}min, {status})"


# ---------------------------------------------------------------------------
# Pet — stores pet details and owns a list of Tasks
# ---------------------------------------------------------------------------

class Pet:
    """
    Stores a pet's profile and the care tasks assigned to it.

    Responsibilities
    ----------------
    - Hold pet metadata (name, species, breed, age).
    - Maintain an ordered list of Tasks.
    - Provide filtered views: pending tasks, tasks by priority, etc.
    - Delegate completion/reset of individual tasks.
    """

    def __init__(
        self,
        name: str,
        species: str,
        breed: str = "",
        age_years: float = 0.0,
    ):
        self.id: uuid.UUID = uuid.uuid4()
        self.name = name
        self.species = species
        self.breed = breed
        self.age_years = age_years
        self._tasks: List[Task] = []

    # -- Task management -----------------------------------------------------

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet. Sets required_pet_id automatically."""
        task.required_pet_id = self.id
        self._tasks.append(task)

    def remove_task(self, task_id: uuid.UUID) -> bool:
        """Remove a task by ID. Returns True if found and removed."""
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        return len(self._tasks) < before

    def get_task(self, task_id: uuid.UUID) -> Optional[Task]:
        """Return a single task by ID, or None."""
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None

    # -- Filtered views ------------------------------------------------------

    def get_tasks(self) -> List[Task]:
        """All tasks assigned to this pet."""
        return list(self._tasks)

    def get_pending_tasks(self) -> List[Task]:
        """Tasks that have not been completed yet."""
        return [t for t in self._tasks if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Tasks already marked done."""
        return [t for t in self._tasks if t.completed]

    def get_tasks_by_priority(self, priority: Priority | str) -> List[Task]:
        """All tasks matching the given priority level."""
        p = Priority.from_any(priority)
        return [t for t in self._tasks if t.priority == p]

    def get_recurring_tasks(self) -> List[Task]:
        """Tasks that repeat on a schedule."""
        return [t for t in self._tasks if t.is_recurring()]

    # -- Completion helpers --------------------------------------------------

    def complete_task(self, task_id: uuid.UUID, today: Optional[date] = None) -> bool:
        """Mark a task done by ID; if recurring, add the next occurrence. Returns True if found."""
        task = self.get_task(task_id)
        if not task:
            return False
        task.complete(today or date.today())
        next_task = task.spawn_next_occurrence()
        if next_task:
            self._tasks.append(next_task)
        return True

    def reset_all_tasks(self) -> None:
        """Clear completion flags (call at the start of each new day)."""
        for t in self._tasks:
            t.reset()

    # -- Serialisation -------------------------------------------------------

    def to_dict(self) -> Dict:
        """Serialize this pet and all its tasks to a JSON-compatible dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age_years": self.age_years,
            "tasks": [t.to_dict() for t in self._tasks],
        }

    def __repr__(self) -> str:
        """Return a compact string representation for debugging."""
        return f"Pet({self.name!r}, {self.species}, {len(self._tasks)} tasks)"


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and provides a unified view of all tasks
# ---------------------------------------------------------------------------

class Owner:
    """
    Manages a collection of pets and provides cross-pet task access.

    Responsibilities
    ----------------
    - Hold owner profile info (name, contact).
    - Maintain an ordered list of Pets.
    - Expose aggregated task views across all pets.
    - Store availability windows used by the Scheduler.
    """

    def __init__(
        self,
        name: str,
        contact: str = "",
        availability_windows: Optional[List[TimeWindow]] = None,
    ):
        self.id: uuid.UUID = uuid.uuid4()
        self.name = name
        self.contact = contact
        self.availability_windows: List[TimeWindow] = availability_windows or [
            TimeWindow(time(7, 0), time(21, 0))
        ]
        self._pets: List[Pet] = []

    # -- Pet management ------------------------------------------------------

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self._pets.append(pet)

    def remove_pet(self, pet_id: uuid.UUID) -> bool:
        """Remove a pet by ID. Returns True if found and removed."""
        before = len(self._pets)
        self._pets = [p for p in self._pets if p.id != pet_id]
        return len(self._pets) < before

    def get_pet(self, pet_id: uuid.UUID) -> Optional[Pet]:
        """Return a pet by ID, or None."""
        for p in self._pets:
            if p.id == pet_id:
                return p
        return None

    def get_pets(self) -> List[Pet]:
        """All pets belonging to this owner."""
        return list(self._pets)

    # -- Cross-pet task views ------------------------------------------------

    def all_tasks(self) -> List[Task]:
        """Every task across all pets."""
        tasks = []
        for pet in self._pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def all_pending_tasks(self) -> List[Task]:
        """All incomplete tasks across all pets."""
        tasks = []
        for pet in self._pets:
            tasks.extend(pet.get_pending_tasks())
        return tasks

    def all_tasks_for_pet(self, pet_id: uuid.UUID) -> List[Task]:
        """All tasks belonging to one specific pet."""
        pet = self.get_pet(pet_id)
        return pet.get_tasks() if pet else []

    def tasks_by_priority(self, priority: Priority | str) -> List[Task]:
        """Tasks at a given priority level, across all pets."""
        p = Priority.from_any(priority)
        return [t for t in self.all_tasks() if t.priority == p]

    # -- Day-reset -----------------------------------------------------------

    def start_new_day(self) -> None:
        """Reset completion flags on all tasks for every pet."""
        for pet in self._pets:
            pet.reset_all_tasks()

    # -- Serialisation -------------------------------------------------------

    def to_dict(self) -> Dict:
        """Serialize this owner, their windows, and all pets to a JSON-compatible dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "contact": self.contact,
            "availability_windows": [
                {"start": str(w.start), "end": str(w.end)}
                for w in self.availability_windows
            ],
            "pets": [p.to_dict() for p in self._pets],
        }

    def __repr__(self) -> str:
        """Return a compact string representation for debugging."""
        return f"Owner({self.name!r}, {len(self._pets)} pets)"


# ---------------------------------------------------------------------------
# TaskInstance — a scheduled slot produced by the Scheduler
# ---------------------------------------------------------------------------

@dataclass
class TaskInstance:
    """A scheduled occurrence of a Task for a specific day/time."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    task_id: Optional[uuid.UUID] = None
    title: str = ""
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    status: str = "scheduled"   # scheduled | completed | skipped
    reason: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None
    pet_id: Optional[uuid.UUID] = None

    def duration(self) -> int:
        """Return the length of this slot in whole minutes, or 0 if times are unset."""
        if self.start and self.end:
            return int((self.end - self.start).total_seconds() // 60)
        return 0

    def mark_completed(self) -> None:
        """Set this slot's status to 'completed'."""
        self.status = "completed"

    def to_dict(self) -> Dict:
        """Serialize this scheduled slot to a JSON-compatible dictionary."""
        return {
            "id": str(self.id),
            "task_id": str(self.task_id) if self.task_id else None,
            "title": self.title,
            "start": self.start.isoformat() if self.start else None,
            "end": self.end.isoformat() if self.end else None,
            "status": self.status,
            "reason": self.reason,
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "pet_id": str(self.pet_id) if self.pet_id else None,
        }


# ---------------------------------------------------------------------------
# Schedule — top-level day-plan container
# ---------------------------------------------------------------------------

@dataclass
class Schedule:
    """The output of a scheduling run: an ordered list of TaskInstances."""
    date: date
    owner_id: uuid.UUID
    pet_id: Optional[uuid.UUID] = None
    slots: List[TaskInstance] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    total_minutes_scheduled: int = 0
    generated_by: str = "Scheduler"

    def to_dict(self) -> Dict:
        """Serialize the full schedule (slots + skipped) to a JSON-compatible dictionary."""
        return {
            "date": self.date.isoformat(),
            "owner_id": str(self.owner_id),
            "pet_id": str(self.pet_id) if self.pet_id else None,
            "total_minutes_scheduled": self.total_minutes_scheduled,
            "generated_by": self.generated_by,
            "slots": [s.to_dict() for s in self.slots],
            "skipped_tasks": [t.to_dict() for t in self.skipped_tasks],
        }

    def persist(self) -> str:
        """Return a JSON string ready to save or pass to the UI."""
        return json.dumps(self.to_dict(), indent=2)

    def summary(self) -> str:
        """Human-readable one-paragraph summary of the day's plan."""
        lines = [f"Schedule for {self.date} ({len(self.slots)} tasks, {self.total_minutes_scheduled} min):"]
        for s in self.slots:
            start = s.start.strftime("%H:%M") if s.start else "?"
            end = s.end.strftime("%H:%M") if s.end else "?"
            lines.append(f"  {start}–{end}  {s.title}")
        if self.skipped_tasks:
            lines.append(f"  Skipped: {', '.join(t.title for t in self.skipped_tasks)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler — the "Brain"
# ---------------------------------------------------------------------------

class Scheduler:
    """
    The brain of PawPal+.

    Responsibilities
    ----------------
    - Retrieve tasks from an Owner (across all pets or per pet).
    - Organise tasks by priority, deadline, or pet.
    - Generate a daily Schedule using a greedy, priority-first algorithm.
    - Mark tasks complete and propagate status back to Pet/Task objects.
    - Provide summary and diagnostic views.

    Usage
    -----
        scheduler = Scheduler()
        schedule  = scheduler.generate_daily_plan(owner, date.today())
        print(schedule.summary())
    """

    def __init__(self, max_daily_minutes: Optional[int] = None):
        self.max_daily_minutes = max_daily_minutes

    # -- Retrieval -----------------------------------------------------------

    def get_all_tasks(self, owner: Owner) -> List[Task]:
        """Return every task across all of the owner's pets."""
        return owner.all_tasks()

    def get_pending_tasks(self, owner: Owner) -> List[Task]:
        """Return only incomplete tasks across all pets."""
        return owner.all_pending_tasks()

    def get_tasks_by_priority(self, owner: Owner, priority: Priority | str) -> List[Task]:
        """Return all tasks at a given priority level across all pets."""
        return owner.tasks_by_priority(priority)

    def get_tasks_for_pet(self, owner: Owner, pet_id: uuid.UUID) -> List[Task]:
        """Return all tasks belonging to one specific pet."""
        return owner.all_tasks_for_pet(pet_id)

    # -- Organisation --------------------------------------------------------

    def sorted_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks HIGH → MEDIUM → LOW, shorter duration first within each tier."""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: (order[t.priority], t.duration_minutes))

    def group_by_pet(self, owner: Owner) -> Dict[str, List[Task]]:
        """Return {pet_name: [tasks]} for easy display."""
        return {pet.name: pet.get_tasks() for pet in owner.get_pets()}

    def group_by_priority(self, owner: Owner) -> Dict[str, List[Task]]:
        """Return {'high': [...], 'medium': [...], 'low': [...]}."""
        return {
            p.value: owner.tasks_by_priority(p)
            for p in Priority
        }

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by earliest_start time using a lambda key; tasks with no start time go last."""
        return sorted(
            tasks,
            key=lambda t: (t.earliest_start is None, t.earliest_start or time(0, 0))
        )

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Return tasks filtered by pet name and/or completion status; pass None to skip a filter."""
        results = []
        for pet in owner.get_pets():
            if pet_name and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.get_tasks():
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def detect_conflicts(self, schedule: "Schedule") -> List[str]:
        """Check scheduled slots for time overlaps and return a list of warning strings."""
        warnings = []
        slots = schedule.slots
        for i in range(len(slots)):
            for j in range(i + 1, len(slots)):
                a, b = slots[i], slots[j]
                if a.start and a.end and b.start and b.end:
                    overlap_start = max(a.start, b.start)
                    overlap_end   = min(a.end,   b.end)
                    if overlap_start < overlap_end:
                        warnings.append(
                            f"CONFLICT: '{a.title}' ({a.start.strftime('%H:%M')}–{a.end.strftime('%H:%M')}) "
                            f"overlaps '{b.title}' ({b.start.strftime('%H:%M')}–{b.end.strftime('%H:%M')})"
                        )
        return warnings

    # -- Scheduling ----------------------------------------------------------

    def generate_daily_plan(self, owner: Owner, target_date: date) -> Schedule:
        """
        Build a Schedule for *target_date* using the owner's pending tasks
        and availability windows.

        Algorithm
        ---------
        1. Collect all pending (incomplete) tasks from all pets.
        2. Sort by priority then duration.
        3. Iterate over each availability window in order.
        4. Greedily place tasks that fit; pass remaining to the next window.
        5. Return a Schedule with placed slots and skipped tasks.
        """
        pending = self.sorted_by_priority(owner.all_pending_tasks())
        valid   = [t for t in pending if t.validate()]
        skipped = [t for t in pending if not t.validate()]

        scheduled: List[TaskInstance] = []
        total_minutes = 0
        remaining = list(valid)

        for window in owner.availability_windows:
            win_start = datetime.combine(target_date, window.start)
            win_end   = datetime.combine(target_date, window.end)
            cursor    = win_start
            still_remaining: List[Task] = []

            for task in remaining:
                result = self._try_place(task, cursor, win_start, win_end, target_date, total_minutes)
                if result is None:
                    still_remaining.append(task)
                    continue

                slot_start, slot_end = result
                reason = (
                    f"priority={task.priority.value}; "
                    f"window={window.start.strftime('%H:%M')}-{window.end.strftime('%H:%M')}; "
                    f"placed at {slot_start.time().strftime('%H:%M')}."
                )
                ti = TaskInstance(
                    task_id=task.id,
                    title=task.title,
                    start=slot_start,
                    end=slot_end,
                    reason=reason,
                    owner_id=owner.id,
                    pet_id=task.required_pet_id,
                )
                scheduled.append(ti)
                cursor = slot_end
                total_minutes += task.duration_minutes

            remaining = still_remaining

        skipped.extend(remaining)

        return Schedule(
            date=target_date,
            owner_id=owner.id,
            slots=scheduled,
            skipped_tasks=skipped,
            total_minutes_scheduled=total_minutes,
            generated_by="Scheduler",
        )

    # -- Task management -----------------------------------------------------

    def complete_task(self, owner: Owner, pet_id: uuid.UUID, task_id: uuid.UUID) -> bool:
        """
        Mark a task done on the Pet object so it won't appear in the next
        pending-task query. Returns True if the task was found.
        """
        pet = owner.get_pet(pet_id)
        if pet:
            return pet.complete_task(task_id)
        return False

    def complete_slot(self, schedule: Schedule, slot_id: uuid.UUID, owner: Owner) -> bool:
        """
        Mark a TaskInstance as completed in the schedule AND propagate the
        completion back to the underlying Task on the Pet.
        """
        for slot in schedule.slots:
            if slot.id == slot_id:
                slot.mark_completed()
                if slot.pet_id and slot.task_id:
                    self.complete_task(owner, slot.pet_id, slot.task_id)
                return True
        return False

    def start_new_day(self, owner: Owner) -> None:
        """Reset all task completion flags across all pets for a fresh day."""
        owner.start_new_day()

    # -- Summary / diagnostics -----------------------------------------------

    def summary(self, owner: Owner) -> str:
        """Print a quick overview of the owner's pets and task counts."""
        lines = [f"=== {owner.name}'s PawPal+ Summary ==="]
        for pet in owner.get_pets():
            pending   = len(pet.get_pending_tasks())
            completed = len(pet.get_completed_tasks())
            lines.append(f"  {pet.name} ({pet.species}): {pending} pending, {completed} done")
            for t in pet.get_tasks():
                tick = "✓" if t.completed else "○"
                lines.append(f"    {tick} [{t.priority.value}] {t.title} ({t.duration_minutes}min)")
        return "\n".join(lines)

    # -- Internal helpers ----------------------------------------------------

    def _try_place(
        self,
        task: Task,
        cursor: datetime,
        win_start: datetime,
        win_end: datetime,
        target_date: date,
        total_minutes: int,
    ) -> Optional[tuple]:
        """Return (slot_start, slot_end) if the task fits, else None."""
        earliest = (
            datetime.combine(target_date, task.earliest_start)
            if task.earliest_start else cursor
        )
        slot_start = max(cursor, earliest)
        slot_end   = slot_start + timedelta(minutes=task.duration_minutes)

        if task.latest_end:
            latest_dt = datetime.combine(target_date, task.latest_end)
            if slot_end > latest_dt:
                earliest_dt = datetime.combine(target_date, task.earliest_start) if task.earliest_start else win_start
                alt_start   = latest_dt - timedelta(minutes=task.duration_minutes)
                if alt_start >= cursor and alt_start >= earliest_dt:
                    slot_start = alt_start
                    slot_end   = slot_start + timedelta(minutes=task.duration_minutes)
                else:
                    return None

        if slot_start < win_start or slot_end > win_end:
            return None
        if self.max_daily_minutes is not None and (total_minutes + task.duration_minutes) > self.max_daily_minutes:
            return None
        return slot_start, slot_end


# ---------------------------------------------------------------------------
# Notification / Notifications (unchanged)
# ---------------------------------------------------------------------------

@dataclass
class Notification:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    task_instance_id: Optional[uuid.UUID] = None
    notify_time: Optional[datetime] = None
    channel: str = "local"   # local | email | push
    message: Optional[str] = None
    sent: bool = False

    def send(self) -> Dict:
        """Mark this notification as sent and return a status dict."""
        self.sent = True
        return {"id": str(self.id), "sent": True, "channel": self.channel}


class Notifications:
    """Queue and dispatch reminders derived from a day's Schedule."""

    def __init__(self):
        self._queue: List[Notification] = []

    def schedule_for_plan(
        self, schedule: Schedule, lead_minutes: int = 10, channel: str = "local"
    ) -> List[Notification]:
        """Build a notification for each slot, firing *lead_minutes* before it starts."""
        self._queue = []
        for inst in schedule.slots:
            if not inst.start:
                continue
            notify_at = inst.start - timedelta(minutes=lead_minutes)
            msg = f"Upcoming: {inst.title} at {inst.start.time().strftime('%H:%M')}"
            self._queue.append(
                Notification(task_instance_id=inst.id, notify_time=notify_at, channel=channel, message=msg)
            )
        return self._queue

    def send_all(self) -> List[Dict]:
        """Send every queued notification and return their status dicts."""
        return [n.send() for n in self._queue]

    def pending(self) -> List[Dict]:
        """Return serialized dicts for all notifications not yet sent."""
        return [
            {
                "id": str(n.id),
                "task_instance_id": str(n.task_instance_id),
                "notify_time": n.notify_time.isoformat() if n.notify_time else None,
                "channel": n.channel,
                "sent": n.sent,
            }
            for n in self._queue
            if not n.sent
        ]
