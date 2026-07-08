"""
PawPal+ Logic Layer
===================
Core classes: Task, Pet, Owner, Scheduler
Persistence:  JSON → ~/.pawpal/data.json

This module is the single source of truth for all backend logic.
app.py imports from here; main.py uses it as a CLI demo.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

# ── Storage ───────────────────────────────────────────────────────────────────
_DATA_FILE = Path.home() / ".pawpal" / "data.json"

# ── Constants ─────────────────────────────────────────────────────────────────
PRIORITIES  = ("critical", "high", "medium", "low", "optional")
FREQUENCIES = ("once", "daily", "weekly")


# ══════════════════════════════════════════════════════════════════════════════
# Task
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Task:
    """A single care activity for a pet."""

    name: str
    time: str                             # "HH:MM" 24-hour, used for sorting
    priority: str                         # one of PRIORITIES
    frequency: str                        # one of FREQUENCIES
    pet_name: str                         # which pet this task belongs to
    duration_minutes: int = 30
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.completed = True

    def next_occurrence(self) -> Optional[Task]:
        """Return a new Task for the next scheduled occurrence, or None for one-time tasks."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        return Task(
            name=self.name,
            time=self.time,
            priority=self.priority,
            frequency=self.frequency,
            pet_name=self.pet_name,
            duration_minutes=self.duration_minutes,
            due_date=self.due_date + delta,
            notes=self.notes,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Pet
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Pet:
    """A pet with their profile and list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age_years: float = 0.0
    weight_kg: float = 0.0
    medical_conditions: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def pending_tasks(self) -> List[Task]:
        """Return only incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.completed]


# ══════════════════════════════════════════════════════════════════════════════
# Owner
# ══════════════════════════════════════════════════════════════════════════════

class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str = "Owner", pets: List[Pet] = None) -> None:
        self.name = name
        self.pets: List[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Aggregate and return all tasks across every pet."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the Pet with the given name (case-insensitive), or None."""
        return next((p for p in self.pets if p.name.lower() == name.lower()), None)

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self) -> None:
        """Persist owner, pet, and task data to JSON at ~/.pawpal/data.json."""
        _DATA_FILE.parent.mkdir(exist_ok=True)
        with open(_DATA_FILE, "w") as f:
            json.dump(_owner_to_dict(self), f, indent=2, default=str)

    @classmethod
    def load(cls) -> Owner:
        """Load owner data from JSON. Returns a blank Owner if no data file exists."""
        if not _DATA_FILE.exists():
            return cls()
        try:
            with open(_DATA_FILE) as f:
                return _owner_from_dict(json.load(f))
        except (json.JSONDecodeError, KeyError):
            return cls()


# ══════════════════════════════════════════════════════════════════════════════
# Scheduler
# ══════════════════════════════════════════════════════════════════════════════

class Scheduler:
    """Retrieves, organises, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_by_time(self, tasks: List[Task] = None) -> List[Task]:
        """Return tasks sorted in ascending chronological order using HH:MM as the sort key."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def filter_by_status(self, completed: bool, tasks: List[Task] = None) -> List[Task]:
        """Return tasks matching the given completion status."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the named pet (case-insensitive)."""
        return [
            t for t in self.owner.get_all_tasks()
            if t.pet_name.lower() == pet_name.lower()
        ]

    def detect_conflicts(self, tasks: List[Task] = None) -> List[str]:
        """
        Detect scheduling conflicts: two incomplete tasks for the same pet at the
        same time. Returns a list of human-readable warning strings.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        warnings: List[str] = []
        seen: dict = {}
        for task in tasks:
            if task.completed:
                continue
            key = (task.pet_name.lower(), task.time)
            if key in seen:
                warnings.append(
                    f"⚠ Conflict: '{task.name}' and '{seen[key]}' are both "
                    f"scheduled at {task.time} for {task.pet_name}."
                )
            else:
                seen[key] = task.name
        return warnings

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Mark a task as complete. For recurring tasks (daily/weekly), automatically
        creates and registers the next occurrence with the owning pet.
        Returns the newly created Task, or None for one-time tasks.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            pet = self.owner.get_pet(task.pet_name)
            if pet:
                pet.add_task(next_task)
        return next_task

    def todays_schedule(self, for_date: date = None) -> List[Task]:
        """Return all pending tasks due on *for_date* (defaults to today), sorted by time."""
        if for_date is None:
            for_date = date.today()
        pending = [
            t for t in self.owner.get_all_tasks()
            if not t.completed and t.due_date == for_date
        ]
        return self.sort_by_time(pending)


# ══════════════════════════════════════════════════════════════════════════════
# JSON serialisation (private helpers)
# ══════════════════════════════════════════════════════════════════════════════

def _task_to_dict(t: Task) -> dict:
    return {
        "id":               t.id,
        "name":             t.name,
        "time":             t.time,
        "priority":         t.priority,
        "frequency":        t.frequency,
        "pet_name":         t.pet_name,
        "duration_minutes": t.duration_minutes,
        "completed":        t.completed,
        "due_date":         t.due_date.isoformat(),
        "notes":            t.notes,
    }


def _task_from_dict(d: dict) -> Task:
    return Task(
        id=d["id"],
        name=d["name"],
        time=d.get("time", "08:00"),
        priority=d.get("priority", "medium"),
        frequency=d.get("frequency", "once"),
        pet_name=d.get("pet_name", ""),
        duration_minutes=d.get("duration_minutes", 30),
        completed=d.get("completed", False),
        due_date=date.fromisoformat(d["due_date"]) if "due_date" in d else date.today(),
        notes=d.get("notes", ""),
    )


def _pet_to_dict(p: Pet) -> dict:
    return {
        "id":                 p.id,
        "name":               p.name,
        "species":            p.species,
        "breed":              p.breed,
        "age_years":          p.age_years,
        "weight_kg":          p.weight_kg,
        "medical_conditions": p.medical_conditions,
        "tasks":              [_task_to_dict(t) for t in p.tasks],
    }


def _pet_from_dict(d: dict) -> Pet:
    return Pet(
        id=d["id"],
        name=d["name"],
        species=d["species"],
        breed=d.get("breed", ""),
        age_years=d.get("age_years", 0.0),
        weight_kg=d.get("weight_kg", 0.0),
        medical_conditions=d.get("medical_conditions", []),
        tasks=[_task_from_dict(t) for t in d.get("tasks", [])],
    )


def _owner_to_dict(o: Owner) -> dict:
    return {"name": o.name, "pets": [_pet_to_dict(p) for p in o.pets]}


def _owner_from_dict(d: dict) -> Owner:
    return Owner(
        name=d.get("name", "Owner"),
        pets=[_pet_from_dict(p) for p in d.get("pets", [])],
    )
