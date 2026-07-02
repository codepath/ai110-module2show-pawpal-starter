# temporary "testing ground" to verify logic works in the terminal.

# importing the classes from pawpal_system.py
from datetime import date
from pawpal_system import Pet, Task, Owner, Schedule

# --- Owner ---
owner = Owner(
    name="Alex Rivera",
    available_minutes_per_day=90,
    preferences={"preferred_time_of_day": "morning"},
)

# --- Pets ---
pet1 = Pet(
    name="Luna",
    species="Dog",
    breed="Golden Retriever",
    age=3,
    special_needs=["scare of thunderstorms", "scare of cars honk"],
)

pet2 = Pet(
    name="Mochi",
    species="Cat",
    breed="Scottish Fold",
    age=5,
    special_needs=[],
)

# --- Tasks ---
task1 = Task(
    name="Morning Walk",
    category="Exercise",
    duration_minutes=30,
    priority="high",
    frequency="daily",
    preferred_time_of_day="morning",
    completed=False,
    scheduled_time="14:00",
    pet_name="Luna"
)

task2 = Task(
    name="Feeding",
    category="Nutrition",
    duration_minutes=10,
    priority="medium",
    frequency="daily",
    preferred_time_of_day="morning",
    completed=False,
    scheduled_time="08:00",
    pet_name="Luna"
)

task3 = Task(
    name="Grooming",
    category="Hygiene",
    duration_minutes=20,
    priority="low",
    frequency="daily",
    preferred_time_of_day="afternoon",
    completed=False,
    scheduled_time="11:30",
    pet_name="Mochi"
)

# --- Conflict Detection Test ---
conflict_task1 = Task(
    name="Medication",
    category="Health",
    duration_minutes=5,
    priority="high",
    frequency="daily",
    preferred_time_of_day="morning",
    completed=False,
    scheduled_time="09:00",
    pet_name="Luna"
)

conflict_task2 = Task(
    name="Dental Cleaning",
    category="Hygiene",
    duration_minutes=15,
    priority="medium",
    frequency="daily",
    preferred_time_of_day="morning",
    completed=False,
    scheduled_time="09:00",
    pet_name="Luna"
)

# --- Luna's schedule: Walk + Feeding ---
schedule_luna = Schedule(schedule_date=date.today(), owner=owner, pet=pet1)
schedule_luna.generate(tasks=[task1, task2], available_minutes=owner.available_minutes_per_day)

# --- Mochi's schedule: Feeding + Grooming ---
schedule_mochi = Schedule(schedule_date=date.today(), owner=owner, pet=pet2)
schedule_mochi.generate(tasks=[task2, task3], available_minutes=owner.available_minutes_per_day)

# --- Conflict Detection Schedule ---
schedule_conflict = Schedule(schedule_date=date.today(), owner=owner, pet=pet1)
schedule_conflict.generate(tasks=[conflict_task1, conflict_task2], available_minutes=owner.available_minutes_per_day)


print("=== Today's Schedule ===")
print(schedule_luna.get_summary())
print()
print(schedule_luna.get_skipped_summary())
print()
print(schedule_mochi.get_summary())
print()
print(schedule_mochi.get_skipped_summary())

print("=== Sorted by Time ===")
for slot, task in schedule_luna.sort_by_time():
    print(f"{task.name}: {task.scheduled_time}")

# Mark one task complete to make filter results more interesting
task1.mark_complete()

print()
print("=== filter_tasks: incomplete tasks on Luna's schedule ===")
for task in schedule_luna.filter_tasks(completed=False):
    print(f"  {task.name} (completed={task.completed})")

print()
print("=== filter_tasks: completed tasks on Luna's schedule ===")
for task in schedule_luna.filter_tasks(completed=True):
    print(f"  {task.name} (completed={task.completed})")

print()
print("=== filter_tasks: tasks for pet 'Luna' ===")
for task in schedule_luna.filter_tasks(pet_name="Luna"):
    print(f"  {task.name}")

print()
print("=== filter_tasks: tasks for pet 'Mochi' (should be empty on Luna's schedule) ===")
results = schedule_luna.filter_tasks(pet_name="Mochi")
print(f"  {results if results else '[]'}")

print()
print("=== Recurring Task: mark_complete() on Feeding ===")
next_task = task2.mark_complete()
print(f"  {task2.name} | schedule_date: {task2.schedule_date} (completed={task2.completed})")
if next_task is not None:
    print(f"  {next_task.name} | schedule_date: {next_task.schedule_date} (next occurrence)")

print()
print("=== Conflict Detection ===")
for warning in schedule_conflict.detect_conflicts():
    print(f"  {warning}")

