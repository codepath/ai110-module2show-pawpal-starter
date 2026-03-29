from typing import List, Optional, TypedDict, Union
from datetime import date


class TaskDict(TypedDict):
    """Type definition for Task dictionary representation."""
    name: str
    duration: int
    priority: int
    due_time: Optional[str]
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
    recurring: bool
    notes: List[str]

    def __init__(
        self,
        name: str,
        duration: int,
        priority: int,
        due_time: Optional[date] = ...,
        recurring: bool = ...
    ) -> None: ...

    def is_due_today(self) -> bool:
        """Check if task is due today.
        
        Returns:
            True if task's due_time is today, False otherwise.
        """
        ...

    def add_note(self, note: str) -> None:
        """Add a note to the task.
        
        Args:
            note: The note text to add.
        """
        ...

    def get_notes(self) -> List[str]:
        """Retrieve all notes for this task.
        
        Returns:
            List of note strings.
        """
        ...

    def to_dict(self) -> TaskDict:
        """Convert task to dictionary representation.
        
        Returns:
            Dictionary containing all task data.
        """
        ...

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
        ...

    def __str__(self) -> str:
        """Return string representation of task."""
        ...


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
        """Initialize a new Pet.
        
        Args:
            name: The pet's name.
            species: The pet's species.
        """
        ...

    def add_task(self, task: Task) -> None:
        """Add a task for this pet.
        
        Args:
            task: Task instance to add.
        """
        ...

    def get_tasks(self) -> List[Task]:
        """Retrieve all tasks for this pet.
        
        Returns:
            List of Task instances.
        """
        ...

    def add_note(self, note: str) -> None:
        """Add a note about this pet.
        
        Args:
            note: The note text to add.
        """
        ...

    def get_notes(self) -> List[str]:
        """Retrieve all notes for this pet.
        
        Returns:
            List of note strings.
        """
        ...

    def to_dict(self) -> PetDict:
        """Convert pet to dictionary representation.
        
        Returns:
            Dictionary containing all pet data.
        """
        ...

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
        ...


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
        """Initialize a new Owner.
        
        Args:
            name: The owner's name.
        """
        ...

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection.
        
        Args:
            pet: Pet instance to add.
        """
        ...

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks across all pets owned by this owner.
        
        Returns:
            List of all Task instances from all pets.
        """
        ...

    def add_note(self, note: str) -> None:
        """Add a note about this owner.
        
        Args:
            note: The note text to add.
        """
        ...

    def get_notes(self) -> List[str]:
        """Retrieve all notes for this owner.
        
        Returns:
            List of note strings.
        """
        ...

    def to_dict(self) -> OwnerDict:
        """Convert owner to dictionary representation.
        
        Returns:
            Dictionary containing all owner data and their pets.
        """
        ...

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
        ...


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
        ...

    def generate_schedule(self, tasks: List[Task]) -> List[Task]:
        """Generate an optimal schedule for the given tasks.
        
        Args:
            tasks: List of tasks to schedule.
            
        Returns:
            List of tasks organized in priority and time order.
            
        Raises:
            ValueError: If tasks cannot fit in available time.
        """
        ...

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (highest priority first).
        
        Args:
            tasks: List of tasks to sort.
            
        Returns:
            New list of tasks sorted by priority in descending order.
        """
        ...

    def detect_conflicts(self, tasks: List[Task]) -> bool:
        """Detect if scheduled tasks have time conflicts.
        
        Args:
            tasks: List of tasks to check for conflicts.
            
        Returns:
            True if conflicts are detected, False otherwise.
        """
        ...


class OwnerRepository:
    """Manages persistence of Owner data.
    
    Responsible for saving and loading Owner instances to/from files.
    
    Attributes:
        file_path: Path to the file where owner data is stored.
    """
    file_path: str

    def __init__(self, file_path: str = ...) -> None:
        """Initialize the repository with a file path.
        
        Args:
            file_path: Path where owner data should be saved/loaded. Defaults to 'owner.json'.
        """
        ...

    def save(self, owner: Owner) -> None:
        """Save an owner to file.
        
        Args:
            owner: Owner instance to save.
            
        Raises:
            IOError: If file cannot be written.
            ValueError: If owner data cannot be serialized.
        """
        ...

    def load(self) -> Optional[Owner]:
        """Load an owner from file.
        
        Returns:
            Owner instance if file exists and is valid, None otherwise.
            
        Raises:
            IOError: If file exists but cannot be read.
            ValueError: If file data is corrupted or invalid format.
        """
        ...