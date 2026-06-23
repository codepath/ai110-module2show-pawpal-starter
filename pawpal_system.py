"""
PawPal+ System Logic Layer
This module contains the core classes for the PawPal+ pet care scheduling system.
"""

import uuid
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple


class Owner:
    """Represents a pet owner with time constraints and preferences."""

    def __init__(self, name: str, available_time_minutes: int):
        """
        Initialize an Owner instance.

        Args:
            name: The owner's name
            available_time_minutes: Daily available time in minutes for pet care
        """
        self._name = name
        self._available_time_minutes = available_time_minutes
        self._preferences = {}

    def get_name(self) -> str:
        """Return the owner's name."""
        return self._name

    def get_available_time(self) -> int:
        """Return the available time in minutes."""
        return self._available_time_minutes

    def set_available_time(self, minutes: int) -> None:
        """
        Set the available time for pet care.

        Args:
            minutes: Available time in minutes
        """
        self._available_time_minutes = minutes

    def add_preference(self, key: str, value) -> None:
        """
        Add or update a preference.

        Args:
            key: Preference key
            value: Preference value
        """
        self._preferences[key] = value

    def get_preferences(self) -> Dict:
        """Return all preferences as a dictionary."""
        return self._preferences


class Pet:
    """Represents a pet with characteristics that affect care needs."""

    def __init__(self, name: str, species: str, age: int, size: str):
        """
        Initialize a Pet instance.

        Args:
            name: The pet's name
            species: Type of pet (dog, cat, bird, etc.)
            age: Pet's age in years
            size: Pet's size (small, medium, large)
        """
        self._name = name
        self._species = species
        self._age = age
        self._size = size
        self._special_needs = []
        self._tasks = []

    def get_name(self) -> str:
        """Return the pet's name."""
        return self._name

    def get_species(self) -> str:
        """Return the pet's species."""
        return self._species

    def add_special_need(self, need: str) -> None:
        """
        Add a special care need for the pet.

        Args:
            need: Description of special need
        """
        self._special_needs.append(need)

    def get_special_needs(self) -> List[str]:
        """Return list of special needs."""
        return self._special_needs

    def get_age(self) -> int:
        """Return the pet's age."""
        return self._age

    def get_size(self) -> str:
        """Return the pet's size."""
        return self._size

    def add_task(self, task: "Task") -> None:
        """
        Add a task to this pet.

        Args:
            task: Task to add to the pet
        """
        self._tasks.append(task)

    def get_tasks(self) -> List["Task"]:
        """Return all tasks for this pet."""
        return self._tasks

    def get_task_count(self) -> int:
        """Return the number of tasks for this pet."""
        return len(self._tasks)


