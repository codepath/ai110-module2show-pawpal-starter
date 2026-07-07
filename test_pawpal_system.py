from pawpal_system import Owner, Pet, Scheduler, Task


def test_owner_can_manage_multiple_pets_and_tasks():
    owner = Owner(info={"name": "Jordan"})
    pet1 = Pet(name="Mochi", weight=5.0, color="cream", breed="mixed")
    pet2 = Pet(name="Biscuit", weight=8.0, color="brown", breed="golden retriever")

    owner.add_pet_info(pet1)
    owner.add_pet_info(pet2)

    task1 = Task(info={"title": "Morning walk"}, duration=20, priority="high")
    task2 = Task(info={"title": "Feed dinner"}, duration=10, priority="medium")
    owner.add_task(task1)
    owner.add_task(task2)

    assert owner.pets == [pet1, pet2]
    assert owner.tasks == [task1, task2]


def test_pet_methods_use_own_state():
    pet = Pet(name="Mochi", weight=5.0, color="cream", breed="mixed")

    assert pet.snack_time() == "Small snack"
    assert pet.accommodations() == "Standard home setup"
    assert pet.get_daily_needs()["snack_time"] == "Small snack"


def test_scheduler_orders_tasks_by_priority_and_duration():
    scheduler = Scheduler(constraints={"available_minutes": 30})
    high_priority_task = Task(info={"title": "Morning walk"}, duration=20, priority="high")
    low_priority_task = Task(info={"title": "Feed dinner"}, duration=10, priority="low")
    scheduler.tasks = [low_priority_task, high_priority_task]

    plan = scheduler.daily_plan({"available_minutes": 30})

    assert plan[0].priority == "high"
    assert len(plan) == 2
