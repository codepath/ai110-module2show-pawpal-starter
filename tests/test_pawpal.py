
from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler

# run python -m pytest

# Test that mark_complete() sets the task's completed status to True
def test_task_completion():
	task = Task(description="Test task")
	assert not task.completed
	task.mark_complete()
	assert task.completed

# Test that adding a task to a Pet increases the number of tasks for that pet
def test_task_addition_to_pet():
	pet = Pet(name="TestPet", species="Dog")
	initial_count = len(pet.tasks)
	task = Task(description="Walk")
	pet.add_task(task)
	assert len(pet.tasks) == initial_count + 1

# Test that sort_by_time() returns tasks in ascending chronological order,
# and that tasks with no time are pushed to the end.
def test_sort_by_time_chronological_order():
	owner = Owner("Alice")
	pet = Pet(name="Buddy", species="Dog")
	owner.add_pet(pet)

	t1 = Task(description="Morning walk", time=datetime(2026, 3, 28, 8, 0))
	t2 = Task(description="Afternoon feed", time=datetime(2026, 3, 28, 12, 0))
	t3 = Task(description="Evening meds", time=datetime(2026, 3, 28, 18, 0))
	t_none = Task(description="Grooming", time=None)

	# Add out of order to ensure sorting actually does work
	for t in [t3, t_none, t1, t2]:
		pet.add_task(t)

	scheduler = Scheduler(owner)
	sorted_tasks = scheduler.sort_by_time()

	assert sorted_tasks[0] is t1
	assert sorted_tasks[1] is t2
	assert sorted_tasks[2] is t3
	assert sorted_tasks[3] is t_none  # timeless task sorts to end

# Test that completing a daily task creates a new task scheduled exactly one day later.
def test_complete_daily_task_creates_next_occurrence():
	owner = Owner("Bob")
	pet = Pet(name="Whiskers", species="Cat")
	owner.add_pet(pet)

	task_time = datetime(2026, 3, 28, 9, 0)
	task = Task(description="Feed", time=task_time, frequency="daily")
	pet.add_task(task)

	scheduler = Scheduler(owner)
	scheduler.complete_task(pet, task)

	assert task.completed  # original task is marked done
	assert len(pet.tasks) == 2  # a follow-up was created

	follow_up = pet.tasks[1]
	assert follow_up.description == "Feed"
	assert follow_up.frequency == "daily"
	assert follow_up.time == task_time + timedelta(days=1)
	assert not follow_up.completed  # follow-up starts incomplete

# Test that detect_conflicts() returns a warning when two tasks for the same pet
# share an identical scheduled datetime, and returns nothing when there is no overlap.
def test_detect_conflicts_flags_duplicate_times():
	owner = Owner("Carol")
	pet = Pet(name="Rex", species="Dog")
	owner.add_pet(pet)

	conflict_time = datetime(2026, 3, 28, 10, 0)
	t1 = Task(description="Walk", time=conflict_time)
	t2 = Task(description="Bath", time=conflict_time)
	t3 = Task(description="Feed", time=datetime(2026, 3, 28, 11, 0))  # no conflict

	for t in [t1, t2, t3]:
		pet.add_task(t)

	scheduler = Scheduler(owner)
	warnings = scheduler.detect_conflicts()

	assert len(warnings) == 1
	assert "Walk" in warnings[0]
	assert "Bath" in warnings[0]
	assert "10:00" in warnings[0]
	assert "Rex" in warnings[0]

# Test that detect_conflicts() returns an empty list when no tasks share a time.
def test_detect_conflicts_no_false_positives():
	owner = Owner("Dave")
	pet = Pet(name="Milo", species="Dog")
	owner.add_pet(pet)

	pet.add_task(Task(description="Walk", time=datetime(2026, 3, 28, 8, 0)))
	pet.add_task(Task(description="Feed", time=datetime(2026, 3, 28, 9, 0)))

	scheduler = Scheduler(owner)
	assert scheduler.detect_conflicts() == []

# Test that generate_schedule() respects the max_tasks_per_day preference.
def test_generate_schedule_respects_max_tasks():
	owner = Owner("Eve", preferences={'max_tasks_per_day': 2, 'available_minutes': 999})
	pet = Pet(name="Luna", species="Dog")
	owner.add_pet(pet)

	for desc in ["Walk", "Feed", "Bath", "Play"]:
		pet.add_task(Task(description=desc, frequency="daily", duration=10))

	scheduler = Scheduler(owner)
	schedule = scheduler.generate_schedule()

	assert len(schedule) == 2  # capped at max_tasks_per_day

# Test that generate_schedule() puts high priority tasks before low priority tasks.
def test_generate_schedule_priority_order():
	owner = Owner("Frank", preferences={'max_tasks_per_day': 5, 'available_minutes': 999})
	pet = Pet(name="Bear", species="Dog")
	owner.add_pet(pet)

	low_task = Task(description="Grooming", frequency="weekly", duration=20, priority="low")
	high_task = Task(description="Medication", frequency="daily", duration=5, priority="high")
	pet.add_task(low_task)   # added first, but lower priority
	pet.add_task(high_task)

	scheduler = Scheduler(owner)
	schedule = scheduler.generate_schedule()

	assert schedule[0][1] is high_task   # high priority task must come first
	assert schedule[1][1] is low_task

# Test that generate_schedule() skips tasks that exceed the available_minutes budget.
def test_generate_schedule_respects_time_budget():
	owner = Owner("Grace", preferences={'max_tasks_per_day': 10, 'available_minutes': 30})
	pet = Pet(name="Coco", species="Cat")
	owner.add_pet(pet)

	fits = Task(description="Feed", frequency="daily", duration=10, priority="medium")
	too_long = Task(description="Grooming", frequency="weekly", duration=60, priority="high")
	pet.add_task(too_long)  # high priority but won't fit
	pet.add_task(fits)

	scheduler = Scheduler(owner)
	schedule = scheduler.generate_schedule()

	descriptions = [task.description for _, task, _ in schedule]
	assert "Feed" in descriptions       # fits within 30 min
	assert "Grooming" not in descriptions  # 60 min exceeds budget
