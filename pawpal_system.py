from typing import List, Optional, TypedDict, Union
from datetime import date, timedelta
import json
import os
import uuid


class TaskDict(TypedDict):
    """Type definition for Task dictionary representation.
    Converts object attributes to a dictionary format for serialization and storage. (for saving to JSON/file)
    due_time is stored as an ISO string (e.g. '2025-04-01') so it survives JSON round-trips.
    start_time is stored in minutes from midnight (e.g. 9*60 = 540 for 9:00 AM).
    task_id is a UUID string that uniquely identifies this task instance across all pets and sessions.
    """
    task_id: str           # UUID4 string — unique per Task instance
    name: str
    duration: int
    priority: int
    due_time: Optional[str]       # ISO date string — must be parsed back to date on load
    start_time: Optional[int]     # minutes from midnight; set by Scheduler.generate_schedule
    preferred_time: Optional[int] # minutes from midnight; owner's preferred start time
    pet_name: Optional[str]       # which pet this task belongs to; preserves context after flat scheduling
    recurring: bool
    recurrence_interval: Optional[str]  # "daily", "weekly", or None
    completed: bool
    notes: List[str]


class PetDict(TypedDict):
    """Type definition for Pet dictionary representation."""
    name: str
    species: str
    tasks: List[TaskDict]
    notes: List[str]


class OwnerDict(TypedDict):
    """Type definition for Owner dictionary representation."""
    name: str
    pets: List[PetDict]
    notes: List[str]


