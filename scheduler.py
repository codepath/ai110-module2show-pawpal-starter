from __future__ import annotations

from datetime import datetime, date
from typing import List

from models import (
    DailyPlan, Frequency, OwnerPreferences, Pet, Priority,
    ScheduledTask, Task, TaskType,
)

# ── Time slots ────────────────────────────────────────────────────────────────

TIME_SLOTS: list[str] = [
    "Morning (7–9 am)",
    "Mid-Morning (10 am–12 pm)",
    "Afternoon (12–3 pm)",
    "Late Afternoon (3–6 pm)",
    "Evening (6–9 pm)",
    "Night (9–11 pm)",
]

# Preferred slots per task type, ordered best → fallback.
SLOT_PREFERENCES: dict[TaskType, list[str]] = {
    TaskType.WALK:       ["Morning (7–9 am)", "Late Afternoon (3–6 pm)", "Evening (6–9 pm)"],
    TaskType.FEEDING:    ["Morning (7–9 am)", "Afternoon (12–3 pm)", "Evening (6–9 pm)"],
    TaskType.MEDICATION: ["Morning (7–9 am)", "Evening (6–9 pm)"],
    TaskType.ENRICHMENT: ["Mid-Morning (10 am–12 pm)", "Afternoon (12–3 pm)", "Late Afternoon (3–6 pm)"],
    TaskType.GROOMING:   ["Mid-Morning (10 am–12 pm)", "Afternoon (12–3 pm)"],
    TaskType.TRAINING:   ["Morning (7–9 am)", "Late Afternoon (3–6 pm)"],
    TaskType.VET_VISIT:  ["Morning (7–9 am)", "Mid-Morning (10 am–12 pm)"],
}

SLOT_CAPACITY_MINUTES = 90  # soft cap per time slot


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_task(task: Task, as_of: datetime) -> float:
    """Return a scheduling priority score. Higher → schedule sooner."""
    priority_score   = task.priority.value * 20          # 20–100
    overdue_bonus    = min(task.hours_overdue(as_of) * 1.5, 60)
    never_done_bonus = 10.0 if task.last_done is None else 0.0
    return priority_score + overdue_bonus + never_done_bonus


# ── Slot assignment ───────────────────────────────────────────────────────────

def _pick_slot(task: Task, slot_used: dict[str, int]) -> str:
    preferred = SLOT_PREFERENCES.get(task.task_type, TIME_SLOTS)
    for slot in preferred:
        if slot_used.get(slot, 0) + task.duration_minutes <= SLOT_CAPACITY_MINUTES:
            return slot
    for slot in TIME_SLOTS:
        if slot_used.get(slot, 0) + task.duration_minutes <= SLOT_CAPACITY_MINUTES:
            return slot
    return preferred[0]  # last-resort; slot will be over capacity


# ── Reason builders ───────────────────────────────────────────────────────────

def _task_reason(task: Task, score: float, as_of: datetime) -> str:
    parts: list[str] = []
    if task.last_done is None:
        parts.append("never done before")
    else:
        h = task.hours_overdue(as_of)
        parts.append(f"{h:.0f}h overdue" if h >= 1 else "just became due")

    label = {
        Priority.CRITICAL: "critical — must not skip",
        Priority.HIGH:     "high priority",
        Priority.MEDIUM:   "medium priority",
        Priority.LOW:      "low priority",
        Priority.OPTIONAL: "optional today",
    }[task.priority]
    parts.append(label)

    return f"{'; '.join(parts)} · score {score:.0f}"


def _overall_reason(
    scheduled: list[ScheduledTask],
    skipped: list[Task],
    not_due: list[Task],
    prefs: OwnerPreferences,
    used: int,
) -> str:
    n = len(scheduled)
    lines = [
        f"{n} task{'s' if n != 1 else ''} scheduled, "
        f"using {used} of {prefs.available_minutes} available minutes."
    ]

    critical = [s for s in scheduled if s.task.priority == Priority.CRITICAL]
    if critical:
        names = ", ".join(s.task.name for s in critical)
        lines.append(f"Critical tasks locked in first: {names}.")

    if skipped:
        names = ", ".join(t.name for t in skipped)
        lines.append(
            f"{len(skipped)} task{'s' if len(skipped) != 1 else ''} skipped "
            f"(wouldn't fit in time budget): {names}. "
            "Consider freeing up time or shortening their duration."
        )

    if not_due:
        names = ", ".join(t.name for t in not_due)
        lines.append(f"Not yet due today: {names}.")

    return " ".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

def generate_plan(pet: Pet, prefs: OwnerPreferences, plan_date: date) -> DailyPlan:
    """
    Build a daily care plan for *pet* given owner *prefs*.

    Algorithm:
      1. Filter to active, due tasks.
      2. Score each task (priority × 20 + overdue-hours × 1.5 + never-done bonus).
      3. Sort descending by score; break ties by duration (shorter first, better budget fit).
      4. Greedy fill: schedule as many tasks as fit in prefs.available_minutes.
      5. Assign each task its preferred time slot.
    """
    as_of = datetime.combine(plan_date, datetime.min.time())

    active  = [t for t in pet.tasks if t.is_active]
    due     = [t for t in active if t.is_due(as_of)]
    not_due = [t for t in active if not t.is_due(as_of)]

    # Highest score first; ties broken by shorter duration (budget efficiency)
    ordered = sorted(due, key=lambda t: (-score_task(t, as_of), t.duration_minutes))

    scheduled: list[ScheduledTask] = []
    skipped:   list[Task]          = []
    remaining  = prefs.available_minutes
    slot_used: dict[str, int] = dict.fromkeys(TIME_SLOTS, 0)

    for task in ordered:
        if task.duration_minutes > remaining:
            skipped.append(task)
            continue
        sc   = score_task(task, as_of)
        slot = _pick_slot(task, slot_used)
        slot_used[slot] += task.duration_minutes
        scheduled.append(ScheduledTask(
            task=task,
            time_slot=slot,
            score=sc,
            reason=_task_reason(task, sc, as_of),
        ))
        remaining -= task.duration_minutes

    used = prefs.available_minutes - remaining
    return DailyPlan(
        plan_date=plan_date,
        pet=pet,
        owner=prefs,
        scheduled=scheduled,
        skipped=skipped,
        not_due=not_due,
        total_minutes_used=used,
        overall_reasoning=_overall_reason(scheduled, skipped, not_due, prefs, used),
    )
