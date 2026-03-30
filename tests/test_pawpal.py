from pawpal.pawpal_system import Pet, Task, TaskType, Priority, RecurrenceScope


def test_mark_complete_changes_status():
    task = Task(
        name="Morning Walk",
        task_type=TaskType.WALK,
        priority=Priority.HIGH,
        scope=RecurrenceScope.DAILY,
        duration_minutes=30,
    )
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_task_count():
    pet = Pet(name="Buddy", species="Dog", age=3)
    task = Task(
        name="Evening Feed",
        task_type=TaskType.FEED,
        priority=Priority.MEDIUM,
        scope=RecurrenceScope.DAILY,
        duration_minutes=15,
    )
    assert len(pet._tasks) == 0

    pet.add_task(task)

    assert len(pet._tasks) == 1
