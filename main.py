"""Temporary testing ground for the PawPal+ domain model.

Run with:  python main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # Create an owner and two pets.
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "Shiba Inu")
    rex = Pet("Rex", "Labrador")
    owner.add_pet(mochi)
    owner.add_pet(rex)

    # Add tasks with different times to the pets.
    mochi.add_task(Task("Morning walk", time(7, 30), frequency="daily"))
    mochi.add_task(Task("Evening walk", time(18, 0), frequency="daily"))
    rex.add_task(Task("Breakfast", time(8, 0), frequency="daily"))
    rex.add_task(Task("Vet visit", time(14, 30), frequency="weekly"))

    # Build and print today's schedule across all pets, ordered by time.
    scheduler = Scheduler(owner)

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for pet, task in scheduler.build_daily_plan():
        status = "done" if task.done else "pending"
        print(f"{task.time.strftime('%H:%M')}  {pet.name:8} {task.name} ({task.frequency}) [{status}]")


if __name__ == "__main__":
    main()
