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
        pass


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    care_metrics: dict[str, str] = field(default_factory=dict)


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
        pass

    def set_availability(self, day: str, windows: list[AvailabilityWindow]) -> None:
        pass


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

    def edit(self, priority: Priority, duration: int) -> None:
        pass


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
        pass

    def display(self) -> str:
        pass


# ---------------------------------------------------------------------------
# WeeklyMonthlyPlan
# ---------------------------------------------------------------------------

@dataclass
class WeeklyMonthlyPlan:
    tasks_by_day: dict[str, list[Task]] = field(default_factory=dict)

    def generate(self, tasks: list[Task]) -> None:
        pass

    def display(self) -> str:
        pass


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
        pass

    def order_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def check_constraints(self, task: Task, window: AvailabilityWindow) -> bool:
        pass

    def generate_rationale(self, schedule: DailySchedule) -> str:
        pass
