import pytest
from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler, ScheduledTask


# --- Fixtures ---

@pytest.fixture
def owner():
    return Owner(name="Jordan", available_start=time(8, 0), available_end=time(20, 0))


@pytest.fixture
def basic_task():
    return Task(id=1, title="Morning Walk", duration_minutes=30, priority="high")


@pytest.fixture
def pet_with_tasks():
    pet = Pet(name="Luna", species="dog", age=3)
    pet.add_task(Task(id=1, title="Morning Walk", duration_minutes=30, priority="high"))
    pet.add_task(Task(id=2, title="Evening Walk", duration_minutes=30, priority="high"))
    pet.add_task(Task(id=3, title="Grooming",     duration_minutes=20, priority="low"))
    return pet


@pytest.fixture
def scheduler_with_pets(owner, pet_with_tasks):
    milo = Pet(name="Milo", species="cat", age=5)
    milo.add_task(Task(id=4, title="Feeding",         duration_minutes=10, priority="high"))
    milo.add_task(Task(id=5, title="Enrichment Play", duration_minutes=15, priority="medium"))

    scheduler = Scheduler(owner=owner)
    scheduler.add_pet(pet_with_tasks)
    scheduler.add_pet(milo)
    return scheduler


# --- Task tests ---

class TestTask:
    def test_mark_complete(self, basic_task):
        assert basic_task.is_completed is False
        basic_task.mark_complete()
        assert basic_task.is_completed is True

    def test_is_high_priority_true(self, basic_task):
        assert basic_task.is_high_priority() is True

    def test_is_high_priority_false(self):
        task = Task(id=2, title="Grooming", duration_minutes=20, priority="low")
        assert task.is_high_priority() is False

    def test_fits_in_window_true(self, basic_task):
        assert basic_task.fits_in_window(time(8, 0), time(20, 0)) is True

    def test_fits_in_window_false(self):
        task = Task(id=3, title="Long Hike", duration_minutes=120, priority="medium")
        assert task.fits_in_window(time(8, 0), time(8, 30)) is False


# --- Pet tests ---

class TestPet:
    def test_add_task_appends(self, pet_with_tasks):
        assert len(pet_with_tasks.get_tasks()) == 3

    def test_add_task_sets_pet_name(self, basic_task):
        pet = Pet(name="Luna", species="dog", age=3)
        pet.add_task(basic_task)
        assert basic_task.pet_name == "Luna"

    def test_remove_task_by_id(self, pet_with_tasks):
        pet_with_tasks.remove_task(task_id=1)
        ids = [t.id for t in pet_with_tasks.get_tasks()]
        assert 1 not in ids
        assert len(ids) == 2

    def test_remove_nonexistent_task_does_nothing(self, pet_with_tasks):
        pet_with_tasks.remove_task(task_id=999)
        assert len(pet_with_tasks.get_tasks()) == 3


# --- Owner tests ---

class TestOwner:
    def test_get_available_window(self, owner):
        assert owner.get_available_window() == (time(8, 0), time(20, 0))

    def test_get_total_available_time(self, owner):
        assert owner.get_total_available_time() == 720


# --- ScheduledTask tests ---

class TestScheduledTask:
    def test_end_time_computed_correctly(self, basic_task):
        st = ScheduledTask(task=basic_task, start_time=time(8, 0))
        assert st.end_time == time(8, 30)

    def test_get_time_range(self, basic_task):
        st = ScheduledTask(task=basic_task, start_time=time(8, 0))
        assert st.get_time_range() == (time(8, 0), time(8, 30))

    def test_to_display_string_includes_pet_name(self):
        task = Task(id=1, title="Morning Walk", duration_minutes=30, priority="high", pet_name="Luna")
        st = ScheduledTask(task=task, start_time=time(8, 0))
        assert "Luna" in st.to_display_string()
        assert "Morning Walk" in st.to_display_string()


# --- Scheduler tests ---

