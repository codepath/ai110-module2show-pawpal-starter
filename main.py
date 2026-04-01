"""
PawPal+ Demo Script
Demonstrates the pet scheduling system with Owner, Pet, Task, and Scheduler classes
"""

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    print("=" * 60)
    print("🐾 PawPal+ - Pet Care Scheduling System")
    print("=" * 60)
    print()
    
    # Create an Owner
    owner = Owner(
        name="Jordan",
        available_time=120,  # 120 minutes available
        preferences={"feeding_time": "morning", "exercise_preference": "evening"}
    )
    print(f"✅ Owner created: {owner.name}")
    print(f"   Available time: {owner.available_time} minutes")
    print()
    
    # Create Pet 1: Mochi (Dog)
    mochi = Pet(
        name="Mochi",
        pet_type="dog",
        age=3
    )
    print(f"✅ Pet 1 created: {mochi.name} ({mochi.pet_type}, age {mochi.age})")
    
    # Create Pet 2: Luna (Cat)
    luna = Pet(
        name="Luna",
        pet_type="cat",
        age=2
    )
    print(f"✅ Pet 2 created: {luna.name} ({luna.pet_type}, age {luna.age})")
    print()
    
    # Add pets to owner
    owner.add_pet(mochi)
    owner.add_pet(luna)
    print(f"✅ Pets added to owner. Total pets: {len(owner.get_pets())}")
    print()
    
    # ===== TASKS FOR MOCHI =====
    print("📋 Adding tasks for Mochi...")
    
    # Task 1: Morning Walk
    task1 = Task(
        task_name="Morning Walk",
        duration=30,
        priority=1,
        prefered_time="morning",
        frequency="daily"
    )
    mochi.add_task(task1)
    print(f"   ✅ {task1.task_name} - {task1.duration} min (Priority: {task1.priority})")
    
    # Task 2: Feeding
    task2 = Task(
        task_name="Feeding",
        duration=15,
        priority=1,
        prefered_time="morning",
        frequency="daily"
    )
    mochi.add_task(task2)
    print(f"   ✅ {task2.task_name} - {task2.duration} min (Priority: {task2.priority})")
    
    # Task 3: Playtime
    task3 = Task(
        task_name="Playtime",
        duration=45,
        priority=2,
        prefered_time="afternoon",
        frequency="daily"
    )
    mochi.add_task(task3)
    print(f"   ✅ {task3.task_name} - {task3.duration} min (Priority: {task3.priority})")
    
    # Task 4: Grooming
    task4 = Task(
        task_name="Grooming",
        duration=60,
        priority=3,
        frequency="weekly"
    )
    mochi.add_task(task4)
    print(f"   ✅ {task4.task_name} - {task4.duration} min (Priority: {task4.priority})")
    print()
    
    # ===== TASKS FOR LUNA =====
    print("📋 Adding tasks for Luna...")
    
    # Task 5: Feeding
    task5 = Task(
        task_name="Feeding",
        duration=10,
        priority=1,
        prefered_time="morning",
        frequency="daily"
    )
    luna.add_task(task5)
    print(f"   ✅ {task5.task_name} - {task5.duration} min (Priority: {task5.priority})")
    
    # Task 6: Litter Box Cleaning
    task6 = Task(
        task_name="Litter Box Cleaning",
        duration=20,
        priority=2,
        frequency="daily"
    )
    luna.add_task(task6)
    print(f"   ✅ {task6.task_name} - {task6.duration} min (Priority: {task6.priority})")
    
    # Task 7: Playtime with toys
    task7 = Task(
        task_name="Interactive Play",
        duration=25,
        priority=2,
        prefered_time="afternoon",
        frequency="daily"
    )
    luna.add_task(task7)
    print(f"   ✅ {task7.task_name} - {task7.duration} min (Priority: {task7.priority})")
    print()
    
    # ===== GENERATE SCHEDULES =====
    print("=" * 60)
    print("📅 TODAY'S SCHEDULE")
    print("=" * 60)
    print()
    
    # Schedule for Mochi
    print(f"🐕 Schedule for {mochi.name}:")
    print("-" * 60)
    scheduler_mochi = Scheduler(owner, mochi, owner.available_time)
    scheduler_mochi.generate_plan()
    print(scheduler_mochi.explain_plan())
    print()
    
    # Schedule for Luna
    print(f"🐈 Schedule for {luna.name}:")
    print("-" * 60)
    scheduler_luna = Scheduler(owner, luna, owner.available_time)
    scheduler_luna.generate_plan()
    print(scheduler_luna.explain_plan())
    print()
    
    # ===== DEMONSTRATE FILTERING FEATURES =====
    print("=" * 60)
    print("🔍 STEP 2: FILTERING FEATURES (Multiple Pets)")
    print("=" * 60)
    print()
    
    # Note: Mark some tasks as completed first to demonstrate filtering
    mochi.update_task_status(task1.task_id, "completed")
    mochi.update_task_status(task2.task_id, "in-progress")
    
    # Feature 1: Filter by Status
    print("1️⃣ FILTER BY STATUS - Showing Mochi's tasks:")
    scheduler_mochi = Scheduler(owner, mochi)
    
    pending = scheduler_mochi.filter_by_status("pending")
    print(f"   Pending tasks: {len(pending)}")
    for t in pending:
        print(f"     • {t.task_name}")
    
    in_progress = scheduler_mochi.filter_by_status("in-progress")
    print(f"   In-Progress tasks: {len(in_progress)}")
    for t in in_progress:
        print(f"     • {t.task_name}")
    
    completed = scheduler_mochi.filter_by_status("completed")
    print(f"   Completed tasks: {len(completed)}")
    for t in completed:
        print(f"     • {t.task_name}")
    print()
    
    # Feature 2: Filter by Time Slot
    print("2️⃣ FILTER BY TIME SLOT - Showing all pets' tasks:")
    
    print("   MOCHI:")
    mochi_morning = scheduler_mochi.filter_by_time_slot("morning")
    print(f"     Morning tasks: {len(mochi_morning)}")
    for t in mochi_morning:
        print(f"       • {t.task_name}")
    
    mochi_afternoon = scheduler_mochi.filter_by_time_slot("afternoon")
    print(f"     Afternoon tasks: {len(mochi_afternoon)}")
    for t in mochi_afternoon:
        print(f"       • {t.task_name}")
    
    mochi_flexible = scheduler_mochi.filter_by_time_slot("flexible")
    print(f"     Flexible tasks: {len(mochi_flexible)}")
    for t in mochi_flexible:
        print(f"       • {t.task_name}")
    print()
    
    print("   LUNA:")
    scheduler_luna_for_demo = Scheduler(owner, luna)
    luna_morning = scheduler_luna_for_demo.filter_by_time_slot("morning")
    print(f"     Morning tasks: {len(luna_morning)}")
    for t in luna_morning:
        print(f"       • {t.task_name}")
    
    luna_afternoon = scheduler_luna_for_demo.filter_by_time_slot("afternoon")
    print(f"     Afternoon tasks: {len(luna_afternoon)}")
    for t in luna_afternoon:
        print(f"       • {t.task_name}")
    
    luna_flexible = scheduler_luna_for_demo.filter_by_time_slot("flexible")
    print(f"     Flexible tasks: {len(luna_flexible)}")
    for t in luna_flexible:
        print(f"       • {t.task_name}")
    print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Owner: {owner.name}")
    print(f"Total pets: {len(owner.get_pets())}")
    print(f"Mochi - Total tasks: {len(mochi.get_tasks())}, Total duration: {mochi.get_total_duration()} min")
    print(f"Luna - Total tasks: {len(luna.get_tasks())}, Total duration: {luna.get_total_duration()} min")
    print(f"Available time: {owner.available_time} minutes")
    print()
    print("✅ Demo completed successfully!")


if __name__ == "__main__":
    main()
