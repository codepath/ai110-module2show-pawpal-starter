from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status():
    task = Task(title="Feed breakfast")

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(pet_name="Buddy")
    initial_count = len(pet.get_tasks())

    pet.add_task(Task(title="Go for a walk"))

    assert len(pet.get_tasks()) == initial_count + 1


def test_daily_task_rolls_over_if_not_completed_today():
    owner = Owner(owner_name="Alex")
    pet = Pet(pet_name="Buddy")
    owner.add_pet(pet)

    task = Task(
        title="Morning meds",
        time="08:00",
        frequency="daily",
        priority="high",
        category="meds",
        completed=True,
    )
    task.last_completed_date = (date.today() - timedelta(days=1)).isoformat()
    pet.add_task(task)

    plan = Scheduler().generatePlan(owner, pet, pet.get_tasks())

    assert [scheduled.title for scheduled in plan.getPlan()] == ["Morning meds"]


def test_tasks_are_sorted_in_chronological_order():
    owner = Owner(owner_name="Jordan")
    pet = Pet(pet_name="Buddy")
    owner.add_pet(pet)

    pet.add_task(Task(title="Evening walk", time="18:00", category="exercise"))
    pet.add_task(Task(title="Breakfast", time="08:00", category="feeding"))
    pet.add_task(Task(title="Lunch", time="12:00", category="feeding"))

    plan = Scheduler().generatePlan(owner, pet, pet.get_tasks())

    assert [task.title for task in plan.getPlan()] == [
        "Breakfast",
        "Lunch",
        "Evening walk",
    ]


def test_generate_plan_records_time_conflicts():
    owner = Owner(owner_name="Sam")
    pet = Pet(pet_name="Mochi")
    owner.add_pet(pet)

    pet.add_task(Task(title="Breakfast", time="08:00", category="feeding"))
    pet.add_task(Task(title="Walk", time="08:00", category="exercise"))

    plan = Scheduler().generatePlan(owner, pet, pet.get_tasks())

    assert plan.conflicts
    assert "08:00" in plan.conflicts[0]


def test_conflict_warning_includes_pet_names_for_same_time_tasks():
    owner = Owner(owner_name="Morgan")
    buddy = Pet(pet_name="Buddy")
    mochi = Pet(pet_name="Mochi")
    owner.add_pet(buddy)
    owner.add_pet(mochi)

    buddy.add_task(Task(title="Breakfast", time="08:00", category="feeding"))
    mochi.add_task(Task(title="Play time", time="08:00", category="enrichment"))

    plan = Scheduler().generatePlan(owner, buddy, buddy.get_tasks() + mochi.get_tasks())

    assert any(
        "08:00" in warning and "Buddy: Breakfast" in warning and "Mochi: Play time" in warning
        for warning in plan.conflicts
    )


def test_same_time_tasks_use_priority_health_and_duration_tie_breakers():
    owner = Owner(owner_name="Taylor")
    pet = Pet(pet_name="Poppy")
    owner.add_pet(pet)

    pet.add_task(
        Task(
            title="Walk",
            time="08:00",
            priority="medium",
            duration_minutes=30,
            category="exercise",
        )
    )
    pet.add_task(
        Task(
            title="Give meds",
            time="08:00",
            priority="medium",
            duration_minutes=10,
            category="meds",
        )
    )
    pet.add_task(
        Task(
            title="Feed breakfast",
            time="08:00",
            priority="high",
            duration_minutes=15,
            category="feeding",
        )
    )

    plan = Scheduler().generatePlan(owner, pet, pet.get_tasks())

    assert [task.title for task in plan.getPlan()] == [
        "Feed breakfast",
        "Give meds",
        "Walk",
    ]


def test_mark_task_complete_creates_next_daily_occurrence():
    owner = Owner(owner_name="Jamie")
    pet = Pet(pet_name="Buddy")
    owner.add_pet(pet)
    pet.add_task(Task(title="Morning meds", frequency="daily", time="08:00", category="meds"))

    scheduler = Scheduler()

    assert scheduler.mark_task_complete(owner, "Buddy", "Morning meds") is True
    assert len(pet.get_tasks()) == 2
    assert pet.get_tasks()[0].completed is True
    assert pet.get_tasks()[1].completed is False
    assert pet.get_tasks()[1].due_date == (date.today() + timedelta(days=1)).isoformat()


def test_mark_task_complete_creates_next_weekly_occurrence():
    owner = Owner(owner_name="Riley")
    pet = Pet(pet_name="Mochi")
    owner.add_pet(pet)
    pet.add_task(Task(title="Bath", frequency="weekly", time="10:00", category="grooming"))

    scheduler = Scheduler()

    assert scheduler.mark_task_complete(owner, "Mochi", "Bath") is True
    assert len(pet.get_tasks()) == 2
    assert pet.get_tasks()[1].due_date == (date.today() + timedelta(weeks=1)).isoformat()


def test_mark_task_complete_does_not_duplicate_one_time_task():
    owner = Owner(owner_name="Casey")
    pet = Pet(pet_name="Poppy")
    owner.add_pet(pet)
    pet.add_task(Task(title="Vet visit", frequency="once", time="15:00", category="vet"))

    scheduler = Scheduler()

    assert scheduler.mark_task_complete(owner, "Poppy", "Vet visit") is True
    assert len(pet.get_tasks()) == 1
