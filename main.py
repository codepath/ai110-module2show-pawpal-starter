"""
Testing ground for pawpal_system.py
"""

from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date, time, timedelta

test_task1 = Task("Walk", date(2026,3,23), time(12), duration=timedelta(hours=1))
test_task2 = Task("Meds", date(2026,3,23), time(), "monthly")
test_task3 = Task("Bath", date(2026,3,23), time(14), duration=timedelta(hours=1))

test_pet1 = Pet("Sparky", tasks=[test_task1, test_task3])
test_pet2 = Pet("Charlie", tasks=[test_task2])

test_owner = Owner("Test", pets=[test_pet1, test_pet2])

test_scheduler = Scheduler(owners=[test_owner])

organized_tasks = test_scheduler.organize_tasks()
print("Today's Schedule")
for task in organized_tasks:
    print(f"  - {task.description} at {task.scheduled_time} (Duration: {task.duration})")