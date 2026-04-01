from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import uuid


@dataclass
class Task:
    """Dataclass representing a pet task"""
    task_name: str
    duration: int  # in minutes
    priority: int  # 1-3, where 1 is highest
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Auto-generated unique ID
    prefered_time: Optional[str] = None  # "morning" or "afternoon"
    frequency: str = "daily"    # "daily", "weekly", or "monthly"
    status: str = "pending"     # "pending", "in-progress", or "completed"
    due_date: datetime = field(default_factory=datetime.now)  # When task is due
    is_recurring_copy: bool = False  # Flag to track if this is an auto-generated recurring copy
    
    def update(self, name: str = None, duration: int = None, priority: int = None, prefered_time: str = None, frequency: str = None) -> bool:
        """Update task details with validation
        
        Validates input before updating:
        - name: not empty string
        - duration: integer between 1-480 minutes
        - priority: integer between 1-3
        - prefered_time: "morning" or "afternoon" (optional, case-insensitive)
        - frequency: "daily", "weekly", or "monthly"
        
        Args:
            name: new task name
            duration: new duration in minutes
            priority: new priority level
            prefered_time: "morning" or "afternoon"
            frequency: "daily", "weekly", or "monthly"
            
        Returns:
            bool: True if all updates were successful, False if any validation failed
        """
        # Validate and update name
        if name is not None:
            if not isinstance(name, str) or not name:
                return False
            self.task_name = name
        
        # Validate and update duration
        if duration is not None:
            if not isinstance(duration, int) or duration <= 0 or duration > 480:
                return False
            self.duration = duration
        
        # Validate and update priority
        if priority is not None:
            if not isinstance(priority, int) or priority < 1 or priority > 3:
                return False
            self.priority = priority
        
        # Validate and update prefered_time (case-insensitive, only "morning" or "afternoon")
        if prefered_time is not None:
            prefered_time_lower = prefered_time.lower()
            if prefered_time_lower not in ["morning", "afternoon"]:
                return False
            self.prefered_time = prefered_time_lower
        
        # Validate and update frequency (only "daily", "weekly", "monthly")
        if frequency is not None:
            if not isinstance(frequency, str) or frequency.lower() not in ["daily", "weekly", "monthly"]:
                return False
            self.frequency = frequency.lower()
        
        return True


    def is_feasible(self, available_time: int) -> bool:
        """Check if task is feasible in a given available time
        
        Args:
            available_time (int): Available time in minutes (must be >= 0)
            
        Returns:
            bool: True if task duration fits in available time, False otherwise
            
        Raises:
            ValueError: If available_time is negative
        """
        if not isinstance(available_time, int) or available_time < 0:
            raise ValueError(f"Available time must be a non-negative integer, got {available_time}")
        
        return self.duration <= available_time
    
    def update_status(self, new_status: str) -> Optional['Task']:
        """Update task status and handle recurring task creation
        
        When status is changed to "completed", automatically creates a new Task instance
        for the next occurrence if the task is recurring.
        
        Args:
            new_status (str): New status - "pending", "in-progress", or "completed"
            
        Returns:
            Task: New Task instance for next occurrence if recurring + completed, None otherwise
            
        Raises:
            ValueError: If new_status is invalid
        """
        # Validate new status
        new_status_lower = new_status.lower()
        if new_status_lower not in ["pending", "in-progress", "completed"]:
            raise ValueError(f"Invalid status '{new_status}'. Must be 'pending', 'in-progress', or 'completed'.")
        
        self.status = new_status_lower
        
        # If task is marked as completed and is recurring, create next occurrence
        if new_status_lower == "completed" and self.frequency in ["daily", "weekly", "monthly"]:
            return self.get_next_occurrence()
        
        return None
    
    def get_next_occurrence(self) -> 'Task':
        """Calculate next occurrence date and create new Task instance
        
        Uses Python's timedelta to calculate the next due date based on frequency:
        - Daily: due_date + 1 day
        - Weekly: due_date + 7 days
        - Monthly: due_date + 30 days (approximate)
        
        Returns:
            Task: New Task instance with same properties but new due date and task_id
            
        Raises:
            ValueError: If frequency is not "daily", "weekly", or "monthly"
        """
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(weeks=1)
        elif self.frequency == "monthly":
            next_due = self.due_date + timedelta(days=30)
        else:
            raise ValueError(f"Cannot calculate next occurrence for frequency: {self.frequency}")
        
        # Create new Task instance for next occurrence
        next_task = Task(
            task_name=self.task_name,
            duration=self.duration,
            priority=self.priority,
            prefered_time=self.prefered_time,
            frequency=self.frequency,
            due_date=next_due,
            is_recurring_copy=True,
            task_id=str(uuid.uuid4())  # New unique ID for the copy
        )
        
        return next_task
    
    def __post_init__(self):
        """Post-initialization validation for Task dataclass"""
        # Validate task_name
        if not isinstance(self.task_name, str) or not self.task_name:
            raise ValueError("Task name cannot be empty")
        
        # Validate duration
        if not isinstance(self.duration, int) or self.duration <= 0 or self.duration > 480:
            raise ValueError(f"Invalid duration {self.duration}. Duration must be an integer between 1 and 480 minutes.")
        
        # Validate priority
        if not isinstance(self.priority, int) or self.priority < 1 or self.priority > 3:
            raise ValueError(f"Invalid priority {self.priority}. Priority must be an integer between 1 and 3.")
        
        # Validate prefered_time (case-insensitive, optional, only "morning" or "afternoon")
        if self.prefered_time is not None:
            if not isinstance(self.prefered_time, str) or not self.prefered_time:
                raise ValueError(f"Invalid prefered_time {self.prefered_time}. Must be a non-empty string.")
            prefered_time_lower = self.prefered_time.lower()
            if prefered_time_lower not in ["morning", "afternoon"]:
                raise ValueError(f"Invalid prefered_time '{self.prefered_time}'. Must be 'morning' or 'afternoon'.")
            self.prefered_time = prefered_time_lower
        
        # Validate frequency (only "daily", "weekly", or "monthly")
        if not isinstance(self.frequency, str) or not self.frequency:
            raise ValueError("Frequency cannot be empty")
        frequency_lower = self.frequency.lower()
        if frequency_lower not in ["daily", "weekly", "monthly"]:
            raise ValueError(f"Invalid frequency '{self.frequency}'. Must be 'daily', 'weekly', or 'monthly'.")
        self.frequency = frequency_lower
        
        # Validate status (only "pending", "in-progress", or "completed")
        if not isinstance(self.status, str) or not self.status:
            raise ValueError("Status cannot be empty")
        status_lower = self.status.lower()
        if status_lower not in ["pending", "in-progress", "completed"]:
            raise ValueError(f"Invalid status '{self.status}'. Must be 'pending', 'in-progress', or 'completed'.")
        self.status = status_lower


