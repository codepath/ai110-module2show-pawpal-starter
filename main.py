#!/usr/bin/env python3
"""
PawPal+ Demo Script

Temporary testing ground to verify backend logic works in the terminal.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, ScheduleEntry
from datetime import date, time, timedelta, datetime

def main():
    # Create an Owner
    owner = Owner(id="owner1", name="Alice", available_time_min=120)  # 2 hours available

    # Create two Pets
    pet1 = Pet(id="pet1", name="Buddy", species="Dog", age=3)
    pet2 = Pet(id="pet2", name="Whiskers", species="Cat", age=2)

    # Add pets to owner
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Create and add tasks to pets
    task1 = Task(id="task1", description="Morning walk", duration_min=30, priority="high", frequency="daily")
    task2 = Task(id="task2", description="Feed breakfast", duration_min=15, priority="medium", frequency="daily")
    task3 = Task(id="task3", description="Playtime", duration_min=45, priority="low", frequency="daily")
    task4 = Task(id="task4", description="Vet checkup", duration_min=60, priority="high", frequency="once")
    task5 = Task(id="task5", description="Bath time", duration_min=20, priority="medium", frequency="weekly",
                 last_scheduled=date.today() - timedelta(days=3))  # scheduled 3 days ago — not due yet

    pet1.add_task(task1)
    pet1.add_task(task2)
    pet1.add_task(task4)  # once — should be scheduled
    pet1.add_task(task5)  # weekly, done 3 days ago — should be skipped
    pet2.add_task(task3)

    # Create Scheduler and build daily plan
    scheduler = Scheduler(owner=owner, date=date.today())
    scheduler.build_daily_plan()

    # Print Today's Schedule
    print(f"Today's Schedule for Owner: {owner.name}")
    for pet in owner.pets:
        print(f"  Pet: {pet.name} ({pet.species})")
        pet_tasks = [entry for entry in scheduler.schedule if entry.pet == pet]
        if pet_tasks:
            for entry in pet_tasks:
                duration_min = entry.task.duration_min
                duration_str = f"{duration_min // 60} hour{'s' if duration_min // 60 > 1 else ''}" if duration_min % 60 == 0 and duration_min > 0 else f"{duration_min} min"
                print(f"    - {entry.task.description} ({entry.task.priority}, {duration_str}, {entry.start.strftime('%H:%M')} - {entry.end.strftime('%H:%M')})")
        else:
            print("    - No tasks scheduled")
    
    print("\nTimeline (sorted by start time):")
    for entry in scheduler.sort_by_time():
        print(f"  {entry.start.strftime('%H:%M')} - {entry.end.strftime('%H:%M')}  [{entry.pet.name}] {entry.task.description}")

    print("\nRecurring task automation:")
    daily_entry = next((e for e in scheduler.schedule if e.task.frequency == "daily"), None)
    if daily_entry:
        print(f"  Completing '{daily_entry.task.description}' (daily)...")
        next_task = scheduler.complete_task(daily_entry.task.id)
        if next_task:
            print(f"  Next occurrence queued: '{next_task.description}' | due after: {next_task.last_scheduled + timedelta(days=1)}")
        else:
            print("  No next occurrence (once-only task).")

    print("\nConflict detection (normal schedule — expect none):")
    for warning in scheduler.warn_conflicts():
        print(f"  {warning}")
    if not scheduler.warn_conflicts():
        print("  No conflicts found.")

    # Conflict scenario: build a scheduler where two tasks share the same start time
    print("\nConflict detection (two tasks at 08:00 — expect warning):")
    conflict_owner = Owner(id="owner2", name="Alex", available_time_min=120)
    conflict_pet = Pet(id="cp1", name="Luna", species="dog", age=2)
    ta = Task(id="ca1", description="Morning walk", duration_min=30, priority="high")
    tb = Task(id="ca2", description="Vet appointment", duration_min=45, priority="high")
    conflict_pet.add_task(ta)
    conflict_pet.add_task(tb)
    conflict_owner.add_pet(conflict_pet)
    conflict_scheduler = Scheduler(owner=conflict_owner, date=date.today())
    conflict_scheduler.build_daily_plan(start_time=time(8, 0))
    # Force both entries to start at 08:00 to simulate a real conflict
    same_start = conflict_scheduler.schedule[0].start
    for entry in conflict_scheduler.schedule:
        entry.start = same_start
        entry.end = same_start + timedelta(minutes=entry.task.duration_min)
    for warning in conflict_scheduler.warn_conflicts():
        print(f"  {warning}")

    print("\nRecurrence check:")
    print(f"  Bath time is_due today: {task5.is_due(date.today())} (weekly, last done 3 days ago — expect False)")
    print(f"  Vet checkup is_due today: {task4.is_due(date.today())} (once, not complete — expect True)")

    print("\nFilter: Buddy's pending tasks:")
    for t in owner.filter_tasks(pet_id="pet1", status="pending"):
        print(f"  - {t.description} ({t.priority})")

    task1.mark_complete()
    print("\nFilter: all complete tasks after marking task1 done:")
    for t in owner.filter_tasks(status="complete"):
        print(f"  - {t.description}")

    if scheduler.overflow_tasks:
        print("\nOverflow tasks:")
        for task in scheduler.overflow_tasks:
            duration_min = task.duration_min
            duration_str = f"{duration_min // 60} hour{'s' if duration_min // 60 > 1 else ''}" if duration_min % 60 == 0 and duration_min > 0 else f"{duration_min} min"
            print(f"  - {task.description} ({task.priority}, {duration_str})")

if __name__ == "__main__":
    main()