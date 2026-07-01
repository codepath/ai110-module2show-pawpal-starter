from pawpal_system import PetTask, Pet


def test_mark_complete_changes_task_status():
    task = PetTask("Walk Buddy", 30, "high")
    assert task.status == "pending"

    task.mark_complete()

    assert task.status == "completed"


def test_adding_task_increases_pet_task_count():
    pet = Pet("Buddy", "Dog")
    assert len(pet.tasks) == 0

    pet.add_task(PetTask("Feed Buddy", 15, "high"))

    assert len(pet.tasks) == 1
