from pawpal_system import (
    Owner,
    Pet,
    Scheduler,
    Task,
    detect_plan_conflicts,
    detect_preferred_time_conflicts,
    filter_tasks_with_pets,
    sort_pairs_by_preferred_time,
)


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", 8 * 60, "daily", completed=False)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Milo", species="dog", age=4, tasks=[])
    assert len(pet.tasks) == 0
    pet.tasks.append(Task("Dinner", 19 * 60 + 30, "daily"))
    assert len(pet.tasks) == 1


def test_weekly_recurrence_respects_weekday():
    mon_only = Task("Grooming", None, "weekly", weekly_weekday=0)
    assert mon_only.applies_for_weekday(0) is True
    assert mon_only.applies_for_weekday(2) is False
    daily = Task("Walk", 8 * 60, "daily")
    assert daily.applies_for_weekday(6) is True


def test_filter_tasks_by_pet_and_status():
    dog = Pet(name="A", species="dog", age=1, tasks=[Task("w", None, "daily")])
    cat = Pet(name="B", species="cat", age=1, tasks=[Task("c", None, "daily")])
    owner = Owner(pets=[dog, cat])
    dog.tasks[0].mark_complete()
    assert len(filter_tasks_with_pets(owner, status="open")) == 1
    assert len(filter_tasks_with_pets(owner, status="done")) == 1
    assert len(filter_tasks_with_pets(owner, pet=dog, status="all")) == 1


def test_sort_pairs_by_preferred_time_orders_none_last():
    pet = Pet("p", "dog", 1, [])
    t_late = Task("late", 12 * 60, "daily")
    t_none = Task("any", None, "daily")
    t_early = Task("early", 8 * 60, "daily")
    pairs = [(pet, t_none), (pet, t_late), (pet, t_early)]
    ordered = [t.description for _, t in sort_pairs_by_preferred_time(pairs)]
    assert ordered == ["early", "late", "any"]


def test_detect_preferred_time_conflicts():
    owner = Owner(
        pets=[
            Pet(
                "p",
                "dog",
                1,
                tasks=[
                    Task("a", 8 * 60, "daily", duration_minutes=60),
                    Task("b", 8 * 60 + 30, "daily", duration_minutes=30),
                ],
            )
        ]
    )
    conflicts = detect_preferred_time_conflicts(owner)
    assert len(conflicts) >= 1


def test_detect_plan_conflicts_finds_overlap():
    pet = Pet("p", "dog", 1, [])
    t1 = Task("a", None, "daily", duration_minutes=30)
    t2 = Task("b", None, "daily", duration_minutes=30)
    plan = [(pet, t1, 8 * 60), (pet, t2, 8 * 60 + 15)]
    assert len(detect_plan_conflicts(plan)) == 1


def test_scheduler_weekday_filters_weekly_tasks():
    pet = Pet("p", "dog", 1, tasks=[Task("weekly job", None, "weekly", weekly_weekday=2)])
    sched = Scheduler(owner=Owner(pets=[pet]))
    on_tuesday = sched.sortTasksByPriority(weekday=2)
    on_monday = sched.sortTasksByPriority(weekday=1)
    assert len(on_tuesday) == 1
    assert len(on_monday) == 0
