from datetime import date, timedelta

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


def test_scheduler_can_sort_tasks_by_time():
    scheduler = Scheduler()
    early_task = Task(description="Feed", time="09:45", frequency="daily")
    late_task = Task(description="Walk", time="08:00", frequency="daily")
    midday_task = Task(description="Nap", time="12:30", frequency="daily")
    scheduler.tasks = [early_task, late_task, midday_task]

    sorted_tasks = scheduler.sort_by_time(scheduler.tasks)

    assert [task.description for task in sorted_tasks] == ["Walk", "Feed", "Nap"]


def test_scheduler_detects_conflicts_for_same_pet_or_different_pets():
    owner = Owner(info={"name": "Jordan"})
    pet1 = Pet(name="Mochi", weight=5.0, color="cream", breed="mixed")
    pet2 = Pet(name="Biscuit", weight=8.0, color="brown", breed="golden retriever")
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    same_pet_conflict = Task(description="Morning walk", time="08:00", frequency="daily")
    different_pet_conflict = Task(description="Feed breakfast", time="08:00", frequency="daily")
    pet1.add_task(same_pet_conflict)
    pet2.add_task(different_pet_conflict)

    scheduler = Scheduler(owner)
    conflicts = scheduler.check_conflicts()

    assert len(conflicts) == 2
    assert {conflict[0].description for conflict in conflicts} == {"Morning walk", "Feed breakfast"}


def test_lightweight_conflict_detection_returns_warning_message():
    scheduler = Scheduler()
    scheduler.tasks = [Task(description="Invalid", time="not-a-time", frequency="daily")]

    warning = scheduler.lightweight_conflict_check()

    assert "Warning" in warning
    assert "conflict" in warning.lower()


def test_recurring_daily_task_creates_a_next_occurrence_when_completed():
    today = date.today()
    task = Task(description="Walk", time="08:00", frequency="daily", due_date=today)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.frequency == "daily"
    assert next_task.due_date == today + timedelta(days=1)


def test_recurring_weekly_task_rolls_forward_by_seven_days_when_completed():
    today = date.today()
    task = Task(description="Grooming", time="14:00", frequency="weekly", due_date=today)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=7)
