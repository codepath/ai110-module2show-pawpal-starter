import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task
from pawpal_system import Owner, Scheduler


def test_mark_complete_changes_task_status():
    task = Task(task_id="t1", title="Morning Walk", duration_minutes=20)
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Jack", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(task_id="t1", title="Morning Walk", duration_minutes=20))
    assert len(pet.get_tasks()) == 1


def test_sort_tasks_by_time_orders_morning_before_evening():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="evening-task",
            title="Evening Walk",
            duration_minutes=20,
            preferred_time="evening",
        )
    )
    pet.add_task(
        Task(
            task_id="morning-task",
            title="Breakfast",
            duration_minutes=10,
            preferred_time="morning",
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    sorted_tasks = scheduler.sort_tasks_by_time()

    assert [task.task_id for task in sorted_tasks] == ["morning-task", "evening-task"]


def test_filter_tasks_by_pet_and_status_returns_only_pending_for_pet():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")

    dog_done = Task(task_id="dog-done", title="Done", duration_minutes=5)
    dog_done.mark_complete()
    dog_pending = Task(task_id="dog-pending", title="Pending", duration_minutes=5)
    cat_pending = Task(task_id="cat-pending", title="Cat Pending", duration_minutes=5)

    dog.add_task(dog_done)
    dog.add_task(dog_pending)
    cat.add_task(cat_pending)
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    filtered = scheduler.filter_tasks_by_pet_status(pet_name="Jack", status="pending")

    assert [task.task_id for task in filtered] == ["dog-pending"]


def test_mark_task_complete_creates_next_daily_occurrence():
    owner = Owner(name="Ben", available_minutes_per_day=20)
    pet = Pet(name="Jack", species="dog")
    recurring = Task(
        task_id="daily-med",
        title="Medication",
        duration_minutes=5,
        frequency="daily",
    )
    pet.add_task(recurring)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    completion_date = date.today()
    next_task = scheduler.mark_task_complete("daily-med", completed_on=completion_date)

    assert recurring.is_completed is True
    assert next_task is not None
    assert next_task.task_id.startswith("daily-med-next-")
    assert next_task.is_completed is False
    assert next_task.due_date == completion_date + timedelta(days=1)

    scheduled_today = scheduler.generate_schedule(day_index=0)
    scheduled_tomorrow = scheduler.generate_schedule(day_index=1)

    assert [task.task_id for task in scheduled_today] == []
    assert [task.task_id for task in scheduled_tomorrow] == [next_task.task_id]


def test_conflict_detection_skips_overlapping_tasks():
    owner = Owner(name="Ben", available_minutes_per_day=60, max_tasks_per_day=5)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="task-a",
            title="Task A",
            duration_minutes=30,
            priority="high",
            start_minute=60,
        )
    )
    pet.add_task(
        Task(
            task_id="task-b",
            title="Task B",
            duration_minutes=30,
            priority="high",
            start_minute=75,
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduled = scheduler.generate_schedule()

    scheduled_ids = {task.task_id for task in scheduled}
    assert len(scheduled_ids) == 1
    assert scheduled_ids in ({"task-a"}, {"task-b"})

    conflict_pairs = scheduler.detect_conflicts(owner.get_all_tasks())
    assert len(conflict_pairs) == 1


def test_next_available_slot_mode_reschedules_conflicting_task():
    owner = Owner(name="Ben", available_minutes_per_day=120, max_tasks_per_day=5)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="task-a",
            title="Task A",
            duration_minutes=30,
            priority="high",
            start_minute=60,
        )
    )
    pet.add_task(
        Task(
            task_id="task-b",
            title="Task B",
            duration_minutes=30,
            priority="high",
            start_minute=75,
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduled = scheduler.generate_schedule(enable_next_available_slot=True)

    assert [task.task_id for task in scheduled] == ["task-a", "task-b"]
    assert pet.get_task_by_id("task-b").start_minute == 90
    assert "next available slot" in scheduler.selection_reasons["task-b"].lower()


def test_next_available_slot_mode_skips_when_no_space_left_in_day():
    owner = Owner(name="Ben", available_minutes_per_day=180, max_tasks_per_day=5)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="late-task-a",
            title="Late Task A",
            duration_minutes=60,
            priority="high",
            start_minute=1380,
        )
    )
    pet.add_task(
        Task(
            task_id="late-task-b",
            title="Late Task B",
            duration_minutes=60,
            priority="high",
            start_minute=1410,
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduled = scheduler.generate_schedule(enable_next_available_slot=True)

    scheduled_ids = [task.task_id for task in scheduled]
    assert scheduled_ids == ["late-task-a"]
    assert any(task.task_id == "late-task-b" for task in scheduler.unscheduled_tasks)


def test_rank_tasks_sorts_by_priority_before_time():
    owner = Owner(name="Ben", available_minutes_per_day=120)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="low-early",
            title="Low Early",
            duration_minutes=10,
            priority="low",
            time="08:00",
        )
    )
    pet.add_task(
        Task(
            task_id="high-later",
            title="High Later",
            duration_minutes=10,
            priority="high",
            time="10:00",
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    ranked = scheduler.rank_tasks()

    assert [task.task_id for task in ranked] == ["high-later", "low-early"]


def test_rank_tasks_uses_time_when_priority_matches():
    owner = Owner(name="Ben", available_minutes_per_day=120)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="high-late",
            title="High Late",
            duration_minutes=10,
            priority="high",
            time="11:30",
        )
    )
    pet.add_task(
        Task(
            task_id="high-early",
            title="High Early",
            duration_minutes=10,
            priority="high",
            time="09:15",
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    ranked = scheduler.rank_tasks()

    assert [task.task_id for task in ranked] == ["high-early", "high-late"]


def test_sort_by_time_orders_hhmm_strings_correctly():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(Task(task_id="t-late", title="Late", duration_minutes=10, time="18:30"))
    pet.add_task(Task(task_id="t-early", title="Early", duration_minutes=10, time="07:15"))
    pet.add_task(Task(task_id="t-mid", title="Mid", duration_minutes=10, time="12:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    sorted_tasks = scheduler.sort_by_time()

    assert [task.task_id for task in sorted_tasks] == ["t-early", "t-mid", "t-late"]


def test_filter_by_alias_filters_completed_tasks_for_specific_pet():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")

    done_task = Task(task_id="dog-done", title="Done", duration_minutes=5)
    done_task.mark_complete()
    dog.add_task(done_task)
    dog.add_task(Task(task_id="dog-pending", title="Pending", duration_minutes=5))
    cat.add_task(Task(task_id="cat-done", title="Cat Done", duration_minutes=5, is_completed=True))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    filtered = scheduler.filter_by(pet_name="Jack", status="completed")

    assert [task.task_id for task in filtered] == ["dog-done"]


def test_get_conflict_warnings_returns_messages_without_crashing():
    owner = Owner(name="Ben", available_minutes_per_day=120, max_tasks_per_day=10)
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")

    dog.add_task(Task(task_id="dog-a", title="Dog Task A", duration_minutes=30, time="09:00"))
    dog.add_task(Task(task_id="dog-b", title="Dog Task B", duration_minutes=20, time="09:15"))
    cat.add_task(Task(task_id="cat-a", title="Cat Task A", duration_minutes=30, time="09:10"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    warnings = scheduler.get_conflict_warnings()

    assert len(warnings) >= 2
    assert any("same pet" in warning for warning in warnings)
    assert any("different pets" in warning for warning in warnings)


# ============================================================================
# TASK VALIDATION TESTS (Happy Paths & Edge Cases)
# ============================================================================

def test_task_creation_with_valid_attributes():
    """Happy path: Create a valid task with all required attributes."""
    task = Task(
        task_id="t1",
        title="Morning Walk",
        duration_minutes=30,
        priority="high",
        category="exercise",
        frequency="daily"
    )
    assert task.task_id == "t1"
    assert task.title == "Morning Walk"
    assert task.duration_minutes == 30
    assert task.is_completed is False


def test_task_initialization_normalizes_whitespace():
    """Task attributes with leading/trailing whitespace are stripped."""
    task = Task(
        task_id="  t1  ",
        title="  Walk  ",
        duration_minutes=20,
        priority="  HIGH  ",
        category="  EXERCISE  "
    )
    assert task.task_id == "t1"
    assert task.title == "Walk"
    assert task.priority == "high"
    assert task.category == "exercise"


def test_task_empty_task_id_raises_error():
    """Edge case: Empty task_id raises ValueError."""
    try:
        Task(task_id="", title="Walk", duration_minutes=20)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "task_id cannot be empty" in str(e)


def test_task_empty_title_raises_error():
    """Edge case: Empty title raises ValueError."""
    try:
        Task(task_id="t1", title="", duration_minutes=20)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "title cannot be empty" in str(e)


def test_task_zero_duration_raises_error():
    """Edge case: Zero duration_minutes raises ValueError."""
    try:
        Task(task_id="t1", title="Walk", duration_minutes=0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "duration_minutes must be greater than 0" in str(e)


def test_task_negative_duration_raises_error():
    """Edge case: Negative duration_minutes raises ValueError."""
    try:
        Task(task_id="t1", title="Walk", duration_minutes=-5)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "duration_minutes must be greater than 0" in str(e)


def test_task_invalid_time_format_raises_error():
    """Edge case: Invalid time format raises ValueError."""
    try:
        Task(task_id="t1", title="Walk", duration_minutes=20, time="9:30 AM")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "time must be in HH:MM format" in str(e)


def test_task_time_out_of_range_raises_error():
    """Edge case: Time values out of range raise ValueError."""
    try:
        Task(task_id="t1", title="Walk", duration_minutes=20, time="25:00")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "time must be in HH:MM format" in str(e)


def test_task_invalid_priority_raises_error():
    """Edge case: Invalid priority raises ValueError."""
    try:
        Task(task_id="t1", title="Walk", duration_minutes=20, priority="urgent")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "priority must be 'low', 'medium', or 'high'" in str(e)


def test_task_negative_start_minute_raises_error():
    """Edge case: Negative start_minute raises ValueError."""
    try:
        Task(task_id="t1", title="Walk", duration_minutes=20, start_minute=-10)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "start_minute cannot be negative" in str(e)


def test_task_is_high_priority():
    """Task.is_high_priority() returns True for high priority tasks."""
    high_task = Task(task_id="t1", title="Walk", duration_minutes=20, priority="high")
    low_task = Task(task_id="t2", title="Walk", duration_minutes=20, priority="low")
    
    assert high_task.is_high_priority() is True
    assert low_task.is_high_priority() is False


def test_task_fits_time_limit():
    """Task.fits_time_limit() checks if task duration fits within limit."""
    task = Task(task_id="t1", title="Walk", duration_minutes=30)
    
    assert task.fits_time_limit(30) is True
    assert task.fits_time_limit(60) is True
    assert task.fits_time_limit(20) is False
    assert task.fits_time_limit(0) is False


def test_task_get_priority_score():
    """Task.get_priority_score() calculates composite scores correctly."""
    basic_task = Task(task_id="t1", title="Walk", duration_minutes=20)
    high_daily_task = Task(
        task_id="t2",
        title="Meds",
        duration_minutes=5,
        priority="high",
        frequency="daily",
        is_required=True
    )
    completed_task = Task(task_id="t3", title="Done", duration_minutes=10)
    completed_task.mark_complete()
    
    assert basic_task.get_priority_score() > 0
    assert high_daily_task.get_priority_score() > basic_task.get_priority_score()
    assert completed_task.get_priority_score() == 0


def test_task_mark_complete_with_date():
    """Task.mark_complete() with completed_on date."""
    task = Task(task_id="t1", title="Walk", duration_minutes=20)
    completion_date = date(2026, 3, 20)
    
    task.mark_complete(completed_on=completion_date)
    
    assert task.is_completed is True
    assert task.last_completed_on == completion_date


def test_task_mark_complete_with_both_day_and_date_raises_error():
    """Edge case: Providing both day_index and completed_on raises error."""
    task = Task(task_id="t1", title="Walk", duration_minutes=20)
    
    try:
        task.mark_complete(day_index=5, completed_on=date.today())
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Provide either day_index or completed_on, not both" in str(e)


def test_task_mark_complete_with_negative_day_index_raises_error():
    """Edge case: Negative day_index raises error."""
    task = Task(task_id="t1", title="Walk", duration_minutes=20)
    
    try:
        task.mark_complete(day_index=-5)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "day_index cannot be negative" in str(e)


def test_task_is_due_on_day():
    """Task.is_due_on_day() checks if task is due on a specific day."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    task = Task(task_id="t1", title="Walk", duration_minutes=20, due_date=today)
    
    assert task.is_due_on_day(0) is True      # Today
    assert task.is_due_on_day(1) is True      # Tomorrow (due_date <= schedule_date)
    # Negative day_index raises ValueError (API constraint)
    try:
        task.is_due_on_day(-1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "day_index cannot be negative" in str(e)


def test_task_update_task_modifies_fields():
    """Task.update_task() modifies fields and re-validates."""
    task = Task(task_id="t1", title="Walk", duration_minutes=20, priority="low")
    
    task.update_task(title="Long Walk", priority="high", duration_minutes=45)
    
    assert task.title == "Long Walk"
    assert task.priority == "high"
    assert task.duration_minutes == 45


def test_task_update_task_with_invalid_field_raises_error():
    """Edge case: Updating unknown field raises AttributeError."""
    task = Task(task_id="t1", title="Walk", duration_minutes=20)
    
    try:
        task.update_task(unknown_field="value")
        assert False, "Should have raised AttributeError"
    except AttributeError as e:
        assert "Unknown task field" in str(e)


def test_task_describe_format():
    """Task.describe() returns human-readable description."""
    task = Task(
        task_id="t1",
        title="Morning Walk",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        description="Fast pace walk"
    )
    description = task.describe()
    
    assert "Morning Walk" in description
    assert "30 min" in description
    assert "high" in description
    assert "daily" in description
    assert "pending" in description


# ============================================================================
# PET TASK MANAGEMENT TESTS
# ============================================================================

def test_pet_add_task_success():
    """Happy path: Add task to pet."""
    pet = Pet(name="Jack", species="dog")
    task = Task(task_id="t1", title="Walk", duration_minutes=20)
    
    pet.add_task(task)
    
    assert len(pet.get_tasks()) == 1
    assert pet.get_task_by_id("t1") == task


def test_pet_add_duplicate_task_id_raises_error():
    """Edge case: Adding duplicate task IDs raises ValueError."""
    pet = Pet(name="Jack", species="dog")
    task1 = Task(task_id="t1", title="Walk", duration_minutes=20)
    task2 = Task(task_id="t1", title="Run", duration_minutes=30)
    
    pet.add_task(task1)
    
    try:
        pet.add_task(task2)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "already exists" in str(e)


def test_pet_remove_task_success():
    """Happy path: Remove task from pet."""
    pet = Pet(name="Jack", species="dog")
    task = Task(task_id="t1", title="Walk", duration_minutes=20)
    pet.add_task(task)
    
    pet.remove_task("t1")
    
    assert len(pet.get_tasks()) == 0
    assert pet.get_task_by_id("t1") is None


def test_pet_remove_nonexistent_task_raises_error():
    """Edge case: Removing non-existent task raises ValueError."""
    pet = Pet(name="Jack", species="dog")
    
    try:
        pet.remove_task("t999")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "was not found" in str(e)


def test_pet_get_task_by_id_returns_none_when_not_found():
    """Edge case: Getting non-existent task returns None."""
    pet = Pet(name="Jack", species="dog")
    
    assert pet.get_task_by_id("t999") is None


def test_pet_get_required_tasks():
    """Pet.get_required_tasks() filters only required tasks."""
    pet = Pet(name="Jack", species="dog")
    required = Task(task_id="t1", title="Medication", duration_minutes=5, is_required=True)
    optional = Task(task_id="t2", title="Play", duration_minutes=20, is_required=False)
    
    pet.add_task(required)
    pet.add_task(optional)
    
    required_tasks = pet.get_required_tasks()
    
    assert len(required_tasks) == 1
    assert required_tasks[0].task_id == "t1"


def test_pet_no_tasks_returns_empty_list():
    """Edge case: Pet with no tasks returns empty list."""
    pet = Pet(name="Jack", species="dog")
    
    assert pet.get_tasks() == []
    assert pet.get_required_tasks() == []


def test_pet_get_summary():
    """Pet.get_pet_summary() returns correct format."""
    pet = Pet(name="Jack", species="dog", energy_level="high")
    pet.add_task(Task(task_id="t1", title="Walk", duration_minutes=20))
    
    summary = pet.get_pet_summary()
    
    assert "Jack" in summary
    assert "dog" in summary
    assert "1 task(s)" in summary
    assert "high" in summary


def test_pet_empty_name_raises_error():
    """Edge case: Pet with empty name raises ValueError."""
    try:
        Pet(name="", species="dog")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "name cannot be empty" in str(e)


def test_pet_empty_species_raises_error():
    """Edge case: Pet with empty species raises ValueError."""
    try:
        Pet(name="Jack", species="")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "species cannot be empty" in str(e)


def test_pet_negative_age_raises_error():
    """Edge case: Pet with negative age raises ValueError."""
    try:
        Pet(name="Jack", species="dog", age=-5)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "age cannot be negative" in str(e)


# ============================================================================
# OWNER SCHEDULING CONSTRAINTS TESTS
# ============================================================================

def test_owner_creation_success():
    """Happy path: Create owner with valid constraints."""
    owner = Owner(
        name="Ben",
        available_minutes_per_day=60,
        preferred_schedule="morning",
        max_tasks_per_day=5
    )
    
    assert owner.name == "Ben"
    assert owner.available_minutes_per_day == 60
    assert owner.preferred_schedule == "morning"
    assert owner.max_tasks_per_day == 5


def test_owner_negative_time_raises_error():
    """Edge case: Owner with negative available_minutes_per_day raises error."""
    try:
        Owner(name="Ben").update_available_time(-10)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "cannot be negative" in str(e)


def test_owner_add_pet_success():
    """Happy path: Add pet to owner."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    owner.add_pet(pet)
    
    assert len(owner.get_pets()) == 1
    assert owner.get_pet("Jack") == pet


def test_owner_add_duplicate_pet_name_raises_error():
    """Edge case: Adding pets with duplicate names raises ValueError."""
    owner = Owner(name="Ben")
    pet1 = Pet(name="Jack", species="dog")
    pet2 = Pet(name="Jack", species="cat")
    
    owner.add_pet(pet1)
    
    try:
        owner.add_pet(pet2)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "already exists" in str(e)


def test_owner_remove_pet_success():
    """Happy path: Remove pet from owner."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    owner.add_pet(pet)
    
    owner.remove_pet("Jack")
    
    assert len(owner.get_pets()) == 0


def test_owner_remove_nonexistent_pet_raises_error():
    """Edge case: Removing non-existent pet raises ValueError."""
    owner = Owner(name="Ben")
    
    try:
        owner.remove_pet("Jack")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "was not found" in str(e)


def test_owner_get_pet_case_insensitive():
    """Owner.get_pet() is case-insensitive."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    owner.add_pet(pet)
    
    assert owner.get_pet("JACK") == pet
    assert owner.get_pet("jack") == pet
    assert owner.get_pet("Jack") == pet


def test_owner_no_pets_returns_empty_list():
    """Edge case: Owner with no pets returns empty list."""
    owner = Owner(name="Ben")
    
    assert owner.get_pets() == []
    assert owner.get_all_tasks() == []


def test_owner_add_preference():
    """Owner.add_preference() adds normalized preference."""
    owner = Owner(name="Ben")
    
    owner.add_preference("Walking")
    owner.add_preference("  PLAY  ")
    
    assert "walking" in owner.task_preferences
    assert "play" in owner.task_preferences


def test_owner_add_duplicate_preference_ignored():
    """Edge case: Adding duplicate preference is ignored."""
    owner = Owner(name="Ben")
    
    owner.add_preference("Walking")
    owner.add_preference("Walking")
    
    assert owner.task_preferences.count("walking") == 1


def test_owner_remove_preference():
    """Owner.remove_preference() removes preference."""
    owner = Owner(name="Ben", task_preferences=["walking", "play"])
    
    owner.remove_preference("walking")
    
    assert "walking" not in owner.task_preferences
    assert "play" in owner.task_preferences


def test_owner_remove_nonexistent_preference_no_error():
    """Edge case: Removing non-existent preference does not crash."""
    owner = Owner(name="Ben")
    owner.remove_preference("walking")
    
    assert owner.task_preferences == []


def test_owner_can_do_task():
    """Owner.can_do_task() checks if task fits constraints."""
    owner = Owner(name="Ben", available_minutes_per_day=60)
    task_fits = Task(task_id="t1", title="Walk", duration_minutes=30)
    task_exceeds = Task(task_id="t2", title="Sleep", duration_minutes=100)
    completed = Task(task_id="t3", title="Done", duration_minutes=10)
    completed.mark_complete()
    
    assert owner.can_do_task(task_fits) is True
    assert owner.can_do_task(task_exceeds) is False
    assert owner.can_do_task(completed) is False


def test_owner_zero_time_available():
    """Edge case: Owner with 0 minutes available can only do 0-duration tasks."""
    owner = Owner(name="Ben", available_minutes_per_day=0)
    task = Task(task_id="t1", title="Walk", duration_minutes=1)
    
    assert owner.can_do_task(task) is False


def test_owner_get_all_tasks_across_pets():
    """Owner.get_all_tasks() collects tasks from all pets."""
    owner = Owner(name="Ben")
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")
    
    dog.add_task(Task(task_id="t1", title="Walk", duration_minutes=20))
    dog.add_task(Task(task_id="t2", title="Play", duration_minutes=15))
    cat.add_task(Task(task_id="t3", title="Cuddle", duration_minutes=10))
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    all_tasks = owner.get_all_tasks()
    
    assert len(all_tasks) == 3
    task_ids = [task.task_id for task in all_tasks]
    assert set(task_ids) == {"t1", "t2", "t3"}


def test_owner_get_summary():
    """Owner.get_summary() returns formatted summary."""
    owner = Owner(name="Ben", available_minutes_per_day=60, preferred_schedule="morning")
    owner.add_pet(Pet(name="Jack", species="dog"))
    
    summary = owner.get_summary()
    
    assert "Ben" in summary
    assert "60 min/day" in summary
    assert "morning" in summary
    assert "1 pet(s)" in summary


# ============================================================================
# SCHEDULER TASK SELECTION & RANKING TESTS
# ============================================================================

def test_scheduler_generate_schedule_happy_path():
    """Happy path: Generate schedule with multiple tasks."""
    owner = Owner(name="Ben", available_minutes_per_day=60, max_tasks_per_day=3)
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task(task_id="t2", title="Play", duration_minutes=15, priority="medium"))
    pet.add_task(Task(task_id="t3", title="Sleep", duration_minutes=30, priority="low"))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.generate_schedule()
    
    assert len(scheduled) >= 1
    scheduled_ids = [task.task_id for task in scheduled]
    assert "t1" in scheduled_ids  # High priority should be selected


def test_scheduler_empty_task_list_returns_empty_schedule():
    """Edge case: Owner with no tasks generates empty schedule."""
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    scheduled = scheduler.generate_schedule()
    
    assert len(scheduled) == 0


def test_scheduler_respects_time_budget():
    """Scheduler respects owner's available_minutes_per_day."""
    owner = Owner(name="Ben", available_minutes_per_day=30, max_tasks_per_day=10)
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task(task_id="t2", title="Play", duration_minutes=20, priority="high"))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.generate_schedule()
    
    total_minutes = sum(task.duration_minutes for task in scheduled)
    assert total_minutes <= 30


def test_scheduler_respects_max_tasks_per_day():
    """Scheduler respects owner's max_tasks_per_day limit."""
    owner = Owner(name="Ben", available_minutes_per_day=1000, max_tasks_per_day=2)
    pet = Pet(name="Jack", species="dog")
    
    for i in range(5):
        pet.add_task(Task(task_id=f"t{i}", title=f"Task {i}", duration_minutes=10))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduled = scheduler.generate_schedule()
    
    assert len(scheduled) <= 2


def test_scheduler_rank_tasks_prioritizes_high_priority():
    """Scheduler ranks high-priority tasks higher."""
    owner = Owner(name="Ben", available_minutes_per_day=60, max_tasks_per_day=2)
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Walk", duration_minutes=20, priority="low"))
    pet.add_task(Task(task_id="t2", title="Meds", duration_minutes=5, priority="high"))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()  # Must refresh before ranking
    ranked = scheduler.rank_tasks()
    
    assert len(ranked) >= 1
    assert ranked[0].task_id == "t2"  # High priority first


def test_scheduler_rank_tasks_prioritizes_required():
    """Scheduler ranks required tasks highest."""
    owner = Owner(name="Ben", available_minutes_per_day=60, max_tasks_per_day=3)
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Optional", duration_minutes=20, is_required=False))
    pet.add_task(Task(task_id="t2", title="Required", duration_minutes=5, is_required=True))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()  # Must refresh before ranking
    ranked = scheduler.rank_tasks()
    
    assert len(ranked) >= 1
    assert ranked[0].task_id == "t2"


def test_scheduler_filter_tasks_excludes_completed():
    """Scheduler.filter_tasks() excludes completed tasks."""
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    
    task1 = Task(task_id="t1", title="Walk", duration_minutes=20)
    task2 = Task(task_id="t2", title="Play", duration_minutes=15)
    task2.mark_complete()
    
    pet.add_task(task1)
    pet.add_task(task2)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    filtered = scheduler.filter_tasks()
    
    assert len(filtered) == 1
    assert filtered[0].task_id == "t1"


def test_scheduler_filter_tasks_excludes_exceeds_time_limit():
    """Scheduler.filter_tasks() excludes tasks exceeding time limit."""
    owner = Owner(name="Ben", available_minutes_per_day=20)
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Walk", duration_minutes=30))
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    filtered = scheduler.filter_tasks()
    
    assert len(filtered) == 0


def test_scheduler_filter_tasks_excludes_future_due_dates():
    """Scheduler.filter_tasks() excludes tasks not yet due."""
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    
    future_date = date.today() + timedelta(days=5)
    pet.add_task(Task(task_id="t1", title="Walk", duration_minutes=20, due_date=future_date))
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    scheduler.generate_schedule(day_index=0)  # Schedule for today
    filtered = scheduler.filter_tasks()
    
    assert len(filtered) == 0


# ============================================================================
# RECURRING TASK & CONFLICT DETECTION TESTS
# ============================================================================

def test_scheduler_mark_task_complete_daily_recurring():
    """Scheduler.mark_task_complete() creates next daily instance."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    task = Task(task_id="daily-med", title="Medication", duration_minutes=5, frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete("daily-med", completed_on=date(2026, 3, 22))
    
    assert task.is_completed is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 23)
    assert next_task.frequency == "daily"


def test_scheduler_mark_task_complete_weekly_recurring():
    """Scheduler.mark_task_complete() creates next weekly instance."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    task = Task(task_id="weekly-bath", title="Bath", duration_minutes=30, frequency="weekly")
    pet.add_task(task)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete("weekly-bath", completed_on=date(2026, 3, 22))
    
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 29)


def test_scheduler_mark_task_complete_one_time_no_next():
    """Scheduler.mark_task_complete() returns None for one-time tasks."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    task = Task(task_id="vet-visit", title="Vet", duration_minutes=60, frequency="once")
    pet.add_task(task)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete("vet-visit")
    
    assert next_task is None
    assert task.is_completed is True


def test_scheduler_mark_task_not_found_raises_error():
    """Edge case: Mark non-existent task raises ValueError."""
    owner = Owner(name="Ben")
    owner.add_pet(Pet(name="Jack", species="dog"))
    
    scheduler = Scheduler(owner)
    
    try:
        scheduler.mark_task_complete("nonexistent")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "was not found" in str(e)


def test_scheduler_detect_conflicts_overlapping_times():
    """Scheduler.detect_conflicts() identifies overlapping tasks."""
    owner = Owner(name="Ben", available_minutes_per_day=120, max_tasks_per_day=10)
    pet = Pet(name="Jack", species="dog")
    
    # Task A: 09:00-09:30
    pet.add_task(Task(task_id="t1", title="Task A", duration_minutes=30, time="09:00"))
    # Task B: 09:15-09:45 (overlaps with A)
    pet.add_task(Task(task_id="t2", title="Task B", duration_minutes=30, time="09:15"))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    conflicts = scheduler.detect_conflicts()
    
    assert len(conflicts) == 1
    assert (conflicts[0][0].task_id == "t1" and conflicts[0][1].task_id == "t2") or \
           (conflicts[0][0].task_id == "t2" and conflicts[0][1].task_id == "t1")


def test_scheduler_detect_conflicts_no_overlap_boundary():
    """Edge case: Tasks touching at boundary (09:00-10:00, 10:00-11:00) do NOT conflict."""
    owner = Owner(name="Ben", available_minutes_per_day=120)
    pet = Pet(name="Jack", species="dog")
    
    # Task A: 09:00-10:00
    pet.add_task(Task(task_id="t1", title="Task A", duration_minutes=60, time="09:00"))
    # Task B: 10:00-11:00 (touches but doesn't overlap)
    pet.add_task(Task(task_id="t2", title="Task B", duration_minutes=60, time="10:00"))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    conflicts = scheduler.detect_conflicts()
    
    assert len(conflicts) == 0


def test_scheduler_detect_conflicts_with_start_minute():
    """Scheduler.detect_conflicts() works with start_minute parameter."""
    owner = Owner(name="Ben", available_minutes_per_day=120)
    pet = Pet(name="Jack", species="dog")
    
    # Task A at 540 minutes (09:00)
    pet.add_task(Task(task_id="t1", title="Task A", duration_minutes=30, start_minute=540))
    # Task B at 555 minutes (09:15) - overlaps
    pet.add_task(Task(task_id="t2", title="Task B", duration_minutes=30, start_minute=555))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    conflicts = scheduler.detect_conflicts()
    
    assert len(conflicts) == 1


def test_scheduler_detect_conflicts_no_time_specified():
    """Edge case: Tasks without explicit time cannot have conflicts detected."""
    owner = Owner(name="Ben", available_minutes_per_day=120)
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Task A", duration_minutes=30))
    pet.add_task(Task(task_id="t2", title="Task B", duration_minutes=30))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    conflicts = scheduler.detect_conflicts()
    
    assert len(conflicts) == 0


def test_scheduler_get_conflict_warnings_format():
    """Scheduler.get_conflict_warnings() produces readable warnings."""
    owner = Owner(name="Ben", available_minutes_per_day=120, max_tasks_per_day=10)
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Walk", duration_minutes=30, time="09:00"))
    pet.add_task(Task(task_id="t2", title="Play", duration_minutes=20, time="09:15"))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    warnings = scheduler.get_conflict_warnings()
    
    assert len(warnings) > 0
    assert "same pet" in warnings[0]
    assert "Walk" in warnings[0]
    assert "Play" in warnings[0]


# ============================================================================
# TIME SORTING & FILTERING TESTS
# ============================================================================

def test_scheduler_sort_by_time_hhmm_format():
    """Scheduler.sort_by_time() orders tasks by HH:MM time values."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Late", duration_minutes=10, time="18:30"))
    pet.add_task(Task(task_id="t2", title="Early", duration_minutes=10, time="07:00"))
    pet.add_task(Task(task_id="t3", title="Mid", duration_minutes=10, time="12:00"))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    sorted_tasks = scheduler.sort_by_time()
    sorted_ids = [task.task_id for task in sorted_tasks]
    
    assert sorted_ids == ["t2", "t3", "t1"]


def test_scheduler_sort_by_time_no_time_pushed_to_end():
    """Edge case: Tasks without explicit time are pushed to the end."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="With Time", duration_minutes=10, time="09:00"))
    pet.add_task(Task(task_id="t2", title="No Time", duration_minutes=10, time=""))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    sorted_tasks = scheduler.sort_by_time()
    sorted_ids = [task.task_id for task in sorted_tasks]
    
    assert sorted_ids == ["t1", "t2"]


def test_scheduler_sort_tasks_by_time_coarse_slots():
    """Scheduler.sort_tasks_by_time() orders by coarse time slots."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    pet.add_task(Task(task_id="t1", title="Evening", duration_minutes=10, preferred_time="evening"))
    pet.add_task(Task(task_id="t2", title="Morning", duration_minutes=10, preferred_time="morning"))
    pet.add_task(Task(task_id="t3", title="Afternoon", duration_minutes=10, preferred_time="afternoon"))
    pet.add_task(Task(task_id="t4", title="Anytime", duration_minutes=10, preferred_time="anytime"))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    sorted_tasks = scheduler.sort_tasks_by_time()
    sorted_ids = [task.task_id for task in sorted_tasks]
    
    # Expected order: morning, afternoon, evening, anytime
    assert sorted_ids.index("t2") < sorted_ids.index("t3")  # morning before afternoon
    assert sorted_ids.index("t3") < sorted_ids.index("t1")  # afternoon before evening


def test_scheduler_filter_by_pet_name_case_insensitive():
    """Scheduler.filter_by() filters by pet name (case-insensitive)."""
    owner = Owner(name="Ben")
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")
    
    dog.add_task(Task(task_id="t1", title="Walk", duration_minutes=20))
    cat.add_task(Task(task_id="t2", title="Cuddle", duration_minutes=10))
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    filtered_lower = scheduler.filter_by(pet_name="jack", status="all")
    filtered_upper = scheduler.filter_by(pet_name="JACK", status="all")
    
    assert len(filtered_lower) == 1
    assert len(filtered_upper) == 1
    assert filtered_lower[0].task_id == "t1"


def test_scheduler_filter_by_status_completed():
    """Scheduler.filter_by() filters by completion status."""
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    task1 = Task(task_id="t1", title="Walk", duration_minutes=20)
    task2 = Task(task_id="t2", title="Play", duration_minutes=15)
    task2.mark_complete()
    
    pet.add_task(task1)
    pet.add_task(task2)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    completed = scheduler.filter_by(status="completed")
    pending = scheduler.filter_by(status="pending")
    
    assert len(completed) == 1
    assert len(pending) == 1
    assert completed[0].task_id == "t2"
    assert pending[0].task_id == "t1"


def test_scheduler_filter_by_invalid_status_raises_error():
    """Edge case: Invalid status filter raises ValueError."""
    owner = Owner(name="Ben")
    owner.add_pet(Pet(name="Jack", species="dog"))
    
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    try:
        scheduler.filter_by(status="unknown")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "status must be" in str(e)


# ============================================================================
# ENHANCED VERIFICATION TESTS
# ============================================================================

def test_sorting_correctness_chronological_order():
    """
    REQUIREMENT: Sorting Correctness - Verify tasks are returned in chronological order.
    
    This test creates multiple tasks with explicit HH:MM times and verifies they are
    sorted in strict chronological (time) order. It tests with 6 tasks scattered across
    the day to ensure proper ordering.
    """
    owner = Owner(name="Ben")
    pet = Pet(name="Jack", species="dog")
    
    # Add tasks in random order with specific times
    times_and_ids = [
        ("14:30", "t_afternoon"),    # 2:30 PM
        ("06:00", "t_early_morning"), # 6:00 AM
        ("22:00", "t_evening"),      # 10:00 PM
        ("12:00", "t_noon"),         # 12:00 PM
        ("09:15", "t_morning"),      # 9:15 AM
        ("18:45", "t_evening_2"),    # 6:45 PM
    ]
    
    for time_str, task_id in times_and_ids:
        pet.add_task(Task(task_id=task_id, title=f"Task {task_id}", duration_minutes=15, time=time_str))
    
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    # Sort tasks by time
    sorted_tasks = scheduler.sort_by_time()
    sorted_times = [task.time for task in sorted_tasks]
    
    # Verify chronological order
    expected_order = ["06:00", "09:15", "12:00", "14:30", "18:45", "22:00"]
    assert sorted_times == expected_order, f"Expected {expected_order}, got {sorted_times}"
    
    # Verify task IDs follow the time order
    sorted_ids = [task.task_id for task in sorted_tasks]
    expected_ids = ["t_early_morning", "t_morning", "t_noon", "t_afternoon", "t_evening_2", "t_evening"]
    assert sorted_ids == expected_ids, f"Expected {expected_ids}, got {sorted_ids}"


def test_recurrence_logic_daily_task_creates_next_instance():
    """
    REQUIREMENT: Recurrence Logic - Confirm that marking a daily task complete 
    creates a new task for the following day.
    
    This test verifies that:
    1. Marking a daily task complete sets is_completed=True
    2. A new task is created with next_due_date = today + 1 day
    3. New task is automatically added to the pet's task list
    4. New task has the same properties as the original (priority, frequency, etc.)
    5. Multiple consecutive completions create chain of recurring tasks
    """
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    
    # Create initial daily task due today
    today = date.today()
    initial_task = Task(
        task_id="daily-walk",
        title="Morning Walk",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        is_required=True,
        due_date=today
    )
    pet.add_task(initial_task)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    
    # Verify initial state
    assert initial_task.is_completed is False
    assert len(pet.get_tasks()) == 1
    
    # Mark first task complete
    next_task_1 = scheduler.mark_task_complete("daily-walk", completed_on=today)
    
    # Verify original task is now marked complete
    assert initial_task.is_completed is True
    assert pet.get_task_by_id("daily-walk").is_completed is True
    
    # Verify next task was created
    assert next_task_1 is not None
    assert next_task_1.is_completed is False
    assert next_task_1.due_date == today + timedelta(days=1)
    assert next_task_1.frequency == "daily"
    assert next_task_1.priority == "high"
    assert next_task_1.is_required is True
    
    # Verify new task is in pet's task list
    assert len(pet.get_tasks()) == 2
    assert pet.get_task_by_id(next_task_1.task_id) is not None
    
    # Mark second task complete and verify chain continues
    next_task_2 = scheduler.mark_task_complete(next_task_1.task_id, completed_on=today + timedelta(days=1))
    
    assert next_task_1.is_completed is True
    assert next_task_2 is not None
    assert next_task_2.due_date == today + timedelta(days=2)
    assert len(pet.get_tasks()) == 3  # Original + 2 generated


def test_conflict_detection_flags_duplicate_times():
    """
    REQUIREMENT: Conflict Detection - Verify that the Scheduler flags duplicate times.
    
    This test verifies that:
    1. Tasks with overlapping time windows are detected as conflicts
    2. Conflict detection works with both explicit times (HH:MM) and start_minute
    3. Multiple conflicts are all identified
    4. Conflict warnings are generated with descriptive messages
    5. Tasks on the same pet vs. different pets are properly labeled
    6. Scheduler.fit_tasks_into_day() skips conflicting tasks during scheduling
    """
    owner = Owner(name="Ben", available_minutes_per_day=300, max_tasks_per_day=10)
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")
    
    # Dog tasks with explicit conflicts
    # Task 1: 09:00-09:30 (30 min)
    dog.add_task(Task(task_id="dog_1", title="Dog Breakfast", duration_minutes=30, time="09:00"))
    # Task 2: 09:15-09:45 (overlaps with Task 1, same pet)
    dog.add_task(Task(task_id="dog_2", title="Dog Play", duration_minutes=30, time="09:15"))
    # Task 3: 10:00-10:15 (no conflict)
    dog.add_task(Task(task_id="dog_3", title="Dog Training", duration_minutes=15, time="10:00"))
    
    # Cat tasks with conflicts across pets
    # Task 4: 09:10-09:40 (overlaps with dog_1 and dog_2, different pet)
    cat.add_task(Task(task_id="cat_1", title="Cat Feeding", duration_minutes=30, time="09:10"))
    # Task 5: 10:00-10:25 (overlaps with dog_3, different pet)
    cat.add_task(Task(task_id="cat_2", title="Cat Play", duration_minutes=25, time="10:00"))
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    
    # Detect all conflicts
    all_conflicts = scheduler.detect_conflicts()
    
    # Should detect:
    # 1. dog_1 <-> dog_2 (same pet)
    # 2. dog_1 <-> cat_1 (different pets)
    # 3. dog_2 <-> cat_1 (different pets)
    # 4. dog_3 <-> cat_2 (different pets)
    assert len(all_conflicts) >= 4, f"Expected at least 4 conflicts, got {len(all_conflicts)}"
    
    # Verify conflict pairs
    conflict_pairs = [(c[0].task_id, c[1].task_id) for c in all_conflicts]
    
    # Check for expected conflicts
    assert any((a == "dog_1" and b == "dog_2") or (a == "dog_2" and b == "dog_1") for a, b in conflict_pairs), \
        "Should detect dog_1 <-> dog_2 conflict (same pet)"
    assert any((a == "dog_1" and b == "cat_1") or (a == "cat_1" and b == "dog_1") for a, b in conflict_pairs), \
        "Should detect dog_1 <-> cat_1 conflict (different pets)"
    assert any((a == "dog_3" and b == "cat_2") or (a == "cat_2" and b == "dog_3") for a, b in conflict_pairs), \
        "Should detect dog_3 <-> cat_2 conflict (different pets)"
    
    # Verify warning messages are generated
    warnings = scheduler.get_conflict_warnings()
    assert len(warnings) >= 4, f"Expected at least 4 warnings, got {len(warnings)}"
    
    # Check that warnings distinguish between same-pet and different-pet conflicts
    same_pet_warnings = [w for w in warnings if "same pet" in w]
    diff_pet_warnings = [w for w in warnings if "different pets" in w]
    
    assert len(same_pet_warnings) >= 1, "Should have at least one same-pet conflict warning"
    assert len(diff_pet_warnings) >= 3, "Should have at least three different-pet conflict warnings"
    
    # Verify Scheduler skips conflicting tasks during daily scheduling
    scheduled = scheduler.generate_schedule(day_index=0)
    scheduled_ids = [task.task_id for task in scheduled]
    
    # Conflicting tasks in same pet should result in only one being scheduled
    dog_scheduled = [t for t in scheduled_ids if t.startswith("dog")]
    assert len(dog_scheduled) <= 2, "Should schedule max 2 non-conflicting dog tasks (dog_1 or dog_2, plus dog_3)"
    
    # At least one of the conflicting tasks should be marked unscheduled with reason
    unscheduled = scheduler.unscheduled_tasks
    assert any("Skipped because it conflicts" in scheduler.selection_reasons.get(task.task_id, "") for task in unscheduled), \
        "Should have at least one task marked as unscheduled due to conflict"


def test_owner_save_and_load_json_roundtrip(tmp_path):
    owner = Owner(
        name="Ben",
        available_minutes_per_day=90,
        preferred_schedule="evening",
        task_preferences=["medication", "feeding"],
        max_tasks_per_day=7,
        notes="Persist this owner",
    )
    pet = Pet(name="Jack", species="dog", age=4, energy_level="high")
    task = Task(
        task_id="persist-1",
        title="Evening Meds",
        duration_minutes=10,
        priority="high",
        frequency="daily",
        preferred_time="evening",
        time="19:30",
        due_date=date.today(),
        is_required=True,
        start_minute=1170,
        notes="with food",
        description="anti-inflammatory",
    )
    pet.add_task(task)
    owner.add_pet(pet)

    data_file = tmp_path / "data.json"
    owner.save_to_json(data_file)

    restored_owner = Owner.load_from_json(data_file)

    assert restored_owner.name == "Ben"
    assert restored_owner.available_minutes_per_day == 90
    assert restored_owner.preferred_schedule == "evening"
    assert restored_owner.task_preferences == ["medication", "feeding"]
    assert restored_owner.max_tasks_per_day == 7
    assert restored_owner.notes == "Persist this owner"

    restored_pet = restored_owner.get_pet("Jack")
    assert restored_pet is not None
    assert restored_pet.species == "dog"

    restored_task = restored_pet.get_task_by_id("persist-1")
    assert restored_task is not None
    assert restored_task.title == "Evening Meds"
    assert restored_task.time == "19:30"
    assert restored_task.start_minute == 1170
    assert restored_task.is_required is True


def test_task_date_fields_roundtrip_in_owner_json(tmp_path):
    owner = Owner(name="Ava")
    pet = Pet(name="Luna", species="cat")
    task = Task(
        task_id="persist-2",
        title="Weekly Grooming",
        duration_minutes=30,
        frequency="weekly",
        due_date=date.today() + timedelta(days=2),
    )
    task.mark_complete(completed_on=date.today())
    pet.add_task(task)
    owner.add_pet(pet)

    data_file = tmp_path / "data.json"
    owner.save_to_json(data_file)
    restored_owner = Owner.load_from_json(data_file)

    restored_task = restored_owner.get_pet("Luna").get_task_by_id("persist-2")
    assert restored_task.due_date == task.due_date
    assert restored_task.last_completed_on == task.last_completed_on
    assert restored_task.is_completed is True


def test_explain_schedule_table_includes_status_and_task_names():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="table-1",
            title="Morning Walk",
            duration_minutes=20,
            priority="high",
            time="08:00",
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_schedule()
    table_text = scheduler.explain_schedule_table()

    assert "Status" in table_text
    assert "Morning Walk" in table_text
    assert "Scheduled" in table_text
