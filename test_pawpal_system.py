import pytest
from datetime import date, time, timedelta, datetime
from pawpal_system import Task, Pet, Owner, Scheduler, ScheduleEntry


def test_task_methods():
    task = Task(id="t1", description="Feed", duration_min=15, priority="high")
    
    assert not task.is_complete
    task.mark_complete()
    assert task.is_complete
    
    assert task.priority_score() == 3 * 10.0 / 15  # 2.0
    
    task_dict = task.to_dict()
    assert task_dict["id"] == "t1"
    assert task_dict["description"] == "Feed"
    assert task_dict["priority"] == "high"


def test_task_invalid_duration():
    with pytest.raises(ValueError, match="duration_min must be greater than zero"):
        Task(id="t2", description="Walk", duration_min=0, priority="medium")

    with pytest.raises(ValueError, match="duration_min must be greater than zero"):
        Task(id="t3", description="Brush", duration_min=-10, priority="low")

    with pytest.raises(ValueError, match="duration_min must be an integer"):
        Task(id="t1", description="Bath", duration_min='', priority="high")


def test_task_invalid_priority():
    with pytest.raises(ValueError, match="priority must be one of"):
        Task(id="t4", description="Walk", duration_min=15, priority="urgent")

    with pytest.raises(ValueError, match="priority must be one of"):
        Task(id="t5", description="Groom", duration_min=20, priority="unknown")


def test_task_mark_complete_idempotent():
    task = Task(id="t6", description="Check teeth", duration_min=10, priority="low")
    assert not task.is_complete

    task.mark_complete()
    assert task.is_complete

    task.mark_complete()
    assert task.is_complete


def test_task_to_dict_immutability():
    task = Task(id="t7", description="Play", duration_min=20, priority="medium")
    task_dict = task.to_dict()

    # ensure required fields exist
    expected_keys = {"id", "description", "duration_min", "priority", "frequency", "constraints", "is_complete"}
    assert set(task_dict.keys()) == expected_keys
    assert task_dict["id"] == "t7"
    assert task_dict["description"] == "Play"

    # mutate returned dict and verify original object is unchanged
    task_dict["description"] = "Naughty"
    task_dict["is_complete"] = True
    assert task.description == "Play"
    assert not task.is_complete


def test_task_priority_score_ordering():
    # create tasks with different priority/duration combos
    high_short = Task(id="hs", description="High short", duration_min=10, priority="high")  # score: 3*10/10 = 3.0
    high_long = Task(id="hl", description="High long", duration_min=30, priority="high")    # score: 3*10/30 = 1.0
    med_short = Task(id="ms", description="Med short", duration_min=10, priority="medium")  # score: 2*10/10 = 2.0
    low_any = Task(id="la", description="Low any", duration_min=20, priority="low")        # score: 1*10/20 = 0.5

    # assert relative ordering: high/short > med/short > high/long > low
    assert high_short.priority_score() > med_short.priority_score()
    assert med_short.priority_score() > high_long.priority_score()
    assert high_long.priority_score() > low_any.priority_score()

    # test sorting by score descending (higher score first)
    tasks = [low_any, high_long, med_short, high_short]
    sorted_tasks = sorted(tasks, key=lambda t: t.priority_score(), reverse=True)
    assert sorted_tasks[0] == high_short
    assert sorted_tasks[1] == med_short
    assert sorted_tasks[2] == high_long
    assert sorted_tasks[3] == low_any


def test_task_frequency_validation():
    # valid frequencies
    Task(id="fd", description="Feed daily", duration_min=15, priority="high", frequency="daily")
    Task(id="fw", description="Feed weekly", duration_min=15, priority="high", frequency="weekly")
    Task(id="fo", description="Feed once", duration_min=15, priority="high", frequency="once")

    # invalid frequency
    with pytest.raises(ValueError, match="frequency must be one of"):
        Task(id="fi", description="Feed invalid", duration_min=15, priority="high", frequency="monthly")

