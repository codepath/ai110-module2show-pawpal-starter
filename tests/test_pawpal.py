"""Automated tests for the PawPal+ logic layer.

Run from the project root with:  python -m pytest
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def build_owner() -> Owner:
    """Helper: one owner, two pets, tasks added out of order across both pets."""
    owner = Owner("Jordan")
    dog = Pet("Biscuit", "dog")
    cat = Pet("Mochi", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Evening walk", "18:00", "daily"))
    cat.add_task(Task("Night meds", "21:00", "daily"))
    dog.add_task(Task("Breakfast", "08:00", "daily"))
    cat.add_task(Task("Feed cat", "08:00", "daily"))  # shares 08:00 with Breakfast
    return owner


# --- Core behavior ---------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from incomplete to complete."""
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_count():
    """Adding a task to a pet increases that pet's task count."""
    pet = Pet("Biscuit", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "08:00"))
    pet.add_task(Task("Feed", "09:00"))
    assert pet.task_count() == 2


# --- Algorithmic behavior --------------------------------------------------

def test_sort_by_time_is_chronological_across_pets():
    """Scheduler returns tasks from ALL pets in chronological order."""
    scheduler = Scheduler(build_owner())
    times = [task.time for task in scheduler.sort_by_time()]
    assert times == ["08:00", "08:00", "18:00", "21:00"]


def test_filter_tasks_by_pet_and_status():
    """filter_tasks narrows by pet name and by completion status."""
    owner = build_owner()
    scheduler = Scheduler(owner)
    assert len(scheduler.filter_tasks(pet_name="Mochi")) == 2

    owner.pets[0].tasks[0].mark_complete()  # complete one dog task
    incomplete = scheduler.filter_tasks(completed=False)
    assert len(incomplete) == 3
    assert all(not t.completed for t in incomplete)


def test_detect_conflicts_flags_same_time_across_pets():
    """Two tasks at the same time (even on different pets) produce one warning."""
    scheduler = Scheduler(build_owner())
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "Biscuit" in conflicts[0] and "Mochi" in conflicts[0]


def test_no_conflict_when_times_are_unique():
    """A schedule with distinct times produces no warnings (edge case)."""
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", "08:00"))
    pet.add_task(Task("Feed", "09:00"))
    assert Scheduler(owner).detect_conflicts() == []


def test_completing_daily_task_creates_next_days_occurrence():
    """Marking a daily task complete auto-creates a fresh task for the next day."""
    owner = Owner("Jordan")
    dog = Pet("Biscuit", "dog")
    owner.add_pet(dog)
    today = date.today().isoformat()
    dog.add_task(Task("Morning walk", "08:00", "daily", due_date=today))
    scheduler = Scheduler(owner)

    follow_up = scheduler.complete_task(dog.tasks[0])

    assert dog.tasks[0].completed is True
    assert dog.task_count() == 2  # original + next occurrence
    assert follow_up is not None
    assert follow_up.completed is False
    expected = (date.today() + timedelta(days=1)).isoformat()
    assert follow_up.due_date == expected


def test_one_off_task_does_not_recur():
    """A 'once' task has no next occurrence (edge case)."""
    task = Task("Vet visit", "14:00", "once")
    assert task.next_occurrence() is None


def test_pet_with_no_tasks_produces_empty_schedule_data():
    """A pet with no tasks contributes nothing and causes no errors (edge case)."""
    owner = Owner("Sam")
    owner.add_pet(Pet("Rex", "dog"))
    scheduler = Scheduler(owner)
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []
