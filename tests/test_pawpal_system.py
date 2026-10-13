import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def make_plan(tasks, available_minutes=120):
    owner = Owner("Jordan", available_minutes=available_minutes)
    pet = Pet("Mochi", "dog", tasks=list(tasks))
    owner.add_pet(pet)
    return Scheduler(owner, pet).build_plan()


def titles(plan):
    return [item.task.title for item in plan.items]


def test_high_priority_chosen_over_low_when_time_is_short():
    plan = make_plan(
        [Task("Brushing", 20, "low"), Task("Meds", 20, "high")],
        available_minutes=20,
    )
    assert titles(plan) == ["Meds"]
    assert [task.title for task, _ in plan.skipped] == ["Brushing"]


def test_plan_never_exceeds_time_budget():
    tasks = [Task(f"Task {i}", 25, "medium") for i in range(10)]
    plan = make_plan(tasks, available_minutes=60)
    assert plan.total_minutes <= 60
    assert len(plan.items) == 2


def test_shorter_task_preferred_among_equal_priority():
    plan = make_plan(
        [Task("Long walk", 50, "high"), Task("Feeding", 10, "high")],
        available_minutes=40,
    )
    assert titles(plan) == ["Feeding"]


def test_preferred_time_places_task_in_that_slot():
    plan = make_plan([Task("Dinner", 10, "high", "evening")])
    assert plan.items[0].start.strftime("%H:%M") == "17:00"


def test_tasks_do_not_overlap():
    plan = make_plan(
        [
            Task("Walk", 30, "high", "morning"),
            Task("Breakfast", 10, "high", "morning"),
            Task("Play", 20, "medium"),
            Task("Brush", 15, "low", "afternoon"),
        ]
    )
    for earlier, later in zip(plan.items, plan.items[1:]):
        assert earlier.end <= later.start


def test_empty_task_list_gives_empty_plan():
    plan = make_plan([])
    assert plan.items == []
    assert plan.skipped == []
    assert "nothing scheduled" in plan.explain()


def test_every_scheduled_task_has_a_reason():
    plan = make_plan([Task("Walk", 30, "high"), Task("Play", 20, "low", "afternoon")])
    assert all(item.reason for item in plan.items)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"priority": "urgent"},
        {"duration_minutes": 0},
        {"preferred_time": "midnight"},
    ],
)
def test_invalid_task_values_are_rejected(kwargs):
    args = {"title": "Walk", "duration_minutes": 30, "priority": "high"}
    args.update(kwargs)
    with pytest.raises(ValueError):
        Task(**args)


def test_remove_task_by_title():
    pet = Pet("Mochi", "dog", tasks=[Task("Walk", 30, "high")])
    assert pet.remove_task("Walk") is True
    assert pet.remove_task("Walk") is False
    assert pet.tasks == []


def assert_no_overlaps(plan):
    for earlier, later in zip(plan.items, plan.items[1:]):
        assert earlier.end <= later.start


def test_overlapping_fixed_tasks_keep_higher_priority():
    plan = make_plan(
        [
            Task("Grooming", 30, "low", fixed_time="09:00"),
            Task("Vet visit", 45, "high", fixed_time="09:15"),
        ]
    )
    assert titles(plan) == ["Vet visit"]
    assert plan.skipped == [
        (plan.pet.tasks[0], "conflicts with Vet visit at 09:15–10:00")
    ]
    assert len(plan.conflicts) == 1
    assert "CONFLICT" in plan.explain()


def test_fixed_task_conflict_tie_keeps_first_listed():
    plan = make_plan(
        [
            Task("Meds", 30, "high", fixed_time="10:00"),
            Task("Vet visit", 10, "high", fixed_time="10:20"),
        ]
    )
    assert titles(plan) == ["Meds"]
    assert [task.title for task, _ in plan.skipped] == ["Vet visit"]


def test_flexible_task_pushed_after_fixed_task():
    plan = make_plan(
        [
            Task("Walk", 30, "medium", "morning"),
            Task("Vet visit", 30, "high", fixed_time="08:10"),
        ]
    )
    starts = {item.task.title: item.start.strftime("%H:%M") for item in plan.items}
    assert starts == {"Vet visit": "08:10", "Walk": "08:40"}
    assert titles(plan) == ["Vet visit", "Walk"]


def test_no_items_overlap_with_mixed_fixed_and_flexible_tasks():
    plan = make_plan(
        [
            Task("Breakfast", 10, "high", "morning"),
            Task("Walk", 30, "high", "morning"),
            Task("Meds", 5, "high", fixed_time="08:20"),
            Task("Vet visit", 30, "medium", fixed_time="08:30"),
            Task("Grooming", 20, "low", fixed_time="08:40"),
            Task("Play", 20, "medium"),
        ],
        available_minutes=240,
    )
    assert_no_overlaps(plan)
    assert [i.start for i in plan.items] == sorted(i.start for i in plan.items)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"fixed_time": "25:00"},
        {"fixed_time": "noon"},
        {"fixed_time": "09:00", "preferred_time": "morning"},
    ],
)
def test_invalid_fixed_time_is_rejected(kwargs):
    with pytest.raises(ValueError):
        Task("Vet visit", 30, "high", **kwargs)


def test_dropped_fixed_task_does_not_use_up_time_budget():
    # Grooming loses its conflict with the vet visit, so its 10 minutes
    # should stay available for Play.
    plan = make_plan(
        [
            Task("Vet visit", 45, "high", fixed_time="09:00"),
            Task("Grooming", 10, "medium", fixed_time="09:15"),
            Task("Play", 15, "low"),
        ],
        available_minutes=60,
    )
    assert sorted(titles(plan)) == ["Play", "Vet visit"]
    assert [task.title for task, _ in plan.skipped] == ["Grooming"]
