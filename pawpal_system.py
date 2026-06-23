"""
Backend logic for PawPal+.

Class skeletons generated from `uml.mmd`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional, Tuple


TaskStatusFilter = Literal["all", "open", "done"]


@dataclass
class Task:
    """A single care activity: what to do, when, how often, and whether it is done."""

    description: str
    time_minutes: Optional[int]
    frequency: str
    completed: bool = False
    duration_minutes: int = 30
    priority: int = 1
    # For frequency == "weekly": which weekday this recurs (0=Monday … 6=Sunday). Ignored otherwise.
    weekly_weekday: Optional[int] = None

    def total_block_minutes(self) -> int:
        """Minutes the task occupies on the timeline (duration + buffer)."""
        return self.duration_minutes + self.getRequiredTimeBuffer()

    def applies_for_weekday(self, weekday: int) -> bool:
        """
        Whether this task is due on the given calendar weekday.
        `weekday` uses datetime semantics: 0=Monday … 6=Sunday.
        """
        freq = self.frequency.lower().strip()
        if freq == "daily":
            return True
        if freq == "as_needed":
            return True
        if freq == "weekly":
            if self.weekly_weekday is None:
                return True
            return weekday == self.weekly_weekday
        return True

    def giveUrgencyScore(self) -> float:
        """Return scheduling urgency for open tasks; completed tasks score 0."""
        if self.completed:
            return 0.0
        base = float(self.priority) * 10.0
        freq = self.frequency.lower().strip()
        freq_bonus = {"daily": 3.0, "weekly": 1.0, "as_needed": 0.5}.get(freq, 1.0)
        return base + freq_bonus

    def getRequiredTimeBuffer(self) -> int:
        """Return extra minutes reserved around a task when placing it on the timeline."""
        return max(5, self.duration_minutes // 10)

    def mark_complete(self) -> None:
        """Mark this task as done for scheduling and urgency purposes."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def getRecommendedFrequence(self) -> str:
        """Return a short species- and age-based care frequency guideline string."""
        s = self.species.lower()
        if s == "dog":
            if self.age <= 2:
                return "3 short walks daily; meals 3x for puppies"
            if self.age >= 8:
                return "2 gentle walks daily; meals 2x; joint care"
            return "2–3 walks daily; meals 2x"
        if s == "cat":
            return "Enrichment/play 2x daily; meals 2–3 small portions"
        return "Follow vet guidance for species-specific care"

    def getHealthConstraints(self) -> List[str]:
        """Return bullet-style health notes for this pet's life stage and species."""
        s = self.species.lower()
        notes: List[str] = []
        if self.age < 1:
            notes.append("Young animal: frequent meals, vet schedule, supervised exercise")
        if s == "dog" and self.age >= 8:
            notes.append("Senior dog: joint-friendly movement, weight and dental checks")
        if s == "cat" and self.age >= 10:
            notes.append("Senior cat: hydration, litter access, renal monitoring")
        return notes if notes else ["Maintain regular wellness exams"]


