from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner("Alex")

dog = Pet("Buddy", "dog")
cat = Pet("Luna", "cat")

# --- Tasks added OUT OF ORDER (low priority / later times first) ---
today = date.today()

# Low-priority dog task added first
dog.add_task(Task("Evening walk",   duration=30, priority=1, due_time=today))
# Cat tasks added before the high-priority dog tasks
cat.add_task(Task("Feed Luna",      duration=10, priority=1, due_time=today,
                  recurring=True, recurrence_interval="daily"))
cat.add_task(Task("Clean litter",   duration=15, priority=2, due_time=today))
# High-priority dog tasks added last
dog.add_task(Task("Morning walk",   duration=30, priority=3, due_time=today,
                  recurring=True, recurrence_interval="weekly"))
dog.add_task(Task("Feed Buddy",     duration=10, priority=2, due_time=today))

owner.add_pet(dog)
owner.add_pet(cat)

# --- Scheduler: 8 AM – 8 PM window ---
scheduler = Scheduler(available_times=[8 * 60, 20 * 60], buffer_minutes=10)
today_tasks = owner.get_today_tasks()

# generate_schedule assigns start_time to each task
result = scheduler.generate_schedule(today_tasks)

# Rebuild Task objects from the scheduled dicts so start_time is set
scheduled_tasks = [Task.from_dict(t) for t in result["scheduled"]]

# --- Helper ---
def fmt_time(minutes):
    h, m = divmod(minutes, 60)
    period = "AM" if h < 12 else "PM"
    h = h % 12 or 12
    return f"{h}:{m:02d} {period}"

# ── 1. Sort by time ───────────────────────────────────────────────────────────
print(f"\n=== Today's Schedule for {owner.name} (sorted by time) ===\n")
sorted_by_time = scheduler.sort_tasks_by_time(scheduled_tasks)
for task in sorted_by_time:
    pet_label = f"[{task.pet_name}]" if task.pet_name else ""
    time_str = fmt_time(task.start_time) if task.start_time is not None else "unscheduled"
    print(f"  {time_str:<12} {task.name} {pet_label}  ({task.duration} min, priority {task.priority})")

if result["dropped"]:
    print("\n  Could not fit:")
    for task in result["dropped"]:
        print(f"    - {task['name']}")

# ── 2. Filter: only Buddy's tasks ────────────────────────────────────────────
print(f"\n=== Buddy's tasks only ===\n")
buddy_tasks = scheduler.filter_tasks(scheduled_tasks, pet_name="Buddy")
for task in buddy_tasks:
    print(f"  {task.name}  ({task.duration} min, priority {task.priority})")

# ── 3. Filter: incomplete tasks ───────────────────────────────────────────────
print(f"\n=== Incomplete tasks ===\n")
incomplete = scheduler.filter_tasks(scheduled_tasks, completed=False)
for task in incomplete:
    pet_label = f"[{task.pet_name}]" if task.pet_name else ""
    print(f"  {task.name} {pet_label}  done={task.completed}")

# ── 4. Mark one task complete, then filter for completed ─────────────────────
scheduled_tasks[0].mark_complete()
print(f"\n=== Completed tasks (after marking '{scheduled_tasks[0].name}' done) ===\n")
completed_list = scheduler.filter_tasks(scheduled_tasks, completed=True)
for task in completed_list:
    pet_label = f"[{task.pet_name}]" if task.pet_name else ""
    print(f"  {task.name} {pet_label}  done={task.completed}")

# ── 5. Recurring task auto-next-occurrence ───────────────────────────────────
print("\n=== Recurring task: mark complete -> auto-create next occurrence ===\n")

# Find the recurring tasks from the original pets
recurring_tasks = [
    t for t in owner.get_all_tasks()
    if t.recurring and t.recurrence_interval in ("daily", "weekly")
]

for task in recurring_tasks:
    print(f"  Before: '{task.name}' [{task.pet_name}]  due={task.due_time}  "
          f"interval={task.recurrence_interval}  completed={task.completed}")

    next_occurrence = task.mark_complete()  # returns new Task for next due date

    print(f"  After:  '{task.name}'  completed={task.completed}")

    if next_occurrence is not None:
        # Add the new occurrence back to the correct pet
        pet = next((p for p in owner.get_pets() if p.name == next_occurrence.pet_name), None)
        if pet:
            pet.add_task(next_occurrence)
        print(f"  Next:   '{next_occurrence.name}' [{next_occurrence.pet_name}]  "
              f"due={next_occurrence.due_time}  interval={next_occurrence.recurrence_interval}  "
              f"completed={next_occurrence.completed}")
    print()

# Confirm the new occurrences are now on the pets
print("=== All tasks after auto-scheduling next occurrences ===\n")
for pet in owner.get_pets():
    for t in pet.get_tasks():
        status = "done" if t.completed else "pending"
        recurring_label = f" (recurring {t.recurrence_interval})" if t.recurring else ""
        print(f"  [{pet.name}] {t.name}{recurring_label}  due={t.due_time}  {status}")

# ── 6. Conflict check on the real schedule (should be clean) ─────────────────
print("=== Conflict check on generated schedule ===\n")
conflicts = scheduler.detect_conflicts(scheduled_tasks)
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No conflicts — schedule is clean.")

# ── 7. Conflict detection demo: two tasks at the same time ───────────────────
print("\n=== Conflict Detection Demo: overlapping tasks ===\n")

# Two tasks for the same pet starting at 8 AM
buddy_feed   = Task("Feed Buddy",   duration=10, priority=2, due_time=today,
                    pet_name="Buddy", start_time=8 * 60)
# A cross-pet task that also starts at 8 AM — overlaps buddy_feed
luna_feed    = Task("Feed Luna",    duration=10, priority=1, due_time=today,
                    pet_name="Luna",  start_time=8 * 60)
# A third task that starts 5 min in — still within buddy_feed's 10-min window
buddy_walk   = Task("Morning walk", duration=30, priority=3, due_time=today,
                    pet_name="Buddy", start_time=8 * 60 + 5)

demo_tasks = [buddy_feed, luna_feed, buddy_walk]
warnings = scheduler.detect_conflicts(demo_tasks)

if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts found.")
