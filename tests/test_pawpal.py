"""
Automated test suite for PawPal+ scheduler logic.

Covers:
  - Sorting correctness (tasks returned in chronological order)
  - Recurrence logic (daily and weekly auto-scheduling)
  - Conflict detection (exact-time duplicates flagged)
  - Filtering (by pet name and completion status)
  - Edge cases (empty pet, pet with no tasks, overdue logic)
  - Core model operations (add/remove pet, cancel appointment, notes)

Run with:
    python -m pytest
"""

from datetime import datetime, timedelta

import pytest

from pawpal_system import Appointment, Owner, Pet, Reminder, Scheduler, Task


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

BASE_TIME = datetime(2026, 4, 1, 9, 0)   # fixed anchor so tests don't drift


@pytest.fixture
def owner():
    return Owner(name="Maya", email="maya@example.com")


@pytest.fixture
def pet(owner):
    p = Pet(name="Buddy", species="Dog", owner_id=owner.owner_id)
    owner.add_pet(p)
    return p


@pytest.fixture
def scheduler(owner):
    return Scheduler(owner=owner)


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

class TestSorting:
    def test_tasks_returned_in_chronological_order(self, owner, pet, scheduler):
        """Tasks added out of order should be returned earliest-first."""
        t1 = Task(title="Walk",  pet_id=pet.pet_id, due_date=BASE_TIME + timedelta(hours=3))
        t2 = Task(title="Feed",  pet_id=pet.pet_id, due_date=BASE_TIME + timedelta(hours=1))
        t3 = Task(title="Meds",  pet_id=pet.pet_id, due_date=BASE_TIME + timedelta(hours=2))
        pet.add_task(t1)
        pet.add_task(t2)
        pet.add_task(t3)

        result = scheduler.sort_by_time()
        assert [t.title for t in result] == ["Feed", "Meds", "Walk"]

    def test_sort_single_task(self, owner, pet, scheduler):
        """A single task sorts without error."""
        t = Task(title="Solo", pet_id=pet.pet_id, due_date=BASE_TIME)
        pet.add_task(t)
        assert scheduler.sort_by_time() == [t]

    def test_sort_empty_returns_empty(self, scheduler):
        """Sorting an owner with no pets/tasks returns an empty list."""
        assert scheduler.sort_by_time() == []

    def test_sort_across_multiple_pets(self, owner, scheduler):
        """Sorting should interleave tasks from different pets correctly."""
        buddy = Pet(name="Buddy", species="Dog", owner_id=owner.owner_id)
        luna  = Pet(name="Luna",  species="Cat", owner_id=owner.owner_id)
        owner.add_pet(buddy)
        owner.add_pet(luna)

        buddy.add_task(Task(title="Walk", pet_id=buddy.pet_id, due_date=BASE_TIME + timedelta(hours=2)))
        luna.add_task( Task(title="Meds", pet_id=luna.pet_id,  due_date=BASE_TIME + timedelta(hours=1)))

        result = scheduler.sort_by_time()
        assert result[0].title == "Meds"
        assert result[1].title == "Walk"


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

