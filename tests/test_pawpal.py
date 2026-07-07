"""
Automated test suite for PawPal+ (pawpal_system.py).

Run with:  python -m pytest tests/test_pawpal.py -v
"""
from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Task, Scheduler


# ── Helpers ───────────────────────────────────────────────────────────────────

TODAY = date(2026, 7, 7)


def make_task(name="Walk", time="08:00", priority="medium",
              frequency="daily", pet_name="Mochi",
              completed=False, due_date=None) -> Task:
    t = Task(
        name=name, time=time, priority=priority,
        frequency=frequency, pet_name=pet_name,
        due_date=due_date or TODAY,
    )
    t.completed = completed
    return t


def make_pet(name="Mochi", tasks=None) -> Pet:
    p = Pet(name=name, species="Dog")
    for t in (tasks or []):
        p.add_task(t)
    return p


def make_owner(*pets) -> Owner:
    o = Owner(name="Jordan")
    for p in pets:
        o.add_pet(p)
    return o


# ── Task tests ────────────────────────────────────────────────────────────────

class TestTask:
    def test_mark_complete_changes_status(self):
        """Calling mark_complete() must flip completed from False to True."""
        task = make_task(completed=False)
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_mark_complete_is_idempotent(self):
        """Calling mark_complete() twice should not raise or undo completion."""
        task = make_task()
        task.mark_complete()
        task.mark_complete()
        assert task.completed is True

    def test_next_occurrence_daily_adds_one_day(self):
        """A daily task's next occurrence should be scheduled for the following day."""
        task = make_task(frequency="daily", due_date=TODAY)
        nxt = task.next_occurrence()
        assert nxt is not None
        assert nxt.due_date == TODAY + timedelta(days=1)

    def test_next_occurrence_weekly_adds_seven_days(self):
        """A weekly task's next occurrence should be seven days later."""
        task = make_task(frequency="weekly", due_date=TODAY)
        nxt = task.next_occurrence()
        assert nxt is not None
        assert nxt.due_date == TODAY + timedelta(weeks=1)

    def test_next_occurrence_once_returns_none(self):
        """A one-time task should not generate a next occurrence."""
        task = make_task(frequency="once")
        assert task.next_occurrence() is None

    def test_next_occurrence_inherits_all_fields(self):
        """The recurrence task should copy name, time, priority, and frequency."""
        task = make_task(name="Evening meds", time="20:00",
                         priority="critical", frequency="daily")
        nxt = task.next_occurrence()
        assert nxt.name == task.name
        assert nxt.time == task.time
        assert nxt.priority == task.priority
        assert nxt.frequency == task.frequency

    def test_new_occurrence_starts_incomplete(self):
        """The next occurrence created after completion should itself be incomplete."""
        task = make_task(frequency="daily")
        task.mark_complete()
        nxt = task.next_occurrence()
        assert nxt.completed is False


# ── Pet tests ─────────────────────────────────────────────────────────────────

class TestPet:
    def test_add_task_increases_task_count(self):
        """Adding a task to a Pet must increase len(pet.tasks) by 1."""
        pet   = make_pet()
        before = len(pet.tasks)
        pet.add_task(make_task())
        assert len(pet.tasks) == before + 1

    def test_get_tasks_returns_all_tasks(self):
        """get_tasks() should return every task, including completed ones."""
        task1 = make_task(name="Walk",           completed=False)
        task2 = make_task(name="Grooming",       completed=True)
        pet   = make_pet(tasks=[task1, task2])
        assert len(pet.get_tasks()) == 2

    def test_pending_tasks_excludes_completed(self):
        """pending_tasks() should omit tasks where completed=True."""
        task1 = make_task(name="Walk",     completed=False)
        task2 = make_task(name="Grooming", completed=True)
        pet   = make_pet(tasks=[task1, task2])
        pending = pet.pending_tasks()
        assert len(pending) == 1
        assert pending[0].name == "Walk"


# ── Owner tests ───────────────────────────────────────────────────────────────

