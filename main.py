from pawpal_system import Owner, Pet, Scheduler, Task
from datetime import datetime, date

# Setup Owner and Pets
owner = Owner(name="Daniel Sobowale", email="dany@gmail.com")

pet1 = Pet(name="Tye", pet_type="Rat", breed="Fancy Rat", age=1)
pet2 = Pet(name="Tee", pet_type="Cat", breed="Tabby", age=3)

owner.add_pet(pet1)
owner.add_pet(pet2)

# Setup Scheduler
scheduler = Scheduler(owner=owner)
owner.set_scheduler(scheduler)

today = date.today()

# Give the owner a free window from 9am to 8pm today
scheduler.add_available_block(
    start=datetime(today.year, today.month, today.day, 9, 0),
    end=datetime(today.year, today.month, today.day, 20, 0),
)

# Create Tasks (each one needs a pet)
task1 = Task(
    title="Walk Tye",
    pet=pet1,
    task_type="exercise",
    description="Take Tye for a walk around the block",
    priority="high",
    duration=30,
)

task2 = Task(
    title="Brush Tee",
    pet=pet2,
    task_type="grooming",
    description="Brush and clean Tee",
    priority="medium",
    duration=20,
)

task3 = Task(
    title="Massage Tye",
    pet=pet1,
    task_type="grooming",
    description="Give Tye a relaxing massage",
    priority="low",
    duration=15,
)

owner.add_task(task1)
owner.add_task(task2)
owner.add_task(task3)

# Generate and print today's schedule
scheduler.generate_daily_schedule(today)
schedule = scheduler.get_schedule(today)

print("=" * 45)
print(f"  TODAY'S PAWPAL SCHEDULE  ({today})")
print("=" * 45)

if not schedule:
    print("No tasks scheduled for today.")
else:
    for i, task in enumerate(schedule, start=1):
        time_str = (
            task.scheduled_time.strftime("%I:%M %p")
            if task.scheduled_time
            else "Unscheduled"
        )
        print(f"\n{i}. {task.title}")
        print(f"   Pet      : {task.pet.name} ({task.pet.pet_type})")
        print(f"   Time     : {time_str}  ({task.duration} min)")
        print(f"   Type     : {task.task_type}")
        print(f"   Priority : {task.priority}")
        print(f"   Status   : {task.status}")
        if task.description:
            print(f"   Notes    : {task.description}")

print("\n" + "=" * 45)
