"""
PawPal+ — backend logic layer
Classes: Task, Pet, Owner, ScheduledItem, Scheduler
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


# ---------------------------------------------------------------------------
# Task — a single care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str                       # "low" | "medium" | "high"
    frequency: str = "daily"            # "daily" | "weekly" | "as-needed"
    completed: bool = False
    due_date: Optional[date] = None     # date this task is next due

    _PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def reset(self) -> None:
        """Reset completion status (e.g. start of a new day)."""
        self.completed = False

    def is_high_priority(self) -> bool:
        """Return True if priority is 'high'."""
        return self.priority == "high"

    def priority_value(self) -> int:
        """Return a numeric sort key — lower = scheduled sooner."""
        return self._PRIORITY_ORDER.get(self.priority, 99)

    def next_occurrence(self) -> "Task":
        """
        Return a fresh, incomplete copy of this task due on its next occurrence.

        Uses timedelta so the next due date is always accurate:
          daily   → today + 1 day
          weekly  → today + 7 days
          as-needed → no automatic recurrence; returns None
        """
        delta_map = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        delta = delta_map.get(self.frequency)
        if delta is None:
            return None   # as-needed tasks don't recur automatically
        base = self.due_date if self.due_date else date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            completed=False,
            due_date=base + delta,
        )

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        due    = f", due {self.due_date}" if self.due_date else ""
        return (
            f"[{status}] {self.title} ({self.duration_minutes} min, "
            f"{self.priority}, {self.frequency}{due})"
        )


# ---------------------------------------------------------------------------
# Pet — stores pet details and owns its task list
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str                          # "dog" | "cat" | "other"
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Returns True if found and removed."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.title != title]
        return len(self.tasks) < before

    def get_pending_tasks(self) -> List[Task]:
        """Return tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return tasks that are already done."""
        return [t for t in self.tasks if t.completed]

    def reset_daily_tasks(self) -> None:
        """Reset all daily tasks at the start of a new day."""
        for task in self.tasks:
            if task.frequency == "daily":
                task.reset()

    def load_default_tasks(self) -> None:
        """Populate species-appropriate default Task objects if the list is empty."""
        if self.tasks:
            return
        defaults = {
            "dog": [
                Task("Morning walk",     30, "high",   "daily"),
                Task("Evening walk",     30, "high",   "daily"),
                Task("Feeding",          15, "high",   "daily"),
                Task("Grooming",         20, "medium", "weekly"),
            ],
            "cat": [
                Task("Feeding",          10, "high",   "daily"),
                Task("Litter box clean", 10, "high",   "daily"),
                Task("Playtime",         15, "medium", "daily"),
            ],
        }
        for task in defaults.get(self.species, [Task("Check-in", 10, "medium", "daily")]):
            self.add_task(task)

    def __repr__(self) -> str:
        return f"Pet({self.name!r}, {self.species}, age={self.age}, tasks={len(self.tasks)})"


# ---------------------------------------------------------------------------
# Owner — manages multiple pets; single source of truth for availability
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_start: str = "08:00"    # 24-h "HH:MM"
    available_end: str   = "20:00"
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        """Remove a pet by name. Returns True if found."""
        before = len(self.pets)
        self.pets = [p for p in self.pets if p.name != name]
        return len(self.pets) < before

    def get_pet(self, name: str) -> Optional[Pet]:
        """Look up a pet by name (case-insensitive)."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> List[tuple]:
        """Return every (pet, task) pair across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> List[tuple]:
        """Return only incomplete (pet, task) pairs across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.get_pending_tasks()]

    def set_availability(self, start: str, end: str) -> None:
        """Update the owner's available time window."""
        self.available_start = start
        self.available_end = end

    def get_preferences(self) -> dict:
        """Return owner time preferences as a dict."""
        return {
            "available_start": self.available_start,
            "available_end": self.available_end,
        }

    def __repr__(self) -> str:
        return (
            f"Owner({self.name!r}, "
            f"{self.available_start}–{self.available_end}, "
            f"pets={[p.name for p in self.pets]})"
        )


# ---------------------------------------------------------------------------
# ScheduledItem — one time-slot in the final daily plan
# ---------------------------------------------------------------------------

@dataclass
class ScheduledItem:
    pet: Pet
    task: Task
    start_time: str      # "HH:MM"
    end_time: str        # "HH:MM"
    reason: str = ""

    def display(self) -> str:
        """Return a human-readable one-line representation of this slot."""
        flag      = " ★" if self.task.is_high_priority() else ""
        pet_label = f"[{self.pet.name}] "
        line = (
            f"{self.start_time}–{self.end_time}  "
            f"{pet_label}{self.task.title}{flag}"
            f"  ({self.task.duration_minutes} min)"
        )
        if self.reason:
            line += f"\n    → {self.reason}"
        return line


