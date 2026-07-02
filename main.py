"""CLI demo for PawPal+: builds a two-pet household and prints today's schedule.

Run with: uv run python main.py
"""

from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def build_demo_household() -> Owner:
    """One owner, two pets, four tasks at different times (all today)."""
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(
        Task(
            "Morning walk",
            time(8, 0),
            date.today(),
            duration_minutes=30,
            frequency=Frequency.DAILY,
        )
    )
    mochi.add_task(
        Task(
            "Evening walk",
            time(18, 30),
            date.today(),
            duration_minutes=30,
            frequency=Frequency.DAILY,
        )
    )

    whiskers = Pet(name="Whiskers", species="cat")
    whiskers.add_task(
        Task(
            "Feeding",
            time(9, 0),
            date.today(),
            duration_minutes=10,
            frequency=Frequency.DAILY,
        )
    )
    whiskers.add_task(
        Task("Litter box cleanup", time(20, 0), date.today(), duration_minutes=15)
    )

    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    return owner


def print_schedule(title: str, entries: list) -> None:
    """Print (pet, task) pairs as one aligned line each."""
    print(f"\n{title}")
    print("-" * len(title))
    if not entries:
        print("(nothing scheduled)")
    for pet, task in entries:
        status = "done" if task.completed else "pending"
        print(
            f"{task.time}  {pet.name} ({pet.species})  {task.description}"
            f"  [{task.duration_minutes} min, {task.frequency}, {task.priority}, {status}]"
        )


def main() -> None:
    owner = build_demo_household()
    scheduler = Scheduler(owner)

    print(
        f"PawPal+ demo — household of {owner.name}: "
        + ", ".join(f"{pet.name} the {pet.species}" for pet in owner.pets)
    )

    print_schedule("Today's Schedule (as entered)", scheduler.tasks_for_today())
    print_schedule("Today's Schedule (sorted by time)", scheduler.sort_by_time())
    print_schedule("Mochi only (filter_by_pet)", scheduler.filter_by_pet("Mochi"))

    scheduler.owner.get_pet("Whiskers").list_tasks()[0].mark_complete()
    print_schedule(
        "Still pending (filter_by_status)", scheduler.filter_by_status(completed=False)
    )

    walk = owner.get_pet("Mochi").list_tasks()[0]
    follow_up = scheduler.complete_task(walk)
    time_str = (
        follow_up.time.strftime("%H:%M")
        if isinstance(follow_up.time, time)
        else follow_up.time
    )
    print(
        f"\nCompleted '{walk.description}' (daily) -> next occurrence "
        f"auto-scheduled for {follow_up.date} at {time_str}"
    )

    owner.get_pet("Whiskers").add_task(
        Task("Medication", time(18, 30), date.today(), duration_minutes=5)
    )
    print(
        "\nAdded 'Medication' for Whiskers at 18:30 (same time as Mochi's evening walk):"
    )
    for warning in scheduler.detect_conflicts():
        print(f"  ⚠️  {warning}")

    owner.get_pet("Mochi").add_task(
        Task(
            "Vet appointment",
            time(16, 0),
            date.today(),
            duration_minutes=45,
            priority=Priority.HIGH,
        )
    )
    print_schedule(
        "Priority view (sort_by_priority: high first, then time)",
        scheduler.sort_by_priority(),
    )

    slot = scheduler.find_next_available_slot(30)
    print(f"\nNext free 30-minute slot today (find_next_available_slot): {slot}")

    # Demo rescheduling a task
    med_task = owner.get_pet("Whiskers").list_tasks()[2]
    print("\nRescheduling Whiskers' Medication from 18:30 to 19:30...")
    warnings = scheduler.reschedule_task(med_task, time(19, 30), date.today())
    new_time_str = (
        med_task.time.strftime("%H:%M")
        if isinstance(med_task.time, time)
        else med_task.time
    )
    print(f"Rescheduled successfully. New time: {new_time_str} on {med_task.date}.")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

    # Demo save/load persistence
    import os

    from pawpal_system import load_from_json, save_to_json

    data_path = "data.json"
    print(f"\nSaving data to {data_path}...")
    save_to_json(owner, data_path)

    print(f"Loading data back from {data_path}...")
    loaded_owner = load_from_json(data_path)
    loaded_scheduler = Scheduler(loaded_owner)

    print(f"Loaded Owner: {loaded_owner.name}")
    print_schedule("Loaded Household Schedule", loaded_scheduler.all_tasks())

    if os.path.exists(data_path):
        os.remove(data_path)


if __name__ == "__main__":
    main()
