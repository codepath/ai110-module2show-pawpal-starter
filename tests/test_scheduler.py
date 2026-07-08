"""Tests for PawPal+ core scheduling logic."""
from datetime import datetime, date, timedelta

import pytest

from models import Frequency, OwnerPreferences, Pet, Priority, Task, TaskType
from scheduler import generate_plan, score_task


# ── Constants ──────────────────────────────────────────────────────────────────
# generate_plan evaluates tasks at midnight of plan_date, so anchor all
# last_done times relative to midnight for predictable results.

TODAY    = date(2026, 7, 7)
MIDNIGHT = datetime(2026, 7, 7, 0, 0)   # as_of used inside generate_plan


# ── Fixtures / helpers ─────────────────────────────────────────────────────────

def make_task(
    name="Task",
    task_type=TaskType.WALK,
    priority=Priority.MEDIUM,
    duration=30,
    frequency=Frequency.DAILY,
    last_done=None,
    is_active=True,
) -> Task:
    t = Task(
        name=name,
        task_type=task_type,
        priority=priority,
        duration_minutes=duration,
        frequency=frequency,
        last_done=last_done,
    )
    t.is_active = is_active
    return t


def make_pet(tasks=None) -> Pet:
    return Pet(name="Mochi", species="Dog", tasks=tasks or [])


def make_prefs(minutes=120) -> OwnerPreferences:
    return OwnerPreferences(name="Jordan", available_minutes=minutes)


# ── Scoring tests ──────────────────────────────────────────────────────────────

class TestScoring:
    def test_critical_outscores_optional(self):
        critical = make_task(priority=Priority.CRITICAL)
        optional = make_task(priority=Priority.OPTIONAL)
        assert score_task(critical, MIDNIGHT) > score_task(optional, MIDNIGHT)

    def test_priority_order_is_preserved(self):
        """All five priority levels rank in the correct descending order."""
        scores = [
            score_task(make_task(priority=p, last_done=MIDNIGHT), MIDNIGHT)
            for p in [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM,
                      Priority.LOW, Priority.OPTIONAL]
        ]
        assert scores == sorted(scores, reverse=True)

    def test_overdue_task_scores_higher_than_fresh(self):
        fresh   = make_task(last_done=MIDNIGHT - timedelta(hours=1))
        overdue = make_task(last_done=MIDNIGHT - timedelta(hours=48))
        assert score_task(overdue, MIDNIGHT) > score_task(fresh, MIDNIGHT)

    def test_never_done_gets_extra_bonus(self):
        never    = make_task(last_done=None)
        just_due = make_task(last_done=MIDNIGHT - timedelta(hours=25))
        # never-done gets +10 bonus on top of priority + overdue pts
        assert score_task(never, MIDNIGHT) > score_task(just_due, MIDNIGHT)

    def test_score_is_always_non_negative(self):
        assert score_task(make_task(last_done=MIDNIGHT), MIDNIGHT) >= 0


# ── Plan generation tests ──────────────────────────────────────────────────────

