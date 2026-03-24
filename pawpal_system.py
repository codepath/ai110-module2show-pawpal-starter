from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import List, Optional, Dict, Tuple


@dataclass
class Task:
    """Represents a single activity for a pet.

    Attributes:
        description: text description
        date: scheduled date
        scheduled_time: time of day
        frequency: e.g. 'once', 'daily', 'weekly'
        duration: optional duration of the activity
        completed: whether the task is done
    """
    description: str
    date: date
    scheduled_time: time
    frequency: str = "once"
    duration: Optional[timedelta] = None
    completed: bool = False

    def mark_complete(self) -> None:
        self.completed = True

    def reschedule(self, new_date: date, new_time: time) -> None:
        self.date = new_date
        self.scheduled_time = new_time

    def get_start_datetime(self) -> datetime:
        return datetime.combine(self.date, self.scheduled_time)

    def get_end_datetime(self) -> Optional[datetime]:
        if self.duration is None:
            return None
        end = self.get_start_datetime() + self.duration
        # handle cross-day if duration pushes into next day
        return end


@dataclass
class Pet:
    """Pet stores basic details and the tasks relevant to this pet."""
    name: str
    species: Optional[str] = None
    age: Optional[int] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        try:
            self.tasks.remove(task)
        except ValueError:
            pass

    def get_tasks(self) -> List[Task]:
        return list(self.tasks)


class Owner:
    """Owner manages multiple pets and exposes their tasks to the Scheduler."""

    def __init__(self, name: str, pets: Optional[List[Pet]] = None, preferences: Optional[Dict] = None):
        self.name = name
        self.pets: List[Pet] = pets if pets is not None else []
        self.preferences: Dict = preferences if preferences is not None else {}

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        tasks: List[Task] = []
        for p in self.pets:
            tasks.extend(p.get_tasks())
        return tasks


class Scheduler:
    """Scheduler is the brain that retrieves, organizes and manages tasks across pets/owners."""

    def __init__(self, owners: Optional[List[Owner]] = None):
        self.owners: List[Owner] = owners if owners is not None else []

    def add_owner(self, owner: Owner) -> None:
        self.owners.append(owner)

    def retrieve_tasks(self, date_: date) -> List[Task]:
        """Return all tasks for the given date across all owners/pets."""
        results: List[Task] = []
        for owner in self.owners:
            for t in owner.get_all_tasks():
                if t.date == date_:
                    results.append(t)
        return results

    def organize_tasks(self, date_: Optional[date] = None) -> List[Task]:
        """Return tasks for date sorted by time.

        If date_ is None, uses today's date.
        """
        target = date_ or date.today()
        tasks = self.retrieve_tasks(target)
        return sorted(tasks, key=lambda t: t.scheduled_time)

    def detect_conflicts(self) -> List[Tuple[Pet, Task, Task]]:
        """Detect overlapping tasks per pet.

        Returns a list of tuples (pet, task1, task2) that conflict.
        Only considers tasks that have a duration set for overlap checking.
        """
        conflicts: List[Tuple[Pet, Task, Task]] = []

        def _times_overlap(a: Task, b: Task) -> bool:
            sa = a.get_start_datetime()
            ea = a.get_end_datetime()
            sb = b.get_start_datetime()
            eb = b.get_end_datetime()
            if ea is None or eb is None:
                return False
            # handle cross-day implicitly by datetime comparison
            latest_start = max(sa, sb)
            earliest_end = min(ea, eb)
            return latest_start < earliest_end

        for owner in self.owners:
            for pet in owner.pets:
                tasks = pet.get_tasks()
                n = len(tasks)
                for i in range(n):
                    for j in range(i + 1, n):
                        t1 = tasks[i]
                        t2 = tasks[j]
                        # only check tasks on same/overlapping dates
                        if t1.date != t2.date:
                            # allow cross-day durations to overlap via datetimes, but skip if dates are different and neither has duration
                            pass
                        if _times_overlap(t1, t2):
                            conflicts.append((pet, t1, t2))

        return conflicts

    def assign_task_to_pet(self, task: Task, pet: Pet) -> None:
        pet.add_task(task)
