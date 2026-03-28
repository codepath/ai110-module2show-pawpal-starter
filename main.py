"""
main.py — demo / testing ground for PawPal+ logic
Run: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


# ── 1. Create owner ──────────────────────────────────────────────────────────
jordan = Owner(name="Jordan", available_start="08:00", available_end="20:00")

# ── 2. Create pets ───────────────────────────────────────────────────────────
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# ── 3. Add tasks to Mochi (dog) ──────────────────────────────────────────────
mochi.add_task(Task(title="Morning walk",    duration_minutes=30, priority="high",   frequency="daily"))
mochi.add_task(Task(title="Feeding",         duration_minutes=10, priority="high",   frequency="daily"))
mochi.add_task(Task(title="Grooming",        duration_minutes=20, priority="medium", frequency="weekly"))

# ── 4. Add tasks to Luna (cat) ───────────────────────────────────────────────
luna.add_task(Task(title="Feeding",          duration_minutes=10, priority="high",   frequency="daily"))
luna.add_task(Task(title="Litter box clean", duration_minutes=10, priority="high",   frequency="daily"))
luna.add_task(Task(title="Playtime",         duration_minutes=15, priority="low",    frequency="daily"))

# ── 5. Register pets with owner ──────────────────────────────────────────────
jordan.add_pet(mochi)
jordan.add_pet(luna)

# ── 6. Build schedule ────────────────────────────────────────────────────────
scheduler = Scheduler(owner=jordan)
scheduler.build_schedule()

# ── 7. Print Today's Schedule ────────────────────────────────────────────────
WIDTH = 56

def divider(char="─"):
    print(char * WIDTH)

def section(title):
    divider()
    print(f"  {title}")
    divider()

print()
print("=" * WIDTH)
print(f"  🐾  PawPal+  —  Daily Schedule for {jordan.name}")
print("=" * WIDTH)
print(f"  Window : {jordan.available_start} – {jordan.available_end}")
print(f"  Pets   : {', '.join(p.name for p in jordan.pets)}")
print()

section("TODAY'S TASKS")
for item in scheduler.schedule:
    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item.task.priority, "⚪")
    print(f"  {item.start_time}–{item.end_time}  {priority_icon} [{item.pet.name}] {item.task.title}")
    print(f"           {item.task.duration_minutes} min  ·  {item.task.frequency}")
    if item.reason:
        print(f"           {item.reason}")
    print()

if scheduler.skipped:
    section("SKIPPED  (didn't fit)")
    for pet, task in scheduler.skipped:
        print(f"  ✗ [{pet.name}] {task.title} ({task.duration_minutes} min)")
    print()

divider("=")
completed = sum(1 for item in scheduler.schedule if item.task.completed)
total     = len(scheduler.schedule)
print(f"  {completed}/{total} tasks completed")
divider("=")
print()