class TestScheduler:
    def test_add_pet(self, owner):
        scheduler = Scheduler(owner=owner)
        pet = Pet(name="Luna", species="dog", age=3)
        scheduler.add_pet(pet)
        assert len(scheduler.pets) == 1

    def test_get_all_tasks_flattens_pets(self, scheduler_with_pets):
        tasks = scheduler_with_pets.get_all_tasks()
        assert len(tasks) == 5

    def test_build_schedule_returns_scheduled_tasks(self, scheduler_with_pets):
        schedule = scheduler_with_pets.build_schedule()
        assert len(schedule) > 0
        assert all(isinstance(st, ScheduledTask) for st in schedule)

    def test_build_schedule_sorted_high_before_low(self, scheduler_with_pets):
        schedule = scheduler_with_pets.build_schedule()
        priorities = [st.task.priority for st in schedule]
        # high priority tasks should appear before low
        assert priorities.index("high") < priorities.index("low")

    def test_build_schedule_skips_tasks_that_dont_fit(self, owner):
        scheduler = Scheduler(owner=owner)
        pet = Pet(name="Luna", species="dog", age=3)
        # fill the window with one giant task, then add a second that won't fit
        pet.add_task(Task(id=1, title="Very Long Task", duration_minutes=700, priority="high"))
        pet.add_task(Task(id=2, title="Short Task",     duration_minutes=30,  priority="medium"))
        scheduler.add_pet(pet)
        schedule = scheduler.build_schedule()
        titles = [st.task.title for st in schedule]
        assert "Very Long Task" in titles
        assert "Short Task" not in titles

    def test_scheduled_tasks_stored_on_instance(self, scheduler_with_pets):
        schedule = scheduler_with_pets.build_schedule()
        assert scheduler_with_pets.scheduled_tasks is schedule


# --- Sorting correctness tests ---

class TestSortingCorrectness:
    def test_sort_by_time_chronological_order(self, owner):
        """sort_by_time() must return tasks in ascending preferred_time order.

        We create three tasks with out-of-order preferred times and confirm
        the sorted result matches the expected chronological sequence.
        """
        scheduler = Scheduler(owner=owner)
        tasks = [
            Task(id=1, title="Afternoon Walk", duration_minutes=30, priority="medium", preferred_time=time(14, 0)),
            Task(id=2, title="Morning Walk",   duration_minutes=30, priority="medium", preferred_time=time(8, 0)),
            Task(id=3, title="Evening Walk",   duration_minutes=30, priority="medium", preferred_time=time(18, 0)),
        ]
        sorted_tasks = scheduler.sort_by_time(tasks)
        times = [t.preferred_time for t in sorted_tasks]
        assert times == [time(8, 0), time(14, 0), time(18, 0)]

    def test_sort_by_time_none_preferred_time_goes_last(self, owner):
        """Tasks with no preferred_time must sort after all tasks that have one.

        None is treated as time.max so it never jumps ahead of a real time.
        """
        scheduler = Scheduler(owner=owner)
        tasks = [
            Task(id=1, title="No Time Task", duration_minutes=20, priority="high", preferred_time=None),
            Task(id=2, title="Morning Task",  duration_minutes=20, priority="high", preferred_time=time(9, 0)),
        ]
        sorted_tasks = scheduler.sort_by_time(tasks)
        assert sorted_tasks[0].title == "Morning Task"
        assert sorted_tasks[1].title == "No Time Task"

    def test_sort_by_time_same_time_tiebreak_by_priority(self, owner):
        """When two tasks share a preferred_time, higher priority must come first.

        The sort key is (preferred_time, priority_rank), so "high" (rank 0)
        beats "low" (rank 2) when times are equal.
        """
        scheduler = Scheduler(owner=owner)
        tasks = [
            Task(id=1, title="Low Task",  duration_minutes=20, priority="low",  preferred_time=time(9, 0)),
            Task(id=2, title="High Task", duration_minutes=20, priority="high", preferred_time=time(9, 0)),
        ]
        sorted_tasks = scheduler.sort_by_time(tasks)
        assert sorted_tasks[0].title == "High Task"
        assert sorted_tasks[1].title == "Low Task"


# --- Recurrence logic tests ---

