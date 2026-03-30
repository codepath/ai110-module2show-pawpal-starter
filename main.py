from datetime import date

from pawpal_system import OwnerInfo, Pet, RigidTask, StaticTask, Scheduler


def main() -> None:
    """Build and print a sample pet care schedule and show any scheduling warnings."""
    owner = OwnerInfo(name="Anato")
    current_date = date.today()

    pet1 = Pet(name="Milo", birthday="2021-04-14", animal="Dog")
    pet2 = Pet(name="Luna", birthday="2022-09-03", animal="Cat")

    # Add tasks out of chronological order to verify sorting
    task1 = RigidTask(
        name="Evening feeding",
        description="Feed Milo before bedtime",
        duration=20,
        ideal_time="20:00",
        priority=3,
        task_date=current_date,
    )

    task2 = StaticTask(
        name="Medication",
        description="Give Luna her fixed 09:00 medication",
        duration=10,
        ideal_time="09:00",
        fixed_time="09:00",
        priority=5,
        task_date=current_date,
    )

    task5 = StaticTask(
        name="Breakfast",
        description="Feed Milo at 09:00",
        duration=15,
        ideal_time="09:00",
        fixed_time="09:00",
        priority=4,
        task_date=current_date,
    )

    task6 = StaticTask(
        name="Grooming",
        description="Brush Milo at 09:00",
        duration=15,
        ideal_time="09:00",
        fixed_time="09:00",
        priority=4,
        task_date=current_date,
    )

    task3 = RigidTask(
        name="Morning walk",
        description="Take Milo for a 30-minute walk",
        duration=30,
        ideal_time="08:00",
        priority=5,
        daily=True,
        task_date=current_date,
    )

    task4 = RigidTask(
        name="Afternoon play",
        description="Play with Milo in the yard",
        duration=25,
        ideal_time="15:00",
        priority=4,
        task_date=current_date,
    )

    pet1.add_task(task1)
    pet1.add_task(task3)
    pet1.add_task(task4)
    pet1.add_task(task5)
    pet1.add_task(task6)
    pet2.add_task(task2)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Mark one daily task complete so the next-day copy is created
    task3.mark_complete(parent_pet=pet1)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_static_conflicts()
    schedule = scheduler.schedule_tasks()

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
        print()

    print("Today's schedule (sorted by date and time):")
    for pet, task in schedule:
        task_date = task.date.isoformat()
        time_string = getattr(task, "scheduled_time", getattr(task, "fixed_time", task.ideal_time))
        print(f"- {task_date} {time_string} | {pet.name}: {task.name} ({task.description})")

    print("\nCompleted tasks:")
    for pet, task in scheduler.filter_tasks_by_completion(True):
        task_date = task.date.isoformat()
        time_string = getattr(task, "scheduled_time", getattr(task, "fixed_time", task.ideal_time))
        print(f"- {task_date} {time_string} | {pet.name}: {task.name}")

    print("\nIncomplete tasks:")
    for pet, task in scheduler.filter_tasks_by_completion(False):
        task_date = task.date.isoformat()
        time_string = getattr(task, "scheduled_time", getattr(task, "fixed_time", task.ideal_time))
        print(f"- {task_date} {time_string} | {pet.name}: {task.name}")


if __name__ == "__main__":
    main()
