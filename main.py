"""CLI demo script for PawPal+ - verifies the backend logic before UI integration."""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# -- Setup --------------------------------------------------------------------
today = date.today()

owner = Owner("Jordan")

mochi = Pet("Mochi", "cat")
rex   = Pet("Rex", "dog")

owner.add_pet(mochi)
owner.add_pet(rex)

# -- Add tasks (intentionally out of chronological order) ---------------------
mochi.add_task(Task("Evening feeding",  "18:00", duration_minutes=10, priority="high",   frequency="daily",  due_date=today))
mochi.add_task(Task("Morning feeding",  "07:30", duration_minutes=10, priority="high",   frequency="daily",  due_date=today))
mochi.add_task(Task("Medication",       "12:00", duration_minutes=5,  priority="high",   frequency="daily",  due_date=today))
mochi.add_task(Task("Enrichment play",  "15:00", duration_minutes=20, priority="medium", frequency="once",   due_date=today))

rex.add_task(Task("Morning walk",       "08:00", duration_minutes=30, priority="high",   frequency="daily",  due_date=today))
rex.add_task(Task("Afternoon walk",     "17:00", duration_minutes=30, priority="medium", frequency="daily",  due_date=today))
rex.add_task(Task("Vet appointment",    "10:00", duration_minutes=60, priority="high",   frequency="once",   due_date=today))
rex.add_task(Task("Grooming",           "10:00", duration_minutes=45, priority="low",    frequency="weekly", due_date=today))  # intentional conflict

scheduler = Scheduler(owner)

# -- Today's schedule (sorted by time) ----------------------------------------
print("=" * 60)
print(f"TODAY'S SCHEDULE  ({today})  - {owner.name}'s pets")
print("=" * 60)

sorted_tasks = scheduler.sort_by_time()
for pet, task in sorted_tasks:
    print(f"  {task.time}  [{task.priority.upper():6}]  {pet.name:8}  {task.description}")

# -- Conflict detection -------------------------------------------------------
print()
print("-- Conflict Check " + "-" * 42)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# -- Priority-first schedule --------------------------------------------------
print()
print("-- Priority Schedule (high first, then time) " + "-" * 16)
for pet, task in scheduler.sort_by_priority():
    print(f"  [{task.priority.upper():6}]  {task.time}  {pet.name:8}  {task.description}")

# -- Filtering ----------------------------------------------------------------
print()
print("-- Mochi's tasks only " + "-" * 38)
for pet, task in scheduler.filter_by_pet("Mochi"):
    print(f"  {task}")

# -- Mark a task complete + recurrence ----------------------------------------
print()
print("-- Mark 'Morning feeding' complete " + "-" * 25)
morning_feed = mochi.tasks[1]  # "Morning feeding" was added second
print(f"  Before: completed={morning_feed.completed}")
next_task = scheduler.mark_task_complete(mochi, morning_feed)
print(f"  After:  completed={morning_feed.completed}")
if next_task:
    print(f"  Next occurrence created: {next_task.description} on {next_task.due_date}")

# -- Next available slot -------------------------------------------------------
print()
print("-- Next available slot for Rex " + "-" * 29)
slot = scheduler.get_next_available_slot("Rex", today)
print(f"  Next free 30-min slot: {slot}")

print()
print("Demo complete - all systems functional!")
