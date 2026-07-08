"""
PawPal+ CLI Demo
================
Verifies backend logic in the terminal before touching the Streamlit UI.
Usage:  python main.py
"""
from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler

LINE = "-" * 62


def _fmt(tasks):
    """Print a formatted list of tasks."""
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        status = "✓" if t.completed else "✗"
        print(
            f"  {t.time}  {t.pet_name:<10} {t.name:<24}"
            f"[{t.priority.upper():<8}] {t.frequency:<7} {status}"
        )


def main():
    print("=== PawPal+ CLI Demo ===\n")

    # ── Build sample data ──────────────────────────────────────────────────────
    owner     = Owner(name="Jordan")
    scheduler = Scheduler(owner)
    today     = date.today()

    mochi    = Pet(name="Mochi",    species="Dog", breed="Shiba Inu",          age_years=3.0)
    whiskers = Pet(name="Whiskers", species="Cat", breed="Domestic Shorthair", age_years=5.0)
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    mochi.add_task(Task("Morning walk",       "07:30", "high",     "daily",  "Mochi",    due_date=today))
    mochi.add_task(Task("Morning feeding",    "08:00", "critical", "daily",  "Mochi",    due_date=today))
    mochi.add_task(Task("Training session",   "17:00", "medium",   "weekly", "Mochi",    due_date=today))
    mochi.add_task(Task("Evening walk",       "18:00", "high",     "daily",  "Mochi",    due_date=today))
    mochi.add_task(Task("Evening medication", "20:00", "critical", "daily",  "Mochi",    due_date=today))

    whiskers.add_task(Task("Breakfast",       "08:30", "high",     "daily",  "Whiskers", due_date=today))
    whiskers.add_task(Task("Afternoon meds",  "13:00", "critical", "daily",  "Whiskers", due_date=today))
    whiskers.add_task(Task("Evening feeding", "19:00", "high",     "daily",  "Whiskers", due_date=today))

    print(f"Owner : {owner.name}")
    print(f"Pets  : {', '.join(f'{p.name} ({p.species})' for p in owner.pets)}\n")

    # ── Today's schedule ───────────────────────────────────────────────────────
    print(LINE)
    print("TODAY'S SCHEDULE  (Scheduler.todays_schedule — sorted by time)")
    print(LINE)
    _fmt(scheduler.todays_schedule(today))

    # ── Conflict check (clean) ─────────────────────────────────────────────────
    print(f"\n{LINE}")
    print("CONFLICT CHECK  (Scheduler.detect_conflicts)")
    print(LINE)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for c in conflicts:
            print(f"  {c}")
    else:
        print("  No scheduling conflicts detected.")

    # ── Inject a conflict ──────────────────────────────────────────────────────
    print(f"\n{LINE}")
    print("DEMO: Adding 'Vet call' at 20:00 for Mochi  (duplicate → conflict)")
    print(LINE)
    mochi.add_task(Task("Vet call follow-up", "20:00", "high", "once", "Mochi", due_date=today))
    for c in scheduler.detect_conflicts():
        print(f"  {c}")

    # ── Filter by pet ──────────────────────────────────────────────────────────
    print(f"\n{LINE}")
    print("FILTER: Incomplete tasks for Mochi  (filter_by_pet + filter_by_status)")
    print(LINE)
    mochi_tasks   = scheduler.filter_by_pet("Mochi")
    mochi_pending = scheduler.filter_by_status(completed=False, tasks=mochi_tasks)
    _fmt(scheduler.sort_by_time(mochi_pending))

    # ── Mark complete + recurrence ─────────────────────────────────────────────
    print(f"\n{LINE}")
    print("DEMO: Mark 'Morning walk' done  (daily → auto-reschedule)")
    print(LINE)
    walk      = next(t for t in mochi.get_tasks() if t.name == "Morning walk")
    next_task = scheduler.mark_task_complete(walk)
    print(f"  ✓  '{walk.name}' marked complete.")
    if next_task:
        print(f"  ↻  Next occurrence → {next_task.due_date} at {next_task.time}  [{next_task.frequency}]")

    # ── Completed tasks ────────────────────────────────────────────────────────
    print(f"\n{LINE}")
    print("COMPLETED TASKS  (filter_by_status completed=True)")
    print(LINE)
    _fmt(scheduler.filter_by_status(completed=True))

    print(f"\n{LINE}")
    print("Demo complete. All backend methods verified.")
    print(LINE)


if __name__ == "__main__":
    main()
