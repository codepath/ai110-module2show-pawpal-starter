"""
PawPal terminal demo.

Demonstrates the Scheduler's sorting, filtering, recurring-task
automation, and conflict detection using tasks added intentionally
out of chronological order.

Run with:
    python pawpal_demo.py
"""

from datetime import datetime, timedelta

from pawpal_system import Appointment, Owner, Pet, Scheduler, Task


def build_demo_data() -> tuple[Owner, list[Pet]]:
    """Create a demo owner with two pets and several tasks."""
    owner = Owner(name="Maya", email="maya@example.com", phone="555-0100")

    buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3, owner_id=owner.owner_id)
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=5, owner_id=owner.owner_id)

    now = datetime.now().replace(second=0, microsecond=0)

    # Tasks added OUT OF ORDER intentionally
    buddy.add_task(Task(title="Evening walk",    pet_id=buddy.pet_id, due_date=now + timedelta(hours=8),  recurrence="daily"))
    buddy.add_task(Task(title="Morning walk",    pet_id=buddy.pet_id, due_date=now + timedelta(hours=1),  recurrence="daily"))
    buddy.add_task(Task(title="Flea treatment",  pet_id=buddy.pet_id, due_date=now + timedelta(days=3)))
    buddy.add_task(Task(title="Afternoon walk",  pet_id=buddy.pet_id, due_date=now + timedelta(hours=5),  recurrence="daily"))

    luna.add_task(Task(title="Medication",       pet_id=luna.pet_id,  due_date=now + timedelta(hours=2),  recurrence="daily"))
    luna.add_task(Task(title="Grooming",         pet_id=luna.pet_id,  due_date=now + timedelta(days=7)))

    # Intentional conflict: two tasks at the exact same time
    conflict_time = now + timedelta(hours=1)
    luna.add_task(Task(title="Vet checkup",      pet_id=luna.pet_id,  due_date=conflict_time))
    buddy.add_task(Task(title="Nail trim",       pet_id=buddy.pet_id, due_date=conflict_time))

    owner.add_pet(buddy)
    owner.add_pet(luna)
    return owner, [buddy, luna]


def print_tasks(tasks: list[Task], label: str) -> None:
    print(f"\n--- {label} ({len(tasks)}) ---")
    for t in tasks:
        status = "✓" if t.is_complete else "○"
        recur = f" [{t.recurrence}]" if t.recurrence else ""
        print(f"  {status} {t.due_date.strftime('%b %d %H:%M')}  {t.title}{recur}")


def main() -> None:
    print("=" * 60)
    print("PawPal Scheduler Demo")
    print("=" * 60)

    owner, (buddy, luna) = build_demo_data()
    scheduler = Scheduler(owner=owner)

    # 1. All tasks unsorted
    print_tasks(scheduler.all_tasks(), "All tasks (unsorted)")

    # 2. Sorted by time
    print_tasks(scheduler.sort_by_time(), "Sorted by due_date")

    # 3. Filter: Buddy's tasks only
    print_tasks(
        scheduler.filter_tasks(pet_name="Buddy"),
        "Buddy's tasks (filtered)",
    )

    # 4. Filter: incomplete tasks only
    print_tasks(
        scheduler.filter_tasks(completed=False),
        "All incomplete tasks",
    )

    # 5. Conflict detection
    print("\n--- Conflict detection ---")
    warnings = scheduler.detect_conflicts()
    if warnings:
        for w in warnings:
            print(" ", w)
    else:
        print("  No conflicts found.")

    # 6. Mark a recurring task complete → auto-creates next occurrence
    print("\n--- Recurring task: mark Morning walk complete ---")
    morning_walk = next(t for t in buddy.tasks if t.title == "Morning walk")
    next_task = scheduler.mark_task_complete(morning_walk, buddy)
    print(f"  '{morning_walk.title}' completed at {morning_walk.completed_at.strftime('%H:%M')}")
    if next_task:
        print(f"  Next occurrence auto-created: {next_task.due_date.strftime('%b %d %H:%M')}")

    # 7. Show Buddy's incomplete tasks after completion
    print_tasks(
        scheduler.filter_tasks(pet_name="Buddy", completed=False),
        "Buddy's remaining tasks",
    )

    # 8. Care summary per pet
    print("\n--- Care summaries ---")
    for pet in owner.pets:
        summary = pet.get_care_summary()
        print(f"\n  {pet.name}:")
        print(f"    Incomplete tasks : {len(summary['incomplete_tasks'])}")
        print(f"    Overdue tasks    : {len(summary['overdue_tasks'])}")
        print(f"    Upcoming appts   : {len(summary['upcoming_appointments'])}")

    print("\nDemo complete.")


if __name__ == "__main__":
    main()