class TestRecurrence:
    def test_daily_task_creates_next_occurrence(self, owner, pet, scheduler):
        """Completing a daily task auto-creates a task due the following day."""
        task = Task(title="Morning walk", pet_id=pet.pet_id,
                    due_date=BASE_TIME, recurrence="daily")
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(task, pet)

        assert task.is_complete is True
        assert task.completed_at is not None
        assert next_task is not None
        assert next_task.title == "Morning walk"
        assert next_task.recurrence == "daily"
        expected_date = (task.completed_at + timedelta(days=1)).date()
        assert next_task.due_date.date() == expected_date

    def test_weekly_task_creates_next_occurrence_seven_days_later(self, owner, pet, scheduler):
        """Completing a weekly task schedules the next occurrence 7 days out."""
        task = Task(title="Grooming", pet_id=pet.pet_id,
                    due_date=BASE_TIME, recurrence="weekly")
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(task, pet)

        assert next_task is not None
        delta = next_task.due_date - task.completed_at
        assert delta.days == 7

    def test_one_time_task_returns_none(self, owner, pet, scheduler):
        """Completing a non-recurring task returns None and adds no new task."""
        task = Task(title="Vet visit", pet_id=pet.pet_id,
                    due_date=BASE_TIME, recurrence=None)
        pet.add_task(task)
        initial_count = len(pet.tasks)

        next_task = scheduler.mark_task_complete(task, pet)

        assert next_task is None
        assert len(pet.tasks) == initial_count   # no new task added

    def test_recurring_task_added_to_pet(self, owner, pet, scheduler):
        """The auto-created next task should appear in pet.tasks."""
        task = Task(title="Feed", pet_id=pet.pet_id,
                    due_date=BASE_TIME, recurrence="daily")
        pet.add_task(task)

        scheduler.mark_task_complete(task, pet)

        assert len(pet.tasks) == 2
        titles = [t.title for t in pet.tasks]
        assert titles.count("Feed") == 2


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:
    def test_exact_same_time_produces_warning(self, owner, pet, scheduler):
        """Two tasks at identical due_dates should produce a conflict warning."""
        conflict_time = BASE_TIME
        t1 = Task(title="Walk", pet_id=pet.pet_id, due_date=conflict_time)
        t2 = Task(title="Feed", pet_id=pet.pet_id, due_date=conflict_time)
        pet.add_task(t1)
        pet.add_task(t2)

        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        # Both task titles should appear somewhere in the warning message
        assert "Walk" in warnings[0] or "Feed" in warnings[0]

    def test_different_times_no_conflict(self, owner, pet, scheduler):
        """Tasks at different times should produce no warnings."""
        pet.add_task(Task(title="Walk", pet_id=pet.pet_id, due_date=BASE_TIME))
        pet.add_task(Task(title="Feed", pet_id=pet.pet_id, due_date=BASE_TIME + timedelta(hours=1)))

        assert scheduler.detect_conflicts() == []

    def test_completed_tasks_excluded_from_conflict_check(self, owner, pet, scheduler):
        """A completed task should not trigger a conflict warning."""
        t1 = Task(title="Old walk", pet_id=pet.pet_id, due_date=BASE_TIME)
        t2 = Task(title="New walk", pet_id=pet.pet_id, due_date=BASE_TIME)
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)

        assert scheduler.detect_conflicts() == []

    def test_three_way_conflict_produces_two_warnings(self, owner, pet, scheduler):
        """Three tasks at the same time → first is stored, second and third each warn."""
        for title in ["A", "B", "C"]:
            pet.add_task(Task(title=title, pet_id=pet.pet_id, due_date=BASE_TIME))

        warnings = scheduler.detect_conflicts()
        assert len(warnings) == 2


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

class TestFiltering:
    def test_filter_by_pet_name(self, owner, scheduler):
        buddy = Pet(name="Buddy", species="Dog", owner_id=owner.owner_id)
        luna  = Pet(name="Luna",  species="Cat", owner_id=owner.owner_id)
        owner.add_pet(buddy)
        owner.add_pet(luna)

        buddy.add_task(Task(title="Walk", pet_id=buddy.pet_id, due_date=BASE_TIME))
        luna.add_task( Task(title="Meds", pet_id=luna.pet_id,  due_date=BASE_TIME))

        result = scheduler.filter_tasks(pet_name="Buddy")
        assert len(result) == 1
        assert result[0].title == "Walk"

    def test_filter_pet_name_case_insensitive(self, owner, scheduler):
        buddy = Pet(name="Buddy", species="Dog", owner_id=owner.owner_id)
        owner.add_pet(buddy)
        buddy.add_task(Task(title="Walk", pet_id=buddy.pet_id, due_date=BASE_TIME))

        assert len(scheduler.filter_tasks(pet_name="buddy")) == 1
        assert len(scheduler.filter_tasks(pet_name="BUDDY")) == 1

    def test_filter_by_incomplete(self, owner, pet, scheduler):
        t1 = Task(title="Done",    pet_id=pet.pet_id, due_date=BASE_TIME)
        t2 = Task(title="Pending", pet_id=pet.pet_id, due_date=BASE_TIME + timedelta(hours=1))
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)

        incomplete = scheduler.filter_tasks(completed=False)
        assert len(incomplete) == 1
        assert incomplete[0].title == "Pending"

    def test_filter_by_complete(self, owner, pet, scheduler):
        t1 = Task(title="Done",    pet_id=pet.pet_id, due_date=BASE_TIME)
        t2 = Task(title="Pending", pet_id=pet.pet_id, due_date=BASE_TIME + timedelta(hours=1))
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)

        complete = scheduler.filter_tasks(completed=True)
        assert len(complete) == 1
        assert complete[0].title == "Done"

    def test_filter_composable_pet_and_status(self, owner, scheduler):
        """Both filters applied together should narrow results correctly."""
        buddy = Pet(name="Buddy", species="Dog", owner_id=owner.owner_id)
        luna  = Pet(name="Luna",  species="Cat", owner_id=owner.owner_id)
        owner.add_pet(buddy)
        owner.add_pet(luna)

        done_buddy = Task(title="Done-Buddy", pet_id=buddy.pet_id, due_date=BASE_TIME)
        todo_buddy = Task(title="Todo-Buddy", pet_id=buddy.pet_id, due_date=BASE_TIME + timedelta(hours=1))
        todo_luna  = Task(title="Todo-Luna",  pet_id=luna.pet_id,  due_date=BASE_TIME)
        done_buddy.mark_complete()
        buddy.add_task(done_buddy)
        buddy.add_task(todo_buddy)
        luna.add_task(todo_luna)

        result = scheduler.filter_tasks(pet_name="Buddy", completed=False)
        assert len(result) == 1
        assert result[0].title == "Todo-Buddy"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_pet_with_no_tasks(self, owner, scheduler):
        """A pet registered but given no tasks should produce empty results."""
        empty_pet = Pet(name="Ghost", species="Cat", owner_id=owner.owner_id)
        owner.add_pet(empty_pet)

        assert scheduler.all_tasks() == []
        assert scheduler.sort_by_time() == []
        assert scheduler.detect_conflicts() == []

    def test_owner_with_no_pets(self, scheduler):
        """Owner with no pets should never raise; all methods return empty."""
        assert scheduler.all_tasks() == []
        assert scheduler.filter_tasks() == []
        assert scheduler.detect_conflicts() == []

    def test_overdue_incomplete_task(self):
        """A task past its due_date and not complete should be overdue."""
        past = datetime(2000, 1, 1, 8, 0)
        task = Task(title="Old task", pet_id="fake", due_date=past)
        assert task.is_overdue() is True

    def test_complete_task_not_overdue(self):
        """A completed task should never report as overdue, even if past due."""
        past = datetime(2000, 1, 1, 8, 0)
        task = Task(title="Old task", pet_id="fake", due_date=past)
        task.mark_complete()
        assert task.is_overdue() is False

    def test_future_task_not_overdue(self):
        future = datetime(2099, 1, 1, 8, 0)
        task = Task(title="Future", pet_id="fake", due_date=future)
        assert task.is_overdue() is False

    def test_mark_complete_sets_timestamp(self):
        task = Task(title="X", pet_id="fake", due_date=BASE_TIME)
        assert task.completed_at is None
        task.mark_complete()
        assert task.completed_at is not None
        assert task.is_complete is True


