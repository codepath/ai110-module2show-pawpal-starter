import sys
sys.stdout.reconfigure(encoding="utf-8")

from datetime import time
from tabulate import tabulate
from colorama import init, Fore, Style

from pawpal_system import Owner, Pet, Task, Scheduler, ScheduledTask

# Initialize colorama (handles Windows ANSI support automatically)
init(autoreset=True)

# ── Emoji map ────────────────────────────────────────────────────────────────
# Keywords are matched (case-insensitive) against the task title. First match
# wins; the catch-all at the end guarantees every task gets an icon.
TASK_EMOJIS = [
    (["walk"],                   "🦮"),
    (["feed", "feeding"],        "🍽️ "),
    (["groom", "grooming"],      "✂️ "),
    (["litter"],                 "🧹"),
    (["play", "enrich"],         "🎾"),
    (["vet", "visit"],           "🏥"),
    (["med", "pill", "tablet"],  "💊"),
    (["bath"],                   "🛁"),
    (["train"],                  "🎓"),
    (["nail", "trim"],           "💅"),
]

def task_emoji(title: str) -> str:
    lowered = title.lower()
    for keywords, icon in TASK_EMOJIS:
        if any(kw in lowered for kw in keywords):
            return icon
    return "📋"


# ── Color helpers ─────────────────────────────────────────────────────────────

PRIORITY_COLOR = {
    "high":   Fore.RED    + Style.BRIGHT,
    "medium": Fore.YELLOW + Style.BRIGHT,
    "low":    Fore.GREEN  + Style.BRIGHT,
}

def priority_badge(priority: str) -> str:
    color = PRIORITY_COLOR.get(priority, "")
    label = f" {priority.upper()} "
    return f"{color}[{label}]{Style.RESET_ALL}"

def status_badge(is_completed: bool) -> str:
    if is_completed:
        return Fore.GREEN + Style.BRIGHT + "✅ done   " + Style.RESET_ALL
    return Fore.CYAN + "⏳ pending" + Style.RESET_ALL

def freq_badge(frequency: str) -> str:
    icons = {"daily": "🔁 daily", "weekly": "📅 weekly", "once": "1️⃣  once"}
    return icons.get(frequency, frequency)

def section(number: int, title: str):
    """Print a bold cyan section header."""
    bar = "─" * 56
    print()
    print(Fore.CYAN + Style.BRIGHT + f"┌{bar}┐")
    print(Fore.CYAN + Style.BRIGHT + f"│  {number}. {title:<51}│")
    print(Fore.CYAN + Style.BRIGHT + f"└{bar}┘" + Style.RESET_ALL)


# ── Setup ─────────────────────────────────────────────────────────────────────

owner = Owner(
    name="Jordan",
    available_start=time(7, 0),
    available_end=time(21, 0),
)

luna = Pet(name="Luna", species="dog", age=3)
milo = Pet(name="Milo", species="cat", age=5)

luna.add_task(Task(id=1, title="Grooming",     duration_minutes=20, priority="low",    frequency="once",   preferred_time=time(11, 0)))
luna.add_task(Task(id=2, title="Evening Walk", duration_minutes=30, priority="high",   frequency="daily",  preferred_time=time(18, 0)))
luna.add_task(Task(id=3, title="Morning Walk", duration_minutes=30, priority="high",   frequency="daily",  preferred_time=time(7, 0)))

milo.add_task(Task(id=4, title="Enrichment Play",  duration_minutes=15, priority="medium", frequency="once",  preferred_time=time(10, 0)))
milo.add_task(Task(id=5, title="Litter Box Clean", duration_minutes=5,  priority="medium", frequency="daily", preferred_time=time(9, 0)))
milo.add_task(Task(id=6, title="Feeding",          duration_minutes=10, priority="high",   frequency="daily", preferred_time=time(8, 0)))

# Mark Grooming as completed to prove recurring logic filters it out
luna.tasks[0].mark_complete()

scheduler = Scheduler(owner=owner)
scheduler.add_pet(luna)
scheduler.add_pet(milo)

# ── Banner ────────────────────────────────────────────────────────────────────

print()
print(Fore.MAGENTA + Style.BRIGHT + "  🐾  PawPal+ — Daily Schedule Demo")
print(Fore.MAGENTA + "  " + "═" * 38)
print(f"  Owner : {Style.BRIGHT}{owner.name}{Style.RESET_ALL}")
print(f"  Window: {owner.available_start.strftime('%I:%M %p')} – {owner.available_end.strftime('%I:%M %p')}"
      f"  ({owner.get_total_available_time()} min available)")