class Task:
    """Represents a pet care task with duration and priority."""

    def __init__(self, name: str, task_type: str, duration_minutes: int, priority: int):
        """
        Initialize a Task instance.

        Args:
            name: Task name
            task_type: Type of task (walk, feeding, meds, enrichment, grooming, etc.)
            duration_minutes: How long the task takes
            priority: Task priority (higher number = higher priority)
        """
        self._task_id = str(uuid.uuid4())
        self._name = name
        self._task_type = task_type
        self._duration_minutes = duration_minutes
        self._priority = priority
        self._base_priority = priority  # Store original priority
        self._description = ""
        self._is_mandatory = False
        self._frequency = "daily"
        self._is_completed = False
        self._recurs = True  # Whether this task recurs
        self._next_occurrence = None  # Next scheduled occurrence date

        # Feature 1: Time-Window Constraints
        self._time_window_start = None  # e.g., "08:00"
        self._time_window_end = None  # e.g., "10:00"

        # Feature 2: Task Dependencies
        self._prerequisites = []  # List of task_ids that must be completed first

        # Feature 3: Dynamic Priority Adjustment
        self._last_completed = None  # datetime of last completion
        self._days_since_completion = 0

    def get_duration(self) -> int:
        """Return task duration in minutes."""
        return self._duration_minutes

    def get_priority(self) -> int:
        """Return task priority."""
        return self._priority

    def set_priority(self, priority: int) -> None:
        """
        Set task priority.

        Args:
            priority: New priority value
        """
        self._priority = priority

    def get_task_type(self) -> str:
        """Return the task type."""
        return self._task_type

    def is_mandatory(self) -> bool:
        """Return whether this task is mandatory."""
        return self._is_mandatory

    def get_task_id(self) -> str:
        """Return the task ID."""
        return self._task_id

    def get_name(self) -> str:
        """Return the task name."""
        return self._name

    def get_description(self) -> str:
        """Return the task description."""
        return self._description

    def set_mandatory(self, is_mandatory: bool) -> None:
        """
        Set whether this task is mandatory.

        Args:
            is_mandatory: True if task must be completed, False otherwise
        """
        self._is_mandatory = is_mandatory

    def set_description(self, description: str) -> None:
        """
        Set the task description.

        Args:
            description: Task description text
        """
        self._description = description

    def set_frequency(self, frequency: str) -> None:
        """
        Set the task frequency.

        Args:
            frequency: How often the task should be done (e.g., "daily", "weekly")
        """
        self._frequency = frequency

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self._is_completed = True

    def is_completed(self) -> bool:
        """Return whether this task is completed."""
        return self._is_completed

    def get_frequency(self) -> str:
        """Return the task frequency."""
        return self._frequency

    def set_recurs(self, recurs: bool) -> None:
        """
        Set whether this task should recur.

        Args:
            recurs: True if task should automatically recur, False otherwise
        """
        self._recurs = recurs

    def get_recurs(self) -> bool:
        """Return whether this task recurs."""
        return self._recurs

    def get_next_occurrence(self) -> Optional[date]:
        """Return the next scheduled occurrence date."""
        return self._next_occurrence

    def complete_and_recur(self) -> Optional["Task"]:
        """
        Mark this task as completed and create a new instance for next occurrence.

        Returns:
            New Task instance for next occurrence if task recurs, None otherwise
        """
        from datetime import timedelta

        # Mark this task as completed
        self.mark_complete()
        self.set_last_completed(date.today())

        # If task doesn't recur, return None
        if not self._recurs:
            return None

        # Calculate next occurrence date based on frequency
        if self._frequency == "daily":
            next_date = date.today() + timedelta(days=1)
        elif self._frequency == "weekly":
            next_date = date.today() + timedelta(weeks=1)
        elif self._frequency == "monthly":
            # Approximate month as 30 days
            next_date = date.today() + timedelta(days=30)
        else:
            # Unknown frequency, default to daily
            next_date = date.today() + timedelta(days=1)

        # Create new task instance for next occurrence
        new_task = Task(
            self._name, self._task_type, self._duration_minutes, self._base_priority
        )

        # Copy all attributes from current task
        new_task.set_description(self._description)
        new_task.set_mandatory(self._is_mandatory)
        new_task.set_frequency(self._frequency)
        new_task.set_recurs(self._recurs)

        # Copy time window if exists
        if self.has_time_window():
            start, end = self.get_time_window()
            new_task.set_time_window(start, end)

        # Copy prerequisites (task IDs will be same)
        for prereq_id in self._prerequisites:
            new_task._prerequisites.append(prereq_id)

        # Set next occurrence date
        new_task._next_occurrence = next_date
        new_task.set_last_completed(date.today())

        return new_task

    # ===== FEATURE 1: TIME-WINDOW CONSTRAINTS =====

    def set_time_window(self, start_time: str, end_time: str) -> None:
        """
        Set the time window during which this task can be scheduled.

        Args:
            start_time: Earliest time for this task (HH:MM format, e.g., "08:00")
            end_time: Latest time for this task (HH:MM format, e.g., "10:00")
        """
        self._time_window_start = start_time
        self._time_window_end = end_time

    def get_time_window(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the time window for this task.

        Returns:
            Tuple of (start_time, end_time) or (None, None) if no window set
        """
        return (self._time_window_start, self._time_window_end)

    def has_time_window(self) -> bool:
        """Return whether this task has a time window constraint."""
        return self._time_window_start is not None and self._time_window_end is not None

    def can_schedule_at_time(self, time_str: str) -> bool:
        """
        Check if this task can be scheduled at the given time.

        Args:
            time_str: Time to check in HH:MM format

        Returns:
            True if task can be scheduled at this time, False otherwise
        """
        if not self.has_time_window():
            return True  # No restriction

        return self._time_window_start <= time_str <= self._time_window_end

    # ===== FEATURE 2: TASK DEPENDENCIES =====

    def add_prerequisite(self, task: "Task") -> None:
        """
        Add a task that must be completed before this task.

        Args:
            task: The task that must be completed first
        """
        if task.get_task_id() not in self._prerequisites:
            self._prerequisites.append(task.get_task_id())

    def get_prerequisites(self) -> List[str]:
        """
        Get the list of prerequisite task IDs.

        Returns:
            List of task IDs that must be completed first
        """
        return self._prerequisites

    def has_prerequisites(self) -> bool:
        """Return whether this task has prerequisites."""
        return len(self._prerequisites) > 0

    def are_prerequisites_met(self, completed_task_ids: List[str]) -> bool:
        """
        Check if all prerequisite tasks have been completed/scheduled.

        Args:
            completed_task_ids: List of task IDs that have been scheduled

        Returns:
            True if all prerequisites are met, False otherwise
        """
        return all(prereq_id in completed_task_ids for prereq_id in self._prerequisites)

    # ===== FEATURE 3: DYNAMIC PRIORITY ADJUSTMENT =====

    def set_last_completed(self, completion_date: date) -> None:
        """
        Set the date this task was last completed.

        Args:
            completion_date: Date when task was last completed
        """
        self._last_completed = completion_date
        self._update_days_since_completion()

    def get_last_completed(self) -> Optional[date]:
        """Get the date this task was last completed."""
        return self._last_completed

    def _update_days_since_completion(self) -> None:
        """Update the number of days since last completion (private helper)."""
        if self._last_completed:
            delta = date.today() - self._last_completed
            self._days_since_completion = delta.days
        else:
            self._days_since_completion = 999  # Never completed

    def get_days_since_completion(self) -> int:
        """Get number of days since task was last completed."""
        self._update_days_since_completion()
        return self._days_since_completion

    def get_dynamic_priority(self) -> int:
        """
        Calculate dynamic priority based on time since last completion.
        Priority increases if task hasn't been done recently.

        Returns:
            Adjusted priority value
        """
        self._update_days_since_completion()

        # Base priority
        adjusted_priority = self._base_priority

        # Boost priority based on days since completion
        if self._days_since_completion >= 7:
            adjusted_priority += 3  # High boost for week-old tasks
        elif self._days_since_completion >= 3:
            adjusted_priority += 2  # Medium boost for 3+ day old tasks
        elif self._days_since_completion >= 1:
            adjusted_priority += 1  # Small boost for day-old tasks

        # Cap priority at 10
        return min(adjusted_priority, 10)

    def reset_to_base_priority(self) -> None:
        """Reset priority to its original base value."""
        self._priority = self._base_priority

    def apply_dynamic_priority(self) -> None:
        """Apply dynamic priority adjustment based on completion history."""
        self._priority = self.get_dynamic_priority()


class ScheduledTask:
    """Represents a task scheduled at a specific time in a plan."""

    def __init__(self, task: Task, start_time: str, end_time: str, order: int):
        """
        Initialize a ScheduledTask instance.

        Args:
            task: The Task to schedule
            start_time: Start time (e.g., "08:00")
            end_time: End time (e.g., "08:30")
            order: Order in the schedule (1st, 2nd, 3rd, etc.)
        """
        self._task = task
        self._start_time = start_time
        self._end_time = end_time
        self._order = order

    def get_task(self) -> Task:
        """Return the associated Task."""
        return self._task

    def get_start_time(self) -> str:
        """Return the start time."""
        return self._start_time

    def get_end_time(self) -> str:
        """Return the end time."""
        return self._end_time

    def get_order(self) -> int:
        """Return the order in the schedule."""
        return self._order


class Plan:
    """Represents a daily care plan with scheduled tasks and explanations."""

    def __init__(self):
        """Initialize a Plan instance."""
        self._scheduled_tasks = []
        self._total_time_minutes = 0
        self._explanation = ""
        self._plan_date = date.today()
        self._excluded_tasks = []

    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> None:
        """
        Add a scheduled task to the plan.

        Args:
            scheduled_task: ScheduledTask to add
        """
        self._scheduled_tasks.append(scheduled_task)
        self._total_time_minutes += scheduled_task.get_task().get_duration()

    def get_scheduled_tasks(self) -> List[ScheduledTask]:
        """Return all scheduled tasks."""
        return self._scheduled_tasks

    def get_total_time(self) -> int:
        """Return total time of all scheduled tasks in minutes."""
        return self._total_time_minutes

    def set_explanation(self, explanation: str) -> None:
        """
        Set the explanation for the plan.

        Args:
            explanation: Text explaining scheduling decisions
        """
        self._explanation = explanation

    def get_explanation(self) -> str:
        """Return the plan explanation."""
        return self._explanation

    def get_excluded_tasks(self) -> List[Task]:
        """Return tasks that couldn't be scheduled."""
        return self._excluded_tasks

    def add_excluded_task(self, task: Task) -> None:
        """
        Add a task that couldn't be scheduled.

        Args:
            task: Task that was excluded from the plan
        """
        self._excluded_tasks.append(task)

    def get_plan_date(self) -> date:
        """Return the date for this plan."""
        return self._plan_date


class Scheduler:
    """Core scheduling logic that generates optimized daily plans."""

    def __init__(self, owner: Owner, pet: Pet):
        """
        Initialize a Scheduler instance.

        Args:
            owner: The Owner for whom to schedule
            pet: The Pet requiring care
        """
        self._tasks = []
        self._owner = owner
        self._pet = pet
        self._constraints = {}

    def add_task(self, task: Task) -> None:
        """
        Add a task to the scheduler.

        Args:
            task: Task to add
        """
        self._tasks.append(task)

    def complete_task(self, task_id: str) -> Optional[Task]:
        """
        Mark a task as complete and handle recurrence.

        Args:
            task_id: UUID of the task to complete

        Returns:
            New Task instance if task recurs, None otherwise
        """
        for task in self._tasks:
            if task.get_task_id() == task_id:
                # Complete the task and get next occurrence
                next_task = task.complete_and_recur()

                # If task recurs, add the new instance to scheduler
                if next_task:
                    self._tasks.append(next_task)
                    return next_task

                return None

        return None

    def get_recurring_tasks(self) -> List[Task]:
        """
        Get all tasks that are set to recur.

        Returns:
            List of recurring tasks
        """
        return [task for task in self._tasks if task.get_recurs()]

    def get_completed_tasks(self) -> List[Task]:
        """
        Get all tasks that have been completed.

        Returns:
            List of completed tasks
        """
        return [task for task in self._tasks if task.is_completed()]

    def remove_task(self, task_id: str) -> None:
        """
        Remove a task by ID.

        Args:
            task_id: UUID of the task to remove
        """
        self._tasks = [t for t in self._tasks if t.get_task_id() != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks."""
        return self._tasks

    def generate_plan(self) -> Plan:
        """
        Generate an optimized daily plan based on tasks and constraints.

        Now includes:
        - Time-window constraints
        - Task dependencies
        - Dynamic priority adjustment

        Returns:
            A Plan object with scheduled tasks and explanation
        """
        plan = Plan()

        if not self._tasks:
            plan.set_explanation("No tasks to schedule.")
            return plan

        # Step 0: Apply dynamic priority adjustment to all tasks
        for task in self._tasks:
            task.apply_dynamic_priority()

        # Step 1: Prioritize tasks (mandatory first, then by priority)
        prioritized_tasks = self._prioritize_tasks()

        # Step 2: Optimize the order of tasks
        optimized_tasks = self._optimize_schedule(prioritized_tasks)

        # Step 3: Schedule tasks within time constraints, respecting time windows and dependencies
        available_time = self._owner.get_available_time()
        current_time = 480  # Start at 8:00 AM (480 minutes from midnight)
        scheduled_count = 0
        excluded_count = 0
        scheduled_task_ids = []  # Track scheduled task IDs for dependency checking

        explanation_parts = []
        explanation_parts.append(
            f"Scheduling plan for {self._pet.get_name()} ({self._pet.get_species()})."
        )
        explanation_parts.append(
            f"Owner: {self._owner.get_name()}, Available time: {available_time} minutes."
        )

        # Track tasks that couldn't be scheduled and reasons
        excluded_reasons = {}

        for task in optimized_tasks:
            task_duration = task.get_duration()

            # Calculate potential start time
            start_hour = current_time // 60
            start_min = current_time % 60
            start_time = f"{start_hour:02d}:{start_min:02d}"

            # Check 1: Time constraint
            if plan.get_total_time() + task_duration > available_time:
                plan.add_excluded_task(task)
                excluded_reasons[task.get_name()] = "insufficient time"
                excluded_count += 1
                continue

            # Check 2: Time-window constraint
            if task.has_time_window() and not task.can_schedule_at_time(start_time):
                # Try to find a valid time slot
                valid_slot_found = False
                temp_time = current_time

                # Look ahead for a valid time slot (up to end of day)
                while temp_time < 1320:  # 22:00 (end of scheduling day)
                    temp_hour = temp_time // 60
                    temp_min = temp_time % 60
                    temp_start = f"{temp_hour:02d}:{temp_min:02d}"

                    if task.can_schedule_at_time(temp_start):
                        current_time = temp_time
                        start_hour = temp_hour
                        start_min = temp_min
                        start_time = temp_start
                        valid_slot_found = True
                        break
                    temp_time += 15  # Check every 15 minutes

                if not valid_slot_found:
                    plan.add_excluded_task(task)
                    window_start, window_end = task.get_time_window()
                    excluded_reasons[task.get_name()] = (
                        f"time window ({window_start}-{window_end}) conflict"
                    )
                    excluded_count += 1
                    continue

            # Check 3: Dependency constraint - check if prerequisites were excluded
            if task.has_prerequisites():
                prereq_excluded = False
                for prereq_id in task.get_prerequisites():
                    if prereq_id in [
                        t.get_task_id() for t in plan.get_excluded_tasks()
                    ]:
                        prereq_excluded = True
                        break

                if prereq_excluded:
                    plan.add_excluded_task(task)
                    excluded_reasons[task.get_name()] = "prerequisite not scheduled"
                    excluded_count += 1
                    continue

            # All checks passed - schedule the task
            current_time += task_duration
            end_hour = current_time // 60
            end_min = current_time % 60
            end_time = f"{end_hour:02d}:{end_min:02d}"

            scheduled_task = ScheduledTask(
                task, start_time, end_time, scheduled_count + 1
            )
            plan.add_scheduled_task(scheduled_task)
            scheduled_task_ids.append(task.get_task_id())
            scheduled_count += 1

        # Build explanation
        explanation_parts.append(
            f"\nScheduled {scheduled_count} task(s) totaling {plan.get_total_time()} minutes."
        )

        if scheduled_count > 0:
            explanation_parts.append("\nAdvanced Scheduling Features:")
            explanation_parts.append(
                "✓ Dynamic priority adjustment based on completion history"
            )
            explanation_parts.append("✓ Time-window constraints respected")
            explanation_parts.append("✓ Task dependencies enforced")
            explanation_parts.append("\nPrioritization strategy:")
            explanation_parts.append("1. Mandatory tasks scheduled first")
            explanation_parts.append("2. Priority adjusted for tasks not done recently")
            explanation_parts.append(
                "3. Tasks sorted by adjusted priority (highest first)"
            )
            explanation_parts.append("4. Tasks optimized for logical flow")

        if excluded_count > 0:
            explanation_parts.append(
                f"\n{excluded_count} task(s) could not be scheduled:"
            )
            for task in plan.get_excluded_tasks():
                reason = excluded_reasons.get(task.get_name(), "unknown reason")
                explanation_parts.append(
                    f"  - {task.get_name()} ({task.get_duration()} min, priority {task.get_priority()}) - {reason}"
                )

        plan.set_explanation("\n".join(explanation_parts))
        return plan

    def _prioritize_tasks(self) -> List[Task]:
        """
        Sort tasks by priority (private helper method).
        Now uses dynamic priority that adjusts based on completion history.

        Returns:
            Sorted list of tasks
        """
        # Sort by: mandatory first, then by dynamic priority (descending), then by duration (ascending)
        return sorted(
            self._tasks,
            key=lambda t: (
                not t.is_mandatory(),
                -t.get_dynamic_priority(),
                t.get_duration(),
            ),
        )

    def _check_time_constraints(self, tasks: List[Task]) -> bool:
        """
        Check if tasks fit within available time (private helper method).

        Args:
            tasks: List of tasks to check

        Returns:
            True if tasks fit, False otherwise
        """
        total_duration = sum(task.get_duration() for task in tasks)
        return total_duration <= self._owner.get_available_time()

    def _optimize_schedule(self, tasks: List[Task]) -> List[Task]:
        """
        Optimize the order of tasks (private helper method).
        Now includes dependency resolution using topological sort.

        Args:
            tasks: List of tasks to optimize

        Returns:
            Optimized list of tasks with dependencies resolved
        """
        # Resolve dependencies using topological sort
        # The topological sort already handles priority ordering
        # and ensures dependencies come before dependent tasks
        return self._resolve_dependencies(tasks)

    def _resolve_dependencies(self, tasks: List[Task]) -> List[Task]:
        """
        Resolve task dependencies using topological sort.

        Args:
            tasks: List of tasks to sort

        Returns:
            List of tasks in dependency order
        """
        # Define task type ordering for logical flow
        task_order = {
            "feeding": 1,
            "meds": 2,
            "walk": 3,
            "enrichment": 4,
            "grooming": 5,
            "training": 6,
            "playtime": 7,
        }

        # Build task lookup by ID
        task_by_id = {task.get_task_id(): task for task in tasks}

        # Build dependency graph
        in_degree = {task.get_task_id(): 0 for task in tasks}
        adjacency = {task.get_task_id(): [] for task in tasks}

        for task in tasks:
            for prereq_id in task.get_prerequisites():
                if prereq_id in task_by_id:
                    adjacency[prereq_id].append(task.get_task_id())
                    in_degree[task.get_task_id()] += 1

        # Topological sort using Kahn's algorithm
        queue = [tid for tid in in_degree if in_degree[tid] == 0]
        sorted_ids = []

        while queue:
            # Sort queue by priority and task type to maintain logical ordering
            queue.sort(
                key=lambda tid: (
                    not task_by_id[tid].is_mandatory(),
                    -task_by_id[tid].get_priority(),
                    task_order.get(task_by_id[tid].get_task_type().lower(), 99),
                )
            )

            current_id = queue.pop(0)
            sorted_ids.append(current_id)

            for neighbor_id in adjacency[current_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        # Return tasks in sorted order
        return [task_by_id[tid] for tid in sorted_ids if tid in task_by_id]