# ---------------------------------------------------------------------------
# Core model operations
# ---------------------------------------------------------------------------

class TestModel:
    def test_owner_add_and_remove_pet(self, owner):
        p = Pet(name="Rex", species="Dog", owner_id=owner.owner_id)
        owner.add_pet(p)
        assert len(owner.pets) == 1

        owner.remove_pet(p.pet_id)
        assert len(owner.pets) == 0

    def test_owner_get_upcoming_tasks_aggregates_all_pets(self, owner):
        buddy = Pet(name="Buddy", species="Dog", owner_id=owner.owner_id)
        luna  = Pet(name="Luna",  species="Cat", owner_id=owner.owner_id)
        owner.add_pet(buddy)
        owner.add_pet(luna)

        buddy.add_task(Task(title="Walk", pet_id=buddy.pet_id, due_date=BASE_TIME))
        luna.add_task( Task(title="Meds", pet_id=luna.pet_id,  due_date=BASE_TIME))

        tasks = owner.get_upcoming_tasks()
        assert len(tasks) == 2

    def test_get_upcoming_excludes_completed(self, owner, pet):
        t1 = Task(title="Done",    pet_id=pet.pet_id, due_date=BASE_TIME)
        t2 = Task(title="Pending", pet_id=pet.pet_id, due_date=BASE_TIME + timedelta(hours=1))
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)

        assert len(owner.get_upcoming_tasks()) == 1

    def test_appointment_cancel(self):
        appt = Appointment(
            pet_id="fake",
            appointment_type="vet checkup",
            provider_name="Dr. Smith",
            location="123 Main St",
            date_time=BASE_TIME + timedelta(days=7),
        )
        assert appt.cancelled is False
        appt.cancel()
        assert appt.cancelled is True

    def test_appointment_add_notes(self):
        appt = Appointment(
            pet_id="fake",
            appointment_type="grooming",
            provider_name="Snip & Clip",
            location="456 Oak Ave",
            date_time=BASE_TIME + timedelta(days=3),
        )
        appt.add_notes("Bring vaccination records.")
        appt.add_notes("Ask about flea treatment.")
        assert "vaccination records" in appt.notes
        assert "flea treatment" in appt.notes

    def test_pet_task_index_enables_complete_by_id(self, owner, pet):
        task = Task(title="Walk", pet_id=pet.pet_id, due_date=BASE_TIME)
        pet.add_task(task)

        pet.complete_task(task.task_id)
        assert task.is_complete is True

    def test_pet_complete_task_unknown_id_does_not_crash(self, owner, pet):
        pet.complete_task("nonexistent-id")   # should be a no-op

    def test_owner_add_reminder(self, owner):
        reminder = Reminder(
            owner_id=owner.owner_id,
            message="Buddy's walk in 10 minutes",
            send_at=BASE_TIME,
        )
        owner.add_reminder(reminder)
        assert len(owner.reminders) == 1
