"""
PawPal+ Persistence Layer

Handles saving and loading pets and their tasks to/from a JSON file
so data survives between application runs.
"""

import json
from datetime import date
from typing import List
from pawpal_system import Pet, Task

DATA_FILE = "pawpal_data.json"


def save_pets(pets: List[Pet], filepath: str = DATA_FILE) -> None:
    """Serialize a list of Pet objects to a JSON file."""
    data = {
        "pets": [
            {
                "id": p.id,
                "name": p.name,
                "species": p.species,
                "age": p.age,
                "tasks": [
                    {
                        "id": t.id,
                        "description": t.description,
                        "duration_min": t.duration_min,
                        "priority": t.priority,
                        "frequency": t.frequency,
                        "constraints": t.constraints,
                        "is_complete": t.is_complete,
                        "last_scheduled": t.last_scheduled.isoformat() if t.last_scheduled else None,
                    }
                    for t in p.tasks
                ],
            }
            for p in pets
        ]
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_pets(filepath: str = DATA_FILE) -> List[Pet]:
    """Load a list of Pet objects from a JSON file. Returns empty list if file not found."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []

    pets = []
    for p_data in data.get("pets", []):
        pet = Pet(
            id=p_data["id"],
            name=p_data["name"],
            species=p_data["species"],
            age=p_data["age"],
        )
        for t_data in p_data.get("tasks", []):
            last_scheduled = (
                date.fromisoformat(t_data["last_scheduled"])
                if t_data.get("last_scheduled")
                else None
            )
            task = Task(
                id=t_data["id"],
                description=t_data["description"],
                duration_min=t_data["duration_min"],
                priority=t_data["priority"],
                frequency=t_data["frequency"],
                constraints=t_data.get("constraints", {}),
                is_complete=t_data.get("is_complete", False),
                last_scheduled=last_scheduled,
            )
            pet.add_task(task)
        pets.append(pet)
    return pets
