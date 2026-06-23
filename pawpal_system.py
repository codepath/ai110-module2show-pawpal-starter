from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta

# Enforced time format for all time strings across the system (HH:MM, 24-hour)
TIME_FORMAT = "%H:%M"


# ---------------------------------------------------------------------------
# Task — a single schedulable care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    task_type: str
    required: bool
    earliest_start: str | None = None   # must follow TIME_FORMAT ("%H:%M")
    latest_end: str | None = None       # must follow TIME_FORMAT ("%H:%M")
    completed: bool = False
    recurrence: str | None = None   # "daily" | "weekly" | "weekdays" | None
    pet_name: str | None = None     # set automatically by Pet.add_task()
    due_date: date | None = None    # populated by next_occurrence(); None = no specific date

    @staticmethod
    def _parse_time(time_str: str) -> datetime:
        """Parse a time string using TIME_FORMAT so all comparisons are consistent."""
        return datetime.strptime(time_str, TIME_FORMAT)

    def priority_value(self) -> int:
        """Map priority label to a numeric value for sorting."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 0)

    def weighted_score(self, current_time: str | None = None) -> float:
        """Compute a composite urgency score used by rank_by_urgency().

        Combines four independent components into one float so tasks can be
        ranked by a richer signal than priority alone:

        - **Base priority** — low=10, medium=20, high=30.
        - **Required bonus** — +20 if ``required`` is True.
        - **Care type bonus** — +12 if ``task_type == "medication"``.
        - **Deadline urgency bonus** — derived from minutes remaining until
          ``latest_end``. A passed deadline (≤ 0 min) or imminent one (≤ 60 min)
          scores +15; ≤ 120 min scores +8; ≤ 240 min scores +3; beyond = +0.
          Tasks with no ``latest_end`` always score +0 for this component.

        Both ``current_time`` and ``latest_end`` are normalised through
        ``TIME_FORMAT`` so the subtraction always compares same-epoch datetimes
        (``1900-01-01 HH:MM``). Passing ``current_time=None`` uses
        ``datetime.now()`` normalised to the same epoch.

        Args:
            current_time (str | None): Reference time as ``HH:MM``. Defaults
                to the current wall-clock time when None.

        Returns:
            float: Composite urgency score. Maximum achievable value is 77.0
                   (high + required + medication + overdue/imminent deadline).
        """
        base = {"low": 10, "medium": 20, "high": 30}.get(self.priority, 0)
        required_bonus = 20 if self.required else 0
        care_bonus = 12 if self.task_type == "medication" else 0

        if self.latest_end is None:
            urgency_bonus = 0
        else:
            # Normalise both sides to the 1900-01-01 epoch used by _parse_time
            if current_time is None:
                now = datetime.strptime(datetime.now().strftime(TIME_FORMAT), TIME_FORMAT)
            else:
                now = self._parse_time(current_time)
            deadline = self._parse_time(self.latest_end)
            minutes_remaining = (deadline - now).total_seconds() / 60

            if minutes_remaining <= 60:    # covers overdue (≤0) and imminent
                urgency_bonus = 15
            elif minutes_remaining <= 120:
                urgency_bonus = 8
            elif minutes_remaining <= 240:
                urgency_bonus = 3
            else:
                urgency_bonus = 0

        return float(base + required_bonus + care_bonus + urgency_bonus)

    def fits_in_window(self, start: str, end: str) -> bool:
        """Return True if the task's timing constraints fall within start–end."""
        window_start = self._parse_time(start)
        window_end = self._parse_time(end)
        if self.earliest_start and self._parse_time(self.earliest_start) < window_start:
            return False
        if self.latest_end and self._parse_time(self.latest_end) > window_end:
            return False
        return True

    def is_required(self) -> bool:
        """Kept as a method for polymorphic access; returns self.required."""
        return self.required

    def can_be_scheduled(self, available_minutes: int) -> bool:
        """Return True if the task fits within the given available time."""
        return self.duration_minutes <= available_minutes

    def is_recurring(self) -> bool:
        """Check whether this task repeats on a schedule.

        Returns:
            bool: True if ``recurrence`` is set to any non-None value
                  ("daily", "weekly", or "weekdays"); False otherwise.
        """
        return self.recurrence is not None

    def next_occurrence(self) -> Task | None:
        """Create a fresh, incomplete copy of this task for its next scheduled date.

        Advances from ``due_date`` (or today if unset) using ``timedelta``:

        - ``"daily"``    — ``base + timedelta(days=1)``
        - ``"weekly"``   — ``base + timedelta(weeks=1)``
        - ``"weekdays"`` — ``base + timedelta(days=1)``, then skips Saturday
          (weekday 5) and Sunday (weekday 6) until a Mon–Fri is reached.

        Uses ``dataclasses.replace()`` so every field is preserved and only
        ``completed`` (reset to False) and ``due_date`` (advanced) are changed.

        Returns:
            Task: A new Task instance with ``completed=False`` and the
                  calculated next ``due_date``.
            None: If this task has no recurrence set (``is_recurring()`` is False)
                  or if the recurrence value is unrecognised.
        """
        if not self.is_recurring():
            return None

        base = self.due_date if self.due_date is not None else date.today()

        if self.recurrence == "daily":
            next_date = base + timedelta(days=1)

        elif self.recurrence == "weekly":
            next_date = base + timedelta(weeks=1)

        elif self.recurrence == "weekdays":
            next_date = base + timedelta(days=1)
            # Keep advancing until we land on Mon–Fri (weekday() 0–4)
            while next_date.weekday() >= 5:
                next_date += timedelta(days=1)

        else:
            return None

        # dataclasses.replace() copies every field and overrides only what we specify
        return replace(self, completed=False, due_date=next_date)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


