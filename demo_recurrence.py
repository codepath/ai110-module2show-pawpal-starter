"""
PawPal+ Task Recurrence Demo
Demonstrates automatic task recurrence when tasks are completed.
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_task_details(task, label="Task"):
    """Print detailed task information."""
    print(f"\n{label}:")
    print(f"  📋 Name: {task.get_name()}")
    print(f"  🆔 ID: {task.get_task_id()[:8]}...")
    print(f"  ⏱️  Duration: {task.get_duration()} minutes")
    print(f"  🎯 Priority: {task.get_priority()}")
    print(f"  📅 Frequency: {task.get_frequency()}")
    print(f"  🔄 Recurs: {task.get_recurs()}")
    print(f"  ✅ Completed: {task.is_completed()}")

    if task.get_next_occurrence():
        print(f"  📆 Next Occurrence: {task.get_next_occurrence()}")

    if task.has_time_window():
        start, end = task.get_time_window()
        print(f"  ⏰ Time Window: {start} - {end}")

    if task.is_mandatory():
        print(f"  ⭐ Mandatory: Yes")


def demo_daily_recurrence():
    """Demonstrate daily task recurrence."""
    print_header("DEMO 1: DAILY TASK RECURRENCE")

    print("\n🎯 Use Case: Daily feeding that automatically recurs")
    print("   When you complete today's feeding, tomorrow's feeding is created")

    # Create a daily feeding task
    feeding = Task("Morning Feeding", "feeding", 15, 8)
    feeding.set_frequency("daily")
    feeding.set_description("Grain-free kibble, 2 cups")

    print_task_details(feeding, "📝 Original Task")

    # Complete the task
    print("\n🔄 Completing the task...")
    next_feeding = feeding.complete_and_recur()

    print_task_details(feeding, "✅ Completed Task")
    print_task_details(next_feeding, "🆕 Next Day's Task")

    print("\n💡 Notice:")
    print("   - Original task is marked complete")
    print("   - New task created for tomorrow")
    print("   - New task has different ID but same properties")
    print("   - Next occurrence is set to tomorrow's date")


def demo_weekly_recurrence():
    """Demonstrate weekly task recurrence."""
    print_header("DEMO 2: WEEKLY TASK RECURRENCE")

    print("\n🎯 Use Case: Weekly grooming that recurs automatically")
    print("   When grooming is done, next week's grooming is scheduled")

    # Create a weekly grooming task
    grooming = Task("Full Grooming Session", "grooming", 60, 6)
    grooming.set_frequency("weekly")
    grooming.set_description("Bath, brush, nail trim, ear cleaning")

    print_task_details(grooming, "📝 Original Task")

    # Complete the task
    print("\n🔄 Completing the task...")
    next_grooming = grooming.complete_and_recur()

    print_task_details(grooming, "✅ Completed Task")
    print_task_details(next_grooming, "🆕 Next Week's Task")

    print("\n💡 Notice:")
    print("   - Next occurrence is 7 days from today")
    print("   - All properties copied to new task")
    print("   - Description preserved")


def demo_non_recurring_task():
    """Demonstrate non-recurring task."""
    print_header("DEMO 3: NON-RECURRING TASK")

    print("\n🎯 Use Case: One-time event that doesn't repeat")
    print("   Example: Vet appointment, special training session")

    # Create a non-recurring task
    vet_visit = Task("Annual Vet Checkup", "medical", 60, 10)
    vet_visit.set_recurs(False)  # Disable recurrence
    vet_visit.set_description("Annual physical exam and vaccinations")

    print_task_details(vet_visit, "📝 Original Task")

    # Complete the task
    print("\n🔄 Completing the task...")
    next_visit = vet_visit.complete_and_recur()

    print_task_details(vet_visit, "✅ Completed Task")

    if next_visit is None:
        print("\n🆕 Next Task: None (task does not recur)")

    print("\n💡 Notice:")
    print("   - Task is completed but doesn't create next occurrence")
    print("   - Useful for one-time events")


def demo_recurring_with_time_window():
    """Demonstrate recurring task with time window constraint."""
    print_header("DEMO 4: RECURRING TASK WITH TIME WINDOW")

    print("\n🎯 Use Case: Daily medication at specific time that recurs")
    print("   Time-sensitive tasks maintain their time windows when recurring")

    # Create daily medication with time window
    medication = Task("Morning Insulin Shot", "meds", 5, 10)
    medication.set_frequency("daily")
    medication.set_time_window("08:00", "09:00")
    medication.set_mandatory(True)
    medication.set_description("Insulin injection with breakfast")

    print_task_details(medication, "📝 Original Task")

    # Complete the task
    print("\n🔄 Completing the task...")
    next_medication = medication.complete_and_recur()

    print_task_details(medication, "✅ Completed Task")
    print_task_details(next_medication, "🆕 Tomorrow's Task")

    print("\n💡 Notice:")
    print("   - Time window preserved (08:00-09:00)")
    print("   - Mandatory status preserved")
    print("   - Tomorrow's dose automatically scheduled")


def demo_recurring_with_dependencies():
    """Demonstrate recurring tasks with dependencies."""
    print_header("DEMO 5: RECURRING TASKS WITH DEPENDENCIES")

    print("\n🎯 Use Case: Medication that depends on feeding, both recurring")
    print("   Dependencies are preserved across recurrences")

    # Create feeding task
    feeding = Task("Breakfast", "feeding", 15, 8)
    feeding.set_frequency("daily")

    # Create medication task that depends on feeding
    medication = Task("Diabetes Medication", "meds", 5, 10)
    medication.set_frequency("daily")
    medication.set_mandatory(True)
    medication.add_prerequisite(feeding)

    print_task_details(feeding, "📝 Task 1: Feeding")
    print_task_details(medication, "📝 Task 2: Medication (depends on feeding)")

    print(f"\n🔗 Dependency: Medication requires Feeding")
    print(f"   Feeding ID: {feeding.get_task_id()[:8]}...")
    print(
        f"   Medication prerequisites: {[pid[:8] + '...' for pid in medication.get_prerequisites()]}"
    )

    # Complete both tasks
    print("\n🔄 Completing feeding...")
    next_feeding = feeding.complete_and_recur()

    print("🔄 Completing medication...")
    next_medication = medication.complete_and_recur()

    print_task_details(next_feeding, "🆕 Tomorrow's Feeding")
    print_task_details(next_medication, "🆕 Tomorrow's Medication")

    print("\n💡 Notice:")
    print("   - Both tasks create next occurrences")
    print("   - Medication still has prerequisite (same feeding task ID)")
    print("   - Note: In real use, you'd need to update prerequisite IDs")
    print("   - Or use a more sophisticated dependency tracking system")


def demo_scheduler_integration():
    """Demonstrate scheduler integration with recurring tasks."""
    print_header("DEMO 6: SCHEDULER INTEGRATION")

    print("\n🎯 Use Case: Completing tasks through scheduler")
    print("   Scheduler automatically adds next occurrence")

    # Create owner and pet
    owner = Owner("Sarah", 120)
    pet = Pet("Max", "dog", 5, "medium")
    scheduler = Scheduler(owner, pet)

    print(f"\n👤 Owner: {owner.get_name()}")
    print(f"🐕 Pet: {pet.get_name()}")

    # Add some recurring tasks
    walk = Task("Morning Walk", "walk", 30, 7)
    walk.set_frequency("daily")

    feeding = Task("Breakfast", "feeding", 15, 8)
    feeding.set_frequency("daily")

    play = Task("Play Session", "playtime", 20, 6)
    play.set_frequency("daily")

    scheduler.add_task(walk)
    scheduler.add_task(feeding)
    scheduler.add_task(play)

    print(f"\n📋 Initial Tasks: {len(scheduler.get_tasks())}")
    print(f"🔄 Recurring Tasks: {len(scheduler.get_recurring_tasks())}")

    for task in scheduler.get_tasks():
        print(f"   - {task.get_name()}")

    # Complete a task through scheduler
    print(f"\n🔄 Completing '{walk.get_name()}' through scheduler...")
    next_walk = scheduler.complete_task(walk.get_task_id())

    print(f"\n📋 Tasks After Completion: {len(scheduler.get_tasks())}")
    print(f"✅ Completed Tasks: {len(scheduler.get_completed_tasks())}")
    print(f"🔄 Recurring Tasks: {len(scheduler.get_recurring_tasks())}")

    print("\nAll tasks:")
    for task in scheduler.get_tasks():
        status = "✅ Complete" if task.is_completed() else "⏳ Pending"
        next_date = (
            f" (Next: {task.get_next_occurrence()})"
            if task.get_next_occurrence()
            else ""
        )
        print(f"   {status} - {task.get_name()}{next_date}")

    print("\n💡 Notice:")
    print("   - Scheduler automatically added next occurrence")
    print("   - Original task still in list (completed)")
    print("   - New task also in list (pending)")
    print("   - Total task count increased by 1")


def demo_multiple_completions():
    """Demonstrate completing task multiple days in a row."""
    print_header("DEMO 7: MULTIPLE COMPLETIONS (SIMULATING DAYS)")

    print("\n🎯 Use Case: Tracking daily task over multiple days")
    print("   See how tasks chain over time")

    # Create a daily feeding task
    feeding = Task("Daily Feeding", "feeding", 15, 8)
    feeding.set_frequency("daily")

    tasks = [feeding]

    print("\n📅 Simulating 5 days of task completion:")

    for day in range(5):
        current_task = tasks[-1]

        print(f"\n--- Day {day + 1} ---")
        print(f"Current task ID: {current_task.get_task_id()[:8]}...")
        print(f"Completed: {current_task.is_completed()}")

        if not current_task.is_completed():
            print("🔄 Completing today's task...")
            next_task = current_task.complete_and_recur()

            if next_task:
                tasks.append(next_task)
                print(f"✅ Task completed!")
                print(f"🆕 Created next occurrence for Day {day + 2}")
                print(f"   Next task ID: {next_task.get_task_id()[:8]}...")

    print(f"\n📊 Summary:")
    print(f"   Total task instances created: {len(tasks)}")
    print(f"   Completed tasks: {sum(1 for t in tasks if t.is_completed())}")
    print(f"   Pending tasks: {sum(1 for t in tasks if not t.is_completed())}")

    print("\n💡 Notice:")
    print("   - Each day creates a new task instance")
    print("   - Chain of tasks spans multiple days")
    print("   - Each task has unique ID")
    print("   - Last task is pending (for next day)")


def demo_monthly_recurrence():
    """Demonstrate monthly task recurrence."""
    print_header("DEMO 8: MONTHLY TASK RECURRENCE")

    print("\n🎯 Use Case: Monthly flea/tick prevention")
    print("   Tasks that happen once per month")

    # Create monthly task
    flea_treatment = Task("Flea & Tick Prevention", "meds", 5, 9)
    flea_treatment.set_frequency("monthly")
    flea_treatment.set_mandatory(True)
    flea_treatment.set_description("Topical flea and tick treatment")

    print_task_details(flea_treatment, "📝 Original Task")

    # Complete the task
    print("\n🔄 Completing the task...")
    next_treatment = flea_treatment.complete_and_recur()

    print_task_details(flea_treatment, "✅ Completed Task")
    print_task_details(next_treatment, "🆕 Next Month's Task")

    print("\n💡 Notice:")
    print("   - Next occurrence is ~30 days from today")
    print("   - Perfect for monthly medications")
    print("   - Prevents forgetting regular treatments")


def main():
    """Run all recurrence demos."""
    print("\n" + "🔄" * 40)
    print("  PAWPAL+ TASK RECURRENCE DEMONSTRATION")
    print("🔄" * 40)

    print("\nThis demo showcases automatic task recurrence:")
    print("  ✅ Daily tasks → Next day")
    print("  ✅ Weekly tasks → Next week")
    print("  ✅ Monthly tasks → Next month")
    print("  ✅ Properties preserved (time windows, dependencies, etc.)")
    print("  ✅ Scheduler integration")

    demo_daily_recurrence()
    input("\n\nPress Enter to continue...")

    demo_weekly_recurrence()
    input("\n\nPress Enter to continue...")

    demo_non_recurring_task()
    input("\n\nPress Enter to continue...")

    demo_recurring_with_time_window()
    input("\n\nPress Enter to continue...")

    demo_recurring_with_dependencies()
    input("\n\nPress Enter to continue...")

    demo_scheduler_integration()
    input("\n\nPress Enter to continue...")

    demo_multiple_completions()
    input("\n\nPress Enter to continue...")

    demo_monthly_recurrence()

    print_header("DEMO COMPLETE")
    print("\n✨ Task recurrence feature demonstration complete!")
    print("\n🎓 Key Takeaways:")
    print("   • Tasks can recur daily, weekly, or monthly")
    print("   • All properties are preserved in new instances")
    print("   • Time windows and dependencies work with recurrence")
    print("   • Scheduler automatically manages recurring tasks")
    print("   • Each occurrence has a unique ID")
    print("   • Perfect for routine pet care tasks")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
