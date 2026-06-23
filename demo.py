"""
PawPal+ Demo Script
Demonstrates the scheduling system with various scenarios.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70 + "\n")


def print_plan(plan):
    """Pretty print a plan."""
    print("📅 DAILY CARE PLAN")
    print("-" * 70)

    scheduled_tasks = plan.get_scheduled_tasks()

    if scheduled_tasks:
        print(f"\n✅ Scheduled Tasks ({len(scheduled_tasks)}):\n")
        for scheduled_task in scheduled_tasks:
            task = scheduled_task.get_task()
            print(
                f"  {scheduled_task.get_order()}. [{scheduled_task.get_start_time()} - {scheduled_task.get_end_time()}] "
                f"{task.get_name()}"
            )
            print(
                f"     Type: {task.get_task_type()} | Duration: {task.get_duration()} min | "
                f"Priority: {task.get_priority()} | Mandatory: {task.is_mandatory()}"
            )

        print(f"\n⏱️  Total Time: {plan.get_total_time()} minutes")
    else:
        print("\n❌ No tasks scheduled")

    excluded_tasks = plan.get_excluded_tasks()
    if excluded_tasks:
        print(f"\n⚠️  Excluded Tasks ({len(excluded_tasks)}):\n")
        for task in excluded_tasks:
            print(
                f"  - {task.get_name()} ({task.get_duration()} min, priority {task.get_priority()})"
            )

    print(f"\n📝 Explanation:\n{plan.get_explanation()}")


def demo_basic_schedule():
    """Demonstrate basic scheduling with plenty of time."""
    print("SCENARIO 1: Basic Schedule - Plenty of Time")
    print_separator()

    # Create owner and pet
    owner = Owner("Sarah", 180)  # 3 hours available
    pet = Pet("Buddy", "dog", 4, "large")
    pet.add_special_need("high energy")

    print(f"👤 Owner: {owner.get_name()}")
    print(
        f"🐕 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    # Create scheduler and add tasks
    scheduler = Scheduler(owner, pet)

    task1 = Task("Morning Feeding", "feeding", 15, 8)
    task2 = Task("Morning Walk", "walk", 45, 7)
    task3 = Task("Play Session", "playtime", 30, 5)
    task4 = Task("Grooming", "grooming", 40, 3)

    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_task(task3)
    scheduler.add_task(task4)

    # Generate and display plan
    plan = scheduler.generate_plan()
    print_plan(plan)


def demo_time_constraints():
    """Demonstrate scheduling with limited time."""
    print_separator()
    print("SCENARIO 2: Time Constraints - Limited Availability")
    print_separator()

    owner = Owner("Mike", 60)  # Only 1 hour available
    pet = Pet("Whiskers", "cat", 7, "small")

    print(f"👤 Owner: {owner.get_name()}")
    print(
        f"🐱 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    scheduler = Scheduler(owner, pet)

    # Add more tasks than can fit
    task1 = Task("Breakfast", "feeding", 10, 9)
    task2 = Task("Litter Box", "grooming", 5, 7)
    task3 = Task("Play Time", "enrichment", 30, 6)
    task4 = Task("Brushing", "grooming", 25, 4)
    task5 = Task("Training", "training", 20, 5)

    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_task(task3)
    scheduler.add_task(task4)
    scheduler.add_task(task5)

    plan = scheduler.generate_plan()
    print_plan(plan)


def demo_mandatory_tasks():
    """Demonstrate mandatory task prioritization."""
    print_separator()
    print("SCENARIO 3: Mandatory Tasks - Medicine First!")
    print_separator()

    owner = Owner("Emma", 90)
    pet = Pet("Rex", "dog", 10, "medium")
    pet.add_special_need("arthritis medication required")

    print(f"👤 Owner: {owner.get_name()}")
    print(
        f"🐕 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"💊 Special Needs: {', '.join(pet.get_special_needs())}")
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    scheduler = Scheduler(owner, pet)

    # Add tasks - note that medicine has lower priority but is mandatory
    task1 = Task("Fun Walk", "walk", 40, 10)
    task2 = Task("Morning Medicine", "meds", 5, 3)
    task2.set_mandatory(True)
    task2.set_description("Arthritis medication with breakfast")

    task3 = Task("Feeding", "feeding", 15, 9)
    task4 = Task("Evening Medicine", "meds", 5, 3)
    task4.set_mandatory(True)
    task4.set_description("Evening dose")

    task5 = Task("Playtime", "playtime", 25, 8)

    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_task(task3)
    scheduler.add_task(task4)
    scheduler.add_task(task5)

    plan = scheduler.generate_plan()
    print_plan(plan)


def demo_task_type_optimization():
    """Demonstrate logical task ordering by type."""
    print_separator()
    print("SCENARIO 4: Task Type Optimization - Logical Flow")
    print_separator()

    owner = Owner("Tom", 150)
    pet = Pet("Luna", "cat", 2, "small")

    print(f"👤 Owner: {owner.get_name()}")
    print(
        f"🐱 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    scheduler = Scheduler(owner, pet)

    # Add tasks with same priority - should be ordered by type
    enrichment = Task("Puzzle Feeder", "enrichment", 20, 5)
    walk = Task("Short Walk", "walk", 15, 5)
    feeding = Task("Dinner", "feeding", 10, 5)
    meds = Task("Vitamins", "meds", 5, 5)
    grooming = Task("Nail Trim", "grooming", 15, 5)
    training = Task("Clicker Training", "training", 25, 5)

    # Add in random order
    scheduler.add_task(walk)
    scheduler.add_task(training)
    scheduler.add_task(grooming)
    scheduler.add_task(feeding)
    scheduler.add_task(enrichment)
    scheduler.add_task(meds)

    plan = scheduler.generate_plan()
    print_plan(plan)
    print(
        "\nℹ️  Notice: Tasks are ordered logically (feeding → meds → walk → enrichment → grooming → training)"
    )


def demo_empty_schedule():
    """Demonstrate empty schedule scenario."""
    print_separator()
    print("SCENARIO 5: Empty Schedule - No Tasks Added")
    print_separator()

    owner = Owner("Alex", 120)
    pet = Pet("Spot", "bird", 1, "small")

    print(f"👤 Owner: {owner.get_name()}")
    print(
        f"🐦 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    scheduler = Scheduler(owner, pet)
    # Don't add any tasks

    plan = scheduler.generate_plan()
    print_plan(plan)


def main():
    """Run all demo scenarios."""
    print("\n🐾 PAWPAL+ SCHEDULING SYSTEM DEMO 🐾\n")
    print("This demo showcases different scheduling scenarios")

    demo_basic_schedule()
    demo_time_constraints()
    demo_mandatory_tasks()
    demo_task_type_optimization()
    demo_empty_schedule()

    print_separator()
    print("✨ Demo Complete! All scenarios executed successfully.")
    print("\nKey Features Demonstrated:")
    print("  ✓ Priority-based task scheduling")
    print("  ✓ Mandatory tasks always scheduled first")
    print("  ✓ Time constraint handling")
    print("  ✓ Logical task type ordering")
    print("  ✓ Detailed explanations for scheduling decisions")
    print("  ✓ Excluded task tracking when time runs out")
    print_separator()


if __name__ == "__main__":
    main()
