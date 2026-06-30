"""Demo script for PawPal+.

Creates an owner with two pets, gives each pet a few care tasks at different
times, builds today's plan for each pet, and prints the schedule to the terminal.
"""

from pawpal_system import (
    Constraints,
    Owner,
    Pet,
    Plan,
    Responsibility,
    Scheduler,
)


def main() -> None:
    # 1. Create the pets.
    rex = Pet(name="Rex", species="dog", energy_level="high")
    mittens = Pet(name="Mittens", species="cat", energy_level="low")

    # 2. Create the owner and register both pets.
    owner = Owner(name="Justin", preferences={"walk_time": "morning"})
    owner.add_pet(rex)
    owner.add_pet(mittens)

    # 3. Add tasks (Responsibilities) to the pets, deliberately *out of time
    #    order* so we can verify the sorting methods reorder them correctly.
    rex.responsibilities = [
        Responsibility(
            title="Evening walk",
            duration_minutes=30,
            priority="medium",
            category="walk",
            fixed_time="18:00",
        ),
        Responsibility(
            title="Morning walk",
            duration_minutes=30,
            priority="high",
            category="walk",
            fixed_time="08:00",
        ),
        Responsibility(
            title="Breakfast",
            duration_minutes=10,
            priority="high",
            category="feeding",
            fixed_time="08:30",
            essential=True,
        ),
    ]

    mittens.responsibilities = [
        Responsibility(
            title="Play time",
            duration_minutes=20,
            priority="low",
            category="enrichment",
            fixed_time="19:00",
        ),
        Responsibility(
            title="Morning feeding",
            duration_minutes=10,
            priority="high",
            category="feeding",
            fixed_time="07:30",
            essential=True,
        ),
        Responsibility(
            title="Litter box cleaning",
            duration_minutes=15,
            priority="medium",
            category="grooming",
            fixed_time="12:00",
        ),
    ]

    # 4. Build and print today's schedule for each pet.
    constraints = Constraints(available_minutes=240, day_of_week="Monday")

    print("=" * 50)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 50)

    for pet in owner.pets:
        plan = Plan(owner=owner, pet=pet, constraints=constraints, date="2026-06-30")
        plan.build()

        print(f"\n{pet.name} ({pet.species})")
        print("-" * 50)
        for item in plan.scheduled:
            print(
                f"  {item.start_time}-{item.end_time}  "
                f"{item.responsibility.title} "
                f"({item.responsibility.category}, {item.responsibility.priority})"
            )
        print(f"  Total: {plan.total_minutes()} min of care")

    # 5. Verify Scheduler.sort_by_time(): tasks were added out of order above,
    #    so feeding raw (unsorted) Scheduler items should print scrambled, and
    #    sort_by_time() should put them back into clock order.
    print("\n" + "=" * 50)
    print("Verify sorting: Scheduler.sort_by_time()")
    print("=" * 50)

    unsorted = [
        Scheduler(task, task.fixed_time, task.fixed_time)
        for task in rex.responsibilities
    ]
    print("\nAs added (out of order):")
    for item in unsorted:
        print(f"  {item.start_time}  {item.responsibility.title}")

    print("\nAfter sort_by_time():")
    for item in Scheduler.sort_by_time(unsorted):
        print(f"  {item.start_time}  {item.responsibility.title}")

    # 6. Verify Owner.filter_tasks(): mark a couple of tasks complete, then
    #    filter by completion status and by pet name.
    print("\n" + "=" * 50)
    print("Verify filtering: Owner.filter_tasks()")
    print("=" * 50)

    rex.responsibilities[1].mark_complete()  # Morning walk
    mittens.responsibilities[1].mark_complete()  # Morning feeding

    def show(label: str, tasks: list[Responsibility]) -> None:
        print(f"\n{label} ({len(tasks)}):")
        for task in tasks:
            flag = "done" if task.completed else "todo"
            print(f"  [{flag}] {task.title}")

    show("All tasks", owner.filter_tasks())
    show("Completed only", owner.filter_tasks(completed=True))
    show("Not completed only", owner.filter_tasks(completed=False))
    show("Rex's tasks", owner.filter_tasks(pet_name="Rex"))
    show(
        "Rex's unfinished tasks",
        owner.filter_tasks(pet_name="Rex", completed=False),
    )


if __name__ == "__main__":
    main()
