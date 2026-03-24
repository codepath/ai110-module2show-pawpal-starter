from datetime import date, time

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
	"""Verify that calling mark_complete() actually changes task's status."""
	t = Task(description="Feed", date=date.today(), scheduled_time=time(9, 0))
	assert not t.completed
	t.mark_complete()
	assert t.completed


def test_adding_task_increases_pet_task_count():
	"""Verify adding task to Pet increases pet's task count."""
	p = Pet(name="Fido")
	assert len(p.get_tasks()) == 0
	t = Task(description="Walk", date=date.today(), scheduled_time=time(18, 30))
	p.add_task(t)
	assert len(p.get_tasks()) == 1