def test_pet_add_task():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    
    pet.add_task(t1)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].id == "t1"


def test_pet_remove_task():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    t2 = Task(id="t2", description="Play", duration_min=30, priority="medium")
    
    pet.add_task(t1)
    pet.add_task(t2)
    
    assert pet.remove_task("t1") is True
    assert len(pet.tasks) == 1
    assert pet.tasks[0].id == "t2"
    
    assert pet.remove_task("nonexistent") is False


def test_pet_edit_task():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    
    pet.add_task(t1)
    assert pet.edit_task("t1", duration_min=20) is True
    assert pet.tasks[0].duration_min == 20
    
    assert pet.edit_task("nonexistent", duration_min=25) is False


def test_pet_get_pending_tasks():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    t2 = Task(id="t2", description="Play", duration_min=30, priority="medium")
    
    pet.add_task(t1)
    pet.add_task(t2)
    
    pending = pet.get_pending_tasks()
    assert len(pending) == 2
    
    t1.mark_complete()
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].id == "t2"


def test_pet_get_tasks_by_priority():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    t2 = Task(id="t2", description="Play", duration_min=30, priority="low")
    t3 = Task(id="t3", description="Groom", duration_min=20, priority="medium")
    
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    
    prioritized = pet.get_tasks_by_priority()
    assert len(prioritized) == 3
    assert prioritized[0].priority == "high"
    assert prioritized[1].priority == "medium"
    assert prioritized[2].priority == "low"


def test_owner_task_aggregation():
    owner = Owner(id="o1", name="Jordan", available_time_min=90)
    pet1 = Pet(id="p1", name="Mochi", species="cat", age=3)
    pet2 = Pet(id="p2", name="Rex", species="dog", age=6)
    
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    t2 = Task(id="t2", description="Walk", duration_min=30, priority="medium")
    t3 = Task(id="t3", description="Brush", duration_min=10, priority="low")

    pet1.add_task(t1)
    pet2.add_task(t2)
    pet2.add_task(t3)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 3

    assert owner.total_time_needed() == 55


def test_owner_pet_remove():
    owner = Owner(id="o1", name="Jordan", available_time_min=90)
    pet1 = Pet(id="p1", name="Mochi", species="cat", age=3)
    pet2 = Pet(id="p2", name="Rex", species="dog", age=6)

    owner.add_pet(pet1)
    owner.add_pet(pet2)
    assert len(owner.pets) == 2

    assert owner.remove_pet("p1") is True
    assert len(owner.pets) == 1
    assert owner.remove_pet("invalid") is False


def test_scheduler_build_daily_plan():
    owner = Owner(id="o1", name="Jordan", available_time_min=40)
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    t2 = Task(id="t2", description="Play", duration_min=30, priority="medium")
    t3 = Task(id="t3", description="Brush", duration_min=10, priority="low")

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, date=date(2026,3,31))
    schedule = scheduler.build_daily_plan(start_time=time(8,0))

    assert len(schedule) == 2
    assert schedule[0].task.description == "Feed"
    assert schedule[1].task.description == "Brush"
    assert len(scheduler.overflow_tasks) == 1
    assert scheduler.overflow_tasks[0].description == "Play"

    explanation = scheduler.explain_decision()
    assert "Included tasks:" in explanation
    assert "Overflow tasks:" in explanation
    assert "Reasoning:" in explanation


def make_scheduler(available_time=120):
    """Helper to build a scheduler with two pets and three tasks."""
    owner = Owner(id="o1", name="Jordan", available_time_min=available_time)
    pet1 = Pet(id="p1", name="Buddy", species="dog", age=3)
    pet2 = Pet(id="p2", name="Whiskers", species="cat", age=2)
    t1 = Task(id="t1", description="Morning walk", duration_min=30, priority="high")
    t2 = Task(id="t2", description="Feed breakfast", duration_min=15, priority="medium")
    t3 = Task(id="t3", description="Playtime", duration_min=45, priority="low")
    pet1.add_task(t1)
    pet1.add_task(t2)
    pet2.add_task(t3)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    scheduler = Scheduler(owner=owner, date=date(2026, 3, 31))
    scheduler.build_daily_plan(start_time=time(8, 0))
    return scheduler, owner, pet1, pet2, t1, t2, t3