class Task:
    """Represents a pet care task with scheduling information.
    Converts dictionary data to an object-oriented format for easier manipulation and access. (for loading from JSON/file)
    Attributes:
        name: Name of the task (e.g., 'Feed dog', 'Walk cat')
        duration: How long the task takes in minutes
        priority: Task priority level (higher = more important)
        due_time: Date the task is due
        recurring: Whether the task repeats regularly
        notes: Additional notes about the task
    """
    task_id: str
    name: str
    duration: int
    priority: int
    due_time: Optional[date]
    start_time: Optional[int]      # minutes from midnight; assigned by Scheduler
    preferred_time: Optional[int]  # minutes from midnight; owner's preferred start time
    pet_name: Optional[str]        # set when task is added to a Pet; used by Scheduler output
    recurring: bool
    completed: bool
    notes: List[str]

    def __init__(
        self,
        name: str,
        duration: int,
        priority: int,
        due_time: Optional[date] = None,
        recurring: bool = False,
        recurrence_interval: Optional[str] = None,
        start_time: Optional[int] = None,
        preferred_time: Optional[int] = None,
        pet_name: Optional[str] = None,
        notes: List[str] = [],
        task_id: Optional[str] = None,
    ) -> None:
        """Initialize a new Task with scheduling and metadata fields."""
        self.task_id = task_id or str(uuid.uuid4())
        self.name = name
        self.duration = duration
        self.completed = False
        self.priority = priority
        self.due_time = due_time
        self.recurring = recurring
        self.recurrence_interval = recurrence_interval  # "daily", "weekly", or None
        self.start_time = start_time
        self.preferred_time = preferred_time
        self.pet_name = pet_name
        self.notes = list(notes)

    def is_due(self, target_date: Optional[date] = None) -> bool:
        """Check if task is due on a given date (defaults to today).

        Args:
            target_date: Date to check against. Defaults to date.today().

        Returns:
            True if task's due_time matches target_date, False otherwise.
        """
        if target_date is None:
            target_date = date.today()
        return self.due_time == target_date

    def is_due_today(self) -> bool:
        """Check if task is due today.

        Returns:
            True if task's due_time is today, False otherwise.
        """
        return self.is_due()

    def _recurrence_days(self) -> int:
        """Return the number of days between this task's recurrences.

        Maps the recurrence_interval string to a day count:
          - "weekly" → 7 days
          - "daily" (or any other value) → 1 day

        Used by both mark_complete and advance_recurrence so the
        interval logic lives in exactly one place.

        Returns:
            Number of days as an int (7 for weekly, 1 for daily).
        """
        return 7 if self.recurrence_interval == "weekly" else 1

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and, if recurring, create the next occurrence.

        Returns:
            A new Task for the next occurrence if recurring (daily or weekly), else None.
        """
        self.completed = True
        if not self.recurring or self.recurrence_interval not in ("daily", "weekly"):
            return None
        next_due = date.today() + timedelta(days=self._recurrence_days())
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            due_time=next_due,
            recurring=self.recurring,
            recurrence_interval=self.recurrence_interval,
            preferred_time=self.preferred_time,
            pet_name=self.pet_name,
            notes=list(self.notes),
        )

    def advance_recurrence(self) -> None:
        """Advance a recurring task to its next due date and reset for the new cycle.

        Does nothing if the task is not recurring or has no due_time.
        """
        if not self.recurring or self.due_time is None:
            return
        self.due_time += timedelta(days=self._recurrence_days())
        self.completed = False
        self.start_time = None

    def add_note(self, note: str) -> None:
        """Add a note to the task.

        Args:
            note: The note text to add.
        """
        self.notes.append(note)

    def get_notes(self) -> List[str]:
        """Retrieve all notes for this task.

        Returns:
            List of note strings.
        """
        return self.notes

    def to_dict(self) -> TaskDict:
        """Convert task to dictionary representation.

        Returns:
            Dictionary containing all task data.
        """
        return {
            "task_id": self.task_id,
            "name": self.name,
            "duration": self.duration,
            "priority": self.priority,
            "due_time": self.due_time.isoformat() if self.due_time is not None else None,
            "start_time": self.start_time,
            "preferred_time": self.preferred_time,
            "pet_name": self.pet_name,
            "recurring": self.recurring,
            "recurrence_interval": self.recurrence_interval,
            "completed": self.completed,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "Task":
        """Create Task instance from dictionary data.

        Args:
            data: Dictionary containing task data.

        Returns:
            New Task instance populated with data from dict.

        Raises:
            KeyError: If required fields are missing from data dict.
            ValueError: If data types are invalid.
        """
        due_time_raw = data.get("due_time")
        due_time = date.fromisoformat(due_time_raw) if due_time_raw is not None else None
        task = Task(
            name=data["name"],
            duration=data["duration"],
            priority=data["priority"],
            due_time=due_time,
            recurring=data.get("recurring", False),
            recurrence_interval=data.get("recurrence_interval"),
            start_time=data.get("start_time"),
            preferred_time=data.get("preferred_time"),
            pet_name=data.get("pet_name"),
            notes=data.get("notes", []),
            task_id=data.get("task_id"),  # None → new UUID generated in __init__
        )
        task.completed = data.get("completed", False)
        return task

    def __str__(self) -> str:
        """Return string representation of task."""
        pet = f" [{self.pet_name}]" if self.pet_name else ""
        return f"{self.name}{pet} ({self.duration} min, priority {self.priority})"


class Pet:
    """Represents a pet with associated tasks and notes.

    Attributes:
        name: Pet's name
        species: Pet's species (e.g., 'dog', 'cat', 'bird')
        tasks: List of tasks associated with this pet
        notes: Additional notes about the pet
    """
    name: str
    species: str
    tasks: List[Task]
    notes: List[str]

    def __init__(self, name: str, species: str) -> None:
        """Initialize a new Pet with an empty task and notes list."""
        self.name = name
        self.species = species
        self.tasks = []
        self.notes = []

    def add_task(self, task: Task) -> None:
        """Add a task for this pet. Also sets task.pet_name to this pet's name
        so the task carries its owner context when passed to Scheduler.

        Silently skips adding a recurring task if one with the same name already exists
        for this pet, preventing duplicates on repeated session loads.

        Args:
            task: Task instance to add.
        """
        if task.recurring:
            for existing in self.tasks:
                if existing.name == task.name and existing.recurring and not existing.completed:
                    return
        self.tasks.append(task)
        task.pet_name = self.name

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name.

        Args:
            task_name: Name of the task to remove.

        Raises:
            ValueError: If no task with that name exists.
        """
        for task in self.tasks:
            if task.name == task_name:
                self.tasks.remove(task)
                return
        raise ValueError(f"No task named '{task_name}' found.")

    def update_task(self, task_name: str, updated_task: Task) -> None:
        """Replace an existing task with an updated version.

        Args:
            task_name: Name of the task to replace.
            updated_task: New Task instance to substitute in.

        Raises:
            ValueError: If no task with that name exists.
        """
        for i, task in enumerate(self.tasks):
            if task.name == task_name:
                self.tasks[i] = updated_task
                return
        raise ValueError(f"No task named '{task_name}' found.")

    def get_today_tasks(self, include_completed: bool = False) -> List[Task]:
        """Return only tasks that are due today and not yet completed.

        Args:
            include_completed: If True, also return already-completed tasks.

        Returns:
            List of Task instances where is_due_today() is True (and not completed by default).
        """
        return [
            t for t in self.tasks
            if t.is_due_today() and (include_completed or not t.completed)
        ]

    def get_tasks(self) -> List[Task]:
        """Retrieve all tasks for this pet.

        Returns:
            List of Task instances.
        """
        return self.tasks

    def add_note(self, note: str) -> None:
        """Add a note about this pet.

        Args:
            note: The note text to add.
        """
        self.notes.append(note)

    def get_notes(self) -> List[str]:
        """Retrieve all notes for this pet.

        Returns:
            List of note strings.
        """
        return self.notes

    def to_dict(self) -> PetDict:
        """Convert pet to dictionary representation.

        Returns:
            Dictionary containing all pet data.
        """
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [task.to_dict() for task in self.tasks],
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "Pet":
        """Create Pet instance from dictionary data.

        Args:
            data: Dictionary containing pet data.

        Returns:
            New Pet instance populated with data from dict.

        Raises:
            KeyError: If required fields are missing from data dict.
            ValueError: If data types are invalid.
        """
        pet = Pet(name=data["name"], species=data["species"])
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        pet.notes = data.get("notes", [])
        return pet


