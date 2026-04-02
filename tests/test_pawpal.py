from pawpal_system import Owner, Pet, Task


def make_pet():
    return Pet(name="Tye", pet_type="Rat")


def make_task(pet):
    return Task(title="Walk Tye", pet=pet, task_type="exercise")


def test_complete_task_changes_status():
    pet = make_pet()
    task = make_task(pet)

    assert task.status == "pending"
    task.complete_task()
    assert task.status == "completed"


def test_add_task_increases_pet_task_count():
    pet = make_pet()
    task = make_task(pet)

    assert len(pet.tasks) == 0
    pet.add_task(task)
    assert len(pet.tasks) == 1
