"""
Tests for PawPal+ core logic.
Run: python -m pytest
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, ScheduledItem


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


# ── Task: basic status ────────────────────────────────────────────────────────

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


# ── Task: recurrence ──────────────────────────────────────────────────────────

def test_daily_task_next_occurrence_is_tomorrow():
    """A daily task's next occurrence should be due exactly one day later."""
    today = date.today()
    task  = Task("Feeding", 10, "high", "daily", due_date=today)
    nxt   = task.next_occurrence()
    assert nxt is not None
    assert nxt.due_date == today + timedelta(days=1)

def test_weekly_task_next_occurrence_is_seven_days():
    """A weekly task's next occurrence should be due exactly seven days later."""
    today = date.today()
    task  = Task("Grooming", 20, "medium", "weekly", due_date=today)
    nxt   = task.next_occurrence()
    assert nxt is not None
    assert nxt.due_date == today + timedelta(weeks=1)

def test_as_needed_task_has_no_next_occurrence():
    """An as-needed task should return None from next_occurrence()."""
    task = Task("Vet visit", 60, "high", "as-needed")
    assert task.next_occurrence() is None

def test_next_occurrence_is_not_completed():
    """A next occurrence should always start as incomplete."""
    task = Task("Walk", 30, "high", "daily", due_date=date.today())
    task.complete()
    nxt = task.next_occurrence()
    assert nxt.completed is False

def test_next_occurrence_inherits_attributes():
    """next_occurrence() should carry over title, duration, and priority."""
    task = Task("Evening walk", 30, "high", "daily", due_date=date.today())
    nxt  = task.next_occurrence()
    assert nxt.title            == task.title
    assert nxt.duration_minutes == task.duration_minutes
    assert nxt.priority         == task.priority

def test_mark_complete_creates_recurrence(owner_with_pets):
    """Marking a daily task complete should append its next occurrence to the pet."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    dog = owner_with_pets.get_pet("Mochi")
    before = len(dog.tasks)
    sched.mark_complete("Morning walk")
    # one new task appended for the next occurrence
    assert len(dog.tasks) == before + 1

def test_mark_complete_next_occurrence_due_tomorrow(owner_with_pets):
    """The new occurrence created by mark_complete() should be due tomorrow."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    dog = owner_with_pets.get_pet("Mochi")
    # Set due_date on the task so next_occurrence() has a base
    for item in sched.schedule:
        if item.task.title == "Morning walk":
            item.task.due_date = date.today()
    sched.mark_complete("Morning walk")
    new_tasks = [t for t in dog.tasks if t.title == "Morning walk" and not t.completed]
    assert len(new_tasks) == 1
    assert new_tasks[0].due_date == date.today() + timedelta(days=1)


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

def test_pet_with_no_tasks_has_empty_pending(sample_pet):
    """Edge case: a pet with no tasks should return an empty pending list."""
    assert sample_pet.get_pending_tasks() == []

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
    assert len(sample_pet.tasks) == 1


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

def test_owner_with_no_pets_has_empty_task_list():
    """Edge case: an owner with no pets should return an empty task list."""
    owner = Owner("Alex")
    assert owner.get_all_tasks() == []
    assert owner.get_all_pending_tasks() == []

def test_owner_set_availability():
    """set_availability() should update the time window."""
    owner = Owner("Jordan")
    owner.set_availability("09:00", "18:00")
    assert owner.available_start == "09:00"
    assert owner.available_end   == "18:00"


# ── Scheduler: core ───────────────────────────────────────────────────────────

def test_scheduler_build_schedule(owner_with_pets):
    """build_schedule() should return a non-empty schedule."""
    scheduler = Scheduler(owner_with_pets)
    schedule  = scheduler.build_schedule()
    assert len(schedule) > 0

def test_scheduler_empty_owner_produces_empty_schedule():
    """Edge case: an owner with no pets should produce an empty schedule."""
    owner = Owner("Alex")
    sched = Scheduler(owner)
    assert sched.build_schedule() == []

def test_scheduler_mark_complete(owner_with_pets):
    """mark_complete() should flip the task's completed flag to True."""
    scheduler = Scheduler(owner_with_pets)
    scheduler.build_schedule()
    first_title = scheduler.schedule[0].task.title
    result = scheduler.mark_complete(first_title)
    assert result is True
    assert scheduler.schedule[0].task.completed is True

def test_scheduler_mark_complete_unknown_title(owner_with_pets):
    """mark_complete() should return False for a title not in the schedule."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    assert sched.mark_complete("Nonexistent task") is False

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


# ── Scheduler: sorting ────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() must return items in ascending start_time order."""
    owner = Owner("Jordan", "08:00", "20:00")
    pet   = Pet("Rex", "dog")
    # Add tasks in reverse chronological order of expected schedule slots
    pet.add_task(Task("Low task",    10, "low"))     # will be scheduled last
    pet.add_task(Task("High task A", 10, "high"))    # will be scheduled first
    pet.add_task(Task("High task B", 10, "high"))    # scheduled second
    owner.add_pet(pet)
    sched = Scheduler(owner)
    sched.build_schedule()
    sorted_items = sched.sort_by_time()
    times = [item.start_time for item in sorted_items]
    assert times == sorted(times), f"Expected sorted times, got {times}"

