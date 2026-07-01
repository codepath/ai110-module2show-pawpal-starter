"""Test suite for the PawPal+ pet scheduling system.

Covers sorting, filtering, recurring tasks, and conflict detection —
happy paths plus edge cases. Run with:  pytest tests/test_pawpal.py
"""

from datetime import date, timedelta

import pytest

from pawpal_system import PetTask, Constraints, Pet, Owner, DailyPlan


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def make_owner(available_minutes=120, preferred_start="08:00", **kwargs):
    return Owner("Alice", Constraints(available_minutes, preferred_start, **kwargs))


# ==========================================================================
# 0. SMOKE TESTS (original)
# ==========================================================================

def test_mark_complete_changes_task_status():
    task = PetTask("Walk Buddy", 30, "high")
    assert task.status == "pending"

    task.mark_complete()

    assert task.status == "completed"


def test_adding_task_increases_pet_task_count():
    pet = Pet("Buddy", "Dog")
    assert len(pet.tasks) == 0

    pet.add_task(PetTask("Feed Buddy", 15, "high"))

    assert len(pet.tasks) == 1


# ==========================================================================
# 1. SORTING
# ==========================================================================

def test_sort_by_time_happy_path():                    # S1
    a = PetTask("a", 10, time="09:00")
    b = PetTask("b", 10, time="08:00")
    c = PetTask("c", 10, time="12:00")
    assert [t.title for t in DailyPlan.sort_by_time([a, b, c])] == ["b", "a", "c"]


def test_sort_by_time_untimed_last():                  # S2
    a = PetTask("a", 10, time="08:15")
    b = PetTask("b", 10, time=None)
    c = PetTask("c", 10, time="07:00")
    assert [t.title for t in DailyPlan.sort_by_time([a, b, c])] == ["c", "a", "b"]


def test_sort_by_time_empty():                         # S3
    assert DailyPlan.sort_by_time([]) == []


def test_sort_by_time_all_untimed_stable():            # S4
    a = PetTask("a", 10, time=None)
    b = PetTask("b", 10, time=None)
    c = PetTask("c", 10, time=None)
    assert [t.title for t in DailyPlan.sort_by_time([a, b, c])] == ["a", "b", "c"]


def test_sort_by_time_duplicate_times_stable():        # S5
    a = PetTask("a", 10, time="08:00")
    b = PetTask("b", 10, time="08:00")
    assert [t.title for t in DailyPlan.sort_by_time([a, b])] == ["a", "b"]


def test_build_orders_by_priority():                   # S6
    tasks = [
        PetTask("low", 10, "low"),
        PetTask("high", 10, "high"),
        PetTask("medium", 10, "medium"),
    ]
    plan = DailyPlan.build(tasks, Constraints(120), date.today())
    assert [t.title for _, _, t in plan.scheduled] == ["high", "medium", "low"]


def test_build_respects_preferred_order():             # S7
    tasks = [
        PetTask("Walk", 10, "high", category="exercise"),
        PetTask("Pills", 10, "high", category="meds"),
    ]
    constraints = Constraints(120, preferred_order=["meds"])
    plan = DailyPlan.build(tasks, constraints, date.today())
    assert [t.title for _, _, t in plan.scheduled] == ["Pills", "Walk"]


def test_build_tie_breaks_by_duration():               # S8
    tasks = [PetTask("long", 30, "high"), PetTask("short", 10, "high")]
    plan = DailyPlan.build(tasks, Constraints(120), date.today())
    assert [t.title for _, _, t in plan.scheduled] == ["short", "long"]


# ==========================================================================
# 2. FILTERING
# ==========================================================================

def test_tasks_by_status_pending():                    # F1
    owner = make_owner()
    pet = Pet("Buddy", "Dog")
    owner.add_pet(pet)
    done = PetTask("done", 10, "high")
    pet.add_task(done)
    pet.add_task(PetTask("todo", 10, "high"))
    done.mark_complete()
    assert [t.title for t in owner.tasks_by_status("pending")] == ["todo"]


def test_tasks_by_status_completed():                  # F2
    owner = make_owner()
    pet = Pet("Buddy", "Dog")
    owner.add_pet(pet)
    done = PetTask("done", 10, "high")
    pet.add_task(done)
    done.mark_complete()
    assert [t.title for t in owner.tasks_by_status("completed")] == ["done"]


def test_tasks_for_pet():                              # F3
    owner = make_owner()
    pet = Pet("Whiskers", "Cat")
    owner.add_pet(pet)
    pet.add_task(PetTask("Feed", 10, "high"))
    pet.add_task(PetTask("Play", 20, "medium"))
    assert [t.title for t in owner.tasks_for("Whiskers")] == ["Feed", "Play"]


def test_tasks_for_pet_with_status():                  # F4
    owner = make_owner()
    pet = Pet("Buddy", "Dog")
    owner.add_pet(pet)
    done = PetTask("Feed", 10, "high")
    pet.add_task(done)
    pet.add_task(PetTask("Walk", 30, "high"))
    done.mark_complete()
    assert [t.title for t in owner.tasks_for("Buddy", status="pending")] == ["Walk"]


def test_tasks_for_unknown_pet_is_empty():             # F5
    assert make_owner().tasks_for("Ghost") == []


def test_tasks_for_pet_with_no_tasks():                # F6
    owner = make_owner()
    owner.add_pet(Pet("Buddy", "Dog"))
    assert owner.tasks_for("Buddy") == []


