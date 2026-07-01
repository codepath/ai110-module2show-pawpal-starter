"""Demo script for PawPal+.

Creates an owner with two pets, gives each pet a few care tasks at different
times, builds today's plan for each pet, and prints the schedule to the terminal.
"""

import sys

from colorama import Fore, Style, init

# Make sure the emojis below survive a non-UTF-8 console (Windows defaults to
# cp1252, which can't encode them). Fall back silently if reconfigure is
# unavailable or the stream doesn't support it.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

from pawpal_system import (
    Constraints,
    Owner,
    Pet,
    Plan,
    Responsibility,
    Scheduler,
    category_emoji,
    priority_emoji,
)

# Enable ANSI colors on every platform (notably older Windows terminals) and
# auto-reset styling after each print so colors never bleed between lines.
init(autoreset=True)

# ANSI color per priority tier, mirroring the traffic-light emojis in
# pawpal_system.PRIORITY_EMOJI so the text and icon agree.
_PRIORITY_COLOR = {
    "high": Fore.RED,
    "medium": Fore.YELLOW,
    "low": Fore.GREEN,
}


def _priority_colored(priority: str) -> str:
    """The priority label wrapped in its tier color (e.g. red for ``high``)."""
    color = _PRIORITY_COLOR.get(priority, Fore.YELLOW)
    return f"{color}{priority}{Style.RESET_ALL}"


def _status(task: Responsibility) -> str:
    """A colored, emoji-tagged done/todo badge for a task."""
    if task.completed:
        return f"{Fore.GREEN}✅ done{Style.RESET_ALL}"
    return f"{Fore.LIGHTBLACK_EX}⬜ todo{Style.RESET_ALL}"


def _header(text: str) -> None:
    """Print a bright, bordered section header."""
    bar = "=" * 50
    print(f"{Fore.CYAN}{Style.BRIGHT}{bar}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{text}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{bar}")


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
    #    Register via add_responsibility so each task is linked back to its pet
    #    (needed for recurring tasks to auto-enqueue their next occurrence).
    for task in [
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
        # Pinned to the same time as Breakfast. Both are essential, so build()
        # keeps both and detect_conflicts() should warn about the overlap.
        Responsibility(
            title="Insulin shot",
            duration_minutes=10,
            priority="high",
            category="meds",
            fixed_time="08:30",
            essential=True,
        ),
    ]:
        rex.add_responsibility(task)

    for task in [
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
    ]:
        mittens.add_responsibility(task)

    # 4. Build and print today's schedule for each pet.
    constraints = Constraints(available_minutes=240, day_of_week="Monday")

    _header(f"🐾 Today's Schedule for {owner.name}")

    for pet in owner.pets:
        plan = Plan(owner=owner, pet=pet, constraints=constraints, date="2026-06-30")
        plan.build()

        print(f"\n{Style.BRIGHT}{pet.name} ({pet.species})")
        print("-" * 50)
        for item in plan.scheduled:
            task = item.responsibility
            print(
                f"  {Fore.CYAN}{item.start_time}-{item.end_time}{Style.RESET_ALL}  "
                f"{category_emoji(task.category)} {task.title} "
                f"({task.category}, {priority_emoji(task.priority)} "
                f"{_priority_colored(task.priority)})"
            )
        print(f"  {Style.DIM}Total: {plan.total_minutes()} min of care{Style.RESET_ALL}")

        # Surface any overlapping slots as a warning (never crashes).
        conflict = plan.detect_conflicts()
        if conflict:
            print(f"  {Fore.RED}⚠️  {conflict}{Style.RESET_ALL}")

    # 5. Verify Scheduler.sort_by_time(): tasks were added out of order above,
    #    so feeding raw (unsorted) Scheduler items should print scrambled, and
    #    sort_by_time() should put them back into clock order.
    print()
    _header("Verify sorting: Scheduler.sort_by_time()")

    unsorted = [
        Scheduler(task, task.fixed_time, task.fixed_time)
        for task in rex.responsibilities
    ]
    print("\nAs added (out of order):")
    for item in unsorted:
        task = item.responsibility
        print(f"  {Fore.CYAN}{item.start_time}{Style.RESET_ALL}  "
              f"{category_emoji(task.category)} {task.title}")

    print("\nAfter sort_by_time():")
    for item in Scheduler.sort_by_time(unsorted):
        task = item.responsibility
        print(f"  {Fore.CYAN}{item.start_time}{Style.RESET_ALL}  "
              f"{category_emoji(task.category)} {task.title}")

    # 5b. Verify Scheduler.sort_by_priority(): the same items reordered by
    #     priority tier (high -> low), with start time breaking ties, so the
    #     most important tasks surface first regardless of when they occur.
    print("\nAfter sort_by_priority():")
    for item in Scheduler.sort_by_priority(unsorted):
        task = item.responsibility
        print(
            f"  {Fore.CYAN}{item.start_time}{Style.RESET_ALL}  "
            f"{category_emoji(task.category)} {task.title} "
            f"({priority_emoji(task.priority)} {_priority_colored(task.priority)})"
        )

    # 6. Verify auto-recurrence: completing a daily/weekly task should append a
    #    fresh, uncompleted copy to the same pet for its next occurrence.
    print()
    _header("Verify recurrence: mark_complete() spawns next occurrence")

    morning_walk = rex.responsibilities[1]  # daily task
    print(f"\nRex has {len(rex.responsibilities)} tasks before completing "
          f"'{morning_walk.title}'.")
    morning_walk.mark_complete()
    mittens.responsibilities[1].mark_complete()  # Morning feeding (daily)
    print(f"Rex has {len(rex.responsibilities)} tasks after completing it "
          f"(next occurrence auto-added):")
    for task in rex.responsibilities:
        print(f"  {_status(task)}  {category_emoji(task.category)} {task.title}")

    # 7. Verify Owner.filter_tasks(): with some tasks now completed (and their
    #    next occurrences pending), filter by completion status and by pet name.
    print()
    _header("Verify filtering: Owner.filter_tasks()")

    def show(label: str, tasks: list[Responsibility]) -> None:
        print(f"\n{Style.BRIGHT}{label} ({len(tasks)}):")
        for task in tasks:
            print(f"  {_status(task)}  {category_emoji(task.category)} {task.title}")

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
