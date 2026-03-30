from datetime import date, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_task(name, duration, priority, start_time=None, pet_name=None, recurring=False, interval=None):
    """Create a Task with optional start_time and pet_name pre-set."""
    t = Task(name, duration=duration, priority=priority,
             due_time=date.today(), recurring=recurring,
             recurrence_interval=interval, pet_name=pet_name)
    t.start_time = start_time
    return t


# ── Original tests (kept) ─────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task("Feed dog", duration=10, priority=2)
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", duration=30, priority=3))
    assert len(pet.get_tasks()) == 1


# ── detect_conflicts ──────────────────────────────────────────────────────────

def test_no_conflicts_when_tasks_do_not_overlap():
    scheduler = Scheduler([8 * 60, 20 * 60])
    tasks = [
        make_task("Feed Buddy", 10, 2, start_time=8 * 60,       pet_name="Buddy"),
        make_task("Morning walk", 30, 3, start_time=8 * 60 + 20, pet_name="Buddy"),
    ]
    assert scheduler.detect_conflicts(tasks) == []


def test_same_pet_overlap_produces_warning():
    scheduler = Scheduler([8 * 60, 20 * 60])
    tasks = [
        make_task("Feed Buddy",   10, 2, start_time=8 * 60,     pet_name="Buddy"),
        make_task("Morning walk", 30, 3, start_time=8 * 60 + 5, pet_name="Buddy"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "WARNING" in warnings[0]
    assert "Feed Buddy" in warnings[0]
    assert "Morning walk" in warnings[0]


def test_cross_pet_overlap_produces_warning():
    scheduler = Scheduler([8 * 60, 20 * 60])
    tasks = [
        make_task("Feed Buddy", 10, 2, start_time=8 * 60, pet_name="Buddy"),
        make_task("Feed Luna",  10, 1, start_time=8 * 60, pet_name="Luna"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "Buddy" in warnings[0]
    assert "Luna" in warnings[0]


def test_three_overlapping_tasks_produce_three_warnings():
    scheduler = Scheduler([8 * 60, 20 * 60])
    tasks = [
        make_task("Feed Buddy",   10, 2, start_time=8 * 60,     pet_name="Buddy"),
        make_task("Feed Luna",    10, 1, start_time=8 * 60,     pet_name="Luna"),
        make_task("Morning walk", 30, 3, start_time=8 * 60 + 5, pet_name="Buddy"),
    ]
    assert len(scheduler.detect_conflicts(tasks)) == 3


def test_tasks_without_start_time_are_skipped():
    scheduler = Scheduler([8 * 60, 20 * 60])
    tasks = [
        make_task("Feed Buddy", 10, 2, start_time=None, pet_name="Buddy"),
        make_task("Feed Luna",  10, 1, start_time=None, pet_name="Luna"),
    ]
    assert scheduler.detect_conflicts(tasks) == []


def test_warnings_are_strings_not_tuples():
    scheduler = Scheduler([8 * 60, 20 * 60])
    tasks = [
        make_task("Task A", 30, 1, start_time=8 * 60),
        make_task("Task B", 30, 1, start_time=8 * 60),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert all(isinstance(w, str) for w in warnings)


# ── generate_schedule ─────────────────────────────────────────────────────────

def test_high_priority_task_scheduled_first():
    scheduler = Scheduler([8 * 60, 20 * 60], buffer_minutes=0)
    tasks = [
        Task("Low priority",  duration=10, priority=1, due_time=date.today()),
        Task("High priority", duration=10, priority=3, due_time=date.today()),
    ]
    result = scheduler.generate_schedule(tasks)
    assert result["scheduled"][0]["name"] == "High priority"


def test_tasks_too_long_are_dropped():
    scheduler = Scheduler([8 * 60, 8 * 60 + 15])  # only 15-min window
    tasks = [
        Task("Short task", duration=10, priority=1, due_time=date.today()),
        Task("Long task",  duration=30, priority=2, due_time=date.today()),
    ]
    result = scheduler.generate_schedule(tasks)
    scheduled_names = [t["name"] for t in result["scheduled"]]
    dropped_names   = [t["name"] for t in result["dropped"]]
    assert "Long task" in dropped_names
    assert "Short task" in scheduled_names


def test_buffer_is_applied_between_tasks():
    scheduler = Scheduler([8 * 60, 20 * 60], buffer_minutes=10)
    tasks = [
        Task("Task A", duration=20, priority=2, due_time=date.today()),
        Task("Task B", duration=20, priority=1, due_time=date.today()),
    ]
    result = scheduler.generate_schedule(tasks)
    a = result["scheduled"][0]
    b = result["scheduled"][1]
    # Task B should start 10 min after Task A ends (20 + 10 buffer)
    assert b["start_time"] == a["start_time"] + a["duration"] + 10


def test_empty_task_list_returns_empty_schedule():
    scheduler = Scheduler([8 * 60, 20 * 60])
    result = scheduler.generate_schedule([])
    assert result["scheduled"] == []
    assert result["dropped"] == []


# ── _recurrence_days ──────────────────────────────────────────────────────────

def test_recurrence_days_daily():
    task = Task("Feed", duration=10, priority=1, recurring=True, recurrence_interval="daily")
    assert task._recurrence_days() == 1


def test_recurrence_days_weekly():
    task = Task("Walk", duration=30, priority=2, recurring=True, recurrence_interval="weekly")
    assert task._recurrence_days() == 7


# ── mark_complete with recurrence ─────────────────────────────────────────────

def test_mark_complete_recurring_returns_next_task():
    task = Task("Feed", duration=10, priority=1,
                due_time=date.today(), recurring=True, recurrence_interval="daily")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_time == date.today() + timedelta(days=1)
    assert next_task.completed == False


def test_mark_complete_non_recurring_returns_none():
    task = Task("One-off task", duration=10, priority=1)
    assert task.mark_complete() is None


# ── advance_recurrence ────────────────────────────────────────────────────────

def test_advance_recurrence_moves_due_date_forward():
    today = date.today()
    task = Task("Walk", duration=30, priority=2,
                due_time=today, recurring=True, recurrence_interval="weekly")
    task.advance_recurrence()
    assert task.due_time == today + timedelta(days=7)
    assert task.completed == False
    assert task.start_time is None


# ── Pet.remove_task / update_task ─────────────────────────────────────────────

def test_remove_task_decreases_count():
    pet = Pet("Buddy", "dog")
    pet.add_task(Task("Walk", duration=30, priority=3))
    pet.remove_task("Walk")
    assert len(pet.get_tasks()) == 0


def test_remove_nonexistent_task_raises():
    pet = Pet("Buddy", "dog")
    with pytest.raises(ValueError):
        pet.remove_task("Nonexistent")


def test_update_task_replaces_task():
    pet = Pet("Buddy", "dog")
    pet.add_task(Task("Walk", duration=30, priority=1))
    updated = Task("Walk", duration=45, priority=2)
    pet.update_task("Walk", updated)
    assert pet.get_tasks()[0].duration == 45
    assert pet.get_tasks()[0].priority == 2


def test_update_nonexistent_task_raises():
    pet = Pet("Buddy", "dog")
    with pytest.raises(ValueError):
        pet.update_task("Ghost task", Task("Ghost task", duration=10, priority=1))


# ── Owner helpers ─────────────────────────────────────────────────────────────

def test_get_all_tasks_collects_across_pets():
    owner = Owner("Alex")
    dog = Pet("Buddy", "dog")
    cat = Pet("Luna", "cat")
    dog.add_task(Task("Walk",  duration=30, priority=3))
    cat.add_task(Task("Feed",  duration=10, priority=2))
    cat.add_task(Task("Brush", duration=15, priority=1))
    owner.add_pet(dog)
    owner.add_pet(cat)
    assert len(owner.get_all_tasks()) == 3


def test_get_today_tasks_excludes_future_tasks():
    owner = Owner("Alex")
    dog = Pet("Buddy", "dog")
    dog.add_task(Task("Today task",  duration=10, priority=1, due_time=date.today()))
    dog.add_task(Task("Future task", duration=10, priority=1,
                      due_time=date.today() + timedelta(days=1)))
    owner.add_pet(dog)
    today = owner.get_today_tasks()
    assert len(today) == 1
    assert today[0].name == "Today task"
