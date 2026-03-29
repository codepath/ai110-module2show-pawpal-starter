from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner("Alex")

dog = Pet("Buddy", "dog")
cat = Pet("Luna", "cat")

# --- Tasks (all due today so they appear in the schedule) ---
today = date.today()

dog.add_task(Task("Morning walk",   duration=30, priority=3, due_time=today))
dog.add_task(Task("Feed Buddy",     duration=10, priority=2, due_time=today))
cat.add_task(Task("Clean litter",   duration=15, priority=2, due_time=today))
cat.add_task(Task("Feed Luna",      duration=10, priority=1, due_time=today))

owner.add_pet(dog)
owner.add_pet(cat)

# --- Schedule ---
# available_times: start slots in minutes from midnight (8am, 9am, 12pm)
scheduler = Scheduler([8 * 60, 9 * 60, 12 * 60])
today_tasks = owner.get_today_tasks()
result = scheduler.generate_schedule(today_tasks)

# --- Print ---
def fmt_time(minutes):
    h, m = divmod(minutes, 60)
    period = "AM" if h < 12 else "PM"
    h = h % 12 or 12
    return f"{h}:{m:02d} {period}"

print(f"\n=== Today's Schedule for {owner.name} ===\n")

if result["scheduled"]:
    for task in result["scheduled"]:
        pet_label = f"[{task['pet_name']}]" if task.get("pet_name") else ""
        print(f"  {fmt_time(task['start_time'])}  {task['name']} {pet_label}  ({task['duration']} min)")
else:
    print("  No tasks scheduled.")

if result["dropped"]:
    print("\n  Could not fit:")
    for task in result["dropped"]:
        print(f"    - {task['name']}")

conflicts = scheduler.detect_conflicts(today_tasks)
print(f"\nConflicts detected: {conflicts}\n")
