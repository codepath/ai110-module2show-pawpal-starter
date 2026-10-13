"""
PawPal+ scheduling logic.

Classes:
  - Task: one pet care activity (what, how long, how important, when preferred
    or fixed to an exact time)
  - Pet: a pet and its list of care tasks
  - Owner: the person caring for the pets, with a daily time budget
  - ScheduledItem: a task placed at a specific time, with the reason it was chosen
  - DailyPlan: the generated schedule plus any tasks that didn't fit
  - Scheduler: chooses and orders tasks for one pet's day
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

# Earliest start time (HH:MM) for each preferred part of the day.
TIME_SLOTS = {"morning": "08:00", "afternoon": "12:00", "evening": "17:00"}
SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, None: 3}


def _parse_time(hhmm: str) -> datetime:
    return datetime.strptime(hhmm, "%H:%M")


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    preferred_time: Optional[str] = None  # "morning", "afternoon", "evening", or None
    fixed_time: Optional[str] = None  # exact start "HH:MM" (e.g. vet visit), or None

    def __post_init__(self) -> None:
        self.priority = self.priority.lower()
        if self.priority not in PRIORITY_RANK:
            raise ValueError(
                f"priority must be one of {list(PRIORITY_RANK)}, got {self.priority!r}"
            )
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.preferred_time is not None and self.preferred_time not in TIME_SLOTS:
            raise ValueError(
                f"preferred_time must be one of {list(TIME_SLOTS)} or None, "
                f"got {self.preferred_time!r}"
            )
        if self.fixed_time is not None:
            try:
                _parse_time(self.fixed_time)
            except ValueError:
                raise ValueError(
                    f"fixed_time must be in HH:MM format, got {self.fixed_time!r}"
                ) from None
            if self.preferred_time is not None:
                raise ValueError("a task cannot have both fixed_time and preferred_time")

    @property
    def priority_rank(self) -> int:
        return PRIORITY_RANK[self.priority]


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove the first task with this title. Returns True if one was removed."""
        for i, task in enumerate(self.tasks):
            if task.title == title:
                del self.tasks[i]
                return True
        return False


@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    day_start: str = "08:00"
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)


@dataclass
class ScheduledItem:
    task: Task
    start: datetime
    reason: str

    @property
    def end(self) -> datetime:
        return self.start + timedelta(minutes=self.task.duration_minutes)

    def time_range(self) -> str:
        return f"{self.start:%H:%M}–{self.end:%H:%M}"

    def overlaps(self, start: datetime, end: datetime) -> bool:
        return self.start < end and start < self.end


@dataclass
class DailyPlan:
    pet: Pet
    items: List[ScheduledItem] = field(default_factory=list)
    skipped: List[Tuple[Task, str]] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    @property
    def total_minutes(self) -> int:
        return sum(item.task.duration_minutes for item in self.items)

    def explain(self) -> str:
        """Human-readable summary of the plan and why each task is (or isn't) in it."""
        lines = [f"Daily plan for {self.pet.name} ({self.pet.species}):"]
        if not self.items:
            lines.append("  (nothing scheduled)")
        for item in self.items:
            lines.append(
                f"  {item.time_range()} — {item.task.title} "
                f"({item.task.duration_minutes} min) [priority: {item.task.priority}]"
            )
            lines.append(f"      why: {item.reason}")
        for task, reason in self.skipped:
            lines.append(f"  SKIPPED — {task.title}: {reason}")
        for conflict in self.conflicts:
            lines.append(f"  CONFLICT — {conflict}")
        lines.append(f"Total scheduled: {self.total_minutes} min")
        return "\n".join(lines)


