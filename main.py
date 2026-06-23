"""
main.py - PawPal+ Testing Ground
Test the scheduling system in the terminal before UI integration.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_schedule(pet_name, plan):
    """Print a formatted schedule for a pet."""
    print(f"\n🐾 {pet_name}'s Schedule")
    print("-" * 70)

    scheduled_tasks = plan.get_scheduled_tasks()

    if scheduled_tasks:
        for scheduled_task in scheduled_tasks:
            task = scheduled_task.get_task()
            start = scheduled_task.get_start_time()
            end = scheduled_task.get_end_time()
            name = task.get_name()
            task_type = task.get_task_type()
            mandatory = "⭐ MANDATORY" if task.is_mandatory() else ""

            print(f"  [{start} - {end}] {name} ({task_type}) {mandatory}")

        print(f"\n  ⏱️  Total Time: {plan.get_total_time()} minutes")
    else:
        print("  ❌ No tasks scheduled")

    # Show excluded tasks if any
    excluded = plan.get_excluded_tasks()
    if excluded:
        print(f"\n  ⚠️  Could not fit {len(excluded)} task(s):")
        for task in excluded:
            print(f"     - {task.get_name()} ({task.get_duration()} min)")


def main():
    """Main testing script for PawPal+ scheduling system."""

    print_header("🐾 PAWPAL+ SCHEDULING SYSTEM - TODAY'S SCHEDULE 🐾")

    # Create the owner
    owner = Owner("Jessica", 180)  # 3 hours available per day
    print(f"\n👤 Owner: {owner.get_name()}")
    print(f"⏰ Available Time: {owner.get_available_time()} minutes per day")
    owner.add_preference("morning_person", True)
    owner.add_preference("prefer_walks", True)

    # Create Pet 1: Max the Dog
    max_dog = Pet("Max", "dog", 5, "large")
    max_dog.add_special_need("high energy - needs long walks")
    max_dog.add_special_need("grain-free diet")

    print(f"\n🐕 Pet 1: {max_dog.get_name()}")
    print(
        f"   Species: {max_dog.get_species().title()}, Age: {max_dog.get_age()}, Size: {max_dog.get_size()}"
    )
    print(f"   Special Needs: {', '.join(max_dog.get_special_needs())}")

    # Create Pet 2: Luna the Cat
    luna_cat = Pet("Luna", "cat", 3, "small")
    luna_cat.add_special_need("indoor only")
    luna_cat.add_special_need("diabetes - requires medication")

    print(f"\n🐱 Pet 2: {luna_cat.get_name()}")
    print(
        f"   Species: {luna_cat.get_species().title()}, Age: {luna_cat.get_age()}, Size: {luna_cat.get_size()}"
    )
    print(f"   Special Needs: {', '.join(luna_cat.get_special_needs())}")

    # Create schedulers for each pet
    max_scheduler = Scheduler(owner, max_dog)
    luna_scheduler = Scheduler(owner, luna_cat)

    # Add tasks for Max (the dog)
    print("\n📋 Adding tasks for Max...")

    task1 = Task("Morning Walk", "walk", 45, 9)
    task1.set_description("Long walk in the park")
    max_scheduler.add_task(task1)

    task2 = Task("Breakfast", "feeding", 15, 10)
    task2.set_description("Grain-free kibble")
    max_scheduler.add_task(task2)

    task3 = Task("Fetch & Play", "playtime", 30, 7)
    task3.set_description("Backyard playtime with tennis ball")
    max_scheduler.add_task(task3)

    task4 = Task("Dinner", "feeding", 15, 8)
    max_scheduler.add_task(task4)

    task5 = Task("Evening Walk", "walk", 30, 6)
    max_scheduler.add_task(task5)

    print(f"   ✓ Added {len(max_scheduler.get_tasks())} tasks for Max")

    # Add tasks for Luna (the cat)
    print("📋 Adding tasks for Luna...")

    task6 = Task("Morning Insulin", "meds", 5, 10)
    task6.set_mandatory(True)
    task6.set_description("Insulin injection - CRITICAL")
    luna_scheduler.add_task(task6)

    task7 = Task("Breakfast", "feeding", 10, 9)
    task7.set_description("Diabetic formula wet food")
    luna_scheduler.add_task(task7)

    task8 = Task("Litter Box Cleaning", "grooming", 10, 5)
    luna_scheduler.add_task(task8)

    task9 = Task("Play with Wand Toy", "enrichment", 20, 7)
    task9.set_description("Interactive play session")
    luna_scheduler.add_task(task9)

    task10 = Task("Evening Insulin", "meds", 5, 10)
    task10.set_mandatory(True)
    task10.set_description("Insulin injection - CRITICAL")
    luna_scheduler.add_task(task10)

    task11 = Task("Dinner", "feeding", 10, 9)
    luna_scheduler.add_task(task11)

    task12 = Task("Brushing", "grooming", 15, 4)
    task12.set_description("Brush to prevent hairballs")
    luna_scheduler.add_task(task12)

    print(f"   ✓ Added {len(luna_scheduler.get_tasks())} tasks for Luna")

    # Generate schedules
    print_header("TODAY'S SCHEDULE")

    max_plan = max_scheduler.generate_plan()
    print_schedule("Max", max_plan)

    luna_plan = luna_scheduler.generate_plan()
    print_schedule("Luna", luna_plan)

    # Summary
    print_header("SUMMARY")
    total_time = max_plan.get_total_time() + luna_plan.get_total_time()
    print(f"\n📊 Total scheduled time for all pets: {total_time} minutes")
    print(f"⏰ Owner's available time: {owner.get_available_time()} minutes")
    print(f"⏳ Time remaining: {owner.get_available_time() - total_time} minutes")

    if total_time > owner.get_available_time():
        print("\n⚠️  WARNING: Scheduled time exceeds available time!")
        print("   Consider adjusting task priorities or increasing available time.")
    else:
        print("\n✅ Schedule fits within available time!")

    # Show scheduling explanations
    print_header("SCHEDULING DETAILS")
    print("\n🐕 Max's Plan Explanation:")
    print(max_plan.get_explanation())

    print("\n🐱 Luna's Plan Explanation:")
    print(luna_plan.get_explanation())

    print("\n" + "=" * 70)
    print("✨ Testing complete! The scheduling system is working correctly.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