# --- sort_by_time ---

def test_sort_by_time_returns_ascending_order():
    scheduler, *_ = make_scheduler()
    sorted_entries = scheduler.sort_by_time()
    starts = [e.start for e in sorted_entries]
    assert starts == sorted(starts)


def test_sort_by_time_empty_schedule():
    owner = Owner(id="o1", name="Jordan", available_time_min=60)
    scheduler = Scheduler(owner=owner, date=date(2026, 3, 31))
    assert scheduler.sort_by_time() == []


# --- filter_tasks ---

def test_filter_tasks_by_pet():
    _, owner, pet1, _, t1, t2, t3 = make_scheduler()
    result = owner.filter_tasks(pet_id="p1")
    assert all(t in result for t in [t1, t2])
    assert t3 not in result


def test_filter_tasks_by_status_pending():
    _, owner, _, _, t1, t2, t3 = make_scheduler()
    t1.mark_complete()
    pending = owner.filter_tasks(status="pending")
    assert t1 not in pending
    assert t2 in pending
    assert t3 in pending


def test_filter_tasks_by_status_complete():
    _, owner, _, _, t1, t2, _ = make_scheduler()
    t1.mark_complete()
    complete = owner.filter_tasks(status="complete")
    assert t1 in complete
    assert t2 not in complete


def test_filter_tasks_combined_pet_and_status():
    _, owner, _, _, t1, t2, _ = make_scheduler()
    t1.mark_complete()
    result = owner.filter_tasks(pet_id="p1", status="pending")
    assert result == [t2]


def test_filter_tasks_no_filters_returns_all():
    _, owner, _, _, t1, t2, t3 = make_scheduler()
    result = owner.filter_tasks()
    assert len(result) == 3
    assert t1 in result
    assert t2 in result
    assert t3 in result


# --- is_due (recurring task gating) ---

def test_is_due_daily_not_yet_scheduled():
    t = Task(id="t1", description="Walk", duration_min=20, priority="low", frequency="daily")
    assert t.is_due(date.today()) is True


def test_is_due_daily_already_scheduled_today():
    t = Task(id="t1", description="Walk", duration_min=20, priority="low", frequency="daily",
             last_scheduled=date.today())
    assert t.is_due(date.today()) is False


def test_is_due_weekly_not_yet_due():
    t = Task(id="t1", description="Bath", duration_min=20, priority="low", frequency="weekly",
             last_scheduled=date.today() - timedelta(days=3))
    assert t.is_due(date.today()) is False


def test_is_due_weekly_now_due():
    t = Task(id="t1", description="Bath", duration_min=20, priority="low", frequency="weekly",
             last_scheduled=date.today() - timedelta(days=7))
    assert t.is_due(date.today()) is True


def test_is_due_once_not_complete():
    t = Task(id="t1", description="Vet", duration_min=60, priority="high", frequency="once")
    assert t.is_due(date.today()) is True


def test_is_due_once_already_complete():
    t = Task(id="t1", description="Vet", duration_min=60, priority="high", frequency="once")
    t.mark_complete()
    assert t.is_due(date.today()) is False


def test_weekly_task_excluded_from_schedule_when_not_due():
    owner = Owner(id="o1", name="Jordan", available_time_min=120)
    pet = Pet(id="p1", name="Buddy", species="dog", age=3)
    weekly_task = Task(id="t1", description="Bath", duration_min=20, priority="high", frequency="weekly",
                       last_scheduled=date.today() - timedelta(days=3))
    pet.add_task(weekly_task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, date=date.today())
    scheduler.build_daily_plan()
    assert len(scheduler.schedule) == 0


# --- detect_conflicts ---