class Scheduler:
    """Builds a one-day plan for a pet within the owner's time budget."""

    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet

    def sort_by_importance(self, tasks: List[Task]) -> List[Task]:
        """Highest priority first; among equal priority, shorter tasks first
        so more tasks fit in the budget."""
        return sorted(tasks, key=lambda t: (-t.priority_rank, t.duration_minutes))

    def select_tasks(self, tasks: List[Task]) -> Tuple[List[Task], List[Tuple[Task, str]]]:
        """Greedily pick tasks in importance order until the time budget runs out."""
        chosen: List[Task] = []
        skipped: List[Tuple[Task, str]] = []
        remaining = self.owner.available_minutes

        for task in self.sort_by_importance(tasks):
            if task.duration_minutes <= remaining:
                chosen.append(task)
                remaining -= task.duration_minutes
            else:
                skipped.append(
                    (task, f"needs {task.duration_minutes} min but only {remaining} min left")
                )
        return chosen, skipped

    def build_plan(self) -> DailyPlan:
        plan = DailyPlan(pet=self.pet)

        # Resolve fixed-time clashes BEFORE applying the time budget, so a
        # dropped task doesn't use up minutes another task could have had.
        # Higher priority wins a conflict; on a tie, the task listed first in
        # pet.tasks wins (sorted() is stable, so listing order breaks ties).
        fixed = sorted(
            (t for t in self.pet.tasks if t.fixed_time is not None),
            key=lambda t: -t.priority_rank,
        )
        kept_fixed: List[ScheduledItem] = []
        dropped = set()
        for task in fixed:
            start = _parse_time(task.fixed_time)
            end = start + timedelta(minutes=task.duration_minutes)
            clash = next((i for i in kept_fixed if i.overlaps(start, end)), None)
            if clash is not None:
                dropped.add(id(task))
                plan.skipped.append(
                    (task, f"conflicts with {clash.task.title} at {clash.time_range()}")
                )
                plan.conflicts.append(
                    f"{task.title} ({start:%H:%M}–{end:%H:%M}) overlaps "
                    f"{clash.task.title} ({clash.time_range()}); "
                    f"kept {clash.task.title}"
                )
                continue
            kept_fixed.append(ScheduledItem(task, start, self._reason(task, start)))

        chosen, budget_skipped = self.select_tasks(
            [t for t in self.pet.tasks if id(t) not in dropped]
        )
        plan.skipped.extend(budget_skipped)
        chosen_ids = {id(t) for t in chosen}
        fixed_items = [i for i in kept_fixed if id(i.task) in chosen_ids]

        # Lay flexible tasks out across the day: preferred part of day first,
        # then priority, so a high-priority evening task still lands in the evening.
        ordered = sorted(
            (t for t in chosen if t.fixed_time is None),
            key=lambda t: (SLOT_ORDER[t.preferred_time], -t.priority_rank),
        )

        cursor = _parse_time(self.owner.day_start)
        for task in ordered:
            start = cursor
            if task.preferred_time is not None:
                start = max(cursor, _parse_time(TIME_SLOTS[task.preferred_time]))
            # Never overlap a fixed task: jump past each one it would hit
            # (fixed items are checked in start order, so one pass is enough).
            duration = timedelta(minutes=task.duration_minutes)
            for item in sorted(fixed_items, key=lambda i: i.start):
                if item.overlaps(start, start + duration):
                    start = item.end
            plan.items.append(ScheduledItem(task, start, self._reason(task, start)))
            cursor = start + duration

        plan.items = sorted(plan.items + fixed_items, key=lambda i: i.start)
        return plan

    def _reason(self, task: Task, start: datetime) -> str:
        reason = f"{task.priority} priority, fits in the {self.owner.available_minutes}-min budget"
        if task.fixed_time is not None:
            return reason + f"; fixed appointment at {task.fixed_time}"
        if task.preferred_time is None:
            return reason + "; no time preference, placed in the next open slot"
        slot_start = _parse_time(TIME_SLOTS[task.preferred_time])
        if start == slot_start:
            return reason + f"; placed at the start of the {task.preferred_time} as preferred"
        return reason + f"; placed in the {task.preferred_time} after earlier tasks finished"


if __name__ == "__main__":
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Morning walk", 30, "high", "morning"))
    mochi.add_task(Task("Breakfast", 10, "high", "morning"))
    mochi.add_task(Task("Heartworm meds", 5, "high", "evening"))
    mochi.add_task(Task("Puzzle toy", 20, "medium"))
    mochi.add_task(Task("Brushing", 15, "low", "afternoon"))
    mochi.add_task(Task("Long hike", 60, "low"))
    mochi.add_task(Task("Vet visit", 30, "high", fixed_time="08:15"))
    owner.add_pet(mochi)

    print(Scheduler(owner, mochi).build_plan().explain())
