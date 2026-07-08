import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status():
    task = Task(description="Feed", time="08:00", frequency="daily")

    task.mark_complete()

    assert task.completed is True


def test_mark_incomplete_changes_task_status():
    task = Task(description="Feed", time="08:00", frequency="daily")
    task.mark_complete()

    task.mark_incomplete()

    assert task.completed is False


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", weight=5.0, color="cream", breed="mixed")
    task = Task(description="Walk", time="09:00", frequency="daily")

    pet.add_task(task)

    assert len(pet.tasks) == 1


def test_owner_options_add_and_remove_pets_and_tasks():
    owner = Owner(info={"name": "Jordan"})
    pet = Pet(name="Mochi", weight=5.0, color="cream", breed="mixed")
    task = Task(description="Feed", time="08:00", frequency="daily")

    owner.add_pet(pet)
    owner.add_task(task)

    assert pet in owner.pets
    assert task in owner.get_all_tasks()

    owner.remove_task(task)
    owner.remove_pet(pet)

    assert task not in owner.get_all_tasks()
    assert pet not in owner.pets


def test_owner_update_preferences_stores_owner_options():
    owner = Owner(info={"name": "Jordan"})

    owner.update_preferences({"notifications": "email", "reminder_lead_minutes": 15})

    assert owner.info["preferences"] == {
        "notifications": "email",
        "reminder_lead_minutes": 15,
    }


def test_daily_plan_respects_max_tasks_constraint_and_includes_pet_tasks():
    owner = Owner(info={"name": "Jordan"})
    pet = Pet(name="Mochi", weight=5.0, color="cream", breed="mixed")
    owner.add_pet(pet)

    pet.add_task(Task(description="Morning walk", time="08:00", frequency="daily", priority="high"))
    pet.add_task(Task(description="Grooming", time="14:00", frequency="weekly", priority="low"))
    owner.add_task(Task(description="Feed dinner", time="18:00", frequency="daily", priority="medium"))

    scheduler = Scheduler(owner, constraints={"max_tasks": 2})
    plan = scheduler.daily_plan()

    assert len(plan) == 2
    assert "Morning walk" in [task.description for task in plan]


def test_sorting_correctness_returns_tasks_in_chronological_order():
    scheduler = Scheduler()
    late_task = Task(description="Nap", time="12:30", frequency="daily")
    early_task = Task(description="Walk", time="08:00", frequency="daily")
    mid_task = Task(description="Feed", time="09:45", frequency="daily")
    scheduler.tasks = [late_task, mid_task, early_task]

    sorted_tasks = scheduler.sort_by_time(scheduler.tasks)

    assert [task.description for task in sorted_tasks] == ["Walk", "Feed", "Nap"]


def test_recurrence_logic_creates_next_day_task_when_daily_task_completed():
    today = date.today()
    task = Task(description="Walk", time="08:00", frequency="daily", due_date=today)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "daily"
    assert next_task.due_date == today + timedelta(days=1)


def test_conflict_detection_flags_duplicate_times():
    owner = Owner(info={"name": "Jordan"})
    pet1 = Pet(name="Mochi", weight=5.0, color="cream", breed="mixed")
    pet2 = Pet(name="Biscuit", weight=8.0, color="brown", breed="golden retriever")
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    pet1.add_task(Task(description="Morning walk", time="08:00", frequency="daily"))
    pet2.add_task(Task(description="Feed breakfast", time="08:00", frequency="daily"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.check_conflicts()

    assert len(conflicts) == 1
    descriptions = {conflicts[0][0].description, conflicts[0][1].description}
    assert descriptions == {"Morning walk", "Feed breakfast"}
