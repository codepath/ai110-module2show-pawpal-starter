"""Unit tests for the PawPal+ object model.

Covers the happy paths plus the edge cases that matter for a scheduler with
sorting, filtering, recurring tasks and conflict detection: an empty task list,
two tasks pinned to the same time, budget/window boundaries, the essential-task
override, weekly-recurrence gating, and re-enqueue idempotency.

Run from the project root with `python -m pytest -v` (or `pytest -v`).
"""

from pawpal_system import (
    Constraints,
    Owner,
    Pet,
    Plan,
    Responsibility,
    Scheduler,
    to_hhmm,
    to_minutes,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def make_task(title: str, duration: int = 30, **kw) -> Responsibility:
    """Thin Responsibility factory with sensible defaults."""
    return Responsibility(title=title, duration_minutes=duration, **kw)


def make_plan(
    tasks,
    *,
    available_minutes: int = 240,
    day_of_week: str = "Monday",
    day_start: str = "07:00",
    day_end: str = "21:00",
    prefs: dict | None = None,
) -> Plan:
    """Build an Owner+Pet+Constraints+Plan, attach tasks, build, and return it.

    Mirrors how main.py wires the objects together so tests exercise the same
    code paths the demo relies on.
    """
    pet = Pet(name="TestPet")
    owner = Owner(name="Tester", preferences=prefs or {})
    owner.add_pet(pet)
    for task in tasks:
        pet.add_responsibility(task)
    constraints = Constraints(
        available_minutes=available_minutes,
        day_start=day_start,
        day_end=day_end,
        day_of_week=day_of_week,
    )
    plan = Plan(owner=owner, pet=pet, constraints=constraints)
    plan.build()
    return plan


def titles(items) -> list[str]:
    """Task titles for concise assertions.

    Works for both ``plan.scheduled`` (``Scheduler`` wrappers) and
    ``plan.skipped`` (raw ``Responsibility`` objects).
    """
    return [getattr(item, "responsibility", item).title for item in items]


# --------------------------------------------------------------------------- #
# Time helpers
# --------------------------------------------------------------------------- #
class TestTimeHelpers:
    def test_to_minutes_round_trip(self):
        assert to_minutes("08:30") == 510
        assert to_hhmm(510) == "08:30"

    def test_midnight(self):
        assert to_minutes("00:00") == 0
        assert to_hhmm(0) == "00:00"

    def test_zero_padded(self):
        assert to_hhmm(570) == "09:30"
        assert to_minutes("21:00") == 21 * 60


# --------------------------------------------------------------------------- #
# Sorting
# --------------------------------------------------------------------------- #
class TestSorting:
    def _sched(self, start: str) -> Scheduler:
        return Scheduler(make_task(start), start, start)

    def test_orders_out_of_order_items(self):
        items = [self._sched("18:00"), self._sched("08:00"), self._sched("12:00")]
        ordered = Scheduler.sort_by_time(items)
        assert [s.start_time for s in ordered] == ["08:00", "12:00", "18:00"]

    def test_empty_list_returns_empty(self):
        # Edge: no tasks at all.
        assert Scheduler.sort_by_time([]) == []

    def test_single_item_unchanged(self):
        items = [self._sched("09:00")]
        assert Scheduler.sort_by_time(items) == items

    def test_already_sorted_unchanged(self):
        items = [self._sched("08:00"), self._sched("09:00")]
        assert [s.start_time for s in Scheduler.sort_by_time(items)] == ["08:00", "09:00"]

    def test_equal_start_times_do_not_error(self):
        items = [self._sched("08:00"), self._sched("08:00")]
        assert len(Scheduler.sort_by_time(items)) == 2


# --------------------------------------------------------------------------- #
# Filtering
# --------------------------------------------------------------------------- #
class TestFiltering:
    def _owner_two_pets(self) -> Owner:
        rex = Pet(name="Rex")
        rex.add_responsibility(make_task("Walk"))
        done = make_task("Breakfast")
        done.completed = True
        rex.add_responsibility(done)

        mittens = Pet(name="Mittens")
        mittens.add_responsibility(make_task("Litter box"))

        owner = Owner(name="Tester")
        owner.add_pet(rex)
        owner.add_pet(mittens)
        return owner

    def test_no_args_returns_all_tasks(self):
        owner = self._owner_two_pets()
        assert len(owner.filter_tasks()) == 3

    def test_completed_partition(self):
        owner = self._owner_two_pets()
        assert {t.title for t in owner.filter_tasks(completed=True)} == {"Breakfast"}
        assert {t.title for t in owner.filter_tasks(completed=False)} == {"Walk", "Litter box"}

    def test_filter_by_pet_name(self):
        owner = self._owner_two_pets()
        assert {t.title for t in owner.filter_tasks(pet_name="Rex")} == {"Walk", "Breakfast"}

    def test_filter_by_pet_and_completion_combined(self):
        owner = self._owner_two_pets()
        result = owner.filter_tasks(pet_name="Rex", completed=False)
        assert {t.title for t in result} == {"Walk"}

    def test_owner_with_no_pets(self):
        # Edge: nothing to filter.
        assert Owner(name="Empty").filter_tasks() == []

    def test_pet_with_no_responsibilities(self):
        # Edge: pet exists but has no tasks.
        owner = Owner(name="Tester")
        owner.add_pet(Pet(name="Ghost"))
        assert owner.filter_tasks() == []

    def test_unknown_pet_name_returns_empty(self):
        owner = self._owner_two_pets()
        assert owner.filter_tasks(pet_name="Nope") == []


# --------------------------------------------------------------------------- #
# Priority ordering & budget selection
# --------------------------------------------------------------------------- #
class TestPriorityAndBudget:
    def test_priority_weight_values(self):
        assert make_task("h", priority="high").priority_weight() == 3
        assert make_task("m", priority="medium").priority_weight() == 2
        assert make_task("l", priority="low").priority_weight() == 1
        # Unknown label falls back to medium (2).
        assert make_task("x", priority="bogus").priority_weight() == 2

    def test_priority_score_is_tier_weighted_minus_duration(self):
        # Weighted sum: 100*tier - duration (higher = ranked first).
        assert make_task("h", 30, priority="high").priority_score() == 100 * 3 - 30
        assert make_task("m", 60, priority="medium").priority_score() == 100 * 2 - 60

    def test_higher_tier_beats_lower_regardless_of_length(self):
        # Tier dominates: a long high-priority task still outranks a short
        # medium one, so under a one-task budget the high task is the one kept.
        plan = make_plan(
            [
                make_task("QuickMedium", 10, priority="medium"),
                make_task("LongHigh", 60, priority="high"),
            ],
            available_minutes=60,
        )
        assert titles(plan.scheduled) == ["LongHigh"]
        assert titles(plan.skipped) == ["QuickMedium"]

    def test_extreme_duration_gap_can_flip_a_near_tier(self):
        # The "duration nudges" edge: a very long high-priority task
        # (300-150=150) scores below a quick medium one (200-10=190), so with
        # room for only one, the shorter medium task wins.
        plan = make_plan(
            [
                make_task("QuickMedium", 10, priority="medium"),
                make_task("VeryLongHigh", 150, priority="high"),
            ],
            available_minutes=150,
        )
        assert titles(plan.scheduled) == ["QuickMedium"]
        assert titles(plan.skipped) == ["VeryLongHigh"]

    def test_priority_order_under_tight_budget(self):
        # Only 60 of the 90 minutes fit: high + medium kept, low dropped.
        plan = make_plan(
            [
                make_task("Low", 30, priority="low"),
                make_task("High", 30, priority="high"),
                make_task("Medium", 30, priority="medium"),
            ],
            available_minutes=60,
        )
        scheduled = set(titles(plan.scheduled))
        assert scheduled == {"High", "Medium"}
        assert "Low" in titles(plan.skipped)

    def test_shorter_duration_first_among_equal_priority(self):
        # Budget fits only one 30-min task; the shorter equal-priority one wins.
        plan = make_plan(
            [
                make_task("Long", 40, priority="medium"),
                make_task("Short", 30, priority="medium"),
            ],
            available_minutes=30,
        )
        assert titles(plan.scheduled) == ["Short"]
        assert titles(plan.skipped) == ["Long"]

    def test_task_exactly_filling_budget_is_kept(self):
        # Boundary: duration == remaining must fit (has_time_for uses <=).
        plan = make_plan([make_task("Exact", 60, priority="high")], available_minutes=60)
        assert titles(plan.scheduled) == ["Exact"]
        assert plan.skipped == []

    def test_essentials_forced_in_past_budget(self):
        # Both essentials kept even though they total 40 > 30 budget.
        plan = make_plan(
            [
                make_task("Meds", 20, essential=True),
                make_task("Feeding", 20, essential=True),
            ],
            available_minutes=30,
        )
        assert set(titles(plan.scheduled)) == {"Meds", "Feeding"}
        assert plan.skipped == []

    def test_zero_budget_keeps_only_essentials(self):
        # Edge: no optional time at all.
        plan = make_plan(
            [
                make_task("Insulin", 10, essential=True),
                make_task("Play", 10, priority="low"),
            ],
            available_minutes=0,
        )
        assert titles(plan.scheduled) == ["Insulin"]
        assert titles(plan.skipped) == ["Play"]


# --------------------------------------------------------------------------- #
# Window placement
# --------------------------------------------------------------------------- #
class TestWindowPlacement:
    def test_fixed_tasks_pinned_at_their_time(self):
        plan = make_plan(
            [
                make_task("Evening", 30, fixed_time="18:00"),
                make_task("Morning", 30, fixed_time="08:00"),
            ]
        )
        rows = {item.responsibility.title: (item.start_time, item.end_time) for item in plan.scheduled}
        assert rows["Morning"] == ("08:00", "08:30")
        assert rows["Evening"] == ("18:00", "18:30")

    def test_non_essential_fixed_before_day_start_skipped(self):
        plan = make_plan([make_task("TooEarly", 30, fixed_time="06:00")])
        assert plan.scheduled == []
        assert titles(plan.skipped) == ["TooEarly"]

    def test_non_essential_fixed_after_day_end_skipped(self):
        plan = make_plan([make_task("TooLate", 30, fixed_time="20:45")], day_end="21:00")
        assert plan.scheduled == []
        assert titles(plan.skipped) == ["TooLate"]

    def test_essential_fixed_outside_window_kept(self):
        # Override: essential meds run even if pinned outside the day window.
        plan = make_plan([make_task("NightMeds", 30, fixed_time="06:00", essential=True)])
        assert titles(plan.scheduled) == ["NightMeds"]

    def test_flexible_task_ending_exactly_at_day_end_kept(self):
        # Boundary: end == window_end is allowed (only end > window_end is dropped).
        plan = make_plan(
            [make_task("FillsDay", 30)],
            day_start="20:30",
            day_end="21:00",
        )
        assert titles(plan.scheduled) == ["FillsDay"]
        assert plan.scheduled[0].end_time == "21:00"

    def test_flexible_task_spilling_past_day_end_skipped(self):
        plan = make_plan(
            [make_task("Overflows", 31)],
            day_start="20:30",
            day_end="21:00",
        )
        assert plan.scheduled == []
        assert titles(plan.skipped) == ["Overflows"]

    def test_flexible_task_pushed_past_pinned_slot(self):
        # The flexible walk would start at the 07:00 day-start, but the pinned
        # meds occupy 07:00-07:30, so it should slide to 07:30.
        plan = make_plan(
            [
                make_task("Meds", 30, fixed_time="07:00"),
                make_task("Walk", 30),
            ]
        )
        walk = next(i for i in plan.scheduled if i.responsibility.title == "Walk")
        assert walk.start_time == "07:30"

    def test_owner_preference_delays_flexible_task(self):
        # walk_time=afternoon → a flexible walk must not start before 12:00.
        plan = make_plan(
            [make_task("Walk", 30, category="walk")],
            prefs={"walk_time": "afternoon"},
        )
        assert plan.scheduled[0].start_time == "12:00"


# --------------------------------------------------------------------------- #
# Recurrence
# --------------------------------------------------------------------------- #
class TestRecurrence:
    def test_completing_daily_task_enqueues_next_occurrence(self):
        pet = Pet(name="Rex")
        task = make_task("Walk", recurrence="daily")
        pet.add_responsibility(task)

        task.mark_complete()
        assert task.completed is True
        assert len(pet.responsibilities) == 2
        fresh = pet.responsibilities[1]
        assert fresh.title == "Walk"
        assert fresh.duration_minutes == 30
        assert fresh.completed is False

    def test_mark_complete_is_idempotent(self):
        # Edge: calling twice must not spawn a duplicate next occurrence.
        pet = Pet(name="Rex")
        task = make_task("Walk", recurrence="daily")
        pet.add_responsibility(task)

        task.mark_complete()
        task.mark_complete()
        assert len(pet.responsibilities) == 2

    def test_weekly_task_re_enqueues(self):
        pet = Pet(name="Rex")
        task = make_task("Bath", recurrence="weekly", weekday="Sunday")
        pet.add_responsibility(task)

        task.mark_complete()
        assert len(pet.responsibilities) == 2
        assert pet.responsibilities[1].recurrence == "weekly"
        assert pet.responsibilities[1].weekday == "Sunday"

    def test_non_recurring_task_does_not_enqueue(self):
        pet = Pet(name="Rex")
        task = make_task("One-off vet visit", recurrence="once")
        pet.add_responsibility(task)

        task.mark_complete()
        assert task.completed is True
        assert len(pet.responsibilities) == 1

    def test_standalone_task_completes_without_pet(self):
        # Edge: never added to a pet → pet is None → completes, enqueues nothing.
        task = make_task("Orphan", recurrence="daily")
        task.mark_complete()
        assert task.completed is True

    def test_completed_tasks_excluded_from_build(self):
        done = make_task("Done", 30)
        done.completed = True
        plan = make_plan([done, make_task("Todo", 30)])
        assert titles(plan.scheduled) == ["Todo"]
        # The completed task is neither scheduled nor skipped (it's filtered out).
        assert "Done" not in titles(plan.scheduled)
        assert "Done" not in titles(plan.skipped)


# --------------------------------------------------------------------------- #
# Weekly scheduling (weekday gating)
# --------------------------------------------------------------------------- #
class TestWeeklyScheduling:
    def test_weekly_task_on_matching_weekday_scheduled(self):
        plan = make_plan(
            [make_task("Bath", 30, recurrence="weekly", weekday="Monday")],
            day_of_week="Monday",
        )
        assert titles(plan.scheduled) == ["Bath"]

    def test_weekly_task_on_other_weekday_skipped(self):
        plan = make_plan(
            [make_task("Bath", 30, recurrence="weekly", weekday="Sunday")],
            day_of_week="Monday",
        )
        assert plan.scheduled == []
        assert titles(plan.skipped) == ["Bath"]
        assert any("weekly" in r for r in plan.explanation.skipped_reasons)


# --------------------------------------------------------------------------- #
# Conflict detection
# --------------------------------------------------------------------------- #
class TestConflictDetection:
    def test_clean_schedule_has_no_conflict(self):
        plan = make_plan(
            [
                make_task("Morning", 30, fixed_time="08:00"),
                make_task("Evening", 30, fixed_time="18:00"),
            ]
        )
        assert plan.detect_conflicts() == ""

    def test_two_essential_tasks_same_time_conflict(self):
        # The main.py Breakfast+Insulin case: both essentials kept, overlap warned.
        plan = make_plan(
            [
                make_task("Breakfast", 10, fixed_time="08:30", essential=True),
                make_task("Insulin", 10, fixed_time="08:30", essential=True),
            ]
        )
        assert len(plan.scheduled) == 2
        warning = plan.detect_conflicts()
        assert warning != ""
        assert "Breakfast" in warning and "Insulin" in warning

    def test_two_non_essential_same_time_second_skipped(self):
        # Non-essentials: build() drops the second, so the schedule is clean.
        plan = make_plan(
            [
                make_task("WalkA", 30, fixed_time="08:00"),
                make_task("WalkB", 30, fixed_time="08:00"),
            ]
        )
        assert len(plan.scheduled) == 1
        assert plan.detect_conflicts() == ""

    def test_adjacent_slots_are_not_a_conflict(self):
        # Boundary: 08:00-08:30 then 08:30-09:00 touch but do not overlap.
        plan = Plan(
            owner=Owner(name="x"),
            pet=Pet(name="p"),
            constraints=Constraints(available_minutes=240),
        )
        plan.scheduled = [
            Scheduler(make_task("A"), "08:00", "08:30"),
            Scheduler(make_task("B"), "08:30", "09:00"),
        ]
        assert plan.detect_conflicts() == ""

    def test_nested_overlap_detected(self):
        # A long task spanning a short one nested inside it must be caught by the
        # all-pairs comparison, not just adjacent-neighbor checks.
        plan = Plan(
            owner=Owner(name="x"),
            pet=Pet(name="p"),
            constraints=Constraints(available_minutes=240),
        )
        plan.scheduled = [
            Scheduler(make_task("Long"), "08:00", "10:00"),
            Scheduler(make_task("Short"), "08:30", "08:45"),
        ]
        warning = plan.detect_conflicts()
        assert "Long" in warning and "Short" in warning

    def test_empty_schedule_has_no_conflict(self):
        # Edge: no tasks scheduled.
        plan = make_plan([])
        assert plan.detect_conflicts() == ""


# --------------------------------------------------------------------------- #
# Plan outputs & idempotency
# --------------------------------------------------------------------------- #
class TestPlanOutputs:
    def test_total_minutes_sums_scheduled_durations(self):
        plan = make_plan(
            [
                make_task("A", 30, fixed_time="08:00"),
                make_task("B", 10, fixed_time="09:00"),
            ]
        )
        assert plan.total_minutes() == 40

    def test_summary_reports_planned_counts(self):
        # 1 scheduled + 1 skipped (budget) → "Planned 1 of 2".
        plan = make_plan(
            [
                make_task("Keep", 30, priority="high"),
                make_task("Drop", 30, priority="low"),
            ],
            available_minutes=30,
        )
        assert "Planned 1 of 2" in plan.explanation.summary
        assert plan.explanation.skipped_reasons  # non-empty

    def test_as_rows_shape(self):
        plan = make_plan([make_task("Walk", 30, fixed_time="08:00", category="walk", priority="high")])
        rows = plan.as_rows()
        assert rows == [
            {
                "Start": "08:00",
                "End": "08:30",
                "Task": "Walk",
                "Category": "walk",
                "Priority": "high",
                "Minutes": 30,
            }
        ]

    def test_build_is_idempotent(self):
        plan = make_plan(
            [
                make_task("A", 30, fixed_time="08:00"),
                make_task("B", 30, fixed_time="09:00"),
            ]
        )
        first = titles(plan.scheduled)
        plan.build()
        assert titles(plan.scheduled) == first
        assert len(plan.scheduled) == 2  # not duplicated

    def test_empty_plan_produces_empty_results(self):
        # The user's "no tasks inputted" edge.
        plan = make_plan([])
        assert plan.scheduled == []
        assert plan.skipped == []
        assert plan.total_minutes() == 0
        assert "Planned 0 of 0" in plan.explanation.summary
        assert plan.detect_conflicts() == ""


# --------------------------------------------------------------------------- #
# Original smoke tests (kept)
# --------------------------------------------------------------------------- #
def test_mark_complete_changes_status():
    """mark_complete() flips a task's status from incomplete to complete."""
    task = Responsibility(title="Morning walk", duration_minutes=30)

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_responsibility_increases_task_count():
    """Adding a task to a Pet increases its responsibility count by one."""
    pet = Pet(name="Rex")

    assert len(pet.responsibilities) == 0
    pet.add_responsibility(Responsibility(title="Breakfast", duration_minutes=10))
    assert len(pet.responsibilities) == 1