def test_sort_by_time_single_item():
    """Edge case: sort_by_time() on a one-item schedule should return that item."""
    owner = Owner("Sam", "09:00", "12:00")
    pet   = Pet("Rex", "dog")
    pet.add_task(Task("Walk", 30, "high"))
    owner.add_pet(pet)
    sched = Scheduler(owner)
    sched.build_schedule()
    assert len(sched.sort_by_time()) == 1

def test_sort_by_time_empty_schedule():
    """Edge case: sort_by_time() on an empty schedule should return []."""
    owner = Owner("Sam")
    sched = Scheduler(owner)
    assert sched.sort_by_time() == []


# ── Scheduler: filtering ──────────────────────────────────────────────────────

def test_filter_by_pet_name(owner_with_pets):
    """filter_tasks(pet_name) should return only items for that pet."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    mochi_items = sched.filter_tasks(pet_name="Mochi")
    assert all(item.pet.name == "Mochi" for item in mochi_items)
    assert len(mochi_items) > 0

def test_filter_by_pet_name_case_insensitive(owner_with_pets):
    """filter_tasks() should match pet names case-insensitively."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    assert sched.filter_tasks(pet_name="mochi") == sched.filter_tasks(pet_name="Mochi")

def test_filter_completed_true(owner_with_pets):
    """filter_tasks(completed=True) should only return completed items."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    sched.mark_complete(sched.schedule[0].task.title)
    done = sched.filter_tasks(completed=True)
    assert all(item.task.completed for item in done)
    assert len(done) == 1

def test_filter_completed_false(owner_with_pets):
    """filter_tasks(completed=False) should only return pending items."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    sched.mark_complete(sched.schedule[0].task.title)
    pending = sched.filter_tasks(completed=False)
    assert all(not item.task.completed for item in pending)

def test_filter_no_match_returns_empty(owner_with_pets):
    """filter_tasks() with a name that doesn't exist should return []."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    assert sched.filter_tasks(pet_name="Ghost") == []


# ── Scheduler: conflict detection ────────────────────────────────────────────

def test_no_conflicts_in_sequential_schedule(owner_with_pets):
    """A normally-built sequential schedule should have zero conflicts."""
    sched = Scheduler(owner_with_pets)
    sched.build_schedule()
    assert sched.detect_conflicts() == []

def test_conflict_detected_for_overlapping_slots():
    """Two items with overlapping time windows must produce a warning."""
    owner = Owner("Sam", "09:00", "12:00")
    pet   = Pet("Rex", "dog")
    owner.add_pet(pet)
    sched = Scheduler(owner)
    # Inject two overlapping items manually
    sched.schedule = [
        ScheduledItem(pet, Task("Walk A", 60, "high"), "09:00", "10:00"),
        ScheduledItem(pet, Task("Walk B", 60, "high"), "09:30", "10:30"),
    ]
    warnings = sched.detect_conflicts()
    assert len(warnings) == 1
    assert "CONFLICT" in warnings[0]

def test_conflict_adjacent_slots_are_not_flagged():
    """Tasks that end exactly when the next one starts are NOT a conflict."""
    owner = Owner("Sam", "09:00", "12:00")
    pet   = Pet("Rex", "dog")
    owner.add_pet(pet)
    sched = Scheduler(owner)
    sched.schedule = [
        ScheduledItem(pet, Task("Walk A", 60, "high"), "09:00", "10:00"),
        ScheduledItem(pet, Task("Walk B", 60, "high"), "10:00", "11:00"),
    ]
    assert sched.detect_conflicts() == []

def test_conflict_detected_across_different_pets():
    """Overlapping slots for different pets should also be flagged."""
    owner = Owner("Sam", "09:00", "12:00")
    dog   = Pet("Rex",  "dog")
    cat   = Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    sched = Scheduler(owner)
    sched.schedule = [
        ScheduledItem(dog, Task("Walk",   30, "high"), "09:00", "09:30"),
        ScheduledItem(cat, Task("Feeding",30, "high"), "09:15", "09:45"),
    ]
    warnings = sched.detect_conflicts()
    assert len(warnings) == 1

def test_no_conflict_with_single_item():
    """Edge case: a one-item schedule can never conflict with itself."""
    owner = Owner("Sam", "09:00", "12:00")
    pet   = Pet("Rex", "dog")
    owner.add_pet(pet)
    sched = Scheduler(owner)
    sched.schedule = [
        ScheduledItem(pet, Task("Walk", 30, "high"), "09:00", "09:30"),
    ]
    assert sched.detect_conflicts() == []
