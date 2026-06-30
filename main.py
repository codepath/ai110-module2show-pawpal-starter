"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's schedule to the terminal.
Run from the project root:  python main.py
"""

from diagrams.pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # 1. Create an owner and at least two pets.
    owner = Owner(name="Jordan", email="jordan@example.com")
    biscuit = Pet(name="Biscuit", species="dog")
    mochi = Pet(name="Mochi", species="cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # 2. Add at least three tasks with different durations/priorities.
    biscuit.add_task(Task("Morning walk", duration_minutes=30, priority="high"))
    biscuit.add_task(Task("Brush coat", duration_minutes=10, priority="low"))
    mochi.add_task(Task("Feeding", duration_minutes=15, priority="high"))
    mochi.add_task(Task("Litter cleanup", duration_minutes=20, priority="medium"))

    # 3. Build today's plan within a time budget and print it.
    scheduler = Scheduler()
    available_minutes = 90
    plan = scheduler.build_plan(owner, available_minutes, day_start="08:00")

    print(f"Today's Schedule for {owner.name} (budget: {available_minutes} min)")
    print("=" * 48)
    if not plan:
        print("Nothing scheduled — no tasks fit the available time.")
    for item in plan:
        print(scheduler.explain(item))


if __name__ == "__main__":
    main()