print(f"  Pets  : {', '.join(p.name + ' (' + p.species + ')' for p in scheduler.pets)}")


# ── 1. ALL TASKS (unsorted) ───────────────────────────────────────────────────

section(1, "ALL TASKS  (as added — unsorted)")

rows = []
for t in scheduler.get_all_tasks():
    pt = t.preferred_time.strftime("%I:%M %p") if t.preferred_time else "—"
    rows.append([
        task_emoji(t.title) + " " + t.title,
        t.pet_name,
        priority_badge(t.priority),
        freq_badge(t.frequency),
        pt,
        status_badge(t.is_completed),
    ])

print(tabulate(
    rows,
    headers=["Task", "Pet", "Priority", "Frequency", "Preferred", "Status"],
    tablefmt="rounded_outline",
))


# ── 2. SORTED by priority + preferred_time ────────────────────────────────────

section(2, "SORTED  by priority → preferred time")

sorted_tasks = scheduler._sort_by_priority(scheduler.get_all_tasks())
rows = []
for i, t in enumerate(sorted_tasks, 1):
    pt = t.preferred_time.strftime("%I:%M %p") if t.preferred_time else "—"
    rows.append([
        str(i),
        task_emoji(t.title) + " " + t.title,
        t.pet_name,
        priority_badge(t.priority),
        pt,
    ])

print(tabulate(
    rows,
    headers=["#", "Task", "Pet", "Priority", "Preferred Time"],
    tablefmt="rounded_outline",
))


# ── 3. FILTER — high priority only ────────────────────────────────────────────

section(3, "FILTER  — high priority tasks only")

rows = []
for t in scheduler.filter_by_priority("high"):
    rows.append([
        task_emoji(t.title) + " " + t.title,
        t.pet_name,
        freq_badge(t.frequency),
        f"{t.duration_minutes} min",
    ])

print(tabulate(rows, headers=["Task", "Pet", "Frequency", "Duration"], tablefmt="rounded_outline"))


# ── 4. FILTER — Luna's tasks ──────────────────────────────────────────────────

section(4, "FILTER  — Luna's tasks only")

rows = []
for t in scheduler.filter_by_pet("Luna"):
    rows.append([
        task_emoji(t.title) + " " + t.title,
        priority_badge(t.priority),
        freq_badge(t.frequency),
        status_badge(t.is_completed),
    ])

print(tabulate(rows, headers=["Task", "Priority", "Frequency", "Status"], tablefmt="rounded_outline"))


# ── 5. RECURRING — eligible tasks today ──────────────────────────────────────

section(5, "RECURRING  — eligible tasks for today")
print(f"  {Fore.YELLOW}(completed one-time tasks are excluded){Style.RESET_ALL}\n")

rows = []
for t in scheduler.generate_recurring_tasks():
    rows.append([
        task_emoji(t.title) + " " + t.title,
        t.pet_name,
        freq_badge(t.frequency),
        priority_badge(t.priority),
    ])

print(tabulate(rows, headers=["Task", "Pet", "Frequency", "Priority"], tablefmt="rounded_outline"))


# ── 6. TODAY'S SCHEDULE ───────────────────────────────────────────────────────

section(6, f"TODAY'S SCHEDULE  — {owner.name}")

schedule = scheduler.build_schedule()

rows = []
for st in schedule:
    t = st.task
    start_str = st.start_time.strftime("%I:%M %p")
    end_str   = st.end_time.strftime("%I:%M %p")
    time_range = f"{start_str} – {end_str}"
    rows.append([
        Fore.WHITE + Style.BRIGHT + time_range + Style.RESET_ALL,
        task_emoji(t.title) + " " + t.title,
        t.pet_name,
        priority_badge(t.priority),
        freq_badge(t.frequency),
        f"{t.duration_minutes} min",
    ])

print(tabulate(
    rows,
    headers=["Time Slot", "Task", "Pet", "Priority", "Frequency", "Duration"],
    tablefmt="rounded_outline",
))

