"""Automated test suite for PawPal+ core logic."""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def owner_with_pets():
    today = date.today()
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "cat")
    rex   = Pet("Rex", "dog")
    owner.add_pet(mochi)
    owner.add_pet(rex)
    return owner, mochi, rex, today


@pytest.fixture
def scheduler(owner_with_pets):
    owner, mochi, rex, today = owner_with_pets
    return Scheduler(owner), mochi, rex, today


# ---------------------------------------------------------------------------
# Phase 2 basic tests
# ---------------------------------------------------------------------------

def test_task_completion_changes_status():
    """mark_complete() must flip completed from False to True."""
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_count():
    """Adding a Task to a Pet should increase the pet's task list length."""
    pet = Pet("Mochi", "cat")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feeding", "07:30"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Medication", "12:00"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order(scheduler):
    sched, mochi, rex, today = scheduler
    mochi.add_task(Task("Evening feeding", "18:00", due_date=today))
    mochi.add_task(Task("Morning feeding", "07:30", due_date=today))
    mochi.add_task(Task("Medication",      "12:00", due_date=today))

    sorted_tasks = sched.sort_by_time()
    times = [t.time for _, t in sorted_tasks]
    assert times == sorted(times), "Tasks should be in ascending time order"


def test_sort_by_priority_high_before_low(scheduler):
    sched, mochi, rex, today = scheduler
    mochi.add_task(Task("Low task",  "09:00", priority="low",  due_date=today))
    mochi.add_task(Task("High task", "09:00", priority="high", due_date=today))

    result = sched.sort_by_priority()
    priorities = [t.priority for _, t in result]
    assert priorities[0] == "high"
    assert priorities[-1] == "low"


# ---------------------------------------------------------------------------
# Recurrence tests
# ---------------------------------------------------------------------------

def test_daily_task_creates_next_occurrence(scheduler):
    """Completing a daily task should create a new task due the next day."""
    sched, mochi, rex, today = scheduler
    task = Task("Morning feeding", "07:30", frequency="daily", due_date=today)
    mochi.add_task(task)

    initial_count = len(mochi.tasks)
    next_task = sched.mark_task_complete(mochi, task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert len(mochi.tasks) == initial_count + 1


def test_weekly_task_creates_next_occurrence(scheduler):
    """Completing a weekly task should create a new task due 7 days later."""
    sched, mochi, rex, today = scheduler
    task = Task("Grooming", "10:00", frequency="weekly", due_date=today)
    rex.add_task(task)

    next_task = sched.mark_task_complete(rex, task)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_once_task_does_not_recur(scheduler):
    """Completing a one-time task should NOT create a follow-up task."""
    sched, mochi, rex, today = scheduler
    task = Task("Vet visit", "10:00", frequency="once", due_date=today)
    mochi.add_task(task)

    initial_count = len(mochi.tasks)
    next_task = sched.mark_task_complete(mochi, task)

    assert next_task is None
    assert len(mochi.tasks) == initial_count  # no new task added


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_conflict_detection_flags_same_time(scheduler):
    """Two tasks for the same pet at the same time/date should be flagged."""
    sched, mochi, rex, today = scheduler
    mochi.add_task(Task("Feeding",   "08:00", due_date=today))
    mochi.add_task(Task("Play time", "08:00", due_date=today))

    warnings = sched.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_no_conflict_for_different_times(scheduler):
    """Tasks at different times should not produce any conflict warnings."""
    sched, mochi, rex, today = scheduler
    mochi.add_task(Task("Feeding",    "08:00", due_date=today))
    mochi.add_task(Task("Medication", "12:00", due_date=today))

    warnings = sched.detect_conflicts()
    assert warnings == []


def test_no_conflict_for_different_pets(scheduler):
    """Same time is OK if tasks belong to different pets."""
    sched, mochi, rex, today = scheduler
    mochi.add_task(Task("Feeding", "08:00", due_date=today))
    rex.add_task(Task("Walk",    "08:00", due_date=today))

    warnings = sched.detect_conflicts()
    assert warnings == []


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------

def test_filter_by_pet_returns_only_that_pet(scheduler):
    """filter_by_pet should return tasks for only the named pet."""
    sched, mochi, rex, today = scheduler
    mochi.add_task(Task("Feeding", "08:00", due_date=today))
    rex.add_task(Task("Walk",    "09:00", due_date=today))

    mochi_tasks = sched.filter_by_pet("Mochi")
    assert all(p.name == "Mochi" for p, _ in mochi_tasks)


def test_filter_by_status_incomplete(scheduler):
    """filter_by_status(completed=False) should exclude completed tasks."""
    sched, mochi, rex, today = scheduler
    t1 = Task("Walk",    "08:00", due_date=today)
    t2 = Task("Feeding", "09:00", due_date=today)
    mochi.add_task(t1)
    mochi.add_task(t2)
    t1.mark_complete()

    pending = sched.filter_by_status(completed=False)
    assert all(not t.completed for _, t in pending)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks(scheduler):
    """A pet with no tasks should produce empty schedule without errors."""
    sched, mochi, rex, today = scheduler
    tasks = sched.filter_by_pet("Mochi")
    assert tasks == []


def test_get_next_available_slot(scheduler):
    """Slot finder should skip occupied times and return a free slot."""
    sched, mochi, rex, today = scheduler
    # Fill 07:00 and 07:30 for Rex
    rex.add_task(Task("Walk 1", "07:00", due_date=today))
    rex.add_task(Task("Walk 2", "07:30", due_date=today))

    slot = sched.get_next_available_slot("Rex", today)
    assert slot == "08:00"
