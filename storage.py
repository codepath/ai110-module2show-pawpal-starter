from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from models import Frequency, OwnerPreferences, Pet, Priority, Task, TaskType

DATA_DIR   = Path.home() / ".pawpal"
PETS_FILE  = DATA_DIR / "pets.json"
OWNER_FILE = DATA_DIR / "owner.json"


def _ensure() -> None:
    DATA_DIR.mkdir(exist_ok=True)


# ── Task serialisation ────────────────────────────────────────────────────────

def _task_to_dict(t: Task) -> dict:
    return {
        "id":               t.id,
        "name":             t.name,
        "task_type":        t.task_type.value,
        "priority":         t.priority.value,
        "duration_minutes": t.duration_minutes,
        "frequency":        t.frequency.value,
        "last_done":        t.last_done.isoformat() if t.last_done else None,
        "notes":            t.notes,
        "is_active":        t.is_active,
    }


def _task_from_dict(d: dict) -> Task:
    return Task(
        id=d["id"],
        name=d["name"],
        task_type=TaskType(d["task_type"]),
        priority=Priority(d["priority"]),
        duration_minutes=d["duration_minutes"],
        frequency=Frequency(d["frequency"]),
        last_done=datetime.fromisoformat(d["last_done"]) if d.get("last_done") else None,
        notes=d.get("notes", ""),
        is_active=d.get("is_active", True),
    )


# ── Pet serialisation ─────────────────────────────────────────────────────────

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


# ── Public API ────────────────────────────────────────────────────────────────

def save_pets(pets: list[Pet]) -> None:
    _ensure()
    with open(PETS_FILE, "w") as f:
        json.dump([_pet_to_dict(p) for p in pets], f, indent=2)


def load_pets() -> list[Pet]:
    if not PETS_FILE.exists():
        return []
    with open(PETS_FILE) as f:
        return [_pet_from_dict(d) for d in json.load(f)]


def save_owner(prefs: OwnerPreferences) -> None:
    _ensure()
    with open(OWNER_FILE, "w") as f:
        json.dump({
            "name":                      prefs.name,
            "available_minutes":         prefs.available_minutes,
            "preferred_morning_minutes": prefs.preferred_morning_minutes,
            "preferred_evening_minutes": prefs.preferred_evening_minutes,
            "notes":                     prefs.notes,
        }, f, indent=2)


def load_owner() -> OwnerPreferences:
    if not OWNER_FILE.exists():
        return OwnerPreferences()
    with open(OWNER_FILE) as f:
        d = json.load(f)
    return OwnerPreferences(
        name=d.get("name", "Owner"),
        available_minutes=d.get("available_minutes", 120),
        preferred_morning_minutes=d.get("preferred_morning_minutes", 45),
        preferred_evening_minutes=d.get("preferred_evening_minutes", 45),
        notes=d.get("notes", ""),
    )
