from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task("Feed dog", duration=10, priority=2)
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", duration=30, priority=3))
    assert len(pet.get_tasks()) == 1