def test_tasks_by_status_no_matches():                 # F7
    owner = make_owner()
    pet = Pet("Buddy", "Dog")
    owner.add_pet(pet)
    pet.add_task(PetTask("todo", 10, "high"))
    assert owner.tasks_by_status("completed") == []


def test_all_tasks_empty_owner():                      # F8
    assert make_owner().all_tasks() == []


# ==========================================================================
# 3. RECURRING TASKS
# ==========================================================================

def test_daily_recurrence_spawns_next():               # R1
    t = PetTask("meds", 5, "high", frequency="daily", due_date=date(2026, 7, 1))
    nxt = t.mark_complete()
    assert t.status == "completed"
    assert nxt is not None
    assert nxt.due_date == date(2026, 7, 2)
    assert nxt.status == "pending"


def test_weekly_recurrence_spawns_next():              # R2
    t = PetTask("bath", 20, "medium", frequency="weekly", due_date=date(2026, 7, 1))
    nxt = t.mark_complete()
    assert nxt is not None
    assert nxt.due_date == date(2026, 7, 8)


def test_no_duplicate_on_recomplete():                 # R3
    t = PetTask("meds", 5, "high", frequency="daily", due_date=date(2026, 7, 1))
    t.mark_complete()
    assert t.mark_complete() is None


def test_non_recurring_spawns_nothing():               # R4
    t = PetTask("Walk", 30, "high")
    assert t.mark_complete() is None
    assert t.status == "completed"


def test_recurrence_without_due_date_uses_today():     # R5
    t = PetTask("meds", 5, "high", frequency="daily")
    nxt = t.mark_complete()
    assert nxt is not None
    assert nxt.due_date == date.today() + timedelta(days=1)


def test_invalid_frequency_raises():                   # R6
    with pytest.raises(ValueError):
        PetTask("x", 5, frequency="monthly")


def test_next_occurrence_not_auto_attached():          # R7
    pet = Pet("Buddy", "Dog")
    t = PetTask("meds", 5, "high", frequency="daily", due_date=date(2026, 7, 1))
    pet.add_task(t)
    assert len(pet.tasks) == 1
    t.mark_complete()
    # mark_complete() returns the next instance but does NOT attach it.
    assert len(pet.tasks) == 1


# ==========================================================================
# 4. CONFLICT DETECTION
# ==========================================================================

def test_no_conflicts_distinct_times():                # C1
    pet = Pet("Buddy", "Dog")
    pet.add_task(PetTask("Feed", 10, "high", time="08:00"))
    pet.add_task(PetTask("Walk", 30, "high", time="17:30"))
    assert DailyPlan.detect_conflicts([pet]) == []


def test_same_pet_conflict():                          # C2
    pet = Pet("Buddy", "Dog")
    pet.add_task(PetTask("Walk", 30, "high", time="17:30"))
    pet.add_task(PetTask("Brush", 10, "low", time="17:30"))
    warnings = DailyPlan.detect_conflicts([pet])
    assert len(warnings) == 1
    assert "17:30" in warnings[0]
    assert "same pet" in warnings[0]


def test_cross_pet_conflict():                         # C3
    p1 = Pet("Buddy", "Dog")
    p1.add_task(PetTask("Walk", 30, "high", time="09:00"))
    p2 = Pet("Mohsen", "Parrot")
    p2.add_task(PetTask("Feed", 10, "high", time="09:00"))
    warnings = DailyPlan.detect_conflicts([p1, p2])
    assert len(warnings) == 1
    assert "different pets" in warnings[0]


def test_untimed_tasks_never_conflict():               # C4
    pet = Pet("Buddy", "Dog")
    pet.add_task(PetTask("a", 10, "high", time=None))
    pet.add_task(PetTask("b", 10, "high", time=None))
    assert DailyPlan.detect_conflicts([pet]) == []


def test_conflict_empty_pets():                        # C5
    assert DailyPlan.detect_conflicts([]) == []


def test_conflict_pets_with_no_tasks():                # C6
    assert DailyPlan.detect_conflicts([Pet("Buddy", "Dog")]) == []


def test_three_way_conflict_single_warning():          # C7
    pet = Pet("Buddy", "Dog")
    for title in ("a", "b", "c"):
        pet.add_task(PetTask(title, 10, "high", time="08:00"))
    warnings = DailyPlan.detect_conflicts([pet])
    assert len(warnings) == 1
    assert all(t in warnings[0] for t in ("a", "b", "c"))


def test_conflicts_sorted_by_time():                   # C8
    pet = Pet("Buddy", "Dog")
    pet.add_task(PetTask("late1", 10, "high", time="17:30"))
    pet.add_task(PetTask("late2", 10, "high", time="17:30"))
    pet.add_task(PetTask("early1", 10, "high", time="09:00"))
    pet.add_task(PetTask("early2", 10, "high", time="09:00"))
    warnings = DailyPlan.detect_conflicts([pet])
    assert len(warnings) == 2
    assert "09:00" in warnings[0]
    assert "17:30" in warnings[1]


def test_detect_conflicts_never_raises():              # C9
    pet = Pet("Buddy", "Dog")
    pet.add_task(PetTask("a", 10, "high", time="08:00"))
    pet.add_task(PetTask("b", 10, "high", time="08:00"))
    result = DailyPlan.detect_conflicts([pet])
    assert isinstance(result, list)
    assert all(isinstance(w, str) for w in result)