# Summary line
sched_count = len(schedule)
skip_count  = len(scheduler.skipped_tasks)
print(f"\n  {Fore.GREEN + Style.BRIGHT}✅ Scheduled: {sched_count}{Style.RESET_ALL}  "
      f"{Fore.RED + Style.BRIGHT}⛔ Skipped: {skip_count}{Style.RESET_ALL}")

if scheduler.skipped_tasks:
    print(f"\n  {Fore.RED + Style.BRIGHT}⛔  Tasks that didn't fit in the window:{Style.RESET_ALL}")
    for t in scheduler.skipped_tasks:
        print(f"     {task_emoji(t.title)} {t.pet_name}: {t.title}  ({t.duration_minutes} min)")


# ── 7. CONFLICT CHECK — single task probe ────────────────────────────────────

section(7, "CONFLICT CHECK  — single task probe")

test_task = Task(id=99, title="Vet Visit", duration_minutes=60, priority="high")
first_start = schedule[0].start_time
last_end    = schedule[-1].end_time

checks = [
    (first_start, "overlaps first slot → expect conflict"),
    (last_end,    "starts after last slot → expect clear"),
]

rows = []
for proposed, note in checks:
    conflict = scheduler.check_conflicts(test_task, proposed_start=proposed)
    if conflict:
        result = Fore.RED + Style.BRIGHT + "⚠️  CONFLICT" + Style.RESET_ALL
    else:
        result = Fore.GREEN + Style.BRIGHT + "✅  CLEAR" + Style.RESET_ALL
    rows.append([
        "🏥 Vet Visit (60 min)",
        proposed.strftime("%I:%M %p"),
        note,
        result,
    ])

print(tabulate(rows, headers=["Task", "Proposed Start", "Notes", "Result"], tablefmt="rounded_outline"))


# ── 8. WARN_CONFLICTS — injected overlap ─────────────────────────────────────

section(8, "WARN_CONFLICTS  — manually injected overlap")
print(f"  {Fore.YELLOW}Injecting two overlapping tasks to trigger the conflict scanner…{Style.RESET_ALL}\n")

conflict_task_a = Task(id=91, title="Vet Visit", duration_minutes=60, priority="high",   pet_name="Luna")
conflict_task_b = Task(id=92, title="Nail Trim", duration_minutes=30, priority="medium", pet_name="Milo")

scheduler.scheduled_tasks.append(ScheduledTask(task=conflict_task_a, start_time=time(10, 0),  reason="manually injected"))
scheduler.scheduled_tasks.append(ScheduledTask(task=conflict_task_b, start_time=time(10, 30), reason="manually injected"))

warnings = scheduler.warn_conflicts()
if warnings:
    for msg in warnings:
        print(f"  {Fore.RED + Style.BRIGHT}⚠️  {msg}{Style.RESET_ALL}")
else:
    print(f"  {Fore.GREEN}✅  No conflicts detected.{Style.RESET_ALL}")


# ── 9. FIND NEXT SLOT ─────────────────────────────────────────────────────────

section(9, "FIND NEXT SLOT  — gap-scan demo")

probe_tasks = [
    Task(id=201, title="Vet Visit",    duration_minutes=60,  priority="high"),
    Task(id=202, title="Training",     duration_minutes=20,  priority="medium"),
    Task(id=203, title="Bath",         duration_minutes=45,  priority="low"),
    Task(id=204, title="Long Hike",    duration_minutes=600, priority="medium"),
]

# Use a clean scheduler (no injected conflicts) for a clean gap-scan demo
clean_sched = Scheduler(owner=owner)
clean_sched.add_pet(luna)
clean_sched.add_pet(milo)
clean_sched.build_schedule()

rows = []
for pt in probe_tasks:
    slot = clean_sched.find_next_slot(pt)
    if slot:
        slot_str = Fore.GREEN + Style.BRIGHT + slot.strftime("%I:%M %p") + Style.RESET_ALL
    else:
        slot_str = Fore.RED + Style.BRIGHT + "⛔  no slot" + Style.RESET_ALL
    rows.append([
        task_emoji(pt.title) + " " + pt.title,
        f"{pt.duration_minutes} min",
        priority_badge(pt.priority),
        slot_str,
    ])

print(tabulate(rows, headers=["Task", "Duration", "Priority", "Next Available Slot"], tablefmt="rounded_outline"))

print()
print(Fore.MAGENTA + Style.BRIGHT + "  🐾  End of demo." + Style.RESET_ALL)
print()
