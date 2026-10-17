from datetime import datetime

from pawpal_system import Owner, Pet, Recurrence, Scheduler, Task, TaskType

owner = Owner("Bob", "Dylan", 25)

dog = Pet("Rex", 3, "male", "dog")
cat = Pet("Mittens", 2, "female", "cat")
owner.add_pet(dog)
owner.add_pet(cat)

today = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

# Added deliberately out of time order.
dog.add_task(Task(TaskType.VET, today.replace(hour=14), duration_minutes=60))
cat.add_task(Task(TaskType.FEED, today.replace(hour=9), priority=2))
dog.add_task(Task(TaskType.WALK, today, duration_minutes=30, recurrence=Recurrence.DAILY))
cat.add_task(Task(TaskType.FEED, today.replace(hour=18)))

# Two tasks at the same time: one for the same pet (Rex), one for a different pet (Mittens).
dog.add_task(Task(TaskType.FEED, today.replace(hour=14), duration_minutes=15))
cat.add_task(Task(TaskType.WALK, today, duration_minutes=20))

scheduler = Scheduler(owner)


def show(title, tasks):
    print(f"\n{title}")
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(f"  {t.due_time:%H:%M}  {t.task_type.value:<5} {t.pet.name:<8} [{status}]")


show("As added (unsorted)", owner.get_all_tasks())
show("Sorted by time", scheduler.sort_by_time(owner.get_all_tasks()))
show("Only Mittens", scheduler.filter_tasks(pet_name="Mittens"))

print("\nConflict check")
for warning in scheduler.get_conflict_warnings() or ["No conflicts"]:
    print(f"  {warning}")

# Completing the recurring walk marks it done and schedules tomorrow's walk.
walk = scheduler.filter_tasks(pet_name="Rex", task_type=TaskType.WALK)[0]
scheduler.complete_task(walk)
show("Completed tasks", scheduler.filter_tasks(completed=True))
show("Pending tasks", scheduler.filter_tasks(completed=False))
show("Today's schedule", scheduler.get_daily_schedule(today.date()))
