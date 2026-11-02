"""Temporary testing ground for the PawPal+ system."""

from datetime import datetime

from Pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    owner = Owner("Jordan", available_minutes=90, preferences=["walk"])
    mochi = Pet("Mochi", "Dog", 3)
    whiskers = Pet("Whiskers", "Cat", 5)
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    mochi.add_task(Task("Morning walk", today.replace(hour=7, minute=30), 30, "high", "Daily"))
    whiskers.add_task(Task("Breakfast", today.replace(hour=8, minute=15), 10, "high", "Daily"))
    whiskers.add_task(Task("Litter box cleaning", today.replace(hour=17), 15, "medium", "Daily"))

    print(f"Owner: {owner.name} | Pets: {', '.join(pet.name for pet in owner.pets)}")
    print(f"Total tasks: {len(owner.get_all_tasks())}\n")

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    print(f"Today's Schedule ({today:%A, %B %d, %Y})")
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