@dataclass
class Pet:
    """Dataclass representing a pet"""
    name: str
    pet_type: str
    age: int
    tasks: List[Task] = field(default_factory=list)
    
    def add_task(self, task: Task) -> None:
        """Add a task to the pet
        
        Args:
            task (Task): Task object to add
            
        Raises:
            TypeError: If task is not a Task instance
            ValueError: If a task with the same ID already exists
        """
        if not isinstance(task, Task):
            raise TypeError(f"Expected Task instance, got {type(task)}")
        
        # Check if task with same ID already exists
        if any(t.task_id == task.task_id for t in self.tasks):
            raise ValueError(f"Task with ID {task.task_id} already exists")
        
        self.tasks.append(task)
    
    def get_tasks(self) -> List[Task]:
        """Get all tasks for the pet
        
        Returns:
            List[Task]: List of all tasks for this pet
        """
        return list(self.tasks)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task by task_id
        
        Args:
            task_id (str): ID of task to remove
            
        Returns:
            bool: True if task was removed, False if task not found
        """
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                self.tasks.pop(i)
                return True
        return False
    
    def update_task_status(self, task_id: str, new_status: str) -> Optional[Task]:
        """Update task status and handle recurring task creation
        
        If the task is marked as "completed" and is recurring, automatically creates a new 
        Task instance for the next occurrence and adds it to the pet's task list.
        
        Args:
            task_id (str): ID of the task to update
            new_status (str): New status - "pending", "in-progress", or "completed"
            
        Returns:
            Task: The newly created recurring task if applicable, None otherwise
            
        Raises:
            ValueError: If task with task_id not found or status is invalid
        """
        task = None
        for t in self.tasks:
            if t.task_id == task_id:
                task = t
                break
        
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Update status and get next occurrence if recurring and completed
        next_task = task.update_status(new_status)
        
        # If recurring and completed, add the next occurrence automatically
        if next_task:
            self.add_task(next_task)
            return next_task
        
        return None
    
    def get_total_duration(self) -> int:
        """Calculate total duration of all tasks
        
        Returns:
            int: Total duration in minutes of all tasks
        """
        return sum(task.duration for task in self.tasks)
    
    def __post_init__(self):
        """Post-initialization validation for Pet dataclass"""
        # Validate name
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Pet name cannot be empty")
        
        # Validate pet_type
        if not isinstance(self.pet_type, str) or not self.pet_type:
            raise ValueError("Pet type cannot be empty")
        
        # Validate age
        if not isinstance(self.age, int) or self.age < 0:
            raise ValueError(f"Invalid age {self.age}. Age must be a non-negative integer.")


@dataclass
class Owner:
    """Dataclass representing a pet owner"""
    name: str
    available_time: int
    available_time_morning: int = 0  # Time available in morning (minutes)
    available_time_afternoon: int = 0  # Time available in afternoon (minutes)
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner
        
        Args:
            pet (Pet): Pet object to add
            
        Raises:
            TypeError: If pet is not a Pet instance
            ValueError: If a pet with the same name, type, and age already exists
        """
        if not isinstance(pet, Pet):
            raise TypeError(f"Expected Pet instance, got {type(pet)}")
        
        # Check if pet with same attributes (name, type, age) already exists
        for existing_pet in self.pets:
            if (existing_pet.name.lower() == pet.name.lower() and
                existing_pet.pet_type.lower() == pet.pet_type.lower() and
                existing_pet.age == pet.age):
                raise ValueError(
                    f"Pet '{pet.name}' ({pet.pet_type}, {pet.age} years old) already exists"
                )
        
        self.pets.append(pet)
    
    def get_pets(self) -> List[Pet]:
        """Get all pets owned
        
        Returns:
            List[Pet]: List of all pets owned by this owner
        """
        return list(self.pets)
    
    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name
        
        Args:
            pet_name (str): Name of the pet to remove
            
        Returns:
            bool: True if pet was removed, False if pet not found
        """
        for i, pet in enumerate(self.pets):
            if pet.name.lower() == pet_name.lower():
                self.pets.pop(i)
                return True
        return False
    
    def set_availability(self, time: int) -> None:
        """Set available time for pet care
        
        Args:
            time (int): Available time in minutes (must be >= 0)
            
        Raises:
            ValueError: If time is negative
        """
        if not isinstance(time, int) or time < 0:
            raise ValueError(f"Available time must be a non-negative integer, got {time}")
        
        self.available_time = time
    
    def __post_init__(self):
        """Post-initialization validation for Owner dataclass"""
        # Validate name
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Owner name cannot be empty")
        
        # Validate available_time
        if not isinstance(self.available_time, int) or self.available_time < 0:
            raise ValueError(f"Invalid available_time {self.available_time}. Must be a non-negative integer.")
        
        # Validate time slot fields
        if not isinstance(self.available_time_morning, int) or self.available_time_morning < 0:
            raise ValueError(f"Invalid available_time_morning {self.available_time_morning}. Must be a non-negative integer.")
        
        if not isinstance(self.available_time_afternoon, int) or self.available_time_afternoon < 0:
            raise ValueError(f"Invalid available_time_afternoon {self.available_time_afternoon}. Must be a non-negative integer.")
        
        # Validate that morning + afternoon = total (if both are set)
        total_slot_time = self.available_time_morning + self.available_time_afternoon
        if total_slot_time > 0 and total_slot_time != self.available_time:
            raise ValueError(
                f"Time slot mismatch: morning ({self.available_time_morning}) + afternoon ({self.available_time_afternoon}) "
                f"= {total_slot_time}, but total available_time is {self.available_time}. They must be equal."
            )
        
        # Auto-assign time slots if not set (50/50 split)
        if self.available_time_morning == 0 and self.available_time_afternoon == 0:
            self.available_time_morning = self.available_time // 2
            self.available_time_afternoon = self.available_time - self.available_time_morning
        
        # Validate preferences is a dict
        if not isinstance(self.preferences, dict):
            raise ValueError("Invalid preferences format. Please provide a valid preference.")
        if "prefered_time" in self.preferences:
            if self.preferences["prefered_time"].lower() not in ["morning", "afternoon"]:
                raise ValueError("Invalid prefered_time in preferences. Must be 'morning' or 'afternoon'.")


class Scheduler:
    """Class for scheduling pet tasks"""
    
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.available_time = owner.available_time
        self.plan: List[Task] = []
    
    def filter_by_constraints(self) -> List[Task]:
        """Filter tasks based on constraints
        
        Only returns tasks that:
        - Are not already completed (status != "completed")
        - Can fit in available time
        
        Returns:
            List[Task]: Tasks that are feasible given time constraints
        """
        feasible_tasks = []
        for task in self.pet.get_tasks():
            if task.status != "completed" and task.is_feasible(self.available_time):
                feasible_tasks.append(task)
        return feasible_tasks
    
    def sort_by_priority(self, tasks: List[Task] = None) -> List[Task]:
        """Sort tasks by priority and preferred time
        
        Args:
            tasks (List[Task], optional): Tasks to sort. If None, uses filtered tasks.
                                         Priority 1 is highest, 3 is lowest.
                                         Morning tasks come before afternoon tasks.
        
        Returns:
            List[Task]: Tasks sorted by priority first, then preferred time
        """
        if tasks is None:
            tasks = self.filter_by_constraints()
        
        return sorted(tasks, key=lambda t: (
            t.priority,
            0 if t.prefered_time == "morning" else 1 if t.prefered_time == "afternoon" else 2
        ))
    
    def sort_by_duration(self, tasks: List[Task] = None, ascending: bool = True) -> List[Task]:
        """Sort tasks by duration (shortest or longest first)
        
        Args:
            tasks (List[Task], optional): Tasks to sort. If None, uses filtered tasks.
            ascending (bool): If True, sorts shortest first. If False, longest first.
        
        Returns:
            List[Task]: Tasks sorted by duration
        """
        if tasks is None:
            tasks = self.filter_by_constraints()
        
        return sorted(tasks, key=lambda t: t.duration, reverse=not ascending)
    
    def filter_by_status(self, status: str, tasks: List[Task] = None) -> List[Task]:
        """Filter tasks by completion status
        
        Algorithmically filters tasks by their current status state:
        - "pending": Tasks waiting to be started
        - "in-progress": Tasks currently being worked on
        - "completed": Tasks that have been finished
        
        Args:
            status (str): Status to filter by - "pending", "in-progress", or "completed"
            tasks (List[Task], optional): Tasks to filter. If None, uses all tasks from pet.
        
        Returns:
            List[Task]: Tasks matching the specified status
            
        Raises:
            ValueError: If status is not valid
        """
        valid_statuses = ["pending", "in-progress", "completed"]
        if status.lower() not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}")
        
        if tasks is None:
            tasks = self.pet.get_tasks()
        
        status_lower = status.lower()
        return [t for t in tasks if t.status == status_lower]
    
    def filter_by_time_slot(self, slot: str, tasks: List[Task] = None) -> List[Task]:
        """Filter tasks by preferred time slot
        
        Algorithmically filters tasks to show only those preferred for a specific time:
        - "morning": Tasks best done in the morning
        - "afternoon": Tasks best done in the afternoon
        - "flexible": Tasks with no time preference
        
        Args:
            slot (str): Time slot to filter - "morning", "afternoon", or "flexible"
            tasks (List[Task], optional): Tasks to filter. If None, uses all tasks from pet.
        
        Returns:
            List[Task]: Tasks matching the specified time slot preference
            
        Raises:
            ValueError: If slot is not valid
        """
        valid_slots = ["morning", "afternoon", "flexible"]
        if slot.lower() not in valid_slots:
            raise ValueError(f"Invalid slot '{slot}'. Must be one of {valid_slots}")
        
        if tasks is None:
            tasks = self.pet.get_tasks()
        
        slot_lower = slot.lower()
        if slot_lower == "flexible":
            # Flexible means no preference (prefered_time is None)
            return [t for t in tasks if t.prefered_time is None]
        else:
            # Morning or afternoon
            return [t for t in tasks if t.prefered_time == slot_lower]
    
    def get_recurring_tasks(self, frequency: str = "daily") -> List[Task]:
        """Get recurring tasks that are not completed
        
        Args:
            frequency (str): "daily", "weekly", or "monthly". Default: "daily"
        
        Returns:
            List[Task]: Tasks with specified frequency that are not completed
        """
        return [t for t in self.pet.get_tasks() 
                if t.frequency == frequency and t.status != "completed"]
    
    def detect_conflicts(self) -> List[str]:
        """Detect scheduling conflicts in the current plan
        
        Checks for:
        - Total duration exceeding available time
        - Morning tasks exceeding morning time slot
        - Afternoon tasks exceeding afternoon time slot
        
        Returns:
            List[str]: List of conflict messages, empty if no conflicts
        """
        conflicts = []
        
        if not self.plan:
            return conflicts
        
        # Get time slot availability from owner
        slot_time_morning = self.owner.available_time_morning
        slot_time_afternoon = self.owner.available_time_afternoon
        
        # Calculate tasks per time slot
        morning_tasks = [t for t in self.plan if t.prefered_time == "morning"]
        afternoon_tasks = [t for t in self.plan if t.prefered_time == "afternoon"]
        no_pref_tasks = [t for t in self.plan if t.prefered_time is None]
        
        morning_duration = sum(t.duration for t in morning_tasks)
        afternoon_duration = sum(t.duration for t in afternoon_tasks)
        no_pref_duration = sum(t.duration for t in no_pref_tasks)
        
        # Check if morning tasks exceed morning slot
        if morning_duration > slot_time_morning:
            excess = morning_duration - slot_time_morning
            conflicts.append(
                f"⚠️ Morning tasks ({morning_duration} min) exceed morning slot ({slot_time_morning} min) by {excess} min. "
                f"Consider moving {len(morning_tasks)} task(s) to afternoon or removing lower priority tasks."
            )
        
        # Check if afternoon tasks exceed afternoon slot
        if afternoon_duration > slot_time_afternoon:
            excess = afternoon_duration - slot_time_afternoon
            conflicts.append(
                f"⚠️ Afternoon tasks ({afternoon_duration} min) exceed afternoon slot ({slot_time_afternoon} min) by {excess} min. "
                f"Consider moving {len(afternoon_tasks)} task(s) to morning or removing lower priority tasks."
            )
        
        # Check total duration vs available time
        total = morning_duration + afternoon_duration + no_pref_duration
        if total > self.available_time:
            conflicts.append(
                f"⚠️ Total duration ({total} min) exceeds available time ({self.available_time} min)"
            )
        
        return conflicts
    
    def generate_plan(self) -> List[Task]:
        """Generate a schedule plan for tasks
        
        Strategy:
        1. Prioritize daily recurring tasks first
        2. Filter remaining tasks by feasibility and completion status
        3. Sort all tasks by priority, then preferred time
        4. Greedily add tasks until time runs out
        
        Returns:
            List[Task]: Ordered list of tasks that fit in available time
        """
        # Get daily recurring tasks first (they must happen)
        recurring = self.get_recurring_tasks("daily")
        
        # Get all other feasible tasks sorted by priority and preferred time
        sorted_tasks = self.sort_by_priority()
        
        # Put recurring tasks at the front, then the rest (avoiding duplicates)
        prioritized = recurring + [t for t in sorted_tasks if t not in recurring]
        
        # Greedily add tasks to plan until time runs out
        self.plan = []
        remaining_time = self.available_time
        
        for task in prioritized:
            if task.duration <= remaining_time:
                self.plan.append(task)
                remaining_time -= task.duration
        
        return self.plan
    
    def explain_plan(self) -> str:
        """Provide explanation of the generated plan
        
        Returns:
            str: Formatted explanation of why tasks were chosen/excluded
        """
        explanation = f"Schedule Plan for {self.pet.name} ({self.pet.pet_type})\n"
        explanation += f"Available time: {self.available_time} minutes\n"
        explanation += "-" * 50 + "\n\n"
        
        if not self.plan:
            explanation += "⚠️  No tasks could be scheduled with available time.\n"
            all_tasks = self.pet.get_tasks()
            if all_tasks:
                explanation += "\nTasks that do NOT fit:\n"
                for task in all_tasks:
                    explanation += f"  • {task.task_name} ({task.duration} min, priority {task.priority}) - "
                    if task.status == "completed":
                        explanation += "already completed\n"
                    elif task.duration > self.available_time:
                        explanation += f"exceeds available time ({task.duration} > {self.available_time})\n"
                    else:
                        explanation += "not selected\n"
            return explanation
        
        # Check for conflicts
        conflicts = self.detect_conflicts()
        if conflicts:
            explanation += "⚠️ Conflicts Detected:\n"
            for conflict in conflicts:
                explanation += f"  {conflict}\n"
            explanation += "\n"
        
        # Explain included tasks
        explanation += f"✅ Scheduled Tasks ({len(self.plan)}):\n"
        total_duration = 0
        for i, task in enumerate(self.plan, 1):
            explanation += f"  {i}. {task.task_name}\n"
            explanation += f"     Duration: {task.duration} min | Priority: {task.priority}"
            if task.frequency != "daily":
                explanation += f" | Frequency: {task.frequency}"
            explanation += "\n"
            if task.prefered_time:
                explanation += f"     Preferred time: {task.prefered_time}\n"
            total_duration += task.duration
        
        explanation += f"\nTotal scheduled time: {total_duration} / {self.available_time} minutes\n"
        explanation += f"Remaining time: {self.available_time - total_duration} minutes\n"
        
        # Explain excluded tasks
        feasible_not_scheduled = [t for t in self.filter_by_constraints() if t not in self.plan]
        if feasible_not_scheduled:
            explanation += f"\n❌ Feasible but NOT scheduled ({len(feasible_not_scheduled)}):\n"
            for task in feasible_not_scheduled:
                explanation += f"  • {task.task_name} ({task.duration} min, priority {task.priority}) - "
                explanation += "lower priority than scheduled tasks\n"
        
        all_tasks = self.pet.get_tasks()
        infeasible = [t for t in all_tasks if not t.is_feasible(self.available_time) and t.status != "completed"]
        if infeasible:
            explanation += f"\n⛔ Too long to fit ({len(infeasible)}):\n"
            for task in infeasible:
                explanation += f"  • {task.task_name} ({task.duration} min) - exceeds available time\n"
        
        # Completed tasks
        completed = [t for t in all_tasks if t.status == "completed"]
        if completed:
            explanation += f"\n✔️ Completed ({len(completed)}):\n"
            for task in completed:
                explanation += f"  • {task.task_name}\n"
        
        return explanation
