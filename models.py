from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import List, Optional
import uuid


class TaskType(Enum):
    WALK = "Walk"
    FEEDING = "Feeding"
    MEDICATION = "Medication"
    ENRICHMENT = "Enrichment"
    GROOMING = "Grooming"
    VET_VISIT = "Vet Visit"
    TRAINING = "Training"


class Priority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    OPTIONAL = 1


class Frequency(Enum):
    MULTIPLE_DAILY = 8      # hours between occurrences
    DAILY = 24
    EVERY_OTHER_DAY = 48
    WEEKLY = 168
    MONTHLY = 720


@dataclass
class Task:
    name: str
    task_type: TaskType
    priority: Priority
    duration_minutes: int
    frequency: Frequency
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    last_done: Optional[datetime] = None
    notes: str = ""
    is_active: bool = True

    def is_due(self, as_of: datetime) -> bool:
        if self.last_done is None:
            return True
        hours_since = (as_of - self.last_done).total_seconds() / 3600
        return hours_since >= self.frequency.value

    def hours_overdue(self, as_of: datetime) -> float:
        if self.last_done is None:
            return float(self.frequency.value)
        hours_since = (as_of - self.last_done).total_seconds() / 3600
        return max(0.0, hours_since - self.frequency.value)

    def next_due_at(self) -> Optional[datetime]:
        if self.last_done is None:
            return None
        return self.last_done + timedelta(hours=self.frequency.value)


@dataclass
class Pet:
    name: str
    species: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    breed: str = ""
    age_years: float = 0.0
    weight_kg: float = 0.0
    medical_conditions: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)


@dataclass
class OwnerPreferences:
    name: str = "Owner"
    available_minutes: int = 120
    preferred_morning_minutes: int = 45
    preferred_evening_minutes: int = 45
    notes: str = ""


@dataclass
class ScheduledTask:
    task: Task
    time_slot: str
    score: float
    reason: str


@dataclass
class DailyPlan:
    plan_date: date
    pet: Pet
    owner: OwnerPreferences
    scheduled: List[ScheduledTask]
    skipped: List[Task]
    not_due: List[Task]
    total_minutes_used: int
    overall_reasoning: str
