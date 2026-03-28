"""
PawPal+ — backend logic layer
Classes: Owner, Pet, Task, ScheduledItem, Scheduler
"""

from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Data classes (pure data holders)
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_start: str = "08:00"   # 24-h string, e.g. "08:00"
    available_end: str = "20:00"

    def set_availability(self, start: str, end: str) -> None:
        """Update the owner's available time window."""
        self.available_start = start
        self.available_end = end

    def get_preferences(self) -> dict:
        """Return owner preferences (extendable in later iterations)."""
        return {
            "available_start": self.available_start,
            "available_end": self.available_end,
        }


@dataclass
class Pet:
    name: str
    species: str          # "dog", "cat", "other"
    owner: Owner

    def get_care_needs(self) -> List[str]:
        """Return a list of default care task titles for this species."""
        defaults = {
            "dog": ["Morning walk", "Evening walk", "Feeding", "Grooming"],
            "cat": ["Feeding", "Litter box cleaning", "Playtime"],
        }
        return defaults.get(self.species, ["Feeding", "Check-in"])


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str         # "low", "medium", "high"

    _PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == "high"

    def priority_value(self) -> int:
        """Numeric priority for sorting (lower = more urgent)."""
        return self._PRIORITY_ORDER.get(self.priority, 99)

    def __repr__(self) -> str:
        return f"Task('{self.title}', {self.duration_minutes}min, {self.priority})"


# ---------------------------------------------------------------------------
# Schedule output types
# ---------------------------------------------------------------------------

@dataclass
class ScheduledItem:
    task: Task
    start_time: str       # "HH:MM"
    end_time: str         # "HH:MM"
    reason: str = ""

    def display(self) -> str:
        """Return a human-readable string for this scheduled slot."""
        flag = " ★" if self.task.is_high_priority() else ""
        return (
            f"{self.start_time}–{self.end_time}  {self.task.title}{flag}"
            f"  ({self.task.duration_minutes} min)"
            + (f"\n  → {self.reason}" if self.reason else "")
        )


# ---------------------------------------------------------------------------
# Scheduler — the planning engine
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, pet: Pet):
        self.pet: Pet = pet
        self.tasks: List[Task] = []
        self.schedule: List[ScheduledItem] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the pending task list."""
        self.tasks.append(task)

    def build_schedule(self) -> List[ScheduledItem]:
        """
        Order tasks by priority (high → medium → low), then by duration
        (shorter first within the same priority level). Fit them
        sequentially into the owner's available window.

        Returns a list of ScheduledItem objects.
        """
        self.schedule = []

        # Sort: primary = priority value, secondary = duration
        sorted_tasks = sorted(
            self.tasks, key=lambda t: (t.priority_value(), t.duration_minutes)
        )

        current_time = self.pet.owner.available_start
        for task in sorted_tasks:
            end_time = self._add_minutes(current_time, task.duration_minutes)
            if end_time > self.pet.owner.available_end:
                break   # no more room in the day
            reason = self._build_reason(task)
            self.schedule.append(
                ScheduledItem(task=task, start_time=current_time, end_time=end_time, reason=reason)
            )
            current_time = end_time

        return self.schedule

    def explain_plan(self) -> str:
        """Return a full text explanation of the schedule."""
        if not self.schedule:
            return "No schedule generated yet. Call build_schedule() first."
        lines = [f"Daily plan for {self.pet.name} ({self.pet.owner.name})\n"]
        for item in self.schedule:
            lines.append(item.display())
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
        if task.is_high_priority():
            return f"High-priority task scheduled first."
        if task.priority == "medium":
            return f"Medium-priority task scheduled after urgent items."
        return f"Low-priority task scheduled if time allows."
