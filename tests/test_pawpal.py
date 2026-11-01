"""Automated regression and new-requirement tests for PawPal+.

Run from a directory containing pawpal_system.py:
    python -m pytest -v test_pawpal_system.py

The three tests under 'New requirements' intentionally FAIL until the requested
features are implemented. Existing behavior tests provide a baseline.
"""

from datetime import date, timedelta

import pytest

from pawpal_system import CareTask, DailySchedule, Owner, Pet


@pytest.fixture
def owner():
    return Owner(name="Jordan", available_minutes=90)


@pytest.fixture
def pet():
    return Pet(name="Mochi", species="dog")


# Existing behavior: should pass on the uploaded backend.

def test_priority_then_duration_sorting(owner, pet):
    pet.add_task(CareTask("Low priority", 5, "low"))
    pet.add_task(CareTask("Long high", 30, "high"))
    pet.add_task(CareTask("Short high", 10, "high"))
    plan = DailySchedule(pet=pet, schedule_date=date(2026, 11, 1)).generate(owner)
    assert [t.title for t in plan] == ["Short high", "Long high", "Low priority"]


def test_daily_task_due_on_following_day_but_not_completion_day():
    task = CareTask("Breakfast", 10, "high", "daily")
    today = date(2026, 11, 1)
    task.mark_complete(on=today)
    assert not task.is_due(today)
    assert task.next_due_date() == today + timedelta(days=1)
    assert task.is_due(today + timedelta(days=1))


def test_weekly_task_due_after_seven_days():
    task = CareTask("Grooming", 30, "medium", "weekly")
    today = date(2026, 11, 1)
    task.mark_complete(on=today)
    assert not task.is_due(today + timedelta(days=6))
    assert task.is_due(today + timedelta(days=7))


def test_no_overbooking_by_total_minutes(owner, pet):
    owner.available_minutes = 40
    pet.add_task(CareTask("Walk", 30, "high"))
    pet.add_task(CareTask("Feed", 20, "medium"))
    schedule = DailySchedule(pet=pet, schedule_date=date(2026, 11, 1))
    result = schedule.generate(owner)
    assert sum(t.duration_minutes for t in result) <= owner.available_minutes
    assert schedule.remaining_minutes >= 0


# New requirements: expected to fail with the current backend.

def test_chronological_sorting_by_start_time(owner, pet):
    """Scheduling should return tasks in ascending time, not priority order."""
    morning = CareTask("Morning feeding", 15, "low")
    afternoon = CareTask("Afternoon walk", 20, "high")
    # Time attributes are pending features; setting them dynamically allows
    # this test to expose the current sorting behavior without requiring
    # constructor support yet.
    morning.start_time = "08:00"
    afternoon.start_time = "15:00"
    pet.add_task(afternoon)
    pet.add_task(morning)
    schedule = DailySchedule(pet=pet, schedule_date=date(2026, 11, 1))
    actual = schedule.generate(owner)
    assert [t.title for t in actual] == ["Morning feeding", "Afternoon walk"]


def test_daily_completion_creates_new_next_day_task(owner, pet):
    """A completed daily occurrence should create a distinct next-day task."""
    completed_on = date(2026, 11, 1)
    original = CareTask("Breakfast", 10, "high", "daily")
    pet.add_task(original)
    original.mark_complete(on=completed_on)
    tomorrow_schedule = DailySchedule(
        pet=pet, schedule_date=completed_on + timedelta(days=1)
    )
    next_day_tasks = tomorrow_schedule.generate(owner)
    matches = [t for t in next_day_tasks if t.title == original.title]
    assert len(matches) == 1
    assert matches[0] is not original, (
        "Expected a new task instance for the next day; currently the same "
        "CareTask instance is reused."
    )


def test_scheduler_flags_duplicate_time_slots():
    """Two tasks starting at the same time should cause a reported conflict."""
    from pawpal_system import Scheduler  # New requirement; not yet implemented.

    scheduler = Scheduler()
    a = CareTask("Feeding", 15, "high")
    b = CareTask("Walking", 30, "medium")
    a.start_time = "09:00"
    b.start_time = "09:00"
    conflicts = scheduler.detect_conflicts([a, b])
    assert conflicts, "Expected at least one time conflict at 09:00."