@dataclass
class Owner:
    pets: List[Pet] = field(default_factory=list)

    def get_all_tasks(self) -> List[Task]:
        """Return every task from every pet in a single flat list."""
        return [task for pet in self.pets for task in pet.tasks]

    def iter_tasks_with_pet(self) -> List[Tuple[Pet, Task]]:
        """Return (pet, task) pairs for all tasks across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


def filter_tasks_with_pets(
    owner: Owner,
    pet: Optional[Pet] = None,
    status: TaskStatusFilter = "all",
) -> List[Tuple[Pet, Task]]:
    """Filter (pet, task) pairs by optional pet and completion status."""
    pairs = owner.iter_tasks_with_pet()
    if pet is not None:
        pairs = [(p, t) for p, t in pairs if p is pet]
    if status == "open":
        pairs = [(p, t) for p, t in pairs if not t.completed]
    elif status == "done":
        pairs = [(p, t) for p, t in pairs if t.completed]
    return pairs


def sort_pairs_by_preferred_time(pairs: List[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
    """Sort by preferred start (tasks without preferred time sort last, then by pet name, description)."""
    out = list(pairs)

    def key(pt: Tuple[Pet, Task]) -> Tuple[int, int, str, str]:
        pet, task = pt
        has_pref = task.time_minutes is not None
        pref = task.time_minutes if has_pref else 0
        # no preferred time -> sort after those with time
        return (0 if has_pref else 1, pref, pet.name.lower(), task.description.lower())

    out.sort(key=key)
    return out


def sort_pairs_by_urgency(pairs: List[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
    """Sort by urgency score and priority (highest first), then pet and description for stability."""
    out = list(pairs)

    def key(pt: Tuple[Pet, Task]) -> Tuple[float, int, str, str]:
        pet, task = pt
        return (
            -task.giveUrgencyScore(),
            -task.priority,
            pet.name.lower(),
            task.description.lower(),
        )

    out.sort(key=key)
    return out


@dataclass(frozen=True)
class TimeRangeConflict:
    """Two scheduled or preferred blocks that overlap in time."""

    pet_a: str
    task_a: str
    start_a: int
    end_a: int
    pet_b: str
    task_b: str
    start_b: int
    end_b: int


def _intervals_overlap(s1: int, e1: int, s2: int, e2: int) -> bool:
    return not (e1 <= s2 or e2 <= s1)


def detect_preferred_time_conflicts(owner: Owner) -> List[TimeRangeConflict]:
    """
    Find overlapping preferred-time windows among open tasks that have a preferred start.
    Each window is [time_minutes, time_minutes + total_block_minutes).
    """
    items: List[Tuple[Pet, Task, int, int]] = []
    for pet, task in owner.iter_tasks_with_pet():
        if task.completed or task.time_minutes is None:
            continue
        start = task.time_minutes
        end = start + task.total_block_minutes()
        items.append((pet, task, start, end))

    conflicts: List[TimeRangeConflict] = []
    for i in range(len(items)):
        pet_a, task_a, sa, ea = items[i]
        for j in range(i + 1, len(items)):
            pet_b, task_b, sb, eb = items[j]
            if _intervals_overlap(sa, ea, sb, eb):
                conflicts.append(
                    TimeRangeConflict(
                        pet_a=pet_a.name,
                        task_a=task_a.description,
                        start_a=sa,
                        end_a=ea,
                        pet_b=pet_b.name,
                        task_b=task_b.description,
                        start_b=sb,
                        end_b=eb,
                    )
                )
    return conflicts


def detect_plan_conflicts(
    plan: List[Tuple[Pet, Task, int]],
) -> List[TimeRangeConflict]:
    """Find overlapping blocks in a generated plan (same pet or different pets)."""
    enriched: List[Tuple[Pet, Task, int, int]] = []
    for pet, task, slot_start in plan:
        end = slot_start + task.total_block_minutes()
        enriched.append((pet, task, slot_start, end))

    conflicts: List[TimeRangeConflict] = []
    for i in range(len(enriched)):
        pet_a, task_a, sa, ea = enriched[i]
        for j in range(i + 1, len(enriched)):
            pet_b, task_b, sb, eb = enriched[j]
            if _intervals_overlap(sa, ea, sb, eb):
                conflicts.append(
                    TimeRangeConflict(
                        pet_a=pet_a.name,
                        task_a=task_a.description,
                        start_a=sa,
                        end_a=ea,
                        pet_b=pet_b.name,
                        task_b=task_b.description,
                        start_b=sb,
                        end_b=eb,
                    )
                )
    return conflicts


@dataclass
class Scheduler:
    """
    Retrieves tasks via the Owner (each Pet's task list), then sorts and places them in a day.
    """

    owner: Owner
    constraintsList: List[Any] = field(default_factory=list)

    def _open_tasks_with_pets(
        self, weekday: Optional[int] = None
    ) -> List[Tuple[Pet, Task]]:
        """List incomplete tasks paired with the pet that owns each task, optionally for a weekday."""
        pairs = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.tasks
            if not task.completed
        ]
        if weekday is not None:
            pairs = [(p, t) for p, t in pairs if t.applies_for_weekday(weekday)]
        return pairs

    def sortTasksByPriority(self, weekday: Optional[int] = None) -> List[Tuple[Pet, Task]]:
        """Sort open (pet, task) pairs by urgency score then priority, highest first."""
        pairs = self._open_tasks_with_pets(weekday=weekday)
        pairs.sort(
            key=lambda pt: (pt[1].giveUrgencyScore(), pt[1].priority),
            reverse=True,
        )
        return pairs

    def findAvailableSlot(
        self,
        start_of_day_minutes: int,
        end_of_day_minutes: int,
        needed_minutes: int,
        occupied: List[Tuple[int, int]],
    ) -> Optional[int]:
        """Find the first start minute that fits `needed_minutes` in gaps of occupied ranges."""
        cursor = start_of_day_minutes
        for block_start, block_end in sorted(occupied):
            if block_start > cursor and block_start - cursor >= needed_minutes:
                return cursor
            cursor = max(cursor, block_end)
        if end_of_day_minutes - cursor >= needed_minutes:
            return cursor
        return None

    def generateOptimizedSchedule(
        self,
        day_start_minutes: int = 7 * 60,
        day_end_minutes: int = 22 * 60,
        weekday: Optional[int] = None,
    ) -> List[Tuple[Pet, Task, int]]:
        """
        Build a non-overlapping day plan: each row is (pet, task, start_minutes_from_midnight).
        If `weekday` is set (0=Monday … 6=Sunday), only tasks that apply on that day are scheduled.
        """
        sorted_pairs = self.sortTasksByPriority(weekday=weekday)
        occupied: List[Tuple[int, int]] = []
        plan: List[Tuple[Pet, Task, int]] = []
        budget = day_end_minutes - day_start_minutes
        used = 0

        for pet, task in sorted_pairs:
            need = task.total_block_minutes()
            if need > budget or used + need > budget:
                continue

            slot: Optional[int] = None
            pref = task.time_minutes
            if pref is not None:
                end_pref = pref + need
                fits_window = day_start_minutes <= pref and end_pref <= day_end_minutes
                overlaps = any(not (end_pref <= s or pref >= e) for s, e in occupied)
                if fits_window and not overlaps:
                    slot = pref

            if slot is None:
                slot = self.findAvailableSlot(
                    day_start_minutes, day_end_minutes, need, occupied
                )
            if slot is None:
                continue

            occupied.append((slot, slot + need))
            plan.append((pet, task, slot))
            used += need

        return plan
