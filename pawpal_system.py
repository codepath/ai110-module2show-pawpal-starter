# pawpal_system.py
"""
Logic layer for PawPal+ app: defines core data model and scheduling classes.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
	from typing import Any

# Task class
class Task:
    """Represents a single activity for a pet."""
    _id_counter = 1
    def __init__(self, description: str, time: Optional[datetime] = None, frequency: str = '', completed: bool = False, duration: int = 0, priority: str = 'medium'):
        self.task_id = Task._id_counter
        Task._id_counter += 1
        self.description = description
        self.time = time
        self.frequency = frequency
        self.completed = completed
        self.duration = duration      # estimated minutes to complete
        self.priority = priority      # 'high', 'medium', or 'low'

    def mark_complete(self):
        """Mark this task as complete."""
        self.completed = True

    def mark_incomplete(self):
        """Mark this task as incomplete."""
        self.completed = False


# Pet class
class Pet:
    """Stores pet details and a list of tasks."""
    _id_counter = 1
    def __init__(self, name: str, species: str, breed: str = '', age: int = 0):
        self.pet_id = Pet._id_counter
        Pet._id_counter += 1
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks


# Owner class
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    def __init__(self, name: str, preferences: Optional[Dict] = None):
        self.name = name
        self.pets: List[Pet] = []
        self.preferences: Dict = preferences if preferences is not None else {
            'max_tasks_per_day': 5,
            'available_minutes': 90,
        }

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def set_preferences(self, prefs: Dict) -> None:
        """Update owner preferences with the given key-value pairs."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks for all pets owned by this owner."""
        return [task for pet in self.pets for task in pet.get_tasks()] #simplified for readability.


