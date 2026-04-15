"""
Automated test suite for PawPal+ core behaviors.
Run with: python -m pytest
"""
import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_owner_with_pet(pet_name="Rex", species="dog"):
    owner = Owner("Test Owner")
    pet = Pet(pet_name, species)
    owner.add_pet(pet)
    return owner, pet


# ── Task completion ────────────────────────────────────────────────────────────

class TestTaskCompletion:
    def test_mark_complete_changes_status(self):
        task = Task("Walk", "08:00", 20, "high")
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_mark_complete_idempotent(self):
        task = Task("Walk", "08:00", 20, "high")
        task.mark_complete()
        task.mark_complete()   # should not raise
        assert task.completed is True


# ── Pet task management ────────────────────────────────────────────────────────

class TestPetTaskManagement:
    def test_add_task_increases_count(self):
        pet = Pet("Mochi", "dog")
        assert len(pet.get_tasks()) == 0
        pet.add_task(Task("Walk", "08:00", 20, "high"))
        assert len(pet.get_tasks()) == 1

    def test_multiple_tasks_all_stored(self):
        pet = Pet("Luna", "cat")
        for i in range(3):
            pet.add_task(Task(f"Task {i}", f"0{i+8}:00", 10, "low"))
        assert len(pet.get_tasks()) == 3


# ── Sorting ────────────────────────────────────────────────────────────────────

class TestSorting:
    def test_sort_by_time_chronological(self):
        owner, pet = make_owner_with_pet()
        pet.add_task(Task("Evening walk",  "18:00", 30, "high"))
        pet.add_task(Task("Morning walk",  "07:00", 20, "high"))
        pet.add_task(Task("Midday feeding","12:00",  5, "medium"))

        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.sort_by_time()
        times = [t.time for _, t in sorted_tasks]
        assert times == sorted(times)

    def test_sort_handles_single_task(self):
        owner, pet = make_owner_with_pet()
        pet.add_task(Task("Walk", "09:00", 20, "high"))
        scheduler = Scheduler(owner)
        result = scheduler.sort_by_time()
        assert len(result) == 1


# ── Filtering ──────────────────────────────────────────────────────────────────

class TestFiltering:
    def test_filter_by_pet_name(self):
        owner, pet_a = make_owner_with_pet("Alpha")
        pet_b = Pet("Beta", "cat")
        owner.add_pet(pet_b)
        pet_a.add_task(Task("Walk",  "08:00", 20, "high"))
        pet_b.add_task(Task("Brush", "09:00", 10, "low"))

        scheduler = Scheduler(owner)
        alpha_tasks = scheduler.filter_tasks(pet_name="Alpha")
        assert all(p == "Alpha" for p, _ in alpha_tasks)
        assert len(alpha_tasks) == 1

    def test_filter_by_completed_false(self):
        owner, pet = make_owner_with_pet()
        t1 = Task("Walk", "08:00", 20, "high")
        t2 = Task("Feed", "12:00", 5,  "medium")
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)

        scheduler = Scheduler(owner)
        pending = scheduler.filter_tasks(completed=False)
        assert len(pending) == 1
        assert pending[0][1].description == "Feed"


# ── Recurrence ─────────────────────────────────────────────────────────────────

class TestRecurrence:
    def test_daily_task_recurs_next_day(self):
        owner, pet = make_owner_with_pet()
        today = date.today()
        task = Task("Walk", "08:00", 20, "high", frequency="daily", due_date=today)
        pet.add_task(task)

        scheduler = Scheduler(owner)
        scheduler.mark_task_complete("Rex", task)

        incomplete = [t for _, t in scheduler.filter_tasks(completed=False)]
        assert len(incomplete) == 1
        assert incomplete[0].due_date == today + timedelta(days=1)

    def test_weekly_task_recurs_next_week(self):
        owner, pet = make_owner_with_pet()
        today = date.today()
        task = Task("Grooming", "10:00", 30, "medium", frequency="weekly", due_date=today)
        pet.add_task(task)

        scheduler = Scheduler(owner)
        scheduler.mark_task_complete("Rex", task)

        incomplete = [t for _, t in scheduler.filter_tasks(completed=False)]
        assert incomplete[0].due_date == today + timedelta(weeks=1)

    def test_once_task_does_not_recur(self):
        owner, pet = make_owner_with_pet()
        task = Task("Vet visit", "10:00", 60, "high", frequency="once")
        pet.add_task(task)

        scheduler = Scheduler(owner)
        scheduler.mark_task_complete("Rex", task)

        incomplete = scheduler.filter_tasks(completed=False)
        assert len(incomplete) == 0


# ── Conflict detection ─────────────────────────────────────────────────────────

class TestConflictDetection:
    def test_detects_same_time_across_pets(self):
        owner, pet_a = make_owner_with_pet("Alpha")
        pet_b = Pet("Beta", "cat")
        owner.add_pet(pet_b)
        pet_a.add_task(Task("Walk",     "08:00", 20, "high"))
        pet_b.add_task(Task("Medicine", "08:00",  5, "high"))

        scheduler = Scheduler(owner)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 1
        assert "08:00" in conflicts[0]

    def test_no_conflicts_different_times(self):
        owner, pet = make_owner_with_pet()
        pet.add_task(Task("Walk",    "08:00", 20, "high"))
        pet.add_task(Task("Feeding", "12:00",  5, "medium"))

        scheduler = Scheduler(owner)
        assert scheduler.detect_conflicts() == []

    def test_multiple_conflicts_detected(self):
        owner, pet_a = make_owner_with_pet("Alpha")
        pet_b = Pet("Beta", "cat")
        owner.add_pet(pet_b)
        # Two pairs of conflicts
        pet_a.add_task(Task("Walk A",  "08:00", 20, "high"))
        pet_b.add_task(Task("Walk B",  "08:00", 20, "high"))
        pet_a.add_task(Task("Feed A",  "12:00",  5, "medium"))
        pet_b.add_task(Task("Feed B",  "12:00",  5, "medium"))

        scheduler = Scheduler(owner)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 2


# ── Edge cases ─────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_owner_with_no_pets(self):
        owner = Owner("Empty")
        scheduler = Scheduler(owner)
        assert scheduler.get_todays_schedule() == []
        assert scheduler.detect_conflicts() == []

    def test_pet_with_no_tasks(self):
        owner, _ = make_owner_with_pet()
        scheduler = Scheduler(owner)
        assert scheduler.get_todays_schedule() == []

    def test_generate_plan_text_no_tasks(self):
        owner = Owner("Jordan")
        scheduler = Scheduler(owner)
        text = scheduler.generate_plan_text()
        assert "No pending tasks" in text
