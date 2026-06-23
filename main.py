from datetime import date, time
from pawpal_system import Priority, TimeWindow, Task, Pet, Owner, Scheduler

scheduler = Scheduler()

# ---------------------------------------------------------------------------
# 1. Owner + two Pets
# ---------------------------------------------------------------------------
owner = Owner(
    name="Jordan",
    availability_windows=[
        TimeWindow(time(7, 0), time(9, 30)),
        TimeWindow(time(17, 0), time(20, 0)),
    ],
)

mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age_years=3.0)
luna  = Pet(name="Luna",  species="cat", breed="Tabby",     age_years=5.0)
owner.add_pet(mochi)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# 2. Add tasks OUT OF ORDER (to prove sort_by_time works)
# ---------------------------------------------------------------------------
mochi.add_task(Task("Grooming",        "Brush coat",                  20, "low",    earliest_start=time(9, 0)))
mochi.add_task(Task("Heartworm pill",  "Hide in peanut butter",        5, "medium", recurrence="daily", latest_end=time(9, 0)))
mochi.add_task(Task("Morning walk",    "Leash walk",                  30, "high",   recurrence="daily", earliest_start=time(7, 0)))
mochi.add_task(Task("Breakfast",       "Half cup dry kibble",         10, "high",   recurrence="daily"))

luna.add_task(Task("Playtime",         "Wand toy session",            15, "low",    earliest_start=time(17, 30)))
luna.add_task(Task("Litter box",       "Scoop and add fresh litter",  10, "medium", recurrence="daily"))
luna.add_task(Task("Evening feeding",  "One pouch of wet food",       10, "high",   recurrence="daily", earliest_start=time(17, 0)))

# ---------------------------------------------------------------------------
# 3. Demo: sort_by_time
# ---------------------------------------------------------------------------
print("=" * 55)
print("  TASKS SORTED BY EARLIEST START TIME")
print("=" * 55)
all_tasks = owner.all_tasks()
for t in scheduler.sort_by_time(all_tasks):
    start = t.earliest_start.strftime("%H:%M") if t.earliest_start else "anytime"
    print(f"  {start:>7}  [{t.priority.value:<6}]  {t.title}")

# ---------------------------------------------------------------------------
# 4. Demo: filter_tasks
# ---------------------------------------------------------------------------
print()
print("=" * 55)
print("  FILTER: Mochi's pending tasks only")
print("=" * 55)
for t in scheduler.filter_tasks(owner, pet_name="Mochi", completed=False):
    print(f"  ○ {t.title}")

# ---------------------------------------------------------------------------
# 5. Demo: generate daily plan + conflict detection
# ---------------------------------------------------------------------------
print()
print("=" * 55)
print("  TODAY'S SCHEDULE")
print("=" * 55)
schedule = scheduler.generate_daily_plan(owner, date.today())

for slot in schedule.slots:
    pet = owner.get_pet(slot.pet_id)
    print(f"  {slot.start.strftime('%I:%M %p')} – {slot.end.strftime('%I:%M %p')}"
          f"  {slot.title:<22} ({pet.name if pet else '?'})")

if schedule.skipped_tasks:
    print(f"\n  Skipped: {', '.join(t.title for t in schedule.skipped_tasks)}")

conflicts = scheduler.detect_conflicts(schedule)
if conflicts:
    print()
    for w in conflicts:
        print(f"  ⚠️  {w}")
else:
    print("\n  ✓ No conflicts detected.")

# ---------------------------------------------------------------------------
# 6. Demo: recurring task — complete it, see next occurrence spawn
# ---------------------------------------------------------------------------
print()
print("=" * 55)
print("  RECURRING TASK: complete 'Morning walk' → next occurrence")
print("=" * 55)
walk = next(t for t in mochi.get_tasks() if t.title == "Morning walk")
print(f"  Before: completed={walk.completed}, next_due={walk.next_due}")
mochi.complete_task(walk.id, today=date.today())
print(f"  After:  completed={walk.completed}, next_due={walk.next_due}")
new_walk = next((t for t in mochi.get_tasks() if t.title == "Morning walk" and not t.completed), None)
print(f"  New occurrence created: {new_walk.title if new_walk else 'None'}, completed={new_walk.completed if new_walk else '—'}")

# ---------------------------------------------------------------------------
# 7. Demo: conflict detection with two overlapping tasks
# ---------------------------------------------------------------------------
print()
print("=" * 55)
print("  CONFLICT DETECTION: two tasks at the same time")
print("=" * 55)
test_pet = Pet("TestPet", "dog")
owner.add_pet(test_pet)
test_pet.add_task(Task("Task A", duration_minutes=30, priority="high",   earliest_start=time(8, 0)))
test_pet.add_task(Task("Task B", duration_minutes=30, priority="medium", earliest_start=time(8, 0)))

# Force-build a schedule that will flag these
conflict_schedule = scheduler.generate_daily_plan(owner, date.today())
warnings = scheduler.detect_conflicts(conflict_schedule)
if warnings:
    for w in warnings:
        print(f"  ⚠️  {w}")
else:
    print("  (greedy scheduler resolved the overlap automatically — no raw conflicts in output)")

print()
print("=" * 55)
print(f"  Total scheduled: {len(schedule.slots)} tasks, {schedule.total_minutes_scheduled} min")
print("=" * 55)
