from pawpal_system import Task, Pet, Owner, Scheduler

mochi = Pet("Mochi", 8.5, "brown", "labrador")
mochi.add_task(Task("Vet checkup", "10:00", "once"))
mochi.add_task(Task("Evening walk", "18:30", "daily"))
mochi.add_task(Task("Morning walk", "08:00", "daily"))
mochi.add_task(Task("Nail trimming", "10:00", "once"))

whiskers = Pet("Whiskers", 4.2, "gray", "tabby")
whiskers.add_task(Task("Feeding", "07:30", "daily"))
whiskers.add_task(Task("Litter box cleaning", "09:00", "daily"))
whiskers.add_task(Task("Grooming", "14:00", "weekly"))

owner = Owner({"name": "Jordan"}, [mochi, whiskers])
scheduler = Scheduler(owner)

print("Today's Schedule")
print(scheduler.explain_plan())

print("\nAll Tasks Sorted by Time")
for task in scheduler.sort_by_time():
    print(f"- {task}")

print("\nAll Tasks Sorted by Priority/Frequency")
for task in scheduler.sort_tasks():
    print(f"- {task}")

print("\nPending Tasks for Mochi")
for task in scheduler.filter_tasks(completed=False, pet_name="Mochi"):
    print(f"- {task}")

print("\nSchedule Conflicts")
conflicts = scheduler.check_conflicts()
if conflicts:
    for task_a, task_b in conflicts:
        print(f"- {task_a.description} and {task_b.description} both at {task_a.time}")
else:
    print("None found.")