class TestRecurrenceLogic:
    def test_complete_daily_task_creates_new_task(self, owner):
        """Completing a daily task must add a fresh, incomplete copy to the pet's task list.

        After complete_task() the pet should have two tasks: the original
        (completed) and the new occurrence (incomplete). This confirms the
        scheduler will include the task again on the next build cycle.
        """
        pet = Pet(name="Luna", species="dog", age=3)
        pet.add_task(Task(id=1, title="Morning Walk", duration_minutes=30,
                          priority="high", frequency="daily"))
        scheduler = Scheduler(owner=owner)
        scheduler.add_pet(pet)

        new_task = scheduler.complete_task(task_id=1)

        assert new_task is not None                  # a next occurrence was created
        assert new_task.is_completed is False        # starts fresh — not already done
        assert new_task.frequency == "daily"         # inherits the recurrence setting
        assert new_task.id != 1                      # gets a distinct ID, not a duplicate
        assert len(pet.get_tasks()) == 2             # original + new occurrence both on pet

    def test_complete_once_task_does_not_create_new_task(self, owner):
        """Completing a one-time task must NOT add a next occurrence.

        next_occurrence() returns None for frequency='once', so the pet's
        task count must stay the same after completion.
        """
        pet = Pet(name="Luna", species="dog", age=3)
        pet.add_task(Task(id=2, title="Vet Visit", duration_minutes=60,
                          priority="high", frequency="once"))
        scheduler = Scheduler(owner=owner)
        scheduler.add_pet(pet)

        new_task = scheduler.complete_task(task_id=2)

        assert new_task is None                  # no recurrence for one-time tasks
        assert len(pet.get_tasks()) == 1         # list unchanged — original task only

    def test_completed_once_task_excluded_from_schedule(self, owner):
        """A completed one-time task must be filtered out of the next build_schedule().

        generate_recurring_tasks() skips 'once' tasks where is_completed=True,
        so they should not appear in the returned schedule.
        """
        pet = Pet(name="Luna", species="dog", age=3)
        pet.add_task(Task(id=3, title="One-off Groom", duration_minutes=20,
                          priority="medium", frequency="once"))
        scheduler = Scheduler(owner=owner)
        scheduler.add_pet(pet)
        scheduler.complete_task(task_id=3)

        schedule = scheduler.build_schedule()
        titles = [st.task.title for st in schedule]
        assert "One-off Groom" not in titles

    def test_new_recurring_task_id_is_unique(self, owner):
        """Each call to complete_task() must yield a strictly increasing new ID.

        _next_task_id starts at 1000 and increments after each recurring
        completion, so two consecutive completions must produce different IDs.
        """
        pet = Pet(name="Luna", species="dog", age=3)
        pet.add_task(Task(id=10, title="Walk A", duration_minutes=20,
                          priority="high", frequency="daily"))
        pet.add_task(Task(id=11, title="Walk B", duration_minutes=20,
                          priority="high", frequency="daily"))
        scheduler = Scheduler(owner=owner)
        scheduler.add_pet(pet)

        new_a = scheduler.complete_task(task_id=10)
        new_b = scheduler.complete_task(task_id=11)
        assert new_a.id != new_b.id


# --- Conflict detection tests ---

