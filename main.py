from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def print_raw_tasks(owner: Owner) -> None:
    print("=" * 60)
    print("RAW TASK INPUT ORDER")
    print("=" * 60)
    for pet in owner.get_pets():
        print(f"\n{pet.pet_name}:")
        for task in pet.get_tasks():
            status = "completed" if task.completed else "open"
            print(
                f"- {task.time or 'Any time':>8} | {task.title:<18} | "
                f"priority={task.priority:<6} | category={task.category:<10} | {status}"
            )


def print_pending_tasks(owner: Owner, scheduler: Scheduler) -> None:
    print("\n" + "=" * 60)
    print("FILTERED TASKS DUE TODAY")
    print("=" * 60)
    pending = scheduler.get_pending_tasks(owner)
    for pet, task in pending:
        print(f"- {pet.pet_name:<8} | {task.time:>5} | {task.title}")
    print(f"\nTotal due today: {len(pending)}")


def print_sorted_schedule(owner: Owner, scheduler: Scheduler) -> None:
    print("\n" + "=" * 60)
    print("SORTED SCHEDULE WITH TIE-BREAKERS")
    print("=" * 60)

    pending = scheduler.organize_by_time(owner)

    if not pending:
        print("No pending tasks for today!")
        return

    for pet, task in pending:
        print(
            f"{task.time:>5} | {pet.pet_name:<8} | {task.title:<18} | "
            f"priority={task.priority:<6} | category={task.category:<10} | {task.duration_minutes:>2} min"
        )


def print_plan_conflicts(owner: Owner, scheduler: Scheduler) -> None:
    print("\n" + "=" * 60)
    print("LIGHTWEIGHT CONFLICT WARNINGS")
    print("=" * 60)
    warnings = scheduler.get_conflict_warnings(owner)

    if warnings:
        for warning in warnings:
            print(f"⚠ {warning}")
    else:
        print("No conflicts detected.")


def main() -> None:
    owner = Owner(owner_name="Dat")
    buddy = Pet(pet_name="Buddy", pet_desc="Golden Retriever", pet_weight=30.0, pet_height=60.0)
    mochi = Pet(pet_name="Mochi", pet_desc="Persian Cat", pet_weight=4.5, pet_height=25.0)

    owner.add_pet(buddy)
    owner.add_pet(mochi)

    # Add tasks intentionally out of order to show filtering and sorting.
    buddy.add_task(
        Task(
            title="Dinner",
            description="1 cup dry kibble",
            time="18:00",
            frequency="daily",
            priority="medium",
            duration_minutes=15,
            category="feeding",
        )
    )
    buddy.add_task(
        Task(
            title="Morning Walk",
            description="30-min walk around the block",
            time="08:00",
            frequency="daily",
            priority="medium",
            duration_minutes=30,
            category="exercise",
        )
    )
    buddy.add_task(
        Task(
            title="Give Meds",
            description="Joint support tablet",
            time="08:00",
            frequency="daily",
            priority="medium",
            duration_minutes=10,
            category="meds",
        )
    )
    buddy.add_task(
        Task(
            title="Old Vet Visit",
            description="Already finished one-time appointment",
            time="14:30",
            frequency="once",
            priority="high",
            duration_minutes=45,
            category="vet",
            completed=True,
            last_completed_date=date.today().isoformat(),
        )
    )

    mochi.add_task(
        Task(
            title="Brush Coat",
            description="Use the fine-tooth comb",
            time="09:00",
            frequency="daily",
            priority="low",
            duration_minutes=20,
            category="grooming",
        )
    )
    mochi.add_task(
        Task(
            title="Breakfast",
            description="Half can of wet food",
            time="08:00",
            frequency="daily",
            priority="high",
            duration_minutes=15,
            category="feeding",
        )
    )
    mochi.add_task(
        Task(
            title="Litter Check",
            description="Already done this morning, so it should be filtered out",
            time="07:30",
            frequency="daily",
            priority="low",
            duration_minutes=5,
            category="general",
            completed=True,
            last_completed_date=date.today().isoformat(),
        )
    )
    mochi.add_task(
        Task(
            title="Evening Feeding",
            description="Second meal for the day",
            time="19:00",
            frequency="daily",
            priority="medium",
            duration_minutes=15,
            category="feeding",
            completed=True,
            last_completed_date=(date.today() - timedelta(days=1)).isoformat(),
        )
    )

    scheduler = Scheduler()
    print_raw_tasks(owner)
    print_pending_tasks(owner, scheduler)
    print_sorted_schedule(owner, scheduler)
    print_plan_conflicts(owner, scheduler)


if __name__ == "__main__":
    main()
