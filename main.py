from pawpal_system import Owner, Pet, Scheduler, Task


def _clock(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"


def main() -> None:
    dog = Pet(name="Milo", species="dog", age=4, tasks=[])
    cat = Pet(name="Luna", species="cat", age=2, tasks=[])

    dog.tasks.extend(
        [
            Task("Morning walk", 8 * 60, "daily"),
            Task("Dinner & meds", 19 * 60 + 30, "daily"),  # 19:30
        ]
    )
    cat.tasks.extend(
        [
            Task("Lunch play", 12 * 60 + 15, "daily"),  # 12:15
            Task("Litter check", 17 * 60, "as_needed"),
        ]
    )

    owner = Owner(pets=[dog, cat])
    scheduler = Scheduler(owner=owner)
    plan = scheduler.generateOptimizedSchedule()
    plan.sort(key=lambda row: row[2])

    print("Today's schedule")
    print("-" * 48)
    for pet, task, slot_start in plan:
        need = task.duration_minutes + task.getRequiredTimeBuffer()
        slot_end = slot_start + need
        print(f"{_clock(slot_start)} – {_clock(slot_end)}  {pet.name}: {task.description}")


if __name__ == "__main__":
    main()