def test_detect_conflicts_none_in_normal_schedule():
    scheduler, *_ = make_scheduler()
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_catches_overlap():
    scheduler, _, pet1, *_ = make_scheduler()
    # inject an entry that overlaps the first scheduled entry
    first = scheduler.schedule[0]
    overlap_task = Task(id="overlap", description="Overlap", duration_min=10, priority="low")
    overlap_entry = ScheduleEntry(
        task=overlap_task, pet=pet1,
        start=first.start,
        end=first.start + timedelta(minutes=10)
    )
    scheduler.schedule.append(overlap_entry)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    tasks_in_conflict = {conflicts[0][0].task.id, conflicts[0][1].task.id}
    assert "overlap" in tasks_in_conflict


def test_detect_conflicts_adjacent_entries_do_not_conflict():
    scheduler, _, pet1, *_ = make_scheduler()
    # build two back-to-back entries with no gap — should not conflict
    start_a = datetime(2026, 3, 31, 8, 0)
    end_a = datetime(2026, 3, 31, 8, 30)
    start_b = end_a  # starts exactly when a ends
    end_b = datetime(2026, 3, 31, 9, 0)
    t_a = Task(id="a", description="A", duration_min=30, priority="low")
    t_b = Task(id="b", description="B", duration_min=30, priority="low")
    scheduler.schedule = [
        ScheduleEntry(task=t_a, pet=pet1, start=start_a, end=end_a),
        ScheduleEntry(task=t_b, pet=pet1, start=start_b, end=end_b),
    ]
    assert scheduler.detect_conflicts() == []


# --- warn_conflicts ---

def test_warn_conflicts_clean_schedule_returns_empty():
    scheduler, *_ = make_scheduler()
    assert scheduler.warn_conflicts() == []


def test_warn_conflicts_returns_string_warnings():
    scheduler, _, pet1, *_ = make_scheduler()
    first = scheduler.schedule[0]
    overlap_task = Task(id="overlap", description="Overlap", duration_min=10, priority="low")
    overlap_entry = ScheduleEntry(
        task=overlap_task, pet=pet1,
        start=first.start,
        end=first.start + timedelta(minutes=10)
    )
    scheduler.schedule.append(overlap_entry)
    warnings = scheduler.warn_conflicts()
    assert len(warnings) == 1
    assert "WARNING" in warnings[0]
    assert "Overlap" in warnings[0] or first.task.description in warnings[0]


# --- next_occurrence / complete_task ---

def test_next_occurrence_daily_creates_new_task():
    t = Task(id="t1", description="Walk", duration_min=20, priority="high", frequency="daily")
    next_t = t.next_occurrence(new_id="t1_next")
    assert next_t is not None
    assert next_t.id == "t1_next"
    assert next_t.description == "Walk"
    assert next_t.frequency == "daily"
    assert next_t.last_scheduled == date.today()
    assert next_t.is_complete is False


def test_next_occurrence_weekly_creates_new_task():
    t = Task(id="t1", description="Bath", duration_min=20, priority="low", frequency="weekly")
    next_t = t.next_occurrence(new_id="t1_next")
    assert next_t is not None
    assert next_t.frequency == "weekly"
    assert next_t.last_scheduled == date.today()


def test_next_occurrence_once_returns_none():
    t = Task(id="t1", description="Vet", duration_min=60, priority="high", frequency="once")
    assert t.next_occurrence(new_id="t1_next") is None


def test_next_occurrence_due_date_is_correct():
    t = Task(id="t1", description="Walk", duration_min=20, priority="low", frequency="daily")
    next_t = t.next_occurrence(new_id="t1_next")
    # last_scheduled = today means is_due returns False today, True tomorrow
    assert next_t.is_due(date.today()) is False
    assert next_t.is_due(date.today() + timedelta(days=1)) is True


