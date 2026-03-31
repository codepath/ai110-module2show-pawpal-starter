from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TaskType(Enum):
    WALK = "walk"
    FEED = "feed"
    VET = "vet"
    MEDICATION = "medication"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"


class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class RecurrenceScope(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# ---------------------------------------------------------------------------
# AvailabilityWindow
# ---------------------------------------------------------------------------

@dataclass
class AvailabilityWindow:
    day: str                        # e.g. "Monday"
    start_time: datetime.time
    end_time: datetime.time

    def duration_minutes(self) -> int:
        """Calculate the duration of the availability window in minutes."""
        start_delta = datetime.timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
        end_delta = datetime.timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)
        result = int((end_delta - start_delta).total_seconds() // 60)
        assert result >= 0, f"duration_minutes must be non-negative, got {result}"
        return result


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    care_metrics: dict[str, str] = field(default_factory=dict)
    _tasks: list[Task] = field(default_factory=list, repr=False)

    def add_task(self, task: Task) -> None:
        """Add a new task to the pet's list of tasks."""
        task.pet_name = self.name
        self._tasks.append(task)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    weekly_availability: list[AvailabilityWindow] = field(default_factory=list)
    available_month_days: list[int] = field(default_factory=list)
    _pets: list[Pet] = field(default_factory=list, repr=False)

    def add_pet(self, pet: Pet) -> None:
        """Add a new pet to the owner's list of pets."""
        original_length = len(self._pets)
        self._pets.append(pet)
        assert pet in self._pets, f"pet {pet.name} was not added to the pets list"
        assert len(self._pets) == original_length + 1, f"expected {original_length + 1} pets, got {len(self._pets)}"

    def set_availability(self, day: str, windows: list[AvailabilityWindow]) -> None:
        """Set or update the owner's availability windows for a specific day."""
        self.weekly_availability = [w for w in self.weekly_availability if w.day != day]
        self.weekly_availability.extend(list(windows))

        for w in windows:
            assert w in self.weekly_availability, f"window {w} was not added to weekly_availability"
        for w in self.weekly_availability:
            if w.day == day:
                assert w in windows, f"stale window {w} for {day} was not removed"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    task_type: TaskType
    priority: Priority
    scope: RecurrenceScope
    duration_minutes: int
    assigned_day: Optional[str] = None
    scheduled_time: Optional[datetime.time] = None
    completed: bool = False
    pet_name: Optional[str] = None

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def edit(self, priority: Priority, duration: int) -> None:
        """Update the priority and duration of the task."""
        self.priority = priority
        self.duration_minutes = duration
        assert isinstance(self.priority, Priority), f"priority must be a Priority, got {type(self.priority)}"
        assert isinstance(self.duration_minutes, int) and self.duration_minutes > 0, f"duration_minutes must be a positive int, got {self.duration_minutes}"


# ---------------------------------------------------------------------------
# DailySchedule
# ---------------------------------------------------------------------------

@dataclass
class DailySchedule:
    date: datetime.date
    daily_tasks: list[Task] = field(default_factory=list)
    non_daily_tasks_on_day: list[Task] = field(default_factory=list)
    rationale: str = ""

    def generate(self, owner: Owner, tasks: list[Task]) -> None:
        """Generate a daily schedule of tasks based on the owner's availability."""
        scheduler = Scheduler()
        day_name = self.date.strftime("%A")

        # Separate daily vs non-daily tasks
        daily_tasks = [t for t in tasks if t.scope == RecurrenceScope.DAILY]
        non_daily = [t for t in tasks if t.scope != RecurrenceScope.DAILY]

        # Fit daily tasks into the owner's availability windows for this day
        day_windows = [w for w in owner.weekly_availability if w.day == day_name]
        fitted = scheduler.fit_tasks_into_slots(daily_tasks, day_windows)

        # Assign scheduled times by walking through windows in order
        current_time: Optional[datetime.time] = None
        window_idx = 0
        remaining = {id(w): w.duration_minutes() for w in day_windows}
        for task in fitted:
            for i in range(window_idx, len(day_windows)):
                w = day_windows[i]
                if remaining[id(w)] >= task.duration_minutes:
                    elapsed = w.duration_minutes() - remaining[id(w)]
                    start = datetime.datetime.combine(self.date, w.start_time) + datetime.timedelta(minutes=elapsed)
                    task.scheduled_time = start.time()
                    remaining[id(w)] -= task.duration_minutes
                    break

        self.daily_tasks = sorted(fitted, key=lambda t: t.scheduled_time or datetime.time.min)

        # Collect weekly/monthly tasks assigned to this day
        day_of_month = self.date.day
        self.non_daily_tasks_on_day = [
            t for t in non_daily
            if (t.scope == RecurrenceScope.WEEKLY and t.assigned_day == day_name)
            or (t.scope == RecurrenceScope.MONTHLY and t.assigned_day == day_name)
        ]

        # Generate rationale
        self.rationale = scheduler.generate_rationale(self)

        # Assertions
        assert all(t.scope == RecurrenceScope.DAILY for t in self.daily_tasks), "daily_tasks must only contain DAILY tasks"
        assert all(t.scope != RecurrenceScope.DAILY for t in self.non_daily_tasks_on_day), "non_daily_tasks must not contain DAILY tasks"
        assert isinstance(self.rationale, str) and len(self.rationale) > 0, "rationale must be a non-empty string"

    def display(self) -> str:
        """Return a formatted string representation of the daily schedule."""
        lines: list[str] = [f"=== Daily Schedule for {self.date.strftime('%A, %B %d, %Y')} ==="]

        if self.daily_tasks:
            lines.append("\nScheduled Tasks:")
            for t in self.daily_tasks:
                time_str = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "TBD"
                lines.append(f"  {time_str} - {t.name} ({t.task_type.value}, {t.priority.name}, {t.duration_minutes}min)")
        else:
            lines.append("\n  No daily tasks scheduled.")

        if self.non_daily_tasks_on_day:
            lines.append("\nAlso Due Today (weekly/monthly):")
            for t in self.non_daily_tasks_on_day:
                lines.append(f"  - {t.name} ({t.task_type.value}, {t.priority.name}, {t.scope.value}, {t.duration_minutes}min)")

        if self.rationale:
            lines.append(f"\nRationale:\n  {self.rationale}")

        result = "\n".join(lines)
        assert isinstance(result, str) and len(result) > 0, "display must return a non-empty string"
        return result


# ---------------------------------------------------------------------------
# WeeklyMonthlyPlan
# ---------------------------------------------------------------------------

@dataclass
class WeeklyMonthlyPlan:
    tasks_by_day: dict[str, list[Task]] = field(default_factory=dict)

    def generate(self, tasks: list[Task]) -> None:
        """Generate a weekly or monthly plan by grouping tasks by their assigned day."""
        self.tasks_by_day = {}
        for task in tasks:
            if task.scope in (RecurrenceScope.WEEKLY, RecurrenceScope.MONTHLY):
                day = task.assigned_day or "Unassigned"
                if day not in self.tasks_by_day:
                    self.tasks_by_day[day] = []
                self.tasks_by_day[day].append(task)

        # Assertions
        total = sum(len(ts) for ts in self.tasks_by_day.values())
        expected = [t for t in tasks if t.scope in (RecurrenceScope.WEEKLY, RecurrenceScope.MONTHLY)]
        assert total == len(expected), f"expected {len(expected)} weekly/monthly tasks, got {total}"
        for day, day_tasks in self.tasks_by_day.items():
            for t in day_tasks:
                assert t.scope in (RecurrenceScope.WEEKLY, RecurrenceScope.MONTHLY), (
                    f"task {t.name} has scope {t.scope}, expected WEEKLY or MONTHLY"
                )

    def display(self) -> str:
        """Return a formatted string representation of the weekly/monthly plan."""
        lines: list[str] = ["=== Weekly / Monthly Plan ==="]
        if not self.tasks_by_day:
            lines.append("  No weekly/monthly tasks scheduled.")
        for day, tasks in self.tasks_by_day.items():
            lines.append(f"\n{day}:")
            for t in tasks:
                lines.append(f"  - {t.name} ({t.task_type.value}, {t.priority.name}, {t.scope.value}, {t.duration_minutes}min)")
        result = "\n".join(lines)
        assert isinstance(result, str) and len(result) > 0, "display must return a non-empty string"
        return result


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

@dataclass
class Scheduler:

    def fit_tasks_into_slots(
        self,
        tasks: list[Task],
        windows: list[AvailabilityWindow],
    ) -> list[Task]:
        """Fit an ordered list of tasks into available time slots based on constraints."""
        ordered = self.order_by_priority(tasks)
        remaining_minutes = {id(w): w.duration_minutes() for w in windows}
        fitted: list[Task] = []

        for task in ordered:
            for window in windows:
                if self.check_constraints(task, window) and remaining_minutes[id(window)] >= task.duration_minutes:
                    remaining_minutes[id(window)] -= task.duration_minutes
                    fitted.append(task)
                    break

        assert all(t in tasks for t in fitted), "fitted contains a task not in the original list"
        assert len(fitted) <= len(tasks), f"fitted more tasks ({len(fitted)}) than provided ({len(tasks)})"
        for t in fitted:
            assert any(
                self.check_constraints(t, w) for w in windows
            ), f"fitted task {t.name} does not satisfy constraints for any window"
        return fitted

    def order_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks in descending order of their priority."""
        result = sorted(tasks, key=lambda t: t.priority.value, reverse=True)

        assert len(result) == len(tasks), f"expected {len(tasks)} tasks, got {len(result)}"
        for i in range(len(result) - 1):
            assert result[i].priority.value >= result[i + 1].priority.value, (
                f"tasks not sorted: {result[i].priority} before {result[i + 1].priority}"
            )
        return result

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks in ascending order of their scheduled_time attribute."""
        result = sorted(tasks, key=lambda t: t.scheduled_time or datetime.time.min)

        assert len(result) == len(tasks), f"expected {len(tasks)} tasks, got {len(result)}"
        for i in range(len(result) - 1):
            time_a = result[i].scheduled_time or datetime.time.min
            time_b = result[i + 1].scheduled_time or datetime.time.min
            assert time_a <= time_b, (
                f"tasks not sorted by time: {time_a} before {time_b}"
            )
        return result

    def filter_by_pet(self, tasks: list[Task], pet_name: str) -> list[Task]:
        """Filter tasks to only those assigned to a specific pet by name."""
        result = [t for t in tasks if t.pet_name == pet_name]

        assert all(t.pet_name == pet_name for t in result), (
            f"filter_by_pet returned a task not belonging to {pet_name}"
        )
        assert len(result) <= len(tasks), f"filtered more tasks ({len(result)}) than provided ({len(tasks)})"
        return result

    def filter_by_completion(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Filter tasks by their completion status."""
        result = [t for t in tasks if t.completed == completed]

        assert all(t.completed == completed for t in result), (
            f"filter_by_completion returned a task with completed={not completed}"
        )
        assert len(result) <= len(tasks), f"filtered more tasks ({len(result)}) than provided ({len(tasks)})"
        return result

    def check_constraints(self, task: Task, window: AvailabilityWindow) -> bool:
        """Check if a task can be scheduled within a specific availability window."""
        fits = task.duration_minutes <= window.duration_minutes()
        day_matches = task.assigned_day is None or task.assigned_day == window.day

        result = fits and day_matches

        assert isinstance(result, bool), f"expected bool, got {type(result)}"
        if result:
            assert task.duration_minutes <= window.duration_minutes(), (
                f"task {task.name} ({task.duration_minutes}min) cannot fit in window ({window.duration_minutes()}min)"
            )
        return result

    def generate_rationale(self, schedule: DailySchedule) -> str:
        """Generate a textual rationale explaining the created daily schedule."""
        lines: list[str] = []

        if schedule.daily_tasks:
            high = [t for t in schedule.daily_tasks if t.priority == Priority.HIGH]
            med = [t for t in schedule.daily_tasks if t.priority == Priority.MEDIUM]
            low = [t for t in schedule.daily_tasks if t.priority == Priority.LOW]
            lines.append(f"Scheduled {len(schedule.daily_tasks)} daily task(s): "
                         f"{len(high)} high, {len(med)} medium, {len(low)} low priority.")
        else:
            lines.append("No daily tasks could be scheduled.")

        if schedule.non_daily_tasks_on_day:
            names = ", ".join(t.name for t in schedule.non_daily_tasks_on_day)
            lines.append(f"Also due today (weekly/monthly): {names}.")

        lines.append("Tasks were ordered by priority and fitted into available time windows.")

        result = " ".join(lines)
        assert isinstance(result, str) and len(result) > 0, "rationale must be a non-empty string"
        return result

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Detect scheduling conflicts where two tasks overlap in the same time slot."""
        scheduled = [t for t in tasks if t.scheduled_time is not None]
        scheduled = sorted(scheduled, key=lambda t: t.scheduled_time or datetime.time.min)
        conflicts: list[tuple[Task, Task]] = []

        for i in range(len(scheduled)):
            start_a = scheduled[i].scheduled_time
            end_a = (datetime.datetime.combine(datetime.date.today(), start_a)
                     + datetime.timedelta(minutes=scheduled[i].duration_minutes)).time()
            for j in range(i + 1, len(scheduled)):
                start_b = scheduled[j].scheduled_time
                if start_b < end_a:
                    conflicts.append((scheduled[i], scheduled[j]))

        assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in conflicts), (
            "each conflict must be a tuple of two tasks"
        )
        assert all(pair[0] in tasks and pair[1] in tasks for pair in conflicts), (
            "conflict contains a task not in the original list"
        )
        return conflicts
