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
)


def main() -> None:
    # 1. Create the pets.
    rex = Pet(name="Rex", species="dog", energy_level="high")
    mittens = Pet(name="Mittens", species="cat", energy_level="low")

    # 2. Create the owner and register both pets.
    owner = Owner(name="Justin", preferences={"walk_time": "morning"})
    owner.add_pet(rex)
    owner.add_pet(mittens)

    # 3. Add tasks (Responsibilities) at different times to the pets.
    rex.responsibilities = [
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
        Responsibility(
            title="Evening walk",
            duration_minutes=30,
            priority="medium",
            category="walk",
            fixed_time="18:00",
        ),
    ]

    mittens.responsibilities = [
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
        Responsibility(
            title="Play time",
            duration_minutes=20,
            priority="low",
            category="enrichment",
            fixed_time="19:00",
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


if __name__ == "__main__":
    main()
