from typing import List, Optional, TypedDict, Union
from datetime import date
import json
import os


class TaskDict(TypedDict):
    """Type definition for Task dictionary representation.
    Converts object attributes to a dictionary format for serialization and storage. (for saving to JSON/file)
    due_time is stored as an ISO string (e.g. '2025-04-01') so it survives JSON round-trips.
    start_time is stored in minutes from midnight (e.g. 9*60 = 540 for 9:00 AM).
    """
    name: str
    duration: int
    priority: int
    due_time: Optional[str]       # ISO date string — must be parsed back to date on load
    start_time: Optional[int]     # minutes from midnight; set by Scheduler.generate_schedule
    pet_name: Optional[str]       # which pet this task belongs to; preserves context after flat scheduling
    recurring: bool
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
    name: str
    duration: int
    priority: int
    due_time: Optional[date]
    start_time: Optional[int]     # minutes from midnight; assigned by Scheduler
    pet_name: Optional[str]       # set when task is added to a Pet; used by Scheduler output
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
        start_time: Optional[int] = None,
        pet_name: Optional[str] = None,
        notes: List[str] = []
    ) -> None:
        """Initialize a new Task with scheduling and metadata fields."""
        self.name = name
        self.duration = duration
        self.completed = False
        self.priority = priority
        self.due_time = due_time
        self.recurring = recurring
        self.start_time = start_time
        self.pet_name = pet_name
        self.notes = list(notes)

    def is_due_today(self) -> bool:
        """Check if task is due today.

        Returns:
            True if task's due_time is today, False otherwise.
        """
        return self.due_time == date.today()

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
            "name": self.name,
            "duration": self.duration,
            "priority": self.priority,
            "due_time": self.due_time.isoformat() if self.due_time is not None else None,
            "start_time": self.start_time,
            "pet_name": self.pet_name,
            "recurring": self.recurring,
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
        return Task(
            name=data["name"],
            duration=data["duration"],
            priority=data["priority"],
            due_time=due_time,
            recurring=data.get("recurring", False),
            start_time=data.get("start_time"),
            pet_name=data.get("pet_name"),
            notes=data.get("notes", []),
        )

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

        Args:
            task: Task instance to add.
        """
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

    def get_today_tasks(self) -> List[Task]:
        """Return only tasks that are due today.

        Returns:
            List of Task instances where is_due_today() is True.
        """
        return [t for t in self.tasks if t.is_due_today()]

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
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_today_tasks(self) -> List[Task]:
        """Retrieve all tasks due today across all pets.

        Returns:
            Flat list of Task instances where is_due_today() is True, across all pets.
            Each task's pet_name field identifies which pet it belongs to.
        """
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_today_tasks())
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

    def __init__(self, available_times: Union[int, List[int]]) -> None:
        """Initialize a Scheduler.

        Args:
            available_times: Either a single time slot (int) or list of available time slots.
        """
        if isinstance(available_times, int):
            self.available_times = [available_times]
        else:
            self.available_times = sorted(available_times)

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

        sorted_tasks = self.sort_tasks_by_priority(tasks)
        current_time = self.available_times[0]
        max_start = self.available_times[-1]

        scheduled = []
        dropped = []

        for task in sorted_tasks:
            if current_time <= max_start:
                task.start_time = current_time
                current_time += task.duration
                scheduled.append(task.to_dict())
            else:
                dropped.append(task.to_dict())

        return {"scheduled": scheduled, "dropped": dropped}

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (highest priority first).

        Args:
            tasks: List of tasks to sort.

        Returns:
            New list of tasks sorted by priority in descending order.
        """
        return sorted(tasks, key=lambda t: t.priority, reverse=True)

    def detect_conflicts(self, tasks: List[Task]) -> bool:
        """Detect if scheduled tasks have overlapping time windows.

        Requires tasks to already have start_time set (i.e. call generate_schedule first).
        A conflict exists when task A's start_time + duration overlaps task B's start_time.
        Tasks with start_time=None are skipped.

        Args:
            tasks: List of tasks to check; each should have start_time and duration set.

        Returns:
            True if any two tasks overlap, False otherwise.
        """
        timed = [t for t in tasks if t.start_time is not None]
        timed.sort(key=lambda t: t.start_time)

        for i in range(len(timed) - 1):
            a = timed[i]
            b = timed[i + 1]
            if a.start_time + a.duration > b.start_time:
                return True
        return False


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
