"""
main.py — demo / testing ground for PawPal+ logic
Demonstrates: sorting, filtering, recurring tasks, and conflict detection.
Run: python main.py
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

WIDTH = 60

def divider(char="─"): print(char * WIDTH)
def section(title):
    print()
    divider()
    print(f"  {title}")
    divider()

# ── Setup ────────────────────────────────────────────────────────────────────
jordan = Owner(name="Jordan", available_start="08:00", available_end="20:00")

mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# Tasks added intentionally OUT OF ORDER to prove sort_by_time() works
mochi.add_task(Task("Evening walk",    30, "high",   "daily",  due_date=date.today()))
mochi.add_task(Task("Feeding",         10, "high",   "daily",  due_date=date.today()))
mochi.add_task(Task("Morning walk",    30, "high",   "daily",  due_date=date.today()))
mochi.add_task(Task("Grooming",        20, "medium", "weekly", due_date=date.today()))

luna.add_task(Task("Feeding",          10, "high",   "daily",  due_date=date.today()))
luna.add_task(Task("Litter box clean", 10, "high",   "daily",  due_date=date.today()))
luna.add_task(Task("Playtime",         15, "low",    "daily",  due_date=date.today()))

jordan.add_pet(mochi)
jordan.add_pet(luna)

scheduler = Scheduler(owner=jordan)
scheduler.build_schedule()

# ── 1. Full schedule ─────────────────────────────────────────────────────────
print()
print("=" * WIDTH)
print(f"  🐾  PawPal+  —  Daily Schedule for {jordan.name}")
print("=" * WIDTH)
print(f"  Window : {jordan.available_start} – {jordan.available_end}")
print(f"  Pets   : {', '.join(p.name for p in jordan.pets)}")

section("TODAY'S TASKS  (sorted by priority, then duration)")
for item in scheduler.schedule:
    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item.task.priority, "⚪")
    print(f"  {item.start_time}–{item.end_time}  {icon} [{item.pet.name}] {item.task.title}")
    print(f"           {item.task.duration_minutes} min  ·  {item.task.frequency}")

# ── 2. Sort by time ──────────────────────────────────────────────────────────
section("SORTED BY START TIME  (sort_by_time)")
for item in scheduler.sort_by_time():
    print(f"  {item.start_time}  [{item.pet.name}] {item.task.title}")

# ── 3. Filter by pet name ────────────────────────────────────────────────────
section("FILTER: only Mochi's tasks  (filter_tasks pet_name='Mochi')")
for item in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"  {item.start_time}–{item.end_time}  {item.task.title}")

# ── 4. Mark complete + recurring next occurrence ─────────────────────────────
section("RECURRING TASK DEMO  (mark_complete → next_occurrence)")
print("  Marking 'Feeding' complete for Mochi...")
scheduler.mark_complete("Feeding")

feeding_tasks = [t for t in mochi.tasks if t.title == "Feeding"]
for t in feeding_tasks:
    status = "✓ done" if t.completed else f"○ next due {t.due_date}"
    print(f"  [{t.title}]  {status}")

section("FILTER: completed tasks only  (filter_tasks completed=True)")
for item in scheduler.filter_tasks(completed=True):
    print(f"  ✓ [{item.pet.name}] {item.task.title}")

section("FILTER: pending tasks only  (filter_tasks completed=False)")
for item in scheduler.filter_tasks(completed=False):
    print(f"  ○ [{item.pet.name}] {item.task.title}")

# ── 5. Conflict detection ────────────────────────────────────────────────────
section("CONFLICT DETECTION  (no conflicts expected above)")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  ✅  No conflicts detected.")

# ── Summary ──────────────────────────────────────────────────────────────────
print()
divider("=")
completed = sum(1 for item in scheduler.schedule if item.task.completed)
total     = len(scheduler.schedule)
print(f"  {completed}/{total} tasks completed")
divider("=")
print()
