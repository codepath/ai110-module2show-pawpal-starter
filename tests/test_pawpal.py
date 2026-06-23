from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(**kwargs):
    defaults = dict(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        task_type="exercise",
        required=True,
    )
    defaults.update(kwargs)
    return Task(**defaults)


def make_scheduler(available_minutes=120, tasks=None):
    """Return a Scheduler with a single pet 'Buddy' pre-loaded with tasks."""
    owner = Owner("Alex", {}, available_minutes)
    pet = Pet(name="Buddy", species="Dog", age=4)
    for task in (tasks or []):
        pet.add_task(task)
    owner.add_pet(pet)
    return Scheduler(owner)


# ---------------------------------------------------------------------------
# Existing tests (unchanged)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", age=4)
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_tasks_by_time_chronological_order():
    """Tasks with earliest_start are returned in ascending time order."""
    t1 = make_task(title="Afternoon walk", earliest_start="14:00")
    t2 = make_task(title="Morning meds",   earliest_start="08:00")
    t3 = make_task(title="Evening feed",   earliest_start="18:30")
    scheduler = make_scheduler(tasks=[t1, t2, t3])

    result = scheduler.sort_tasks_by_time([t1, t2, t3])

    assert [r.title for r in result] == ["Morning meds", "Afternoon walk", "Evening feed"]


def test_sort_tasks_by_time_untimed_tasks_go_last():
    """Tasks without earliest_start float to the end, after all timed tasks."""
    timed   = make_task(title="Walk",  earliest_start="08:00")
    untimed = make_task(title="Brush", earliest_start=None)
    scheduler = make_scheduler(tasks=[timed, untimed])

    result = scheduler.sort_tasks_by_time([untimed, timed])

    assert result[0].title == "Walk"
    assert result[1].title == "Brush"


def test_sort_tasks_by_time_same_start_time_stable():
    """Two tasks sharing the same earliest_start preserve their input order (stable sort)."""
    t1 = make_task(title="Feed",  earliest_start="08:00")
    t2 = make_task(title="Brush", earliest_start="08:00")
    scheduler = make_scheduler(tasks=[t1, t2])

    result = scheduler.sort_tasks_by_time([t1, t2])

    assert result[0].title == "Feed"
    assert result[1].title == "Brush"


def test_sort_tasks_by_time_empty_list():
    """Sorting an empty list returns an empty list without error."""
    scheduler = make_scheduler()
    assert scheduler.sort_tasks_by_time([]) == []


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_next_occurrence_daily_advances_one_day():
    """A daily task's next occurrence lands exactly one day later."""
    task = make_task(recurrence="daily", due_date=date(2026, 3, 30))
    nxt = task.next_occurrence()

    assert nxt.due_date == date(2026, 3, 31)
    assert nxt.completed is False


def test_next_occurrence_weekly_advances_seven_days():
    task = make_task(recurrence="weekly", due_date=date(2026, 3, 30))
    nxt = task.next_occurrence()

    assert nxt.due_date == date(2026, 4, 6)


def test_next_occurrence_weekdays_skips_weekend():
    """A weekdays task due on Friday should reschedule to the following Monday."""
    task = make_task(recurrence="weekdays", due_date=date(2026, 4, 3))  # Friday
    nxt = task.next_occurrence()

    assert nxt.due_date == date(2026, 4, 6)  # Monday


def test_next_occurrence_non_recurring_returns_none():
    """A task with no recurrence returns None from next_occurrence."""
    task = make_task(recurrence=None)
    assert task.next_occurrence() is None


def test_complete_and_reschedule_marks_done_and_creates_next():
    """Completing a daily task marks it done and attaches a new task to the pet."""
    task = make_task(title="Medicine", recurrence="daily", due_date=date(2026, 3, 30))
    scheduler = make_scheduler(tasks=[task])
    pet = scheduler.owner.pets[0]

    next_task = scheduler.complete_and_reschedule(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 31)
    assert next_task.completed is False
    assert next_task in pet.tasks


def test_complete_and_reschedule_non_recurring_returns_none():
    """complete_and_reschedule returns None for a non-recurring task."""
    task = make_task(recurrence=None)
    scheduler = make_scheduler(tasks=[task])

    result = scheduler.complete_and_reschedule(task)

    assert result is None
    assert task.completed is True  # still marked done even if not recurring


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_overlapping_windows():
    """Two tasks whose windows overlap are returned as a conflicting pair."""
    a = make_task(title="Walk", earliest_start="08:00", latest_end="09:00")
    b = make_task(title="Bath", earliest_start="08:30", latest_end="09:30")
    scheduler = make_scheduler(tasks=[a, b])

    conflicts = scheduler.detect_conflicts([a, b])

    assert len(conflicts) == 1
    assert (a, b) in conflicts


def test_detect_conflicts_same_start_time():
    """Two tasks sharing an identical start time are flagged as conflicting."""
    a = make_task(title="Walk", earliest_start="08:00", latest_end="09:00")
    b = make_task(title="Feed", earliest_start="08:00", latest_end="08:30")
    scheduler = make_scheduler(tasks=[a, b])

    conflicts = scheduler.detect_conflicts([a, b])

    assert len(conflicts) == 1


def test_detect_conflicts_adjacent_windows_no_conflict():
    """Tasks that touch but do not overlap are NOT flagged (strict < boundary)."""
    a = make_task(title="Walk", earliest_start="08:00", latest_end="09:00")
    b = make_task(title="Feed", earliest_start="09:00", latest_end="09:30")
    scheduler = make_scheduler(tasks=[a, b])

    assert scheduler.detect_conflicts([a, b]) == []


