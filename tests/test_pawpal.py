"""
Tests for PawPal+ core logic.
Run: python -m pytest
"""

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_task():
    return Task(title="Morning walk", duration_minutes=30, priority="high", frequency="daily")

@pytest.fixture
def sample_pet():
    return Pet(name="Mochi", species="dog", age=3)

@pytest.fixture
def owner_with_pets():
    owner = Owner(name="Jordan", available_start="08:00", available_end="20:00")
    dog = Pet(name="Mochi", species="dog", age=3)
    cat = Pet(name="Luna", species="cat", age=5)
    dog.add_task(Task("Morning walk",    30, "high",   "daily"))
    dog.add_task(Task("Feeding",         10, "high",   "daily"))
    cat.add_task(Task("Feeding",         10, "high",   "daily"))
    cat.add_task(Task("Litter box clean",10, "high",   "daily"))
    cat.add_task(Task("Playtime",        15, "low",    "daily"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


# ── Task tests ────────────────────────────────────────────────────────────────

def test_task_starts_incomplete(sample_task):
    """A new Task should not be completed by default."""
    assert sample_task.completed is False

def test_task_complete_sets_flag(sample_task):
    """Calling complete() should mark the task as completed."""
    sample_task.complete()
    assert sample_task.completed is True

def test_task_reset_clears_flag(sample_task):
    """Calling reset() after complete() should restore completed to False."""
    sample_task.complete()
    sample_task.reset()
    assert sample_task.completed is False

def test_task_is_high_priority():
    """is_high_priority() should return True only for high-priority tasks."""
    assert Task("Walk", 20, "high").is_high_priority() is True
    assert Task("Walk", 20, "medium").is_high_priority() is False
    assert Task("Walk", 20, "low").is_high_priority() is False

def test_task_priority_value_ordering():
    """High priority should sort before medium, medium before low."""
    high   = Task("A", 10, "high").priority_value()
    medium = Task("B", 10, "medium").priority_value()
    low    = Task("C", 10, "low").priority_value()
    assert high < medium < low


# ── Pet tests ─────────────────────────────────────────────────────────────────

def test_add_task_increases_count(sample_pet):
    """Adding a task to a Pet should increase its task count by 1."""
    before = len(sample_pet.tasks)
    sample_pet.add_task(Task("Feeding", 10, "high"))
    assert len(sample_pet.tasks) == before + 1

def test_add_multiple_tasks(sample_pet):
    """Adding three tasks should result in exactly three tasks on the pet."""
    for title in ["Feeding", "Walk", "Grooming"]:
        sample_pet.add_task(Task(title, 10, "medium"))
    assert len(sample_pet.tasks) == 3

def test_remove_task(sample_pet):
    """remove_task() should delete the task and return True."""
    sample_pet.add_task(Task("Grooming", 20, "medium"))
    result = sample_pet.remove_task("Grooming")
    assert result is True
    assert all(t.title != "Grooming" for t in sample_pet.tasks)

def test_remove_nonexistent_task(sample_pet):
    """remove_task() should return False when the title doesn't exist."""
    assert sample_pet.remove_task("Nonexistent") is False

def test_get_pending_tasks(sample_pet):
    """get_pending_tasks() should exclude completed tasks."""
    t1 = Task("Walk",    30, "high")
    t2 = Task("Feeding", 10, "high")
    sample_pet.add_task(t1)
    sample_pet.add_task(t2)
    t1.complete()
    pending = sample_pet.get_pending_tasks()
    assert t1 not in pending
    assert t2 in pending

def test_load_default_tasks_dog(sample_pet):
    """load_default_tasks() should populate dog-appropriate Task objects."""
    sample_pet.load_default_tasks()
    titles = [t.title for t in sample_pet.tasks]
    assert "Morning walk" in titles
    assert "Feeding" in titles

def test_load_default_tasks_does_not_overwrite(sample_pet):
    """load_default_tasks() should not overwrite existing tasks."""
    sample_pet.add_task(Task("Custom task", 5, "low"))
    sample_pet.load_default_tasks()
    assert len(sample_pet.tasks) == 1  # still just the one custom task


# ── Owner tests ───────────────────────────────────────────────────────────────

def test_owner_add_pet():
    """Adding a pet to an owner should appear in owner.pets."""
    owner = Owner("Jordan")
    pet   = Pet("Mochi", "dog")
    owner.add_pet(pet)
    assert pet in owner.pets

def test_owner_get_all_tasks(owner_with_pets):
    """get_all_tasks() should return (pet, task) pairs for every task."""
    pairs = owner_with_pets.get_all_tasks()
    assert len(pairs) == 5   # 2 dog + 3 cat tasks

def test_owner_get_all_pending_excludes_done(owner_with_pets):
    """get_all_pending_tasks() should not include completed tasks."""
    first_pet, first_task = owner_with_pets.get_all_tasks()[0]
    first_task.complete()
    pending = owner_with_pets.get_all_pending_tasks()
    assert (first_pet, first_task) not in pending

def test_owner_set_availability():
    """set_availability() should update the time window."""
    owner = Owner("Jordan")
    owner.set_availability("09:00", "18:00")
    assert owner.available_start == "09:00"
    assert owner.available_end   == "18:00"


# ── Scheduler tests ───────────────────────────────────────────────────────────

def test_scheduler_build_schedule(owner_with_pets):
    """build_schedule() should return a non-empty schedule."""
    scheduler = Scheduler(owner_with_pets)
    schedule  = scheduler.build_schedule()
    assert len(schedule) > 0

def test_scheduler_mark_complete(owner_with_pets):
    """mark_complete() should flip the task's completed flag to True."""
    scheduler = Scheduler(owner_with_pets)
    scheduler.build_schedule()
    first_title = scheduler.schedule[0].task.title
    result = scheduler.mark_complete(first_title)
    assert result is True
    assert scheduler.schedule[0].task.completed is True

def test_scheduler_high_priority_comes_first(owner_with_pets):
    """The first scheduled item should be a high-priority task."""
    scheduler = Scheduler(owner_with_pets)
    scheduler.build_schedule()
    assert scheduler.schedule[0].task.priority == "high"

def test_scheduler_skipped_when_window_too_short():
    """Tasks that don't fit in the window should appear in scheduler.skipped."""
    owner = Owner("Sam", available_start="08:00", available_end="08:05")
    pet   = Pet("Rex", "dog")
    pet.add_task(Task("Long walk", 120, "high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    assert len(scheduler.skipped) == 1

def test_scheduler_get_todays_tasks(owner_with_pets):
    """get_todays_tasks() should only return items not yet completed."""
    scheduler = Scheduler(owner_with_pets)
    scheduler.build_schedule()
    scheduler.mark_complete(scheduler.schedule[0].task.title)
    pending = scheduler.get_todays_tasks()
    assert len(pending) == len(scheduler.schedule) - 1
