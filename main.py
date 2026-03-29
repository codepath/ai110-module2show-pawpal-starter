from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_data() -> Owner:
	owner = Owner(
		name="Ben",
		available_minutes_per_day=45,
		preferred_schedule="morning",
		task_preferences=["exercise", "feeding", "daily"],
		max_tasks_per_day=4,
	)

	dog = Pet(name="Jack", species="dog", breed="Corgi", age=4, energy_level="high")
	cat = Pet(name="Leah", species="cat", breed="Siamese", age=3, energy_level="medium")

	# Tasks added intentionally out of chronological order to demonstrate sort_by_time()
	dog.add_task(
		Task(
			task_id="jack-evening-walk",
			title="Evening Walk",
			description="Wind-down walk after dinner.",
			duration_minutes=20,
			priority="medium",
			category="exercise",
			preferred_time="evening",
			time="19:00",
		)
	)
	dog.add_task(
		Task(
			task_id="jack-lunch",
			title="Lunch",
			description="Midday feeding and water refill.",
			duration_minutes=10,
			priority="medium",
			category="feeding",
			preferred_time="afternoon",
			time="12:00",
		)
	)
	dog.add_task(
		Task(
			task_id="jack-breakfast",
			title="Breakfast",
			description="Serve breakfast and refill water.",
			duration_minutes=10,
			priority="high",
			category="feeding",
			preferred_time="morning",
			time="07:30",
			is_required=True,
		)
	)
	dog.add_task(
		Task(
			task_id="jack-walk",
			title="Morning Walk",
			description="Neighborhood walk before work.",
			duration_minutes=20,
			priority="high",
			category="exercise",
			preferred_time="morning",
			time="08:15",
			is_required=True,
		)
	)

	cat.add_task(
		Task(
			task_id="leah-play",
			title="Laser Play",
			description="Interactive play session in the living room.",
			duration_minutes=15,
			priority="medium",
			category="exercise",
			preferred_time="evening",
			time="21:00",
		)
	)
	cat.add_task(
		Task(
			task_id="leah-morning-cuddle",
			title="Morning Cuddle",
			description="Short bonding session before work.",
			duration_minutes=5,
			priority="low",
			category="enrichment",
			preferred_time="morning",
			time="07:30",
		)
	)
	cat.add_task(
		Task(
			task_id="leah-medication",
			title="Medication",
			description="Give daily medication with a treat.",
			duration_minutes=5,
			priority="high",
			category="medical",
			preferred_time="morning",
			time="09:00",
			is_required=True,
			is_completed=True,
		)
	)
	cat.add_task(
		Task(
			task_id="leah-evening-meal",
			title="Evening Meal",
			description="Dinner and fresh water.",
			duration_minutes=10,
			priority="high",
			category="feeding",
			preferred_time="evening",
			time="17:30",
			is_required=True,
		)
	)

	owner.add_pet(dog)
	owner.add_pet(cat)
	return owner


def print_schedule(owner: Owner) -> None:
	scheduler = Scheduler(owner)
	todays_schedule = scheduler.generate_schedule()

	print("Today's Schedule")
	print("=" * 40)
	print(owner.get_summary())
	print()

	for index, task in enumerate(todays_schedule, start=1):
		pet_name = scheduler.task_pet_lookup.get(task.task_id, "Unknown pet")
		reason = scheduler.selection_reasons.get(task.task_id, "Selected by the scheduler.")
		print(f"{index}. {pet_name} - {task.title}")
		print(f"   Time: {task.duration_minutes} minutes")
		print(f"   Priority: {task.priority}")
		print(f"   Preferred time: {task.preferred_time}")
		print(f"   Reason: {reason}")
		print()

	if scheduler.unscheduled_tasks:
		print("Tasks not scheduled today:")
		for task in scheduler.unscheduled_tasks:
			pet_name = scheduler.task_pet_lookup.get(task.task_id, "Unknown pet")
			reason = scheduler.selection_reasons.get(task.task_id, "Not scheduled.")
			print(f"- {pet_name}: {task.title} ({task.duration_minutes} minutes) -> {reason}")


def print_sorted_by_time(owner: Owner) -> None:
	print()
	print("All Tasks Sorted by HH:MM Time")
	print("=" * 40)
	scheduler = Scheduler(owner)
	scheduler.refresh_inputs()
	sorted_tasks = scheduler.sort_by_time()
	for task in sorted_tasks:
		pet_name = scheduler.task_pet_lookup.get(task.task_id, "Unknown")
		time_label = task.time if task.time else "no time set"
		status = "done" if task.is_completed else "pending"
		print(f"  {time_label}  {pet_name:<6}  {task.title} [{status}]")


def print_filtered(owner: Owner) -> None:
	scheduler = Scheduler(owner)
	scheduler.refresh_inputs()

	print()
	print("Filter: Jack's pending tasks")
	print("=" * 40)
	jack_pending = scheduler.filter_by(pet_name="Jack", status="pending")
	for task in jack_pending:
		print(f"  - {task.title} ({task.preferred_time}, {task.duration_minutes} min, {task.time})")

	print()
	print("Filter: all completed tasks (any pet)")
	print("=" * 40)
	completed_all = scheduler.filter_by(status="completed")
	for task in completed_all:
		pet_name = scheduler.task_pet_lookup.get(task.task_id, "Unknown")
		print(f"  - {pet_name}: {task.title}")


def print_conflict_warnings(owner: Owner) -> None:
	print()
	print("Conflict Warnings")
	print("=" * 40)
	scheduler = Scheduler(owner)
	scheduler.refresh_inputs()
	warnings = scheduler.get_conflict_warnings()
	if not warnings:
		print("  No task conflicts detected.")
		return
	for warning in warnings:
		print(f"  - {warning}")


if __name__ == "__main__":
	demo_owner = build_demo_data()
	print_sorted_by_time(demo_owner)
	print_filtered(demo_owner)
	print_conflict_warnings(demo_owner)
	print_schedule(demo_owner)
