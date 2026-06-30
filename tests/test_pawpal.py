"""Simple unit tests for the PawPal+ object model."""

from pawpal_system import Pet, Responsibility


def test_mark_complete_changes_status():
    """mark_complete() flips a task's status from incomplete to complete."""
    task = Responsibility(title="Morning walk", duration_minutes=30)

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_responsibility_increases_task_count():
    """Adding a task to a Pet increases its responsibility count by one."""
    pet = Pet(name="Rex")

    assert len(pet.responsibilities) == 0
    pet.add_responsibility(Responsibility(title="Breakfast", duration_minutes=10))
    assert len(pet.responsibilities) == 1