def test_detect_conflicts_no_overlap():
    """Non-overlapping windows produce no conflicts."""
    a = make_task(title="Walk", earliest_start="07:00", latest_end="08:00")
    b = make_task(title="Feed", earliest_start="09:00", latest_end="10:00")
    scheduler = make_scheduler(tasks=[a, b])

    assert scheduler.detect_conflicts([a, b]) == []


def test_detect_conflicts_missing_bounds_ignored():
    """A task missing latest_end is excluded from conflict checking."""
    a = make_task(title="Walk", earliest_start="08:00", latest_end="09:00")
    b = make_task(title="Feed", earliest_start="08:30")   # no latest_end
    scheduler = make_scheduler(tasks=[a, b])

    assert scheduler.detect_conflicts([a, b]) == []


def test_detect_conflicts_empty_list():
    scheduler = make_scheduler()
    assert scheduler.detect_conflicts([]) == []


# ---------------------------------------------------------------------------
# Edge cases — pet / owner / pipeline
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_empty_schedule():
    """A pet with no tasks produces an empty schedule without error."""
    scheduler = make_scheduler(tasks=[])
    assert scheduler.generate_schedule() == []


def test_owner_with_no_pets_empty_schedule():
    """An owner with no pets produces an empty schedule without error."""
    owner = Owner("Alex", {}, 120)
    assert Scheduler(owner).generate_schedule() == []


def test_zero_available_minutes_nothing_scheduled():
    """When the owner has no time, no tasks are scheduled."""
    task = make_task(duration_minutes=30)
    scheduler = make_scheduler(available_minutes=0, tasks=[task])
    assert scheduler.generate_schedule() == []


def test_task_fits_exactly_in_available_time():
    """A task whose duration equals remaining time is scheduled; balance hits 0."""
    task = make_task(duration_minutes=30)
    scheduler = make_scheduler(available_minutes=30, tasks=[task])

    schedule = scheduler.generate_schedule()

    assert len(schedule) == 1
    assert scheduler.owner.remaining_availability() == 0


def test_required_tasks_scheduled_before_optional():
    """Required tasks precede optional ones in the generated schedule."""
    optional = make_task(title="Play",     priority="low",  required=False, duration_minutes=10)
    required = make_task(title="Medicine", priority="high", required=True,  duration_minutes=10)
    scheduler = make_scheduler(available_minutes=120, tasks=[optional, required])

    schedule = scheduler.generate_schedule()

    titles = [e["title"] for e in schedule]
    assert titles.index("Medicine") < titles.index("Play")


def test_all_completed_tasks_produce_empty_schedule():
    """If every task is already complete, the schedule is empty."""
    task = make_task()
    task.mark_complete()
    scheduler = make_scheduler(tasks=[task])
    assert scheduler.generate_schedule() == []


# ---------------------------------------------------------------------------
# Weighted scoring
# ---------------------------------------------------------------------------

def test_weighted_score_base_only():
    """Low priority, not required, no deadline, not medication → 10.0."""
    task = make_task(priority="low", required=False, task_type="exercise", latest_end=None)
    assert task.weighted_score("09:00") == 10.0


def test_weighted_score_all_bonuses_no_deadline():
    """High + required + medication, no deadline → 30 + 20 + 12 + 0 = 62.0."""
    task = make_task(priority="high", required=True, task_type="medication", latest_end=None)
    assert task.weighted_score("09:00") == 62.0


def test_weighted_score_urgency_tier_imminent():
    """30 min remaining (≤60) → urgency bonus = 15."""
    task = make_task(priority="low", required=False, task_type="exercise", latest_end="09:30")
    assert task.weighted_score("09:00") == 10 + 15


def test_weighted_score_urgency_tier_moderate():
    """90 min remaining (≤120) → urgency bonus = 8."""
    task = make_task(priority="low", required=False, task_type="exercise", latest_end="10:30")
    assert task.weighted_score("09:00") == 10 + 8


def test_weighted_score_urgency_tier_approaching():
    """180 min remaining (≤240) → urgency bonus = 3."""
    task = make_task(priority="low", required=False, task_type="exercise", latest_end="12:00")
    assert task.weighted_score("09:00") == 10 + 3


def test_weighted_score_overdue_deadline():
    """Deadline already passed (negative remaining) → treated as maximally urgent (+15)."""
    task = make_task(priority="low", required=False, task_type="exercise", latest_end="08:00")
    assert task.weighted_score("09:00") == 10 + 15


def test_rank_by_urgency_highest_score_first():
    """rank_by_urgency returns the task with the highest score at index 0."""
    t_low  = make_task(title="Play",     priority="low",  required=False, task_type="exercise")
    t_high = make_task(title="Medicine", priority="high", required=True,  task_type="medication")
    scheduler = make_scheduler(tasks=[t_low, t_high])

    result = scheduler.rank_by_urgency([t_low, t_high], current_time="09:00")

    assert result[0] is t_high
    assert result[1] is t_low


def test_rank_by_urgency_does_not_mutate_input():
    """rank_by_urgency must not modify the original list."""
    t_low  = make_task(title="Play",     priority="low",  required=False)
    t_high = make_task(title="Medicine", priority="high", required=True)
    original = [t_low, t_high]
    scheduler = make_scheduler(tasks=[t_low, t_high])

    scheduler.rank_by_urgency(original, current_time="09:00")

    assert original[0] is t_low  # input list unchanged


def test_rank_by_urgency_empty_list():
    """rank_by_urgency on an empty list returns an empty list."""
    scheduler = make_scheduler()
    assert scheduler.rank_by_urgency([], current_time="09:00") == []