class TestOwner:
    def test_add_pet_increases_pet_count(self):
        """add_pet() must increase len(owner.pets) by 1."""
        owner = Owner(name="Jordan")
        before = len(owner.pets)
        owner.add_pet(make_pet())
        assert len(owner.pets) == before + 1

    def test_get_all_tasks_aggregates_across_pets(self):
        """get_all_tasks() should return tasks from every pet combined."""
        pet1  = make_pet(name="Mochi",    tasks=[make_task(pet_name="Mochi")])
        pet2  = make_pet(name="Whiskers", tasks=[make_task(pet_name="Whiskers"),
                                                  make_task(pet_name="Whiskers")])
        owner = make_owner(pet1, pet2)
        assert len(owner.get_all_tasks()) == 3

    def test_get_pet_by_name(self):
        """get_pet() should return the correct Pet by name (case-insensitive)."""
        pet   = make_pet(name="Mochi")
        owner = make_owner(pet)
        assert owner.get_pet("mochi") is pet
        assert owner.get_pet("MOCHI") is pet

    def test_get_pet_returns_none_for_unknown(self):
        owner = make_owner(make_pet(name="Mochi"))
        assert owner.get_pet("Buddy") is None


# ── Scheduler tests ───────────────────────────────────────────────────────────

class TestScheduler:
    def test_sort_by_time_returns_chronological_order(self):
        """sort_by_time() must return tasks in ascending HH:MM order."""
        tasks = [
            make_task(name="C", time="18:00"),
            make_task(name="A", time="07:30"),
            make_task(name="B", time="13:00"),
        ]
        pet   = make_pet(tasks=tasks)
        owner = make_owner(pet)
        sched = Scheduler(owner)
        result = sched.sort_by_time()
        times  = [t.time for t in result]
        assert times == sorted(times)

    def test_sort_by_time_accepts_explicit_list(self):
        """sort_by_time() should also sort an explicitly passed list."""
        tasks = [make_task(name="Late", time="21:00"),
                 make_task(name="Early", time="06:00")]
        sched = Scheduler(make_owner())
        result = sched.sort_by_time(tasks)
        assert result[0].name == "Early"
        assert result[1].name == "Late"

    def test_filter_by_status_completed(self):
        """filter_by_status(completed=True) should only return done tasks."""
        done    = make_task(name="Done task", completed=True)
        pending = make_task(name="Pending",   completed=False)
        pet     = make_pet(tasks=[done, pending])
        sched   = Scheduler(make_owner(pet))
        result  = sched.filter_by_status(completed=True)
        assert all(t.completed for t in result)
        assert len(result) == 1

    def test_filter_by_status_pending(self):
        """filter_by_status(completed=False) should only return incomplete tasks."""
        done    = make_task(name="Done",    completed=True)
        pending = make_task(name="Pending", completed=False)
        pet     = make_pet(tasks=[done, pending])
        sched   = Scheduler(make_owner(pet))
        result  = sched.filter_by_status(completed=False)
        assert not any(t.completed for t in result)

    def test_filter_by_pet_returns_correct_tasks(self):
        """filter_by_pet() should only return tasks whose pet_name matches."""
        mochi_task    = make_task(name="Walk",      pet_name="Mochi")
        whiskers_task = make_task(name="Grooming",  pet_name="Whiskers")
        pet1 = make_pet(name="Mochi",    tasks=[mochi_task])
        pet2 = make_pet(name="Whiskers", tasks=[whiskers_task])
        sched = Scheduler(make_owner(pet1, pet2))
        result = sched.filter_by_pet("Mochi")
        assert len(result) == 1
        assert result[0].name == "Walk"

    def test_conflict_detection_flags_same_time_same_pet(self):
        """Two incomplete tasks for the same pet at the same time → conflict warning."""
        t1 = make_task(name="Meds",     time="20:00", pet_name="Mochi")
        t2 = make_task(name="Vet call", time="20:00", pet_name="Mochi")
        pet   = make_pet(name="Mochi", tasks=[t1, t2])
        sched = Scheduler(make_owner(pet))
        warnings = sched.detect_conflicts()
        assert len(warnings) == 1
        assert "20:00" in warnings[0]
        assert "Mochi" in warnings[0]

    def test_conflict_detection_ignores_different_pets(self):
        """Same time for different pets is not a conflict."""
        t1 = make_task(name="Mochi meal",    time="08:00", pet_name="Mochi")
        t2 = make_task(name="Whiskers meal", time="08:00", pet_name="Whiskers")
        pet1  = make_pet(name="Mochi",    tasks=[t1])
        pet2  = make_pet(name="Whiskers", tasks=[t2])
        sched = Scheduler(make_owner(pet1, pet2))
        assert sched.detect_conflicts() == []

    def test_conflict_detection_ignores_completed_tasks(self):
        """A completed task should not trigger a conflict even at the same time."""
        done    = make_task(name="Done meds",  time="20:00", completed=True)
        pending = make_task(name="Vet call",   time="20:00", completed=False)
        pet   = make_pet(name="Mochi", tasks=[done, pending])
        sched = Scheduler(make_owner(pet))
        assert sched.detect_conflicts() == []

    def test_mark_task_complete_sets_completed(self):
        """mark_task_complete() must mark the task as done."""
        task  = make_task(frequency="once")
        pet   = make_pet(tasks=[task])
        sched = Scheduler(make_owner(pet))
        sched.mark_task_complete(task)
        assert task.completed is True

    def test_recurring_daily_task_creates_next_occurrence(self):
        """Marking a daily task complete must add a new task for the next day."""
        task  = make_task(name="Morning walk", frequency="daily", due_date=TODAY)
        pet   = make_pet(tasks=[task])
        owner = make_owner(pet)
        sched = Scheduler(owner)
        before_count = len(pet.tasks)
        next_task    = sched.mark_task_complete(task)
        assert next_task is not None
        assert next_task.due_date == TODAY + timedelta(days=1)
        assert len(pet.tasks) == before_count + 1

    def test_recurring_weekly_task_creates_next_occurrence(self):
        """Marking a weekly task complete must add a new task for 7 days later."""
        task  = make_task(frequency="weekly", due_date=TODAY)
        pet   = make_pet(tasks=[task])
        sched = Scheduler(make_owner(pet))
        next_task = sched.mark_task_complete(task)
        assert next_task is not None
        assert next_task.due_date == TODAY + timedelta(weeks=1)

    def test_once_task_creates_no_next_occurrence(self):
        """Marking a one-time task complete must NOT add a new task."""
        task  = make_task(frequency="once")
        pet   = make_pet(tasks=[task])
        sched = Scheduler(make_owner(pet))
        next_task = sched.mark_task_complete(task)
        assert next_task is None
        assert len(pet.tasks) == 1  # count unchanged

    def test_todays_schedule_returns_pending_tasks_for_today(self):
        """todays_schedule() should return only incomplete tasks due today."""
        today_task     = make_task(name="Today",     due_date=TODAY,                completed=False)
        tomorrow_task  = make_task(name="Tomorrow",  due_date=TODAY + timedelta(1), completed=False)
        completed_task = make_task(name="Done today", due_date=TODAY,               completed=True)
        pet   = make_pet(tasks=[today_task, tomorrow_task, completed_task])
        sched = Scheduler(make_owner(pet))
        result = sched.todays_schedule(TODAY)
        assert len(result) == 1
        assert result[0].name == "Today"

    def test_todays_schedule_is_sorted_by_time(self):
        """todays_schedule() must return tasks in HH:MM ascending order."""
        t1 = make_task(name="Late",  time="20:00", due_date=TODAY)
        t2 = make_task(name="Early", time="07:00", due_date=TODAY)
        pet   = make_pet(tasks=[t1, t2])
        sched = Scheduler(make_owner(pet))
        result = sched.todays_schedule(TODAY)
        assert result[0].name == "Early"
        assert result[1].name == "Late"

    def test_no_tasks_produces_empty_schedule(self):
        """An owner with no tasks should produce an empty schedule."""
        sched = Scheduler(make_owner(make_pet()))
        assert sched.todays_schedule(TODAY) == []
