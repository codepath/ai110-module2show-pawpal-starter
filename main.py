from datetime import date

from pawpal_system import PetTask, Constraints, Pet, Owner, DailyPlan

# Owner with a 2-hour care budget starting at 08:00.
owner = Owner("Alice", Constraints(available_minutes=120, preferred_start="08:00"))

# Pets, registered with the owner.
buddy = Pet("Buddy", "Dog")
whiskers = Pet("Whiskers", "Cat")
mohsen= Pet("Mohsen", "parrot")
owner.add_pet(buddy)
owner.add_pet(whiskers)
owner.add_pet(mohsen)

# Care tasks (title, duration in minutes, priority, preferred time).
buddy.add_task(PetTask("Feed Buddy", 15, "high", time="08:00"))
buddy.add_task(PetTask("Walk Buddy", 30, "high", time="17:30"))
whiskers.add_task(PetTask("Feed Whiskers", 10, "high", time="08:15"))
whiskers.add_task(PetTask("Play with Whiskers", 20, "medium", time="12:00"))
mohsen.add_task(PetTask("Feed Mohsen", 10, "high", time="09:00"))
mohsen.add_task(PetTask("Clean Mohsen's cage", 15, "medium"))  # no set time

# Buddy's morning feed is already done for the day.
owner.tasks_for("Buddy", status="pending")[0].mark_complete()

# Build today's plan and print it.
plan = owner.build_plan()
 
print(f"Daily plan for {owner.name} — {plan.day}")
if plan.scheduled:
    for start, end, task in plan.scheduled:
        print(f"  {start}-{end}  {task.title} ({task.duration_minutes} min) [{task.priority}]")
else:
    print("  No tasks scheduled.")

if plan.skipped:
    print("Skipped:", ", ".join(task.title for task in plan.skipped))

print()
print(plan.explain())

# --- New sorting method: tasks ordered by time of day ---------------------
print()
print("All tasks sorted by time of day:")
for task in DailyPlan.sort_by_time(owner.all_tasks()):
    when = task.time if task.time else "--:--"
    print(f"  {when}  {task.title} [{task.status}]")

# --- New filtering methods: by completion status and by pet ---------------
print()
print("Pending tasks:", ", ".join(t.title for t in owner.tasks_by_status("pending")))
print("Completed tasks:", ", ".join(t.title for t in owner.tasks_by_status("completed")))

print()
print("Whiskers' tasks:", ", ".join(t.title for t in owner.tasks_for("Whiskers")))
print(
    "Buddy's pending tasks:",
    ", ".join(t.title for t in owner.tasks_for("Buddy", status="pending")),
)

# --- Recurring tasks: completing one auto-creates the next occurrence ------
print()
daily_meds = PetTask(
    "Give Buddy meds", 5, "high", frequency="daily", due_date=date.today()
)
buddy.add_task(daily_meds)
print(f"Recurring: {daily_meds.title} due {daily_meds.due_date} [{daily_meds.status}]")

next_meds = daily_meds.mark_complete()  # spawns tomorrow's instance
if next_meds:
    buddy.add_task(next_meds)  # attach the auto-created task to the pet
    print(
        f"  completed -> next instance due {next_meds.due_date} [{next_meds.status}]"
    )

# Completing the same task again must NOT create a duplicate.
duplicate = daily_meds.mark_complete()
print(f"  completing again returns {duplicate} (no duplicate created)")

# --- Conflict detection: warn (don't raise) on shared time slots ----------
print()
buddy.add_task(PetTask("Brush Buddy", 10, "low", time="17:30"))  # clashes w/ Walk Buddy
whiskers.add_task(PetTask("Groom Whiskers", 10, "low", time="09:00"))  # clashes w/ Feed Mohsen
conflicts = DailyPlan.detect_conflicts(owner.pets)
if conflicts:
    print("Schedule conflicts:")
    for warning in conflicts:
        print(f"  - {warning}")
else:
    print("No schedule conflicts.")