class Owner:
    """Represents a pet owner with their pets and notes.

    Attributes:
        name: Owner's name
        pets: List of Pet instances owned by this owner
        notes: Additional notes about the owner
    """
    name: str
    pets: List[Pet]
    notes: List[str]

    def __init__(self, name: str) -> None:
        """Initialize a new Owner with an empty pets and notes list."""
        self.name = name
        self.pets = []
        self.notes = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection.

        Args:
            pet: Pet instance to add.
        """
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Retrieve all pets owned by this owner.

        Returns:
            List of Pet instances.
        """
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks across all pets owned by this owner.

        Returns:
            Flat list of all Task instances from all pets.
        """
        return [t for pet in self.pets for t in pet.get_tasks()]

    def get_today_tasks(self, include_completed: bool = False) -> List[Task]:
        """Retrieve all tasks due today across all pets.

        Args:
            include_completed: If True, also return already-completed tasks.

        Returns:
            Flat list of Task instances due today across all pets.
        """
        return [
            t
            for pet in self.pets
            for t in pet.get_today_tasks(include_completed=include_completed)
        ]

    def get_tasks_filtered(
        self,
        pet_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List["Task"]:
        """Return tasks filtered by pet and/or completion status.

        Args:
            pet_name: Only return tasks belonging to this pet. None = all pets.
            status: "completed", "incomplete", or None (return all).

        Returns:
            Flat list of matching Task instances across all pets.
        """
        tasks = self.get_all_tasks()
        if pet_name:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if status == "completed":
            tasks = [t for t in tasks if t.completed]
        elif status == "incomplete":
            tasks = [t for t in tasks if not t.completed]
        return tasks

    def add_note(self, note: str) -> None:
        """Add a note about this owner.

        Args:
            note: The note text to add.
        """
        self.notes.append(note)

    def get_notes(self) -> List[str]:
        """Retrieve all notes for this owner.

        Returns:
            List of note strings.
        """
        return self.notes

    def to_dict(self) -> OwnerDict:
        """Convert owner to dictionary representation.

        Returns:
            Dictionary containing all owner data and their pets.
        """
        return {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "Owner":
        """Create Owner instance from dictionary data.

        Args:
            data: Dictionary containing owner data.

        Returns:
            New Owner instance populated with data from dict, including all pets.

        Raises:
            KeyError: If required fields are missing from data dict.
            ValueError: If data types are invalid.
        """
        owner = Owner(name=data["name"])
        owner.pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        owner.notes = data.get("notes", [])
        return owner


class ScheduleResult(TypedDict):
    """Return type for Scheduler.generate_schedule.
    Separates tasks that fit in available time from those that were dropped,
    so callers can show the user what got left out instead of raising an exception.
    """
    scheduled: List[TaskDict]   # tasks that fit, each with start_time assigned (minutes from midnight)
    dropped: List[TaskDict]     # tasks that could not fit in available_times


class Scheduler:
    """Manages pet task scheduling and conflict detection.

    Attributes:
        available_times: List of available time slots (in minutes) for scheduling.
    """
    available_times: List[int]

    def __init__(self, available_times: Union[int, List[int]], buffer_minutes: int = 10) -> None:
        """Initialize a Scheduler.

        Args:
            available_times: Either a single time (int) or [start, end] window in minutes from midnight.
            buffer_minutes: Gap inserted between consecutive tasks (default 10 min).
        """
        if isinstance(available_times, int):
            self.available_times = [available_times]
        else:
            self.available_times = sorted(available_times)
        self.buffer_minutes = buffer_minutes

    def generate_schedule(self, tasks: List[Task]) -> ScheduleResult:
        """Generate an optimal schedule for the given tasks.

        Assigns a start_time (minutes from midnight) to each task that fits within
        available_times. Tasks that do not fit are returned in 'dropped' rather than
        raising — the caller can inform the user which tasks were left out.

        Tasks preserve their pet_name so the output stays linked to each pet.

        Args:
            tasks: List of tasks to schedule (typically from Owner.get_today_tasks()).

        Returns:
            ScheduleResult with 'scheduled' (tasks with start_time assigned) and
            'dropped' (tasks that could not fit in available time).
        """
        if not self.available_times:
            return {"scheduled": [], "dropped": [t.to_dict() for t in tasks]}

        remaining = self.sort_tasks_by_priority(tasks)
        current_time = self.available_times[0]
        max_end = self.available_times[-1]   # tasks must FINISH by this time

        scheduled = []

        while remaining:
            # Pick the highest-priority task that still fits in the window
            fitted = next(
                (t for t in remaining if current_time + t.duration <= max_end),
                None,
            )
            if fitted is None:
                break  # nothing left fits; all remaining go to dropped
            remaining.remove(fitted)

            # Honor preferred_time if it's still reachable and fits before the window ends
            if (
                fitted.preferred_time is not None
                and fitted.preferred_time >= current_time
                and fitted.preferred_time + fitted.duration <= max_end
            ):
                fitted.start_time = fitted.preferred_time
            else:
                fitted.start_time = current_time

            current_time = fitted.start_time + fitted.duration + self.buffer_minutes
            scheduled.append(fitted.to_dict())

        dropped = [t.to_dict() for t in remaining]
        return {"scheduled": scheduled, "dropped": dropped}

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by due date ascending, then by start time ascending.

        Tasks with no due_time sort last; tasks with no start_time sort after
        those that have one.

        Args:
            tasks: List of tasks to sort.

        Returns:
            New list sorted chronologically.
        """
        return sorted(
            tasks,
            key=lambda t: (
                t.due_time or date.max,
                t.start_time if t.start_time is not None else float("inf"),
            ),
        )

    def filter_tasks(
        self,
        tasks: List[Task],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Filter a list of tasks by pet name and/or completion status.

        Args:
            tasks: List of Task instances to filter.
            pet_name: If provided, only return tasks whose pet_name matches.
            completed: If True, return only completed tasks.
                       If False, return only incomplete tasks.
                       If None, return all regardless of completion status.

        Returns:
            New list containing only the tasks that match every supplied filter.
        """
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (highest priority first).

        Args:
            tasks: List of tasks to sort.

        Returns:
            New list of tasks sorted by priority in descending order.
        """
        return sorted(tasks, key=lambda t: (t.priority, t.is_due_today()), reverse=True)

    @staticmethod
    def _fmt_time(minutes: int) -> str:
        """Format minutes-from-midnight as a human-readable 12-hour clock string."""
        h, m = divmod(minutes, 60)
        period = "AM" if h < 12 else "PM"
        h = h % 12 or 12
        return f"{h}:{m:02d} {period}"

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Detect overlapping scheduled tasks and return warning messages.

        Lightweight strategy: sort tasks by start_time, then check every pair
        (i, j) where j > i.  Because the list is sorted, once task j starts at
        or after task i ends we can stop checking further j values for task i.
        Works for same-pet and cross-pet conflicts alike — no crash, just warnings.

        Requires tasks to already have start_time set (i.e. call generate_schedule
        first, or set start_time manually for testing).  Tasks with start_time=None
        are skipped.

        Args:
            tasks: List of tasks to check; each should have start_time and duration set.

        Returns:
            List of human-readable warning strings, one per overlapping pair.
            An empty list means no conflicts.
        """
        timed = [t for t in tasks if t.start_time is not None]
        timed.sort(key=lambda t: t.start_time)

        warnings = []
        for i in range(len(timed)):
            a = timed[i]
            for j in range(i + 1, len(timed)):
                b = timed[j]
                if a.start_time + a.duration <= b.start_time:
                    break  # sorted order — no later task can overlap a either
                a_pet = f"[{a.pet_name}]" if a.pet_name else ""
                b_pet = f"[{b.pet_name}]" if b.pet_name else ""
                warnings.append(
                    f"WARNING: '{a.name}' {a_pet} "
                    f"({self._fmt_time(a.start_time)}, {a.duration} min) "
                    f"overlaps with '{b.name}' {b_pet} "
                    f"({self._fmt_time(b.start_time)}, {b.duration} min)"
                )
        return warnings


class OwnerRepository:
    """Manages persistence of Owner data.

    Responsible for saving and loading Owner instances to/from files.

    Attributes:
        file_path: Path to the file where owner data is stored.
    """
    file_path: str

    def __init__(self, file_path: str = "owner.json") -> None:
        """Initialize the repository with a file path.

        Args:
            file_path: Path where owner data should be saved/loaded. Defaults to 'owner.json'.
        """
        self.file_path = file_path

    def save(self, owner: Owner) -> None:
        """Save an owner to file.

        Args:
            owner: Owner instance to save.

        Raises:
            IOError: If file cannot be written.
            ValueError: If owner data cannot be serialized.
        """
        with open(self.file_path, "w") as f:
            json.dump(owner.to_dict(), f, indent=2)

    def load(self) -> Optional[Owner]:
        """Load an owner from file.

        Returns:
            Owner instance if file exists and is valid, None otherwise.

        Raises:
            IOError: If file exists but cannot be read.
            ValueError: If file data is corrupted or invalid format.
        """
        if not os.path.exists(self.file_path):
            return None
        with open(self.file_path, "r") as f:
            data = json.load(f)
        return Owner.from_dict(data)
