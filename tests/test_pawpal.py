"""
PawPal+ automated test suite
=============================
Covers both the original happy-path tests and the new algorithmic behaviors:
  - task completion
  - task addition
  - sort_by_time correctness
  - recurrence / next-occurrence spawning
  - conflict detection
  - edge cases (no tasks, same-time tasks, non-recurring completion)
"""
from datetime import date, time, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, TimeWindow, Schedule, TaskInstance
import uuid


# ---------------------------------------------------------------------------
# Original tests (happy path)
# ---------------------------------------------------------------------------

def test_task_completion():
    """Calling complete() on a Task should change completed to True."""
    task = Task(title="Morning walk", duration_minutes=30, priority="high")

    assert task.completed is False  # starts incomplete

    task.complete()

    assert task.completed is True


def test_task_addition_increases_count():
    """Adding a Task to a Pet should increase that pet's task count by one."""
    pet = Pet(name="Mochi", species="dog")

    assert len(pet.get_tasks()) == 0  # starts empty

    pet.add_task(Task(title="Feeding", duration_minutes=10, priority="high"))

    assert len(pet.get_tasks()) == 1


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks with earlier earliest_start should come first after sort_by_time."""
    scheduler = Scheduler()

    # Add tasks deliberately out of order
    tasks = [
        Task("Evening walk",  duration_minutes=20, earliest_start=time(18, 0)),
        Task("Morning meds",  duration_minutes=5,  earliest_start=time(7, 30)),
        Task("Lunch feeding", duration_minutes=10, earliest_start=time(12, 0)),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    # Extract the start times from the sorted result
    starts = [t.earliest_start for t in sorted_tasks]

    assert starts == [time(7, 30), time(12, 0), time(18, 0)]


def test_sort_by_time_puts_no_start_tasks_last():
    """Tasks with no earliest_start should land at the end of the sorted list."""
    scheduler = Scheduler()

    tasks = [
        Task("Anytime grooming", duration_minutes=15),          # no start time
        Task("Morning walk",     duration_minutes=30, earliest_start=time(7, 0)),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    # The task with a start time should come first
    assert sorted_tasks[0].title == "Morning walk"
    assert sorted_tasks[1].earliest_start is None


# ---------------------------------------------------------------------------
# Recurrence tests
# ---------------------------------------------------------------------------

def test_daily_task_spawns_next_occurrence_on_completion():
    """Completing a daily task should automatically add a new copy to the pet."""
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task("Litter box", duration_minutes=10, priority="medium", recurrence="daily"))

    assert len(pet.get_tasks()) == 1  # only the original

    original = pet.get_tasks()[0]
    today = date.today()
    pet.complete_task(original.id, today=today)

    # Pet should now have 2 tasks: the completed original + the new occurrence
    assert len(pet.get_tasks()) == 2

    # The original is marked done
    assert pet.get_tasks()[0].completed is True

    # The new occurrence is pending and due tomorrow
    new_task = pet.get_tasks()[1]
    assert new_task.completed is False
    assert new_task.next_due == today + timedelta(days=1)


def test_weekly_task_spawns_next_occurrence_seven_days_later():
    """Completing a weekly task should set next_due to today + 7 days."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Vet checkup", duration_minutes=60, priority="high", recurrence="weekly"))

    today = date.today()
    original = pet.get_tasks()[0]
    pet.complete_task(original.id, today=today)

    new_task = pet.get_tasks()[1]
    assert new_task.next_due == today + timedelta(weeks=1)


def test_non_recurring_task_does_not_spawn_next_occurrence():
    """Completing a one-off task should NOT add a new task to the pet."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Flea treatment", duration_minutes=10, priority="high"))  # no recurrence

    original = pet.get_tasks()[0]
    pet.complete_task(original.id, today=date.today())

    # Still only 1 task — no new occurrence created
    assert len(pet.get_tasks()) == 1


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def _make_slot(title: str, start: time, end: time, target_date=None) -> TaskInstance:
    """Helper: build a TaskInstance at a specific time for conflict tests."""
    d = target_date or date.today()
    from datetime import datetime
    return TaskInstance(
        task_id=uuid.uuid4(),
        title=title,
        start=datetime.combine(d, start),
        end=datetime.combine(d, end),
    )


def test_conflict_detection_flags_overlapping_slots():
    """Two slots whose times overlap should produce at least one warning."""
    scheduler = Scheduler()

    # Build a fake schedule with two overlapping slots
    slot_a = _make_slot("Morning walk",  time(7, 0), time(7, 30))
    slot_b = _make_slot("Breakfast",     time(7, 15), time(7, 25))  # overlaps slot_a

    fake_schedule = Schedule(date=date.today(), owner_id=uuid.uuid4(), slots=[slot_a, slot_b])

    warnings = scheduler.detect_conflicts(fake_schedule)

    assert len(warnings) >= 1
    assert "Morning walk" in warnings[0] or "Breakfast" in warnings[0]


def test_conflict_detection_no_warning_for_sequential_slots():
    """Slots that run back-to-back (not overlapping) should produce no warnings."""
    scheduler = Scheduler()

    slot_a = _make_slot("Morning walk", time(7, 0),  time(7, 30))
    slot_b = _make_slot("Breakfast",   time(7, 30), time(7, 40))  # starts exactly when a ends

    fake_schedule = Schedule(date=date.today(), owner_id=uuid.uuid4(), slots=[slot_a, slot_b])

    warnings = scheduler.detect_conflicts(fake_schedule)

    assert warnings == []


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_scheduler_handles_pet_with_no_tasks():
    """Generating a schedule when all pets have zero tasks should return an empty slot list."""
    owner = Owner("Jordan", availability_windows=[TimeWindow(time(7, 0), time(21, 0))])
    owner.add_pet(Pet("Mochi", "dog"))  # pet exists but has no tasks

    schedule = Scheduler().generate_daily_plan(owner, date.today())

    assert schedule.slots == []
    assert schedule.total_minutes_scheduled == 0


def test_filter_tasks_by_pet_name():
    """filter_tasks with a pet_name should return only that pet's tasks."""
    owner = Owner("Jordan", availability_windows=[TimeWindow(time(7, 0), time(21, 0))])

    mochi = Pet("Mochi", "dog")
    luna  = Pet("Luna",  "cat")
    mochi.add_task(Task("Walk",    duration_minutes=30, priority="high"))
    luna.add_task(Task("Feeding",  duration_minutes=10, priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    results = Scheduler().filter_tasks(owner, pet_name="Mochi")

    assert len(results) == 1
    assert results[0].title == "Walk"


def test_filter_tasks_by_completion_status():
    """filter_tasks with completed=False should exclude finished tasks."""
    owner = Owner("Jordan", availability_windows=[TimeWindow(time(7, 0), time(21, 0))])
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk",     duration_minutes=30, priority="high"))
    pet.add_task(Task("Grooming", duration_minutes=20, priority="low"))
    owner.add_pet(pet)

    # Complete the first task
    pet.complete_task(pet.get_tasks()[0].id, today=date.today())

    pending = Scheduler().filter_tasks(owner, completed=False)

    # Only the non-recurring Grooming should remain pending
    titles = [t.title for t in pending if not t.completed]
    assert "Grooming" in titles
    assert "Walk" not in titles
