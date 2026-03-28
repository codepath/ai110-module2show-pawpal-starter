from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# Create an Owner
owner = Owner(name="Alex")

# Create two Pets
pet1 = Pet(name="Buddy", species="Dog", breed="Labrador", age=5)
pet2 = Pet(name="Mittens", species="Cat", breed="Siamese", age=3)

# Add pets to owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create Tasks — added intentionally OUT OF ORDER to test SORTING
now = datetime.now()
task3 = Task(description="Playtime",           time=now.replace(hour=17, minute=0), frequency="daily")
task6 = Task(description="Evening cuddle",     time=now.replace(hour=17, minute=0), frequency="weekly")
task1 = Task(description="Morning walk",       time=now.replace(hour=7,  minute=0), frequency="daily")
task5 = Task(description="Feed dinner",        time=now.replace(hour=18, minute=0), frequency="daily")
task4 = Task(description="Litter box cleaning",time=now.replace(hour=9,  minute=0), frequency="daily")
task2 = Task(description="Feed breakfast",     time=now.replace(hour=8,  minute=0), frequency="daily")

# Assign tasks to pets (still out of order)
pet1.add_task(task3)
pet1.add_task(task1)
pet1.add_task(task2)

pet2.add_task(task6)
pet2.add_task(task4)
pet2.add_task(task5)

# Mark one task complete to test filtering
task1.mark_complete()

# Create Scheduler
scheduler = Scheduler(owner)

# --- 1. sort_by_time ---
print("=== Sorted Schedule (sort_by_time) ===")
for task in scheduler.sort_by_time():
    pet_name = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
    time_str = task.time.strftime('%H:%M') if task.time else 'No time'
    print(f"  {time_str} | {task.description:<25} | Pet: {pet_name}")

# --- 2. filter by status: pending ---
print("\n=== Pending Tasks (filter_tasks completed=False) ===")
for task in scheduler.filter_tasks(completed=False):
    print(f"  [ ] {task.description}")

# --- 3. filter by status: completed ---
print("\n=== Completed Tasks (filter_tasks completed=True) ===")
for task in scheduler.filter_tasks(completed=True):
    print(f"  [x] {task.description}")

# --- 4. filter by pet name ---
print("\n=== Buddy's Tasks Only (filter_by_pet_name) ===")
for task in scheduler.filter_by_pet_name("Buddy"):
    time_str = task.time.strftime('%H:%M') if task.time else 'No time'
    print(f"  {time_str} | {task.description}")

# --- 5. combined filter: Mittens' pending tasks ---
print("\n=== Mittens' Pending Tasks (filter_tasks pet_name + completed=False) ===")
for task in scheduler.filter_tasks(completed=False, pet_name="Mittens"):
    time_str = task.time.strftime('%H:%M') if task.time else 'No time'
    print(f"  {time_str} | {task.description}")

# --- 6. Recurring Task Demo (complete_task) ---
print("\n=== Recurring Task Demo (complete_task) ===")

# Show Buddy's tasks BEFORE completing the morning walk
print("  Buddy's tasks BEFORE:")
for task in scheduler.filter_by_pet_name("Buddy"):
    time_str = task.time.strftime('%H:%M') if task.time else 'No time'
    status = "done" if task.completed else "pending"
    print(f"    {time_str} | {task.description} [{status}]")

# Use complete_task() on the Scheduler — it marks it done AND adds tomorrow's occurrence
scheduler.complete_task(pet1, task1)

# Show Buddy's tasks AFTER — a new 'Morning walk' for tomorrow should appear
print("  Buddy's tasks AFTER (complete_task called on 'Morning walk'):")
for task in scheduler.filter_by_pet_name("Buddy"):
    time_str = task.time.strftime('%Y-%m-%d %H:%M') if task.time else 'No time'
    status = "done" if task.completed else "pending"
    print(f"    {time_str} | {task.description} [{status}]")

# --- 7. Conflict Detection Demo ---
print("\n=== Conflict Detection Demo ===")

# Add a duplicate-time task to Buddy to trigger a conflict
conflict_task = Task(description="Vet check-in", time=now.replace(hour=17, minute=0), frequency="once")
pet1.add_task(conflict_task)  # Playtime is also at 17:00 — this will conflict

warnings = scheduler.detect_conflicts()
if warnings:
    for msg in warnings:
        print(f"  {msg}")
else:
    print("  No conflicts detected.")

