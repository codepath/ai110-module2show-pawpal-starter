import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task(description="Feed", time="08:00", frequency="daily")

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", weight=5.0, color="cream", breed="mixed")
    task = Task(description="Walk", time="09:00", frequency="daily")

    pet.add_task(task)

    assert len(pet.tasks) == 1
