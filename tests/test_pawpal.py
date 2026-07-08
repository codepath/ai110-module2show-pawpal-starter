"""Tests for the PawPal+ domain model."""

from datetime import time

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from not-done to done."""
    task = Task("Morning walk", time(7, 30))

    assert task.done is False
    assert task.get_status() is False

    task.mark_complete()

    assert task.done is True
    assert task.get_status() is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Mochi", "Shiba Inu")

    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Breakfast", time(8, 0)))

    assert len(pet.get_tasks()) == 1

    pet.add_task(Task("Evening walk", time(18, 0)))

    assert len(pet.get_tasks()) == 2
