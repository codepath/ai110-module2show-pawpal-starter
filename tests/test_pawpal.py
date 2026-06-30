"""Tests for core PawPal+ behaviors.

Run from the project root:  pytest
"""

from diagrams.pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task's status to done."""
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.done is False  # tasks start incomplete

    task.mark_complete()

    assert task.done is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0  # no tasks yet

    pet.add_task(Task("Feeding", duration_minutes=10, priority="high"))

    assert len(pet.tasks) == 1