# Scheduler class
class Scheduler:
    """The 'Brain' that retrieves, organizes, and manages tasks across pets."""
    def __init__(self, owner: Owner):
        """Initialize the Scheduler with an Owner."""
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from all pets."""
        return self.owner.get_all_tasks()

    def get_tasks_by_pet(self, pet: Pet) -> List[Task]:
        """Retrieve all tasks for a specific pet."""
        return pet.get_tasks()

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Retrieve tasks filtered by completion status."""
        return [task for task in self.get_all_tasks() if task.completed == completed]

    def filter_by_pet_name(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the pet with the given name.

        Args:
            pet_name: The name of the pet to filter by. Matching is case-insensitive,
                      so 'buddy', 'Buddy', and 'BUDDY' all resolve to the same pet.

        Returns:
            A list of Task objects assigned to the matched pet.
            Returns an empty list if no pet with that name exists.
        """
        matched_pet = next(
            (p for p in self.owner.pets if p.name.lower() == pet_name.lower()), None
        )
        if matched_pet is None:
            return []
        return matched_pet.get_tasks()

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by completion status, pet name, or both combined.

        Both arguments are optional. Omitting one disables that filter.
        When both are provided, only tasks satisfying both conditions are returned.

        Args:
            completed: If True, return only completed tasks. If False, return only
                       pending tasks. If None (default), completion status is ignored.
            pet_name:  If provided, return only tasks belonging to the pet with this
                       name (case-insensitive). If None (default), tasks from all
                       pets are included.

        Returns:
            A list of Task objects matching all supplied filter criteria.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [
                task for task in tasks
                if any(
                    task in p.tasks
                    for p in self.owner.pets
                    if p.name.lower() == pet_name.lower()
                )
            ]
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        return tasks

    def get_tasks_by_frequency(self, frequency: str) -> List[Task]:
        """Retrieve tasks filtered by frequency."""
        return [task for task in self.get_all_tasks() if task.frequency == frequency]

    def complete_task(self, pet: Pet, task: Task) -> None:
        """Mark a task complete and auto-schedule the next occurrence if recurring.

        Calls task.mark_complete() then, for 'daily' and 'weekly' tasks, creates a
        new Task with the same description and frequency scheduled one interval later
        (daily → +1 day, weekly → +7 days) and adds it to the pet's task list.
        Tasks with frequency 'once' or 'monthly', or tasks with no scheduled time,
        are marked complete without generating a follow-up.

        Args:
            pet:  The Pet object that owns the task. The follow-up task, if created,
                  is added directly to this pet.
            task: The Task to mark as complete. Must already be assigned to pet.

        Returns:
            None. Side effects: task.completed is set to True; a new Task may be
            appended to pet.tasks.
        """

        # Step 1: Mark the task as done using the existing Task method.
        # We keep mark_complete() unchanged so nothing else breaks.
        task.mark_complete()

        # Step 2: Map frequency strings to how far ahead the next occurrence should be.
        # Only 'daily' and 'weekly' are recurring — 'monthly' and 'once' are intentionally excluded.
        _delta_map = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        }

        # Step 3: Look up the delta. If the frequency isn't in the map (e.g. 'once'),
        # delta will be None and no new task will be created.
        delta = _delta_map.get(task.frequency)

        # Step 4: Only create a follow-up task if this is a recurring task with a set time.
        # Both conditions must be true — a recurring task with no time can't be rescheduled.
        if delta and task.time:
            next_task = Task(
                description=task.description,   # same activity name
                time=task.time + delta,          # shift the time forward by one interval
                frequency=task.frequency,        # preserve the same recurrence pattern
                duration=task.duration,          # preserve original duration
                priority=task.priority,          # preserve original priority
            )
            # Step 5: Add the new task directly to the same pet's task list.
            # The Scheduler owns this orchestration — Pet and Task stay simple.
            pet.add_task(next_task)

    def sort_by_time(self) -> List[Task]:
        """Return all tasks across all pets sorted by scheduled time, ascending.

        Uses Python's built-in sorted() with a lambda key on task.time. Tasks that
        have no time set (time is None) are pushed to the end of the list by
        substituting datetime.max as their sort key.

        Returns:
            A new sorted list of Task objects. The original task lists on each Pet
            are not modified. Tasks sharing the same time retain their original
            relative order (stable sort).

        Notes:
            If task.time were stored as a zero-padded 'HH:MM' string instead of a
            datetime, this lambda would still sort correctly because lexicographic
            order matches chronological order for that format.
        """
        return sorted(
            self.get_all_tasks(),
            key=lambda task: task.time if task.time is not None else datetime.max
        )

    def detect_conflicts(self) -> List[str]:
        """Detect scheduling conflicts within each pet's task list and return warning messages.

        A conflict is defined as two tasks belonging to the same pet that share an
        identical scheduled datetime. Tasks with no time set are ignored. Cross-pet
        overlaps are not flagged — only same-pet conflicts are relevant here.

        The method uses a pairwise O(n²) comparison per pet, which is efficient
        enough for the small task lists typical in this application.

        Returns:
            A list of human-readable warning strings, one per conflict pair.
            Each message identifies the two conflicting task descriptions, their
            shared time, and the pet's name. Returns an empty list if no conflicts
            are found — the caller can safely iterate without checking for None.
        """
        warnings: List[str] = []
        # Check each pet independently — a conflict only matters within the same pet's schedule
        for pet in self.owner.pets:
            # Only consider tasks that actually have a time set
            timed_tasks = [t for t in pet.get_tasks() if t.time is not None]
            # Compare every pair of tasks for this pet (O(n²), fine for small task lists)
            for i in range(len(timed_tasks)):
                for j in range(i + 1, len(timed_tasks)):
                    # A conflict is an exact same hour and minute — build a readable warning string
                    if timed_tasks[i].time == timed_tasks[j].time:
                        time_str = timed_tasks[i].time.strftime('%H:%M')
                        warnings.append(
                            f"WARNING: '{timed_tasks[i].description}' and '{timed_tasks[j].description}' "
                            f"are both scheduled at {time_str} for {pet.name}."
                        )
        return warnings

    def generate_schedule(self) -> List[tuple]:
        """Select and order tasks for today based on priority and owner constraints.

        Picks from all pending (incomplete) tasks across every pet. Tasks are ranked
        by priority (high → medium → low) then by scheduled time. Selection stops
        when either the max_tasks_per_day limit or the available_minutes budget is
        exhausted. Each returned tuple carries enough context to render a rich UI row.

        Returns:
            A list of (pet, task, reason) tuples for selected tasks, where reason is
            a human-readable string explaining why the task was chosen and when it
            happens (e.g. 'Selected – high priority · 30 min · 60 min remaining').
        """
        _priority_rank = {'high': 0, 'medium': 1, 'low': 2}
        max_tasks = self.owner.preferences.get('max_tasks_per_day', 5)
        available_minutes = self.owner.preferences.get('available_minutes', 90)

        # Build (pet, task) pairs for all pending tasks
        candidates = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.get_tasks()
            if not task.completed
        ]

        # Sort by priority rank, then by scheduled time (timeless tasks go last)
        candidates.sort(
            key=lambda pt: (_priority_rank.get(pt[1].priority, 1), pt[1].time if pt[1].time else datetime.max)
        )

        selected = []
        minutes_used = 0
        for pet, task in candidates:
            if len(selected) >= max_tasks:
                break
            if task.duration > 0 and minutes_used + task.duration > available_minutes:
                continue  # skip this task — not enough time, try lower-priority ones
            minutes_used += task.duration
            time_str = task.time.strftime('%H:%M') if task.time else 'anytime'
            mins_remaining = available_minutes - minutes_used
            reason = (
                f"Selected – {task.priority} priority · "
                f"{task.duration} min · {mins_remaining} min remaining after"
                if task.duration > 0
                else f"Selected – {task.priority} priority · scheduled {time_str}"
            )
            selected.append((pet, task, reason))

        return selected

    def explain_plan(self) -> str:
        """Return a plain-text summary of the generated schedule with per-task reasoning."""
        schedule = self.generate_schedule()
        if not schedule:
            return "No tasks selected for today. Add tasks or adjust preferences."
        lines = ["Today's plan:\n"]
        for i, (pet, task, reason) in enumerate(schedule, 1):
            time_str = task.time.strftime('%H:%M') if task.time else 'no time set'
            lines.append(f"  {i}. [{pet.name}] {task.description} @ {time_str} — {reason}")
        return "\n".join(lines)