class TestPlanGeneration:
    def test_empty_task_list_produces_empty_plan(self):
        plan = generate_plan(make_pet([]), make_prefs(), TODAY)
        assert plan.scheduled == []
        assert plan.skipped   == []

    def test_due_task_is_scheduled(self):
        t = make_task(last_done=None)  # never done → always due
        plan = generate_plan(make_pet([t]), make_prefs(), TODAY)
        assert len(plan.scheduled) == 1
        assert plan.scheduled[0].task.name == "Task"

    def test_not_yet_due_task_is_excluded(self):
        """A task completed 1h ago with a daily frequency should not appear."""
        t = make_task(last_done=MIDNIGHT - timedelta(hours=1), frequency=Frequency.DAILY)
        plan = generate_plan(make_pet([t]), make_prefs(), TODAY)
        assert plan.scheduled == []
        assert t in plan.not_due

    def test_high_priority_scheduled_before_low(self):
        low  = make_task(name="Play", priority=Priority.LOW,  last_done=None)
        high = make_task(name="Meds", priority=Priority.HIGH, last_done=None)
        plan = generate_plan(make_pet([low, high]), make_prefs(), TODAY)
        names = [s.task.name for s in plan.scheduled]
        assert names.index("Meds") < names.index("Play")

    def test_task_skipped_when_it_exceeds_remaining_budget(self):
        big = make_task(name="LongBath", duration=200, last_done=None)
        plan = generate_plan(make_pet([big]), make_prefs(minutes=60), TODAY)
        assert plan.scheduled == []
        assert big in plan.skipped

    def test_time_budget_is_never_exceeded(self):
        tasks = [make_task(name=f"T{i}", duration=25, last_done=None) for i in range(10)]
        plan  = generate_plan(make_pet(tasks), make_prefs(minutes=90), TODAY)
        assert plan.total_minutes_used <= 90

    def test_total_minutes_matches_sum_of_scheduled_durations(self):
        tasks = [make_task(name=f"T{i}", duration=20, last_done=None) for i in range(3)]
        plan  = generate_plan(make_pet(tasks), make_prefs(minutes=120), TODAY)
        assert plan.total_minutes_used == sum(s.task.duration_minutes for s in plan.scheduled)

    def test_critical_task_included_over_lower_priority_filler(self):
        """A critical 10-min task should beat out filler tasks for the limited budget."""
        critical = make_task(
            name="Insulin", task_type=TaskType.MEDICATION,
            priority=Priority.CRITICAL, duration=10, last_done=None,
        )
        filler = [make_task(name=f"F{i}", duration=40, last_done=None) for i in range(3)]
        plan   = generate_plan(make_pet(filler + [critical]), make_prefs(minutes=90), TODAY)
        assert "Insulin" in [s.task.name for s in plan.scheduled]

    def test_inactive_task_is_never_scheduled(self):
        t = make_task(last_done=None, is_active=False)
        plan = generate_plan(make_pet([t]), make_prefs(), TODAY)
        assert plan.scheduled == []

    def test_reasoning_strings_are_non_empty(self):
        t = make_task(last_done=None)
        plan = generate_plan(make_pet([t]), make_prefs(), TODAY)
        assert plan.overall_reasoning.strip()
        assert plan.scheduled[0].reason.strip()

    def test_plan_date_is_reflected_in_result(self):
        plan = generate_plan(make_pet([]), make_prefs(), TODAY)
        assert plan.plan_date == TODAY

    def test_multiple_daily_task_due_after_interval(self):
        """Task with 8h interval done 9h before midnight → should be due."""
        t = make_task(
            frequency=Frequency.MULTIPLE_DAILY,
            last_done=MIDNIGHT - timedelta(hours=9),
        )
        plan = generate_plan(make_pet([t]), make_prefs(), TODAY)
        assert len(plan.scheduled) == 1

    def test_multiple_daily_task_not_due_before_interval(self):
        """Task with 8h interval done 3h before midnight → not yet due."""
        t = make_task(
            frequency=Frequency.MULTIPLE_DAILY,
            last_done=MIDNIGHT - timedelta(hours=3),
        )
        plan = generate_plan(make_pet([t]), make_prefs(), TODAY)
        assert plan.scheduled == []

    def test_weekly_task_not_due_after_one_day(self):
        """A weekly task completed 25h ago is nowhere near its 168h interval."""
        t = make_task(frequency=Frequency.WEEKLY, last_done=MIDNIGHT - timedelta(hours=25))
        plan = generate_plan(make_pet([t]), make_prefs(), TODAY)
        assert plan.scheduled == []

    def test_shorter_tasks_fill_budget_more_efficiently(self):
        """When two tasks tie on score, the shorter one should be scheduled first."""
        long_task  = make_task(name="Long",  duration=60, last_done=None)
        short_task = make_task(name="Short", duration=20, last_done=None)
        # Both same priority and both never done → same score; shorter should lead
        plan = generate_plan(make_pet([long_task, short_task]), make_prefs(minutes=120), TODAY)
        names = [s.task.name for s in plan.scheduled]
        assert names.index("Short") < names.index("Long")
