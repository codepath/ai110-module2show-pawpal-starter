from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

buddy = Pet(
    name="Buddy",
    species="Dog",
    age=4,
    daily_needs=["Morning walk", "Feeding"],
    special_needs=["Medication - joint supplement"],
)

luna = Pet(
    name="Luna",
    species="Cat",
    age=2,
    daily_needs=["Feeding"],
    special_needs=[],
)

# ---------------------------------------------------------------------------
# Tasks — added intentionally OUT OF ORDER to exercise sort_tasks_by_time()
# ---------------------------------------------------------------------------

# Buddy's tasks (added latest-first so sorting is visible)
evening_walk = Task(
    title="Evening walk",
    duration_minutes=25,
    priority="medium",
    task_type="exercise",
    required=False,
    earliest_start="18:00",
    latest_end="19:30",
)

joint_med = Task(
    title="Joint supplement",
    duration_minutes=5,
    priority="high",
    task_type="medication",
    required=True,
    earliest_start="08:00",
    latest_end="09:00",
)

morning_walk = Task(
    title="Morning walk",
    duration_minutes=30,
    priority="high",
    task_type="exercise",
    required=True,
    earliest_start="07:00",
    latest_end="09:00",
)

buddy_feeding = Task(
    title="Buddy — feeding",
    duration_minutes=10,
    priority="medium",
    task_type="feeding",
    required=True,
    earliest_start="07:30",
    latest_end="08:30",
    recurrence="daily",
)

# Luna's tasks (also out of order — evening before morning)
enrichment = Task(
    title="Luna — play / enrichment",
    duration_minutes=20,
    priority="low",
    task_type="enrichment",
    required=False,
    earliest_start="17:00",
    latest_end="19:00",
    recurrence="weekdays",
)

luna_feeding = Task(
    title="Luna — feeding",
    duration_minutes=10,
    priority="medium",
    task_type="feeding",
    required=True,
    earliest_start="08:00",
    latest_end="09:00",
    recurrence="daily",
)

# No time window — should sink to the bottom when sorted by time
grooming = Task(
    title="Buddy — grooming",
    duration_minutes=15,
    priority="low",
    task_type="grooming",
    required=False,
    # earliest_start / latest_end intentionally omitted
)

# Add tasks in the out-of-order sequence defined above
buddy.add_task(evening_walk)   # 18:00  ← added first but should sort last
buddy.add_task(joint_med)      # 08:00
buddy.add_task(morning_walk)   # 07:00  ← should sort first
buddy.add_task(buddy_feeding)  # 07:30
buddy.add_task(grooming)       # None   ← no window, should sink to end

luna.add_task(enrichment)      # 17:00  ← added first but should sort after morning
luna.add_task(luna_feeding)    # 08:00

# Two tasks intentionally sharing overlapping windows to trigger conflict detection.
# Both run 08:00-09:00 — a same-pet clash for Buddy.
vet_checkup = Task(
    title="Vet check-up",
    duration_minutes=45,
    priority="high",
    task_type="medical",
    required=True,
    earliest_start="08:00",
    latest_end="09:00",
)

# A cross-pet clash: Luna's feeding (08:00-09:00) will also conflict with vet_checkup
# because they share the same window even though they belong to different pets.
buddy.add_task(vet_checkup)

# Mark one task complete so status filtering is visible
joint_med.mark_complete()

# ---------------------------------------------------------------------------
# Owner & Scheduler
# ---------------------------------------------------------------------------

owner = Owner(
    name="Alex",
    preferences={"morning": True, "evening": False},
    available_minutes=120,
    available_windows=[("07:00", "09:00"), ("17:00", "19:00")],
)

owner.add_pet(buddy)
owner.add_pet(luna)

scheduler = Scheduler(owner=owner)
all_tasks = owner.all_tasks()

# ---------------------------------------------------------------------------
# Demo 1 — Sort by time
# ---------------------------------------------------------------------------

