import pytest

from pawpal_system import CareTask, DailySchedule, Owner, Pet


def test_pet_add_task_adds_valid_task():
    pet = Pet(name="Mochi", species="dog")
    task = CareTask(title="Morning walk", duration_minutes=20)

    pet.add_task(task)

    assert pet.care_tasks == [task]


def test_pet_add_task_ignores_duplicate_task():
    pet = Pet(name="Mochi", species="dog")
    task = CareTask(title="Morning walk", duration_minutes=20)

    pet.add_task(task)
    pet.add_task(task)

    assert pet.care_tasks == [task]


def test_pet_add_task_rejects_invalid_task():
    pet = Pet(name="Mochi", species="dog")
    task = CareTask(title="Morning walk", duration_minutes=0)

    with pytest.raises(ValueError, match="Invalid task"):
        pet.add_task(task)


def test_pet_remove_task_removes_existing_task():
    pet = Pet(name="Mochi", species="dog")
    task = CareTask(title="Morning walk", duration_minutes=20)
    pet.add_task(task)

    removed = pet.remove_task(task)

    assert removed is True
    assert task not in pet.care_tasks


def test_pet_remove_task_returns_false_for_missing_task():
    pet = Pet(name="Mochi", species="dog")
    task = CareTask(title="Morning walk", duration_minutes=20)

    assert pet.remove_task(task) is False
    assert pet.care_tasks == []


def test_daily_schedule_add_task_adds_extra_task():
    pet = Pet(name="Mochi", species="dog")
    schedule = DailySchedule(pet=pet)
    task = CareTask(title="Grooming", duration_minutes=15)

    schedule.add_task(task)

    assert schedule.tasks == [task]


def test_daily_schedule_add_task_ignores_duplicate_task():
    pet = Pet(name="Mochi", species="dog")
    schedule = DailySchedule(pet=pet)
    task = CareTask(title="Grooming", duration_minutes=15)

    schedule.add_task(task)
    schedule.add_task(task)

    assert schedule.tasks == [task]


def test_daily_schedule_add_task_rejects_invalid_task():
    pet = Pet(name="Mochi", species="dog")
    schedule = DailySchedule(pet=pet)
    task = CareTask(title="Grooming", duration_minutes=0)

    with pytest.raises(ValueError, match="Invalid task"):
        schedule.add_task(task)


def test_schedule_generation_includes_pet_and_schedule_tasks():
    pet = Pet(name="Mochi", species="dog")
    pet_task = CareTask(title="Breakfast", duration_minutes=10)
    extra_task = CareTask(title="Walk", duration_minutes=20)
    pet.add_task(pet_task)
    schedule = DailySchedule(pet=pet)
    schedule.add_task(extra_task)

    owner = Owner(name="Jordan", available_minutes=60)

    scheduled = schedule.generate(owner)

    assert scheduled == [pet_task, extra_task]

# -----------------------------------
# Recurrence and completion filtering
# -----------------------------------

from datetime import date, timedelta

TODAY = date(2026, 11, 2)


def make_schedule(*tasks, on=TODAY):
    pet = Pet(name="Mochi", species="dog")
    for task in tasks:
        pet.add_task(task)
    return DailySchedule(pet=pet, schedule_date=on)


def test_daily_task_eligible_again_on_new_day():
    task = CareTask("Breakfast", 10, recurrence="daily")
    task.mark_complete(TODAY - timedelta(days=1))
    owner = Owner(name="Jordan", available_minutes=60)

    assert make_schedule(task).generate(owner) == [task]


def test_completed_daily_task_not_scheduled_again_same_day():
    task = CareTask("Breakfast", 10, recurrence="daily")
    task.mark_complete(TODAY)
    schedule = make_schedule(task)

    assert schedule.generate(Owner(name="Jordan", available_minutes=60)) == []
    assert schedule.skipped_tasks == [task]
    assert "already completed" in schedule.explain_task(task)


def test_weekly_task_ineligible_until_due():
    task = CareTask("Bath", 30, recurrence="weekly")
    task.mark_complete(TODAY - timedelta(days=6))
    owner = Owner(name="Jordan", available_minutes=60)

    schedule = make_schedule(task)
    assert schedule.generate(owner) == []
    assert f"next due {TODAY + timedelta(days=1)}" in schedule.explain_task(task)

    assert make_schedule(task, on=TODAY + timedelta(days=1)).generate(owner) == [task]


def test_one_time_task_excluded_after_completion():
    task = CareTask("Vet visit", 45, recurrence="once")
    owner = Owner(name="Jordan", available_minutes=60)
    assert make_schedule(task).generate(owner) == [task]

    task.mark_complete(TODAY)
    later = TODAY + timedelta(days=30)
    assert make_schedule(task, on=later).generate(owner) == []


def test_completion_is_tracked_per_task():
    walk = CareTask("Walk", 20, recurrence="daily")
    feed = CareTask("Feed", 10, recurrence="daily")
    walk.mark_complete(TODAY)

    assert make_schedule(walk, feed).generate(Owner(name="Jordan", available_minutes=60)) == [feed]


# -----------------------------------
# Sorting and time filtering
# -----------------------------------

def test_high_priority_considered_first():
    low = CareTask("Play", 5, priority="low")
    high = CareTask("Meds", 30, priority="high")
    owner = Owner(name="Jordan", available_minutes=30)

    assert make_schedule(low, high).generate(owner) == [high]


def test_shorter_task_first_when_priority_matches():
    long_task = CareTask("Walk", 30, priority="medium")
    short_task = CareTask("Brush", 10, priority="medium")
    owner = Owner(name="Jordan", available_minutes=60)

    assert make_schedule(long_task, short_task).generate(owner) == [short_task, long_task]


def test_preference_breaks_tie_then_original_order():
    a = CareTask("Fetch", 10)
    b = CareTask("Walk", 10)
    c = CareTask("Brush", 10)
    owner = Owner(name="Jordan", available_minutes=60, preferences=["walk"])

    assert make_schedule(a, b, c).generate(owner) == [b, a, c]


def test_task_exceeding_available_time_is_skipped():
    big = CareTask("Hike", 90, priority="high")
    small = CareTask("Feed", 10, priority="low")
    owner = Owner(name="Jordan", available_minutes=60)
    schedule = make_schedule(big, small)

    assert schedule.generate(owner) == [small]
    assert schedule.skipped_tasks == [big]
    assert "needs 90 min" in schedule.explain_task(big)
    assert sum(t.duration_minutes for t in schedule.scheduled_tasks) <= owner.available_minutes


def test_empty_task_list():
    schedule = make_schedule()

    assert schedule.generate(Owner(name="Jordan", available_minutes=60)) == []
    assert schedule.remaining_minutes == 60
    assert "No tasks scheduled." in schedule.get_summary()


def test_zero_available_minutes_skips_everything():
    task = CareTask("Feed", 5)
    schedule = make_schedule(task)

    assert schedule.generate(Owner(name="Jordan", available_minutes=0)) == []
    assert schedule.skipped_tasks == [task]
    assert schedule.remaining_minutes == 0


def test_repeated_generation_has_no_duplicates():
    task = CareTask("Feed", 5)
    schedule = make_schedule(task)
    schedule.add_task(task)
    owner = Owner(name="Jordan", available_minutes=60)

    schedule.generate(owner)
    scheduled = schedule.generate(owner)

    assert scheduled == [task]
    assert schedule.tasks == [task]
    assert schedule.remaining_minutes == 55
