"""
PawPal+ Advanced Features Demo
Demonstrates the three new scheduling enhancements:
1. Time-Window Constraints
2. Task Dependencies
3. Dynamic Priority Adjustment
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_plan(plan, title="DAILY SCHEDULE"):
    """Pretty print a plan."""
    print(f"\n📅 {title}")
    print("-" * 80)

    scheduled_tasks = plan.get_scheduled_tasks()

    if scheduled_tasks:
        print(f"\n✅ Scheduled Tasks ({len(scheduled_tasks)}):\n")
        for scheduled_task in scheduled_tasks:
            task = scheduled_task.get_task()
            print(
                f"  {scheduled_task.get_order()}. [{scheduled_task.get_start_time()} - {scheduled_task.get_end_time()}] "
                f"{task.get_name()}"
            )

            details = []
            details.append(f"Type: {task.get_task_type()}")
            details.append(f"Duration: {task.get_duration()} min")
            details.append(f"Priority: {task.get_priority()}")

            if task.is_mandatory():
                details.append("⭐ MANDATORY")
            if task.has_time_window():
                start, end = task.get_time_window()
                details.append(f"Window: {start}-{end}")
            if task.has_prerequisites():
                details.append(f"Has {len(task.get_prerequisites())} prerequisite(s)")

            print(f"     {' | '.join(details)}")

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

    print(f"\n📝 Explanation:\n")
    for line in plan.get_explanation().split("\n"):
        print(f"  {line}")


def demo_time_windows():
    """Demonstrate Feature 1: Time-Window Constraints."""
    print_header("FEATURE 1: TIME-WINDOW CONSTRAINTS")

    print("\n🎯 Use Case: Some tasks MUST happen at specific times")
    print("   Example: Morning medication at 8-9am, Evening walk after 5pm")

    owner = Owner("Alice", 150)  # 2.5 hours available
    pet = Pet("Max", "dog", 8, "medium")
    pet.add_special_need("arthritis - requires timed medication")

    print(f"\n👤 Owner: {owner.get_name()}")
    print(
        f"🐕 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    scheduler = Scheduler(owner, pet)

    # Morning medication MUST be between 8:00-9:00
    morning_meds = Task("Morning Arthritis Medication", "meds", 5, 10)
    morning_meds.set_mandatory(True)
    morning_meds.set_time_window("08:00", "09:00")
    morning_meds.set_description("Must be given with food, between 8-9am")

    # Breakfast can be anytime in the morning
    breakfast = Task("Breakfast", "feeding", 15, 9)
    breakfast.set_time_window("08:00", "10:00")

    # Walk - flexible timing
    walk = Task("Morning Walk", "walk", 30, 7)

    # Evening medication MUST be between 6:00-7:00 PM
    evening_meds = Task("Evening Arthritis Medication", "meds", 5, 10)
    evening_meds.set_mandatory(True)
    evening_meds.set_time_window("18:00", "19:00")
    evening_meds.set_description("Must be given with food, between 6-7pm")

    # Play session - anytime
    play = Task("Indoor Play", "playtime", 20, 6)

    scheduler.add_task(morning_meds)
    scheduler.add_task(breakfast)
    scheduler.add_task(walk)
    scheduler.add_task(evening_meds)
    scheduler.add_task(play)

    plan = scheduler.generate_plan()
    print_plan(plan)

    print("\n💡 Notice:")
    print("   - Morning medication is scheduled within 08:00-09:00 window")
    print("   - Evening medication is scheduled within 18:00-19:00 window")
    print("   - Flexible tasks fill in the remaining time")


def demo_task_dependencies():
    """Demonstrate Feature 2: Task Dependencies."""
    print_header("FEATURE 2: TASK DEPENDENCIES")

    print("\n🎯 Use Case: Some tasks must happen in a specific order")
    print("   Example: Feed before medicine, Bath before grooming")

    owner = Owner("Bob", 120)  # 2 hours available
    pet = Pet("Luna", "cat", 4, "small")
    pet.add_special_need("diabetes - insulin with meals")

    print(f"\n👤 Owner: {owner.get_name()}")
    print(
        f"🐱 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    scheduler = Scheduler(owner, pet)

    # Create tasks with dependencies
    breakfast = Task("Breakfast", "feeding", 10, 8)
    breakfast.set_description("Diabetic formula wet food")

    # Insulin MUST come after feeding
    insulin = Task("Morning Insulin Shot", "meds", 5, 10)
    insulin.set_mandatory(True)
    insulin.set_description("MUST be given immediately after breakfast")
    insulin.add_prerequisite(breakfast)  # ← Dependency!

    # Exercise after medication
    play = Task("Interactive Play", "enrichment", 20, 7)
    play.set_description("Helps regulate blood sugar")
    play.add_prerequisite(insulin)  # ← Dependency chain: breakfast → insulin → play

    # Litter box - no dependencies
    litter = Task("Litter Box Cleaning", "grooming", 10, 6)

    # Brushing - can happen anytime
    brush = Task("Brushing", "grooming", 15, 5)

    print("\n🔗 Dependency Chain:")
    print("   Breakfast → Insulin → Play")
    print("   (Litter and Brushing are independent)")

    # Add tasks in RANDOM order to test dependency resolution
    scheduler.add_task(play)
    scheduler.add_task(brush)
    scheduler.add_task(insulin)
    scheduler.add_task(litter)
    scheduler.add_task(breakfast)

    plan = scheduler.generate_plan()
    print_plan(plan)

    print("\n💡 Notice:")
    print("   - Despite being added randomly, tasks are in correct dependency order")
    print("   - Breakfast → Insulin → Play sequence is maintained")
    print("   - Independent tasks (litter, brush) fit around the dependency chain")


def demo_dynamic_priority():
    """Demonstrate Feature 3: Dynamic Priority Adjustment."""
    print_header("FEATURE 3: DYNAMIC PRIORITY ADJUSTMENT")

    print("\n🎯 Use Case: Tasks get more urgent as time passes since last completion")
    print("   Example: Grooming is low priority, but after a week it becomes urgent")

    owner = Owner("Carol", 90)  # 1.5 hours available
    pet = Pet("Buddy", "dog", 3, "large")

    print(f"\n👤 Owner: {owner.get_name()}")
    print(
        f"🐕 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    scheduler = Scheduler(owner, pet)

    # Task 1: Done today - base priority 5
    feeding = Task("Feeding", "feeding", 15, 5)
    feeding.set_last_completed(date.today())
    feeding.set_description("Done today - no boost")

    # Task 2: Done 2 days ago - base priority 4, gets +1 boost = 5
    play = Task("Playtime", "playtime", 25, 4)
    play.set_last_completed(date.today() - timedelta(days=2))
    play.set_description("Done 2 days ago - gets +1 priority boost")

    # Task 3: Done 4 days ago - base priority 3, gets +2 boost = 5
    grooming = Task("Brushing & Nail Trim", "grooming", 30, 3)
    grooming.set_last_completed(date.today() - timedelta(days=4))
    grooming.set_description("Done 4 days ago - gets +2 priority boost")

    # Task 4: Done 10 days ago! - base priority 2, gets +3 boost = 5
    bath = Task("Bath", "grooming", 45, 2)
    bath.set_last_completed(date.today() - timedelta(days=10))
    bath.set_description("Done 10 days ago! - gets +3 priority boost")

    # Task 5: Never done - base priority 6, max boost
    training = Task("Obedience Training", "training", 20, 6)
    training.set_description("Never completed - gets max boost")

    print("\n📊 Task Priorities (Base → Dynamic):")
    print(
        f"   1. Feeding:      {feeding.get_priority()} → {feeding.get_dynamic_priority()} (done today)"
    )
    print(
        f"   2. Playtime:     {play.get_priority()} → {play.get_dynamic_priority()} (2 days ago)"
    )
    print(
        f"   3. Grooming:     {grooming.get_priority()} → {grooming.get_dynamic_priority()} (4 days ago)"
    )
    print(
        f"   4. Bath:         {bath.get_priority()} → {bath.get_dynamic_priority()} (10 days ago)"
    )
    print(
        f"   5. Training:     {training.get_priority()} → {training.get_dynamic_priority()} (never)"
    )

    scheduler.add_task(feeding)
    scheduler.add_task(play)
    scheduler.add_task(grooming)
    scheduler.add_task(bath)
    scheduler.add_task(training)

    plan = scheduler.generate_plan()
    print_plan(plan)

    print("\n💡 Notice:")
    print("   - Tasks are prioritized by adjusted priority, not base priority")
    print("   - Old tasks (Bath, Grooming) scheduled before recent tasks")
    print("   - This prevents important tasks from being perpetually skipped")


def demo_all_features_combined():
    """Demonstrate all three features working together."""
    print_header("COMBINED DEMO: ALL THREE FEATURES TOGETHER")

    print("\n🎯 Real-World Scenario: Senior dog with special needs")

    owner = Owner("Dr. Sarah", 180)  # 3 hours available
    pet = Pet("Rex", "dog", 12, "large")
    pet.add_special_need("senior dog - arthritis and diabetes")
    pet.add_special_need("requires timed medication and monitored exercise")

    print(f"\n👤 Owner: {owner.get_name()}")
    print(
        f"🐕 Pet: {pet.get_name()} (Age {pet.get_age()}, {pet.get_size()} {pet.get_species()})"
    )
    print(f"💊 Special Needs: {', '.join(pet.get_special_needs())}")
    print(f"⏰ Available Time: {owner.get_available_time()} minutes")

    scheduler = Scheduler(owner, pet)

    # Morning routine with dependencies and time windows
    breakfast = Task("Breakfast", "feeding", 15, 8)
    breakfast.set_time_window("07:00", "09:00")
    breakfast.set_last_completed(date.today() - timedelta(days=1))

    insulin = Task("Insulin Shot", "meds", 5, 10)
    insulin.set_mandatory(True)
    insulin.set_time_window("07:30", "09:30")
    insulin.add_prerequisite(breakfast)  # After feeding

    arthritis_med = Task("Arthritis Medication", "meds", 5, 10)
    arthritis_med.set_mandatory(True)
    arthritis_med.set_time_window("08:00", "10:00")
    arthritis_med.add_prerequisite(breakfast)  # With food

    # Gentle exercise after medications settle
    gentle_walk = Task("Gentle Morning Walk", "walk", 20, 7)
    gentle_walk.set_description("Short, slow walk for senior dog")
    gentle_walk.add_prerequisite(insulin)
    gentle_walk.add_prerequisite(arthritis_med)
    gentle_walk.set_last_completed(date.today() - timedelta(days=1))

    # Grooming - hasn't been done in a while
    nail_trim = Task("Nail Trimming", "grooming", 15, 3)
    nail_trim.set_last_completed(date.today() - timedelta(days=14))  # 2 weeks!

    # Physical therapy exercises
    pt_exercises = Task("Physical Therapy Exercises", "enrichment", 15, 5)
    pt_exercises.set_description("Gentle stretches for arthritis")
    pt_exercises.set_last_completed(date.today() - timedelta(days=3))

    # Mental enrichment
    puzzle = Task("Puzzle Feeder", "enrichment", 20, 4)
    puzzle.set_description("Mental stimulation")
    puzzle.set_last_completed(date.today())

    print("\n🔧 Features Applied:")
    print("   ⏰ Time Windows: Medications must be at specific times")
    print("   🔗 Dependencies: Medications after feeding, walk after meds settle")
    print("   📈 Dynamic Priority: Nail trim boosted (14 days old!)")

    scheduler.add_task(breakfast)
    scheduler.add_task(insulin)
    scheduler.add_task(arthritis_med)
    scheduler.add_task(gentle_walk)
    scheduler.add_task(nail_trim)
    scheduler.add_task(pt_exercises)
    scheduler.add_task(puzzle)

    plan = scheduler.generate_plan()
    print_plan(plan, "REX'S SENIOR CARE SCHEDULE")

    print("\n💡 Analysis:")
    print("   - All mandatory medications scheduled within time windows")
    print("   - Dependency chain maintained: breakfast → meds → walk")
    print("   - Nail trim prioritized despite low base priority (14 days overdue!)")
    print("   - Recent tasks (puzzle) scheduled last or excluded")


def main():
    """Run all advanced feature demos."""
    print("\n" + "🐾" * 40)
    print("  PAWPAL+ ADVANCED FEATURES DEMONSTRATION")
    print("🐾" * 40)

    print("\nThis demo showcases three new intelligent scheduling features:")
    print("  1️⃣  Time-Window Constraints - Tasks at specific times")
    print("  2️⃣  Task Dependencies - Tasks in required order")
    print("  3️⃣  Dynamic Priority Adjustment - Urgency increases with time")

    demo_time_windows()

    input("\n\nPress Enter to continue to Feature 2...")

    demo_task_dependencies()

    input("\n\nPress Enter to continue to Feature 3...")

    demo_dynamic_priority()

    input("\n\nPress Enter to see all features combined...")

    demo_all_features_combined()

    print_header("DEMO COMPLETE")
    print("\n✨ All three advanced features demonstrated successfully!")
    print("\n🎓 Key Takeaways:")
    print("   • Time windows ensure critical tasks happen at the right time")
    print("   • Dependencies maintain logical task ordering automatically")
    print("   • Dynamic priority prevents important tasks from being neglected")
    print("   • All features work together seamlessly for realistic scheduling")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