# ---------------------------------------------------------------------------
# Pet — stores pet details and a list of tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int | None
    special_needs: list[str] = field(default_factory=list)
    daily_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def needs_medication(self) -> bool:
        """Return True if any special need mentions medication."""
        return any(
            "medication" in need.lower() or "med" in need.lower()
            for need in self.special_needs
        )

    def requires_extra_care(self) -> bool:
        """Return True if the pet has any special needs."""
        return len(self.special_needs) > 0

    def care_summary(self) -> str:
        """Return a human-readable summary of the pet's care profile."""
        age_str = str(self.age) if self.age is not None else "unknown"
        lines = [f"{self.name} ({self.species}, age {age_str})"]
        if self.daily_needs:
            lines.append(f"  Daily needs: {', '.join(self.daily_needs)}")
        if self.special_needs:
            lines.append(f"  Special needs: {', '.join(self.special_needs)}")
        if not self.daily_needs and not self.special_needs:
            lines.append("  No specific needs recorded.")
        return "\n".join(lines)

    def add_task(self, task: Task) -> None:
        """Attach an existing Task to this pet and record the pet's name on it."""
        task.pet_name = self.name
        self.tasks.append(task)

    def generate_tasks(self) -> list[Task]:
        """Convert daily_needs and special_needs into Task objects and attach them.

        Establishes the Pet -> Task relationship from the UML: tasks originate
        from a pet's declared needs rather than being created independently.
        """
        generated: list[Task] = []

        for need in self.daily_needs:
            generated.append(Task(
                title=need,
                duration_minutes=15,
                priority="medium",
                task_type="daily",
                required=True,
            ))

        for need in self.special_needs:
            priority = "high" if "medication" in need.lower() else "medium"
            generated.append(Task(
                title=need,
                duration_minutes=10,
                priority=priority,
                task_type="special",
                required=True,
            ))

        self.tasks.extend(generated)
        return generated


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and provides access to all their tasks
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        name: str,
        preferences: dict,
        available_minutes: int,
        available_windows: list[tuple[str, str]] | None = None,
    ) -> None:
        """Initialise owner with identity, time budget, preferences, and an empty pet list."""
        self.name = name
        self.preferences = preferences          # e.g. {"morning": True, "evening": False}
        self.available_minutes = available_minutes
        self.available_windows = available_windows or []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flatten and return every task across all owned pets.

        This is the primary retrieval point for the Scheduler — it only needs
        to call owner.all_tasks() rather than iterating pets itself.
        """
        return [task for pet in self.pets for task in pet.tasks]

    def is_available(self, duration: int) -> bool:
        """Return True if the owner has enough minutes left for the given duration."""
        return self.remaining_availability() >= duration

    def prefers_time_of_day(self, time_of_day: str) -> bool:
        """Return the owner's preference for a given time of day label."""
        return bool(self.preferences.get(time_of_day, False))

    def remaining_availability(self) -> int:
        """Return how many minutes the owner still has available."""
        return self.available_minutes

    def tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Retrieve every task that belongs to a specific pet.

        The name comparison is case-insensitive so "buddy" and "Buddy" both match.

        Args:
            pet_name (str): The name of the pet whose tasks should be returned.

        Returns:
            list[Task]: A new list containing the matched pet's tasks, or an
                        empty list if no pet with that name is registered.
        """
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return list(pet.tasks)
        return []

    def use_minutes(self, duration: int) -> None:
        """Deduct duration from available_minutes.

        Raises ValueError if duration exceeds remaining availability so
        available_minutes can never go negative.
        """
        if duration > self.available_minutes:
            raise ValueError(
                f"Cannot use {duration} minutes — only "
                f"{self.available_minutes} remaining."
            )
        self.available_minutes -= duration


# ---------------------------------------------------------------------------
# Scheduler — retrieves, organises, and manages tasks across all pets
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialise the scheduler with an owner whose pets and tasks it will manage."""
        self.owner = owner

    def select_tasks(self) -> list[Task]:
        """Return tasks that are incomplete and fit within remaining availability."""
        return [
            task for task in self.owner.all_tasks()
            if not task.completed
            and task.can_be_scheduled(self.owner.remaining_availability())
        ]

    def order_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks: required first, then by descending priority value."""
        return sorted(tasks, key=lambda t: (not t.is_required(), -t.priority_value()))

    def allocate_time(self, tasks: list[Task]) -> list[dict]:
        """Assign tasks to the schedule while owner time permits.

        Each allocated task is recorded as a dict and deducted from the
        owner's available minutes.
        """
        schedule = []
        for task in tasks:
            if self.owner.is_available(task.duration_minutes):
                self.owner.use_minutes(task.duration_minutes)
                schedule.append({
                    "title": task.title,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "required": task.required,
                    "task_type": task.task_type,
                })
        return schedule

    def generate_schedule(self) -> list[dict]:
        """Run the full pipeline: select → order → allocate → validate.

        Conflict warnings are printed before the schedule is returned so the
        owner is informed without the program crashing or the schedule being blocked.
        """
        for warning in self.conflict_warnings():
            print(warning)
        selected = self.select_tasks()
        ordered = self.order_tasks(selected)
        schedule = self.allocate_time(ordered)
        self.validate_schedule(schedule)
        return schedule

    def validate_schedule(self, schedule: list[dict]) -> bool:
        """Verify available_minutes did not go negative after allocation.

        allocate_time() is the primary guard via use_minutes(); this is a
        defensive sanity check that remaining availability is non-negative.
        """
        if self.owner.remaining_availability() < 0:
            raise RuntimeError("Schedule overran owner's available time budget.")
        return True

    def explain_plan(self, schedule: list[dict]) -> str:
        """Return a human-readable explanation of the generated schedule."""
        if not schedule:
            return f"{self.owner.name} has no tasks scheduled today."
        lines = [f"Schedule for {self.owner.name}:"]
        for i, entry in enumerate(schedule, 1):
            req_label = "required" if entry["required"] else "optional"
            lines.append(
                f"  {i}. {entry['title']} — {entry['duration_minutes']} min "
                f"[{entry['priority']} priority, {req_label}]"
            )
        lines.append(
            f"\nTime remaining after scheduling: "
            f"{self.owner.remaining_availability()} minutes"
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Sort by time
    # ------------------------------------------------------------------

    def rank_by_urgency(
        self,
        tasks: list[Task],
        current_time: str | None = None,
    ) -> list[Task]:
        """Sort tasks by composite urgency score, highest first.

        Delegates all score computation to ``Task.weighted_score()`` so that
        scoring logic stays on the Task and this method only handles ordering.
        The original list is not modified.

        Args:
            tasks (list[Task]): The task list to rank.
            current_time (str | None): Reference time passed through to
                ``weighted_score()``. If None, each call uses ``datetime.now()``.

        Returns:
            list[Task]: A new list sorted by ``weighted_score`` descending.
        """
        return sorted(
            tasks,
            key=lambda t: t.weighted_score(current_time),
            reverse=True,
        )

    def sort_tasks_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort a list of tasks in chronological order by their earliest start time.

        A lambda key function is passed to ``sorted()``. Python calls it once per
        task and compares the returned values to determine order. Each task maps to
        a two-element tuple ``(bucket, time)`` so that tasks with a defined window
        always precede tasks without one:

        - ``(0, parsed_time)`` — task has ``earliest_start``; sorted chronologically.
        - ``(1, datetime.min)`` — task has no ``earliest_start``; floats to the end.

        Args:
            tasks (list[Task]): The task list to sort. The original list is not
                                modified.

        Returns:
            list[Task]: A new list sorted by ``earliest_start`` ascending, with
                        tasks that have no time window at the end.
        """
        return sorted(
            tasks,
            key=lambda t: (
                (1, datetime.min)                    # no window → end of list
                if t.earliest_start is None
                else (0, Task._parse_time(t.earliest_start))  # HH:MM → chronological
            ),
        )

    # ------------------------------------------------------------------
    # Filter by pet / status
    # ------------------------------------------------------------------

    def filter_tasks(
        self,
        tasks: list[Task],
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Filter a task list by pet ownership and/or completion status.

        Filters are applied in sequence and can be combined freely. Passing
        neither argument returns the original list unchanged.

        Pet matching uses object identity (``id()``) rather than string
        comparison so that two tasks with the same title belonging to
        different pets are never confused.

        Args:
            tasks (list[Task]): The source task list to filter.
            pet_name (str | None): If provided, only tasks whose ``pet_name``
                matches this value (via ``Owner.tasks_for_pet``) are kept.
                Defaults to None (no pet filter).
            completed (bool | None): If True, return only completed tasks.
                If False, return only pending tasks. If None, return all.
                Defaults to None.

        Returns:
            list[Task]: A new list containing only the tasks that satisfy
                        all supplied filter criteria.
        """
        if pet_name is not None:
            pet_ids = {id(t) for t in self.owner.tasks_for_pet(pet_name)}
            tasks = [t for t in tasks if id(t) in pet_ids]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    # ------------------------------------------------------------------
    # Recurring tasks
    # ------------------------------------------------------------------

    def recurring_tasks(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return every task that has a recurrence schedule set.

        Args:
            tasks (list[Task] | None): The task list to inspect. If None,
                defaults to ``owner.all_tasks()`` (all tasks across all pets).

        Returns:
            list[Task]: Tasks for which ``is_recurring()`` returns True.
                        Returns an empty list if none are recurring.
        """
        source = tasks if tasks is not None else self.owner.all_tasks()
        return [t for t in source if t.is_recurring()]

    def complete_and_reschedule(self, task: Task) -> Task | None:
        """Mark a recurring task done and automatically queue its next occurrence.

        Combines completion and rescheduling into one atomic step so callers
        never have to call ``mark_complete()`` and ``next_occurrence()`` separately.

        Steps:
            1. Call ``task.mark_complete()`` on the existing instance.
            2. Call ``task.next_occurrence()`` to produce a fresh copy with the
               advanced ``due_date`` calculated via ``timedelta``.
            3. Locate the pet that owns this task by matching ``task.pet_name``
               against ``owner.pets`` and attach the new task via ``pet.add_task()``.

        Args:
            task (Task): The recurring task that has just been completed.
                         Must have ``pet_name`` set (done automatically by
                         ``Pet.add_task()``) for the new occurrence to be
                         assigned to the correct pet.

        Returns:
            Task: The newly created next occurrence, already attached to the pet.
            None: If the task is not recurring (``is_recurring()`` is False).
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is None:
            return None

        # Find the owning pet and attach the next occurrence
        for pet in self.owner.pets:
            if pet.name == task.pet_name:
                pet.add_task(next_task)
                break

        return next_task

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[tuple[Task, Task]]:
        """Find all pairs of tasks whose time windows overlap.

        Only tasks that have *both* ``earliest_start`` and ``latest_end`` set
        are considered; tasks missing either bound are ignored (treated as
        unconstrained and therefore incapable of clashing).

        Two tasks A and B conflict when their windows intersect:
            ``A.earliest_start < B.latest_end  AND  B.earliest_start < A.latest_end``

        The O(n²) pair comparison is intentional — pet schedules are small
        (typically < 20 tasks) so the simplicity outweighs any optimisation gain.

        Args:
            tasks (list[Task] | None): Task list to scan. Defaults to
                ``owner.all_tasks()`` if None.

        Returns:
            list[tuple[Task, Task]]: Unordered pairs ``(a, b)`` where the two
                tasks have overlapping windows. Returns an empty list if there
                are no conflicts.
        """
        source = tasks if tasks is not None else self.owner.all_tasks()
        bounded = [t for t in source if t.earliest_start and t.latest_end]
        conflicts: list[tuple[Task, Task]] = []
        for i, a in enumerate(bounded):
            a_start = Task._parse_time(a.earliest_start)
            a_end   = Task._parse_time(a.latest_end)
            for b in bounded[i + 1:]:
                b_start = Task._parse_time(b.earliest_start)
                b_end   = Task._parse_time(b.latest_end)
                if a_start < b_end and b_start < a_end:
                    conflicts.append((a, b))
        return conflicts

    def conflict_warnings(self, tasks: list[Task] | None = None) -> list[str]:
        """Produce a human-readable warning message for every conflicting task pair.

        Wraps ``detect_conflicts()`` and formats each pair as a single string.
        This method never raises — it always returns a list, making it safe to
        call at any point in the scheduling pipeline without guarding against
        exceptions.

        Each warning identifies:
        - Both task titles and their ``HH:MM``-bounded windows.
        - Whether the clash is between tasks of the *same pet* or *different pets*
          (cross-pet), so the owner knows whether one or both pets are affected.

        Args:
            tasks (list[Task] | None): Task list to check. Defaults to
                ``owner.all_tasks()`` if None.

        Returns:
            list[str]: One warning string per conflicting pair. Returns an empty
                       list when no conflicts are found.
        """
        warnings: list[str] = []
        for a, b in self.detect_conflicts(tasks):
            pet_a = a.pet_name or "unknown pet"
            pet_b = b.pet_name or "unknown pet"

            if pet_a == pet_b:
                scope = f"same pet ({pet_a})"
            else:
                scope = f"cross-pet: {pet_a} vs {pet_b}"

            warnings.append(
                f"WARNING: '{a.title}' ({a.earliest_start}-{a.latest_end}) "
                f"overlaps '{b.title}' ({b.earliest_start}-{b.latest_end}) "
                f"[{scope}]"
            )
        return warnings
