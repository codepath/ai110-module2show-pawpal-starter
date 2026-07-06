"""CLI demo for PawPal+.

Runs the logic layer end-to-end in the terminal (no Streamlit) so we can verify
that scheduling, sorting, conflict detection, and recurrence all work. Run with:

    python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # 1. One owner with two pets.
    owner = Owner("Jordan")
    biscuit = Pet("Biscuit", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # 2. Several tasks added OUT OF ORDER and across BOTH pets.
    #    (Breakfast and Feed cat deliberately share 08:00 to trigger a conflict.)
    biscuit.add_task(Task("Evening walk", "18:00", "daily"))
    mochi.add_task(Task("Night meds", "21:00", "daily"))
    biscuit.add_task(Task("Breakfast", "08:00", "daily"))
    mochi.add_task(Task("Feed cat", "08:00", "daily"))
    biscuit.add_task(Task("Vet appointment", "14:00", "once"))

    scheduler = Scheduler(owner)

    # 3. Today's schedule: sorted by time, with conflict warnings.
    print("=" * 52)
    print(scheduler.todays_schedule())
    print("=" * 52)

    # 4. Show a filter in action.
    print("\nBiscuit's tasks only:")
    for task in scheduler.filter_tasks(pet_name="Biscuit"):
        print(f"  - {task.time} {task.description}")

    # 5. Show recurrence: complete the daily walk -> next day's walk appears.
    print("\nCompleting Biscuit's Evening walk (daily)...")
    follow_up = scheduler.complete_task(biscuit.tasks[0])
    if follow_up:
        print(f"  -> Auto-created next occurrence for {follow_up.due_date}")

    # 6. Remaining incomplete work, still sorted and cross-pet.
    print("\nRemaining incomplete tasks (time-sorted):")
    for task in scheduler.sort_by_time(include_completed=False):
        print(f"  - {task.time} {task.description} [{task.frequency}]")


if __name__ == "__main__":
    main()
