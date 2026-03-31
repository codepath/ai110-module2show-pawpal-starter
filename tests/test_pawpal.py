import datetime

from pawpal.pawpal_system import (
    AvailabilityWindow, DailySchedule, Owner, Pet, Scheduler,
    Task, TaskType, Priority, RecurrenceScope,
)


def test_mark_complete_changes_status():
    task = Task(
        name="Morning Walk",
        task_type=TaskType.WALK,
        priority=Priority.HIGH,
        scope=RecurrenceScope.DAILY,
        duration_minutes=30,
    )
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_task_count():
    pet = Pet(name="Buddy", species="Dog", age=3)
    task = Task(
        name="Evening Feed",
        task_type=TaskType.FEED,
        priority=Priority.MEDIUM,
        scope=RecurrenceScope.DAILY,
        duration_minutes=15,
    )
    assert len(pet._tasks) == 0

    pet.add_task(task)

    assert len(pet._tasks) == 1


# ---------------------------------------------------------------------------
# sort_by_time
# ---------------------------------------------------------------------------

def test_sort_by_time_orders_ascending():
    scheduler = Scheduler()
    t1 = Task(name="Walk", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30,
              scheduled_time=datetime.time(10, 0))
    t2 = Task(name="Feed", task_type=TaskType.FEED, priority=Priority.MEDIUM,
              scope=RecurrenceScope.DAILY, duration_minutes=15,
              scheduled_time=datetime.time(8, 0))

    result = scheduler.sort_by_time([t1, t2])

    assert result[0].name == "Feed"
    assert result[1].name == "Walk"


def test_sort_by_time_none_scheduled_time_comes_first():
    scheduler = Scheduler()
    t1 = Task(name="Walk", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30,
              scheduled_time=datetime.time(9, 0))
    t2 = Task(name="Groom", task_type=TaskType.GROOMING, priority=Priority.LOW,
              scope=RecurrenceScope.DAILY, duration_minutes=20)

    result = scheduler.sort_by_time([t1, t2])

    assert result[0].name == "Groom"
    assert result[1].name == "Walk"


# ---------------------------------------------------------------------------
# filter_by_pet
# ---------------------------------------------------------------------------

def test_filter_by_pet_returns_matching_tasks():
    scheduler = Scheduler()
    t1 = Task(name="Walk Biscuit", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30, pet_name="Biscuit")
    t2 = Task(name="Walk Rex", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30, pet_name="Rex")

    result = scheduler.filter_by_pet([t1, t2], "Biscuit")

    assert len(result) == 1
    assert result[0].name == "Walk Biscuit"


def test_filter_by_pet_returns_empty_when_no_match():
    scheduler = Scheduler()
    t1 = Task(name="Walk Rex", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30, pet_name="Rex")

    result = scheduler.filter_by_pet([t1], "Biscuit")

    assert len(result) == 0


def test_add_task_sets_pet_name():
    pet = Pet(name="Biscuit", species="Cat", age=5)
    task = Task(name="Feed", task_type=TaskType.FEED, priority=Priority.MEDIUM,
                scope=RecurrenceScope.DAILY, duration_minutes=10)

    pet.add_task(task)

    assert task.pet_name == "Biscuit"


# ---------------------------------------------------------------------------
# filter_by_completion
# ---------------------------------------------------------------------------

def test_filter_by_completion_incomplete():
    scheduler = Scheduler()
    t1 = Task(name="Walk", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30, completed=True)
    t2 = Task(name="Feed", task_type=TaskType.FEED, priority=Priority.MEDIUM,
              scope=RecurrenceScope.DAILY, duration_minutes=15)

    result = scheduler.filter_by_completion([t1, t2], completed=False)

    assert len(result) == 1
    assert result[0].name == "Feed"


def test_filter_by_completion_completed():
    scheduler = Scheduler()
    t1 = Task(name="Walk", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30, completed=True)
    t2 = Task(name="Feed", task_type=TaskType.FEED, priority=Priority.MEDIUM,
              scope=RecurrenceScope.DAILY, duration_minutes=15)

    result = scheduler.filter_by_completion([t1, t2], completed=True)

    assert len(result) == 1
    assert result[0].name == "Walk"


# ---------------------------------------------------------------------------
# detect_conflicts
# ---------------------------------------------------------------------------

def test_detect_conflicts_finds_overlap():
    scheduler = Scheduler()
    t1 = Task(name="Walk", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30,
              scheduled_time=datetime.time(9, 0))
    t2 = Task(name="Feed", task_type=TaskType.FEED, priority=Priority.MEDIUM,
              scope=RecurrenceScope.DAILY, duration_minutes=15,
              scheduled_time=datetime.time(9, 15))

    conflicts = scheduler.detect_conflicts([t1, t2])

    assert len(conflicts) == 1
    assert conflicts[0] == (t1, t2)


def test_detect_conflicts_no_overlap():
    scheduler = Scheduler()
    t1 = Task(name="Walk", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30,
              scheduled_time=datetime.time(9, 0))
    t2 = Task(name="Feed", task_type=TaskType.FEED, priority=Priority.MEDIUM,
              scope=RecurrenceScope.DAILY, duration_minutes=15,
              scheduled_time=datetime.time(9, 30))

    conflicts = scheduler.detect_conflicts([t1, t2])

    assert len(conflicts) == 0


def test_detect_conflicts_skips_unscheduled_tasks():
    scheduler = Scheduler()
    t1 = Task(name="Walk", task_type=TaskType.WALK, priority=Priority.HIGH,
              scope=RecurrenceScope.DAILY, duration_minutes=30,
              scheduled_time=datetime.time(9, 0))
    t2 = Task(name="Groom", task_type=TaskType.GROOMING, priority=Priority.LOW,
              scope=RecurrenceScope.DAILY, duration_minutes=20)

    conflicts = scheduler.detect_conflicts([t1, t2])

    assert len(conflicts) == 0