class TestConflictDetection:
    def _make_overlapping_scheduler(self, owner):
        """Helper: return a scheduler whose scheduled_tasks list contains two
        overlapping ScheduledTask objects injected directly (bypassing the
        greedy algorithm, which would never produce overlaps on its own)."""
        task_a = Task(id=1, title="Walk",    duration_minutes=60, priority="high", pet_name="Luna")
        task_b = Task(id=2, title="Feeding", duration_minutes=30, priority="high", pet_name="Luna")
        scheduler = Scheduler(owner=owner)
        # Inject overlapping slots manually: both start at 09:00, so they fully overlap
        scheduler.scheduled_tasks = [
            ScheduledTask(task=task_a, start_time=time(9, 0)),
            ScheduledTask(task=task_b, start_time=time(9, 0)),
        ]
        return scheduler

    def test_get_all_conflicts_detects_exact_same_start_time(self, owner):
        """Two tasks at the same start time must be flagged as a conflict.

        This is the clearest duplicate-time case: task_b starts exactly when
        task_a starts, so the overlap equals task_b's full duration (30 min).
        """
        scheduler = self._make_overlapping_scheduler(owner)
        conflicts = scheduler.get_all_conflicts()

        assert len(conflicts) == 1
        assert conflicts[0]["overlap_minutes"] == 30   # task_b's 30-min duration fully overlaps

    def test_warn_conflicts_returns_non_empty_list(self, owner):
        """warn_conflicts() must return at least one warning string when there is an overlap.

        The string should mention both task titles so the owner knows which
        tasks are the problem.
        """
        scheduler = self._make_overlapping_scheduler(owner)
        warnings = scheduler.warn_conflicts()

        assert len(warnings) > 0
        assert "Walk" in warnings[0]
        assert "Feeding" in warnings[0]

    def test_no_conflicts_in_normal_schedule(self, scheduler_with_pets):
        """The greedy scheduler must never produce overlapping slots.

        build_schedule() places each task sequentially, so get_all_conflicts()
        should always return an empty list for a normally-built schedule.
        """
        scheduler_with_pets.build_schedule()
        assert scheduler_with_pets.get_all_conflicts() == []

    def test_warn_conflicts_empty_when_no_scheduled_tasks(self, owner):
        """warn_conflicts() on an empty schedule must return [] without errors.

        Callers rely on a falsy return value meaning 'all clear', so an empty
        list (not an exception) is the correct response here.
        """
        scheduler = Scheduler(owner=owner)
        assert scheduler.warn_conflicts() == []

    def test_check_conflicts_true_when_overlapping(self, owner):
        """check_conflicts() must return True when a proposed task overlaps the schedule.

        We schedule a 60-min task at 09:00 (runs until 10:00), then check
        whether a new task proposed at 09:30 would conflict — it should.
        """
        existing_task = Task(id=1, title="Long Walk", duration_minutes=60,
                             priority="high", pet_name="Luna")
        scheduler = Scheduler(owner=owner)
        scheduler.scheduled_tasks = [ScheduledTask(task=existing_task, start_time=time(9, 0))]

        new_task = Task(id=2, title="Feeding", duration_minutes=20,
                        priority="medium", pet_name="Milo")
        # Proposed at 09:30 — inside the 09:00–10:00 window of the existing task
        assert scheduler.check_conflicts(new_task, proposed_start=time(9, 30)) is True

    def test_check_conflicts_false_when_not_overlapping(self, owner):
        """check_conflicts() must return False when the proposed slot is clear.

        The existing task ends at 10:00; a new task proposed at 10:00 starts
        exactly when the old one ends — back-to-back is not an overlap.
        """
        existing_task = Task(id=1, title="Long Walk", duration_minutes=60,
                             priority="high", pet_name="Luna")
        scheduler = Scheduler(owner=owner)
        scheduler.scheduled_tasks = [ScheduledTask(task=existing_task, start_time=time(9, 0))]

        new_task = Task(id=2, title="Feeding", duration_minutes=20,
                        priority="medium", pet_name="Milo")
        # Proposed at 10:00 — exactly when the previous task finishes, no overlap
        assert scheduler.check_conflicts(new_task, proposed_start=time(10, 0)) is False


# --- find_next_slot tests ---

