from datetime import date, timedelta

from pawpal_system import OwnerInfo, Pet, RigidTask, StaticTask, Scheduler


def test_mark_complete_updates_status() -> None:
    task = RigidTask(
        name="Walk",
        description="Morning walk",
        duration=30,
        ideal_time="08:00",
        priority=5,
    )

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_task_count() -> None:
    pet = Pet(name="Milo", birthday="2021-04-14", animal="Dog")
    initial_count = pet.task_count

    task = StaticTask(
        name="Medication",
        description="Give medication at 09:00",
        duration=10,
        ideal_time="09:00",
        fixed_time="09:00",
        priority=5,
    )

    pet.add_task(task)

    assert pet.task_count == initial_count + 1


def test_filter_tasks_by_completion() -> None:
    owner = OwnerInfo(name="Anato")
    pet = Pet(name="Milo", birthday="2021-04-14", animal="Dog")

    completed_task = RigidTask(
        name="Walk",
        description="Morning walk",
        duration=30,
        ideal_time="08:00",
        priority=5,
    )
    completed_task.mark_complete()

    incomplete_task = RigidTask(
        name="Play",
        description="Playtime",
        duration=15,
        ideal_time="10:00",
        priority=3,
    )

    pet.add_task(completed_task)
    pet.add_task(incomplete_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    completed = scheduler.filter_tasks_by_completion(True)
    incomplete = scheduler.filter_tasks_by_completion(False)

    assert len(completed) == 1
    assert completed[0][1].completed is True
    assert len(incomplete) == 1
    assert incomplete[0][1].completed is False


def test_schedule_tasks_returns_chronological_order() -> None:
    owner = OwnerInfo(name="Anato")
    pet = Pet(name="Milo", birthday="2021-04-14", animal="Dog")

    early_task = RigidTask(
        name="Early walk",
        description="Morning exercise",
        duration=20,
        ideal_time="07:00",
        priority=4,
        task_date=date(2026, 3, 30),
    )
    late_task = RigidTask(
        name="Late feed",
        description="Feed Milo",
        duration=15,
        ideal_time="18:00",
        priority=2,
        task_date=date(2026, 3, 30),
    )
    tomorrow_task = RigidTask(
        name="Tomorrow checkup",
        description="Vet appointment",
        duration=30,
        ideal_time="09:00",
        priority=5,
        task_date=date(2026, 3, 31),
    )

    pet.add_task(late_task)
    pet.add_task(tomorrow_task)
    pet.add_task(early_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduled = scheduler.schedule_tasks()

    assert [task.name for _, task in scheduled] == [
        "Early walk",
        "Late feed",
        "Tomorrow checkup",
    ]


def test_scheduler_detects_duplicate_static_task_times() -> None:
    owner = OwnerInfo(name="Anato")
    pet = Pet(name="Milo", birthday="2021-04-14", animal="Dog")
    task_date = date(2026, 3, 29)

    first_task = StaticTask(
        name="Med A",
        description="Medication A",
        duration=10,
        ideal_time="09:00",
        fixed_time="09:00",
        priority=5,
        task_date=task_date,
    )
    second_task = StaticTask(
        name="Med B",
        description="Medication B",
        duration=10,
        ideal_time="09:00",
        fixed_time="09:00",
        priority=5,
        task_date=task_date,
    )

    pet.add_task(first_task)
    pet.add_task(second_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_static_conflicts()

    assert len(warnings) == 1
    assert "09:00" in warnings[0]
    assert "Med A" in warnings[0]
    assert "Med B" in warnings[0]


def test_detect_static_conflicts_returns_warning() -> None:
    owner = OwnerInfo(name="Anato")
    pet = Pet(name="Milo", birthday="2021-04-14", animal="Dog")
    task_date = date(2026, 3, 29)

    task1 = StaticTask(
        name="Morning meds",
        description="Give medication",
        duration=10,
        ideal_time="09:00",
        fixed_time="09:00",
        priority=5,
        task_date=task_date,
    )
    task2 = StaticTask(
        name="Breakfast",
        description="Feed Milo",
        duration=15,
        ideal_time="09:00",
        fixed_time="09:00",
        priority=5,
        task_date=task_date,
    )

    pet.add_task(task1)
    pet.add_task(task2)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_static_conflicts()

    assert len(warnings) == 1
    assert "Milo has 2 static tasks scheduled at 2026-03-29 09:00" in warnings[0]


def test_daily_task_recreates_after_completion() -> None:
    owner = OwnerInfo(name="Anato")
    pet = Pet(name="Milo", birthday="2021-04-14", animal="Dog")
    start_date = date(2026, 3, 29)

    daily_task = RigidTask(
        name="Daily walk",
        description="Take Milo on a daily walk",
        duration=30,
        ideal_time="08:00",
        priority=5,
        daily=True,
        task_date=start_date,
    )

    pet.add_task(daily_task)
    owner.add_pet(pet)

    daily_task.mark_complete(parent_pet=pet)

    assert daily_task.completed is True
    assert pet.task_count == 2
    new_task = pet.list_tasks()[-1]
    assert new_task.name == "Daily walk"
    assert new_task.completed is False
    assert new_task.daily is True
    assert new_task.date == start_date + timedelta(days=1)


def test_flexible_tasks_with_same_priority_get_different_times() -> None:
    owner = OwnerInfo(name="Anato")
    pet = Pet(name="Milo", birthday="2021-04-14", animal="Dog")

    task1 = RigidTask(
        name="Walk A",
        description="Flexible walk A",
        duration=30,
        ideal_time="08:00",
        priority=5,
    )
    task2 = RigidTask(
        name="Walk B",
        description="Flexible walk B",
        duration=30,
        ideal_time="08:00",
        priority=5,
    )
    task3 = RigidTask(
        name="Walk C",
        description="Flexible walk C",
        duration=30,
        ideal_time="08:00",
        priority=5,
    )

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    schedule = scheduler.schedule_tasks()

    times = [task.scheduled_time for _, task in schedule]
    assert len(times) == 3
    assert len(set(times)) == 3