def test_complete_task_marks_done_and_queues_next():
    scheduler, _, pet1, _, t1, *_ = make_scheduler()
    tasks_before = len(pet1.tasks)
    next_task = scheduler.complete_task(t1.id)

    assert t1.is_complete is True
    assert next_task is not None
    assert len(pet1.tasks) == tasks_before + 1
    assert pet1.tasks[-1].id == f"{t1.id}_next"


def test_complete_task_once_does_not_queue_next():
    owner = Owner(id="o1", name="Jordan", available_time_min=120)
    pet = Pet(id="p1", name="Buddy", species="dog", age=3)
    t = Task(id="vet1", description="Vet checkup", duration_min=60, priority="high", frequency="once")
    pet.add_task(t)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, date=date.today())
    scheduler.build_daily_plan()
    next_task = scheduler.complete_task("vet1")
    assert t.is_complete is True
    assert next_task is None
    assert len(pet.tasks) == 1  # no new task added


def test_complete_task_unknown_id_returns_none():
    scheduler, *_ = make_scheduler()
    assert scheduler.complete_task("nonexistent") is None

def test_all_tasks_exceed_available_time():
    owner = Owner(id="o1", name="Jordan", available_time_min=30)
    pet = Pet(id="p1", name="Buddy", species="dog", age=3)
    t1 = Task(id="t1", description="Long walk", duration_min=60, priority="high")
    t2 = Task(id="t2", description="Long bath", duration_min=45, priority="medium")
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, date=date.today())
    scheduler.build_daily_plan()

    assert len(scheduler.schedule) == 0
    assert len(scheduler.overflow_tasks) == 2


def test_pet_with_no_tasks():
    owner = Owner(id = "o1", name = "Jordan", available_time_min= 60)
    pet = Pet(id = "p1", name = "Buddy", species="dog", age = 3)

    # no add_task calls
    owner.add_pet(pet)
    scheduler = Scheduler(owner = owner, date = date.today())
    scheduler.build_daily_plan()

    assert len(scheduler.schedule) == 0
    assert len(scheduler.overflow_tasks) == 0

def test_owner_with_no_pets():
    owner = Owner(id = "o1", name = "Michael", available_time_min= 120)
    all_tasks = owner.get_all_tasks()
    
    assert len(all_tasks) == 0
    assert owner.total_time_needed() == 0

def test_detect_conflicts_same_start_time():
    owner = Owner(id = "o1", name = "Jordan", available_time_min= 120)
    pet = Pet(id = "p1", name = "Buddy", species="dog", age = 3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner = owner, date = date.today())

    # manullay place two entries at the same start time 
    t1 = Task(id = "t1", description="Walk", duration_min= 30, priority="high")
    t2 = Task(id = "t2", description="Feed", duration_min=45, priority = "medium")

    same_start = datetime(2026, 4, 1, 1, 8, 0)

    scheduler.schedule = [
    ScheduleEntry(task=t1, pet=pet, start=same_start, end=same_start + timedelta(minutes=30)),
    ScheduleEntry(task=t2, pet=pet, start=same_start, end=same_start + timedelta(minutes=45)),
    ]

    assert len(scheduler.detect_conflicts()) == 1

    

def test_complete_task_no_duplicate_on_rerun():
    owner = Owner(id="o1", name="Jordan", available_time_min=120)
    pet = Pet(id="p1", name="Buddy", species="dog", age=3)
    t1 = Task(id="t1", description="Walk", duration_min=30, priority="high", frequency="daily")
    pet.add_task(t1)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, date=date.today())
    scheduler.build_daily_plan()

    # complete the task — next occurrence should be queued
    scheduler.complete_task("t1")
    assert len(pet.tasks) == 2 # original + next occurrence

    # re-run the plan — next occurrence is not due today
    scheduler.build_daily_plan()
    scheduled_ids = [e.task.id for e in scheduler.schedule]
    assert "t1_next" not in scheduled_ids  # should not be scheduled today
    assert len(pet.tasks) == 2 # still only one next occurrence, no duplicate


if __name__ == "__main__":
    pytest.main(["-q"])