class TestFindNextSlot:
    def test_empty_schedule_returns_window_start(self, owner):
        """With no tasks scheduled, the first open slot is the start of the owner's window.

        The gap-scan sees no occupied intervals, so the only candidate is
        available_start (08:00). A short task must fit immediately.
        """
        scheduler = Scheduler(owner=owner)
        task = Task(id=1, title="Walk", duration_minutes=30, priority="high")
        assert scheduler.find_next_slot(task) == time(8, 0)

    def test_returns_slot_after_existing_task(self, owner):
        """A task that fills 08:00–09:00 should push the next slot to 09:00.

        The gap-scan adds each task's end_time as a candidate. After a 60-min
        task starting at 08:00, the next candidate is 09:00 and must be returned.
        """
        scheduler = Scheduler(owner=owner)
        blocker = Task(id=1, title="Long Walk", duration_minutes=60,
                       priority="high", pet_name="Luna")
        scheduler.scheduled_tasks = [ScheduledTask(task=blocker, start_time=time(8, 0))]

        new_task = Task(id=2, title="Feeding", duration_minutes=20, priority="medium")
        assert scheduler.find_next_slot(new_task) == time(9, 0)

    def test_finds_gap_between_two_tasks(self, owner):
        """A free gap between two scheduled tasks must be preferred over the tail slot.

        Schedule: Walk 08:00–08:30, Grooming 09:00–09:20 (30-min gap at 08:30).
        A 20-min task must fit in the 08:30 gap rather than after 09:20.
        """
        scheduler = Scheduler(owner=owner)
        task_a = Task(id=1, title="Walk",     duration_minutes=30, priority="high",   pet_name="Luna")
        task_b = Task(id=2, title="Grooming", duration_minutes=20, priority="medium", pet_name="Luna")
        scheduler.scheduled_tasks = [
            ScheduledTask(task=task_a, start_time=time(8, 0)),   # ends 08:30
            ScheduledTask(task=task_b, start_time=time(9, 0)),   # starts 09:00 → 30-min gap
        ]

        new_task = Task(id=3, title="Feeding", duration_minutes=20, priority="medium")
        # 20 min fits in the 08:30–09:00 gap (30 min wide)
        assert scheduler.find_next_slot(new_task) == time(8, 30)

    def test_skips_gap_too_small_and_finds_next(self, owner):
        """When a gap exists but is too narrow, the scan must continue to the next gap.

        Schedule: Walk 08:00–08:30, Grooming 08:40–09:00 (only 10-min gap at 08:30).
        A 20-min task cannot fit in 10 minutes, so it must land after 09:00.
        """
        scheduler = Scheduler(owner=owner)
        task_a = Task(id=1, title="Walk",     duration_minutes=30, priority="high",   pet_name="Luna")
        task_b = Task(id=2, title="Grooming", duration_minutes=20, priority="medium", pet_name="Luna")
        scheduler.scheduled_tasks = [
            ScheduledTask(task=task_a, start_time=time(8, 0)),   # ends 08:30
            ScheduledTask(task=task_b, start_time=time(8, 40)),  # 10-min gap — too small for 20 min
        ]

        new_task = Task(id=3, title="Feeding", duration_minutes=20, priority="medium")
        assert scheduler.find_next_slot(new_task) == time(9, 0)

    def test_returns_none_when_window_is_full(self, owner):
        """When no gap is large enough, find_next_slot must return None, not crash.

        A single task that fills the entire 720-min window leaves no room for
        anything else — the method must return None cleanly.
        """
        scheduler = Scheduler(owner=owner)
        # 720 min = exactly 08:00–20:00, the full window
        blocker = Task(id=1, title="All Day", duration_minutes=720,
                       priority="high", pet_name="Luna")
        scheduler.scheduled_tasks = [ScheduledTask(task=blocker, start_time=time(8, 0))]

        new_task = Task(id=2, title="Walk", duration_minutes=30, priority="medium")
        assert scheduler.find_next_slot(new_task) is None

    def test_task_fits_exactly_at_end_of_window(self, owner):
        """A task that fills the remaining window exactly must be returned, not rejected.

        If 30 minutes remain and the task is 30 minutes, it fits (end == window_end
        is allowed by the <= comparison). Off-by-one errors would return None here.
        """
        scheduler = Scheduler(owner=owner)
        # Fill 08:00–19:30 (690 min), leaving exactly 30 min until 20:00
        blocker = Task(id=1, title="Big Task", duration_minutes=690,
                       priority="high", pet_name="Luna")
        scheduler.scheduled_tasks = [ScheduledTask(task=blocker, start_time=time(8, 0))]

        tight_task = Task(id=2, title="Walk", duration_minutes=30, priority="medium")
        assert scheduler.find_next_slot(tight_task) == time(19, 30)
