"""Core behavior suite for the PawPal+ logic layer (real objects, no mocks)."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def make_task(description: str = "Morning walk", time: str = "08:00", **kwargs) -> Task:
    return Task(
        description=description,
        time=time,
        date=kwargs.pop("date", date.today()),
        **kwargs
    )


def test_mark_complete_changes_task_status():
    task = make_task()
    task.mark_complete()
    assert task.completed is True


def test_new_task_starts_incomplete():
    assert make_task().completed is False


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(make_task())
    assert len(pet.list_tasks()) == 1


def test_pending_tasks_excludes_completed_ones():
    pet = Pet(name="Mochi", species="dog")
    done = make_task("Feeding", "09:00")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task("Evening walk", "18:00"))
    assert [t.description for t in pet.pending_tasks()] == ["Evening walk"]


def test_owner_add_and_get_pet():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    owner.add_pet(mochi)
    assert owner.get_pet("Mochi") is mochi


def test_get_pet_returns_none_for_unknown_name():
    assert Owner(name="Jordan").get_pet("Ghost") is None


def two_pet_household() -> Owner:
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")
    mochi.add_task(make_task("Morning walk", "08:00"))
    whiskers.add_task(make_task("Feeding", "09:00"))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    return owner


def test_scheduler_collects_tasks_across_multiple_pets():
    scheduler = Scheduler(two_pet_household())
    pet_names = {pet.name for pet, _task in scheduler.all_tasks()}
    assert pet_names == {"Mochi", "Whiskers"}


def test_sort_by_time_orders_tasks_chronologically_across_pets():
    from datetime import time

    owner = two_pet_household()
    owner.get_pet("Mochi").add_task(make_task("Evening walk", "18:30"))
    owner.get_pet("Whiskers").add_task(make_task("Play session", "07:15"))
    times = [task.time for _pet, task in Scheduler(owner).sort_by_time()]
    assert times == [time(7, 15), time(8, 0), time(9, 0), time(18, 30)]


def test_filter_by_status_returns_only_pending_tasks():
    owner = two_pet_household()
    owner.get_pet("Mochi").list_tasks()[0].mark_complete()
    pending = Scheduler(owner).filter_by_status(completed=False)
    assert [task.description for _pet, task in pending] == ["Feeding"]


def test_filter_by_pet_returns_only_that_pets_tasks():
    scheduler = Scheduler(two_pet_household())
    entries = scheduler.filter_by_pet("Whiskers")
    assert [(pet.name, task.description) for pet, task in entries] == [
        ("Whiskers", "Feeding")
    ]


def test_completing_daily_task_marks_original_completed():
    owner = two_pet_household()
    mochi = owner.get_pet("Mochi")
    walk = mochi.list_tasks()[0]
    walk.frequency = "daily"
    Scheduler(owner).complete_task(walk)
    assert walk.completed is True


def test_completing_daily_task_schedules_new_task():
    owner = two_pet_household()
    mochi = owner.get_pet("Mochi")
    walk = mochi.list_tasks()[0]
    walk.frequency = "daily"
    follow_up = Scheduler(owner).complete_task(walk)
    assert follow_up in mochi.list_tasks()


def test_completing_daily_task_schedules_for_tomorrow():
    from datetime import timedelta

    owner = two_pet_household()
    mochi = owner.get_pet("Mochi")
    walk = mochi.list_tasks()[0]
    walk.frequency = "daily"
    follow_up = Scheduler(owner).complete_task(walk)
    assert follow_up.date == date.today() + timedelta(days=1)


def test_completing_daily_task_schedules_as_incomplete():
    owner = two_pet_household()
    mochi = owner.get_pet("Mochi")
    walk = mochi.list_tasks()[0]
    walk.frequency = "daily"
    follow_up = Scheduler(owner).complete_task(walk)
    assert follow_up.completed is False


def test_completing_weekly_task_schedules_it_next_week():
    from datetime import timedelta

    owner = two_pet_household()
    whiskers = owner.get_pet("Whiskers")
    bath = make_task("Bath", "11:00", frequency="weekly")
    whiskers.add_task(bath)
    follow_up = Scheduler(owner).complete_task(bath)
    assert follow_up.date == date.today() + timedelta(days=7)


def test_completing_one_off_task_returns_no_follow_up():
    owner = two_pet_household()
    whiskers = owner.get_pet("Whiskers")
    feeding = whiskers.list_tasks()[0]
    assert Scheduler(owner).complete_task(feeding) is None


def test_completing_one_off_task_does_not_add_to_list():
    owner = two_pet_household()
    whiskers = owner.get_pet("Whiskers")
    feeding = whiskers.list_tasks()[0]
    Scheduler(owner).complete_task(feeding)
    assert len(whiskers.list_tasks()) == 1


def test_detect_conflicts_flags_same_time_tasks_across_pets():
    owner = two_pet_household()
    owner.get_pet("Whiskers").add_task(make_task("Medication", "08:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1


def test_detect_conflicts_warning_contains_time():
    owner = two_pet_household()
    owner.get_pet("Whiskers").add_task(make_task("Medication", "08:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert "08:00" in warnings[0]


def test_detect_conflicts_warning_contains_first_pet_name():
    owner = two_pet_household()
    owner.get_pet("Whiskers").add_task(make_task("Medication", "08:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert "Mochi" in warnings[0]


def test_detect_conflicts_warning_contains_second_pet_name():
    owner = two_pet_household()
    owner.get_pet("Whiskers").add_task(make_task("Medication", "08:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert "Whiskers" in warnings[0]


def test_detect_conflicts_flags_overlapping_time_blocks():
    owner = two_pet_household()
    owner.get_pet("Whiskers").add_task(
        make_task("Medication", "08:10", duration_minutes=15)
    )
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1


def test_detect_conflicts_returns_empty_list_when_no_collisions():
    assert Scheduler(two_pet_household()).detect_conflicts() == []


def test_detect_conflicts_ignores_completed_tasks():
    owner = two_pet_household()
    owner.get_pet("Whiskers").add_task(make_task("Medication", "08:00"))
    owner.get_pet("Mochi").list_tasks()[0].mark_complete()
    assert Scheduler(owner).detect_conflicts() == []


def test_tasks_for_today_excludes_future_days():
    from datetime import timedelta

    owner = two_pet_household()
    owner.get_pet("Mochi").add_task(
        make_task("Vet visit", "10:00", date=date.today() + timedelta(days=3))
    )
    descriptions = [
        task.description for _pet, task in Scheduler(owner).tasks_for_today()
    ]
    assert "Vet visit" not in descriptions


def test_tasks_for_today_includes_all_today_tasks():
    from datetime import timedelta

    owner = two_pet_household()
    owner.get_pet("Mochi").add_task(
        make_task("Vet visit", "10:00", date=date.today() + timedelta(days=3))
    )
    descriptions = [
        task.description for _pet, task in Scheduler(owner).tasks_for_today()
    ]
    assert len(descriptions) == 2