print("=" * 50)
print("  SORT BY EARLIEST START TIME")
print("  (tasks were added out of order)")
print("=" * 50)
sorted_tasks = scheduler.sort_tasks_by_time(all_tasks)
for task in sorted_tasks:
    window = (
        f"{task.earliest_start} – {task.latest_end}"
        if task.earliest_start
        else "no window"
    )
    print(f"  [{window:>22}]  {task.title}")

# ---------------------------------------------------------------------------
# Demo 2 — Filter by pet name
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("  FILTER BY PET: Buddy only")
print("=" * 50)
buddy_tasks = scheduler.filter_tasks(all_tasks, pet_name="Buddy")
for task in buddy_tasks:
    print(f"  {task.title} ({task.duration_minutes} min, {task.priority})")

print()
print("=" * 50)
print("  FILTER BY PET: Luna only")
print("=" * 50)
luna_tasks = scheduler.filter_tasks(all_tasks, pet_name="Luna")
for task in luna_tasks:
    print(f"  {task.title} ({task.duration_minutes} min, {task.priority})")

# ---------------------------------------------------------------------------
# Demo 3 — Filter by completion status
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("  FILTER BY STATUS: Pending tasks")
print("=" * 50)
pending = scheduler.filter_tasks(all_tasks, completed=False)
for task in pending:
    print(f"  {task.title}")

print()
print("=" * 50)
print("  FILTER BY STATUS: Completed tasks")
print("=" * 50)
completed = scheduler.filter_tasks(all_tasks, completed=True)
for task in completed:
    print(f"  {task.title}")

# ---------------------------------------------------------------------------
# Demo 4 — Combine: Buddy's pending tasks, sorted by time
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("  COMBINED: Buddy pending tasks, time-sorted")
print("=" * 50)
buddy_pending = scheduler.filter_tasks(all_tasks, pet_name="Buddy", completed=False)
buddy_pending_sorted = scheduler.sort_tasks_by_time(buddy_pending)
for task in buddy_pending_sorted:
    window = (
        f"{task.earliest_start} – {task.latest_end}"
        if task.earliest_start
        else "no window"
    )
    print(f"  [{window:>22}]  {task.title}")

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Demo 5 — Conflict detection
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("  CONFLICT DETECTION: conflict_warnings()")
print("=" * 50)
warnings = scheduler.conflict_warnings()
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts found.")

# ---------------------------------------------------------------------------
# Schedule — runs BEFORE recurring demo so extra task copies don't add noise
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("         PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 50)
# generate_schedule also calls conflict_warnings() internally and prints them
schedule = scheduler.generate_schedule()
print(scheduler.explain_plan(schedule))
print("=" * 50)

# ---------------------------------------------------------------------------
# Demo 6 — Recurring task: complete and reschedule
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("  RECURRING TASK: complete_and_reschedule()")
print("=" * 50)

# Give buddy_feeding an explicit due_date so the output is deterministic
buddy_feeding.due_date = date.today()

print(f"  Before: '{buddy_feeding.title}'")
print(f"    recurrence : {buddy_feeding.recurrence}")
print(f"    due_date   : {buddy_feeding.due_date}  (today)")
print(f"    completed  : {buddy_feeding.completed}")

next_feeding = scheduler.complete_and_reschedule(buddy_feeding)

print(f"\n  After marking complete:")
print(f"    completed  : {buddy_feeding.completed}")

if next_feeding:
    print(f"\n  Next occurrence auto-created:")
    print(f"    title      : {next_feeding.title}")
    print(f"    due_date   : {next_feeding.due_date}  (today + 1 day via timedelta)")
    print(f"    completed  : {next_feeding.completed}")
    print(f"    pet_name   : {next_feeding.pet_name}")

# Same demo for a weekdays recurring task (enrichment)
print()
print("  — Weekdays recurrence —")
enrichment.due_date = date.today()
next_enrichment = scheduler.complete_and_reschedule(enrichment)
if next_enrichment:
    delta = next_enrichment.due_date - date.today()
    print(f"  '{enrichment.title}' -> next due: {next_enrichment.due_date}  (+{delta.days} day(s), skipping weekends via timedelta)")
