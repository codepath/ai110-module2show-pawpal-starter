"""Tests for the PawPal+ system."""

from datetime import datetime

from Pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", datetime(2026, 11, 1, 7, 30), 30, "high")
    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "Dog", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", datetime(2026, 11, 1, 8, 15), 10, "high"))

    assert len(pet.tasks) == 1
