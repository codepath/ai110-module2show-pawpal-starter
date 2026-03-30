"""PawPal+ Demo Script — verifies core logic in the terminal."""

import datetime
from pawpal.pawpal_system import (
    Owner, Pet, Task, TaskType, Priority, RecurrenceScope,
    AvailabilityWindow, DailySchedule,
)

# --- Create an Owner ---
owner = Owner(name="Isaac")

# --- Create two Pets and register them ---
dog = Pet(name="Biscuit", species="Dog", age=4, care_metrics={"energy": "high"})
cat = Pet(name="Mochi", species="Cat", age=2, care_metrics={"energy": "low"})

owner.add_pet(dog)
owner.add_pet(cat)

# --- Set owner availability for today ---
today = datetime.date.today()
day_name = today.strftime("%A")

owner.set_availability(day_name, [
    AvailabilityWindow(day=day_name, start_time=datetime.time(7, 0), end_time=datetime.time(9, 0)),
    AvailabilityWindow(day=day_name, start_time=datetime.time(17, 0), end_time=datetime.time(19, 0)),
])

# --- Create Tasks (at least 3 with different times) ---
tasks = [
    Task(name="Morning walk (Biscuit)",   task_type=TaskType.WALK,       priority=Priority.HIGH,   scope=RecurrenceScope.DAILY, duration_minutes=30),
    Task(name="Feed Mochi",               task_type=TaskType.FEED,       priority=Priority.HIGH,   scope=RecurrenceScope.DAILY, duration_minutes=15),
    Task(name="Brush Biscuit",            task_type=TaskType.GROOMING,   priority=Priority.LOW,    scope=RecurrenceScope.DAILY, duration_minutes=20),
    Task(name="Vet checkup (Mochi)",      task_type=TaskType.VET,        priority=Priority.MEDIUM, scope=RecurrenceScope.MONTHLY, duration_minutes=60, assigned_day=day_name),
]

# --- Generate and print today's schedule ---
schedule = DailySchedule(date=today)
schedule.generate(owner, tasks)

print(schedule.display())