# ---------------------------------------------------------------------------
# Scheduler — the brain that retrieves, organizes, and manages tasks
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner: Owner = owner
        self.schedule: List[ScheduledItem] = []
        self.skipped: List[tuple] = []    # (pet, task) pairs that didn't fit

    # ------------------------------------------------------------------
    # Core scheduling
    # ------------------------------------------------------------------

    def build_schedule(self) -> List[ScheduledItem]:
        """
        Collect all pending tasks from the owner's pets, sort by priority then
        duration, and fit them sequentially into the owner's time window.
        Tasks that don't fit are stored in self.skipped (not silently dropped).
        """
        self.schedule = []
        self.skipped  = []

        pending = self.owner.get_all_pending_tasks()
        sorted_pairs = sorted(
            pending, key=lambda pair: (pair[1].priority_value(), pair[1].duration_minutes)
        )

        current_time = self.owner.available_start
        for pet, task in sorted_pairs:
            end_time = self._add_minutes(current_time, task.duration_minutes)
            if end_time > self.owner.available_end:
                self.skipped.append((pet, task))
                continue
            self.schedule.append(
                ScheduledItem(
                    pet=pet,
                    task=task,
                    start_time=current_time,
                    end_time=end_time,
                    reason=self._build_reason(task),
                )
            )
            current_time = end_time

        return self.schedule

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sort_by_time(self) -> List[ScheduledItem]:
        """
        Return the schedule sorted by start_time ascending.

        "HH:MM" zero-padded strings compare correctly with Python's default
        string ordering (lexicographic), so a simple lambda is sufficient:
          key=lambda item: item.start_time
        """
        return sorted(self.schedule, key=lambda item: item.start_time)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[ScheduledItem]:
        """
        Return a filtered view of the current schedule.

        Parameters
        ----------
        pet_name  : if given, keep only items belonging to that pet (case-insensitive).
        completed : if True, keep only completed items; if False, only pending.
                    If None, completion status is not filtered.
        """
        results = self.schedule
        if pet_name is not None:
            results = [i for i in results if i.pet.name.lower() == pet_name.lower()]
        if completed is not None:
            results = [i for i in results if i.task.completed == completed]
        return results

    # ------------------------------------------------------------------
    # Mark complete + recurring task automation
    # ------------------------------------------------------------------

    def mark_complete(self, task_title: str) -> bool:
        """
        Mark a scheduled task as completed by title.

        For recurring tasks (daily / weekly), automatically creates the next
        occurrence and appends it to the pet's task list so it appears in
        tomorrow's schedule. Returns True if the task was found.
        """
        for item in self.schedule:
            if item.task.title == task_title:
                item.task.complete()
                # Auto-schedule next occurrence for recurring tasks
                next_task = item.task.next_occurrence()
                if next_task is not None:
                    item.pet.add_task(next_task)
                return True
        return False

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> List[str]:
        """
        Check for overlapping time slots across all scheduled items.

        Strategy: convert each slot to integer minutes, then compare every
        pair with an overlap test:  A.start < B.end  and  B.start < A.end.
        Returns a list of human-readable warning strings (empty = no conflicts).

        Tradeoff: this is O(n²) — acceptable for a single day of pet tasks
        (typically < 20 items), but would need a sweep-line algorithm at scale.
        """
        warnings = []
        items = self.schedule

        def to_minutes(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                a_start, a_end = to_minutes(a.start_time), to_minutes(a.end_time)
                b_start, b_end = to_minutes(b.start_time), to_minutes(b.end_time)
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"⚠ CONFLICT: [{a.pet.name}] {a.task.title} "
                        f"({a.start_time}–{a.end_time}) overlaps with "
                        f"[{b.pet.name}] {b.task.title} "
                        f"({b.start_time}–{b.end_time})"
                    )
        return warnings

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_todays_tasks(self) -> List[ScheduledItem]:
        """Return scheduled items that are not yet completed."""
        return [item for item in self.schedule if not item.task.completed]

    def explain_plan(self) -> str:
        """Return a full human-readable explanation of the schedule."""
        if not self.schedule:
            return "No schedule yet — call build_schedule() first."

        pet_names = ", ".join(p.name for p in self.owner.pets)
        lines = [
            f"Daily plan for {self.owner.name}'s pets: {pet_names}",
            f"Window: {self.owner.available_start} – {self.owner.available_end}",
            "",
        ]
        for item in self.schedule:
            lines.append(item.display())

        if self.skipped:
            lines.append("\nSkipped (didn't fit in the time window):")
            for pet, task in self.skipped:
                lines.append(f"  • [{pet.name}] {task.title} ({task.duration_minutes} min)")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _add_minutes(time_str: str, minutes: int) -> str:
        """Add minutes to a 'HH:MM' string and return a new 'HH:MM' string."""
        h, m = map(int, time_str.split(":"))
        total = h * 60 + m + minutes
        return f"{total // 60:02d}:{total % 60:02d}"

    @staticmethod
    def _build_reason(task: Task) -> str:
        """Generate a short explanation of why this task was scheduled when it was."""
        reasons = {
            "high":   "High-priority — scheduled first.",
            "medium": "Medium-priority — scheduled after urgent tasks.",
            "low":    "Low-priority — scheduled if time allows.",
        }
        freq_note = f" Repeats {task.frequency}." if task.frequency != "daily" else ""
        return reasons.get(task.priority, "") + freq_note
