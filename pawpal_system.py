"""PawPal+ object model.

Mirrors diagrams/uml_draft.mmd. The scheduling logic lives in :meth:`Plan.build`,
which reads the pet's responsibilities and the owner's preferences and produces a
time-ordered schedule plus a human-readable explanation.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace


# Numeric weight per priority label; used for sorting tasks.
_PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}

# Weighted-score coefficients (see Responsibility.priority_score). The tier
# weight dominates so a more essential task is scheduled first; the per-minute
# penalty only nudges ordering — it takes a large duration gap (> one tier's
# worth of minutes) for a shorter, lower-tier task to overtake a higher one.
_PRIORITY_TIER_WEIGHT = 100
_DURATION_PENALTY = 1

# Earliest preferred clock time (minutes since midnight) for a part of day.
# Used to honor owner preferences such as {"walk_time": "afternoon"}.
_TIME_OF_DAY_START = {"morning": 7 * 60, "afternoon": 12 * 60, "evening": 17 * 60}


def to_minutes(hhmm: str) -> int:
    """Convert a ``"HH:MM"`` clock string to minutes since midnight (e.g.
    ``"08:30"`` -> ``510``)."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight back to a ``"HH:MM"`` string (e.g.
    ``510`` -> ``"08:30"``)."""
    hours, mins = divmod(int(minutes), 60)
    return f"{hours:02d}:{mins:02d}"


@dataclass
class Pet:
    """The animal being cared for. Owns the care tasks it needs."""

    name: str
    species: str = "dog"  # "dog" | "cat" | "other"
    energy_level: str = "medium"  # "low" | "medium" | "high"
    notes: str = ""
    responsibilities: list[Responsibility] = field(default_factory=list)

    def add_responsibility(self, task: Responsibility) -> None:
        """Add a care task to this pet.

        Links the task back to this pet so completing a recurring task can
        enqueue its next occurrence automatically (see
        :meth:`Responsibility.mark_complete`)."""
        task.pet = self
        self.responsibilities.append(task)


@dataclass
class Owner:
    """The person doing the caring. Holds durable preferences; the day's
    budget and window live in ``Constraints``."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)  # e.g. {"walk_time": "morning"}

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Responsibility]:
        """Return this owner's tasks, optionally filtered.

        Pass ``completed=True``/``False`` to keep only finished/unfinished tasks,
        and/or ``pet_name`` to keep only tasks belonging to that pet. Filters
        that are left as ``None`` are not applied; with no arguments every task
        across all pets is returned.
        """
        tasks: list[Responsibility] = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.responsibilities:
                if completed is not None and task.completed != completed:
                    continue
                tasks.append(task)
        return tasks


@dataclass
class Responsibility:
    """One unit of care work (walk, feeding, meds, enrichment, grooming, ...)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # walk | feeding | meds | enrichment | grooming
    recurrence: str = "daily"  # "daily" | "weekly"
    weekday: str | None = None  # for weekly tasks: the day they run, e.g. "Monday"
    fixed_time: str | None = None  # e.g. "08:00" for meds pinned to a time
    essential: bool = False  # meds/feeding that must never be dropped
    completed: bool = False  # whether the owner has finished this task today
    # Back-reference to the owning pet, set by Pet.add_responsibility. Excluded
    # from repr/eq to avoid an infinite Pet<->Responsibility reference cycle.
    pet: Pet | None = field(default=None, repr=False, compare=False)

    def priority_weight(self) -> int:
        """Numeric weight for the priority tier (high=3, medium=2, low=1)."""
        return _PRIORITY_WEIGHTS.get(self.priority, 2)

    def priority_score(self) -> float:
        """Weighted score used to rank optional tasks (higher = scheduled first).

        A weighted sum of two factors: the priority tier (heavily weighted, so a
        more essential task is prioritized) minus a small per-minute penalty (so
        that among comparably-important tasks the shorter, more efficient one
        goes first). The tier weight dominates, so a higher-priority task
        normally outranks a lower one regardless of length; only an extreme
        duration gap — more than one tier's worth of minutes — can let a short
        lower-tier task overtake a much longer higher-tier one."""
        return _PRIORITY_TIER_WEIGHT * self.priority_weight() - _DURATION_PENALTY * self.duration_minutes

    def next_occurrence(self) -> Responsibility:
        """A fresh, uncompleted copy of this task for its next scheduled day.

        The model carries no concrete date on a task (dates live on ``Plan``),
        so the next occurrence is simply this task reset to not-completed; its
        ``recurrence``/``weekday`` already say when it next runs."""
        return replace(self, completed=False)

    def mark_complete(self) -> None:
        """Mark this task as done for the day.

        For recurring tasks (``daily``/``weekly``), automatically enqueue the
        next occurrence on the same pet so the work reappears once today's is
        finished. No-op if already completed, so calling twice won't spawn
        duplicates."""
        if self.completed:
            return
        self.completed = True
        if self.recurrence in ("daily", "weekly") and self.pet is not None:
            self.pet.add_responsibility(self.next_occurrence())


@dataclass
class Constraints:
    """The day's context and limits handed to the plan.

    ``available_minutes`` is the hard budget cap (total minutes of work allowed);
    ``day_start``/``day_end`` is the clock window tasks must be placed within.
    ``build()`` must honor both: a task fits only if it stays under the budget
    *and* lands inside the window.
    """

    available_minutes: int
    day_start: str = "07:00"
    day_end: str = "21:00"
    day_of_week: str = "Monday"

    def has_time_for(self, remaining_minutes: int, duration: int) -> bool:
        """Whether ``duration`` still fits within the remaining budget."""
        return duration <= remaining_minutes

    def window_minutes(self) -> int:
        """Length of the clock window (``day_end`` - ``day_start``) in minutes."""
        return to_minutes(self.day_end) - to_minutes(self.day_start)


@dataclass
class Explanation:
    """The reasoning behind the whole plan."""

    summary: str = ""
    strategy: str = ""
    reasons: list[str] = field(default_factory=list)
    skipped_reasons: list[str] = field(default_factory=list)

    def as_text(self) -> str:
        """Render the explanation as markdown for the UI."""
        lines: list[str] = []
        if self.summary:
            lines.append(f"**{self.summary}**")
        if self.strategy:
            lines.append("")
            lines.append(self.strategy)
        if self.reasons:
            lines.append("")
            lines.append("**Why these tasks:**")
            lines.extend(f"- {reason}" for reason in self.reasons)
        if self.skipped_reasons:
            lines.append("")
            lines.append("**What was skipped:**")
            lines.extend(f"- {reason}" for reason in self.skipped_reasons)
        return "\n".join(lines)


@dataclass
class Scheduler:
    """One responsibility placed at a concrete time slot in the plan."""

    responsibility: Responsibility
    start_time: str  # "HH:MM"
    end_time: str  # "HH:MM"

    def start_minutes(self) -> int:
        """Start time as minutes since midnight; the key used for sorting."""
        return to_minutes(self.start_time)

    @staticmethod
    def sort_by_time(items: list[Scheduler]) -> list[Scheduler]:
        """Return ``items`` sorted into clock order by their start time."""
        return sorted(items, key=lambda item: item.start_minutes())


@dataclass
class Plan:
    """The daily plan: holds the inputs it was built from and the schedule it
    produces. Construct from an owner + one of their pets + constraints, then
    call :meth:`build` (which reads ``pet.responsibilities`` and
    ``owner.preferences``)."""

    owner: Owner
    pet: Pet
    constraints: Constraints
    date: str = ""

    # Results, populated by build().
    scheduled: list[Scheduler] = field(default_factory=list)
    skipped: list[Responsibility] = field(default_factory=list)
    explanation: Explanation = field(default_factory=Explanation)

    def build(self) -> None:
        """Run the scheduling logic, populating ``scheduled``, ``skipped`` and
        ``explanation``.

        Reads tasks from ``self.pet.responsibilities`` and applies
        ``self.owner.preferences``. Essential responsibilities are scheduled
        first and are never dropped, even if doing so exceeds the budget;
        non-essential tasks are filled in by their weighted priority score
        (tier blended with duration efficiency) while time remains."""
        # Reset results so build() is idempotent.
        self.scheduled = []
        self.skipped = []
        reasons: list[str] = []
        skipped_reasons: list[str] = []

        window_start = to_minutes(self.constraints.day_start)
        window_end = to_minutes(self.constraints.day_end)

        # 1. Keep only tasks that run today (daily, or weekly on this weekday).
        #    Tasks already finished today are done with: they neither take a slot
        #    nor consume the budget.
        eligible: list[Responsibility] = []
        for task in self.pet.responsibilities:
            if task.completed:
                continue
            if task.recurrence == "weekly" and task.weekday != self.constraints.day_of_week:
                self.skipped.append(task)
                skipped_reasons.append(
                    f"{task.title}: weekly task runs on {task.weekday}, "
                    f"not {self.constraints.day_of_week}."
                )
                continue
            eligible.append(task)

        # 2. Rank non-essential tasks by their weighted priority score (tier
        #    heavily weighted, minus a small per-minute penalty), highest first,
        #    so more essential tasks come first and shorter ones break near-ties.
        #    Essential tasks are handled separately and always kept.
        essential = [t for t in eligible if t.essential]
        optional = sorted(
            (t for t in eligible if not t.essential),
            key=lambda t: -t.priority_score(),
        )

        # 3. Select tasks against the time budget. Essentials are forced in even
        #    if they push the total over the budget; optionals fill what's left.
        remaining = self.constraints.available_minutes
        selected: list[Responsibility] = []
        for task in essential:
            selected.append(task)
            remaining -= task.duration_minutes
        for task in optional:
            if self.constraints.has_time_for(remaining, task.duration_minutes):
                selected.append(task)
                remaining -= task.duration_minutes
            else:
                self.skipped.append(task)
                skipped_reasons.append(
                    f"{task.title}: not enough time left in the {self.constraints.available_minutes}-min "
                    f"budget ({task.duration_minutes} min needed, {max(remaining, 0)} min free)."
                )

        # 4. Place selected tasks on the clock in two passes so flexible work can
        #    flow *around* the fixed appointments instead of colliding with them.
        placed: list[Scheduler] = []
        occupied: list[tuple[int, int]] = []  # (start, end) of placed tasks

        # 4a. Pin fixed-time tasks first. Drop a non-essential one that falls
        #     outside the day window or overlaps an already-pinned slot; essential
        #     fixed tasks (meds/feeding) are kept regardless.
        fixed = sorted(
            (t for t in selected if t.fixed_time is not None),
            key=lambda t: to_minutes(t.fixed_time),
        )
        for task in fixed:
            start = to_minutes(task.fixed_time)
            end = start + task.duration_minutes
            if not task.essential and (start < window_start or end > window_end):
                self.skipped.append(task)
                skipped_reasons.append(
                    f"{task.title}: fixed at {task.fixed_time}, outside the "
                    f"{self.constraints.day_start}-{self.constraints.day_end} window."
                )
                continue
            if not task.essential and self._overlaps(start, end, occupied):
                self.skipped.append(task)
                skipped_reasons.append(
                    f"{task.title}: its fixed {task.fixed_time} slot overlaps another task."
                )
                continue
            placed.append(Scheduler(task, to_hhmm(start), to_hhmm(end)))
            occupied.append((start, end))
            reasons.append(self._reason_for(task, start, end))

        occupied.sort()

        # 4b. Flow flexible tasks from a moving cursor, sliding each past any
        #     pinned slot it would run into, nudged toward the owner's preferred
        #     time of day where one applies.
        cursor = window_start
        flexible = sorted(
            (t for t in selected if t.fixed_time is None),
            key=lambda t: self._earliest_start(t, window_start),
        )
        for task in flexible:
            start = max(cursor, self._earliest_start(task, window_start))
            end = start + task.duration_minutes
            for slot_start, slot_end in occupied:  # occupied is sorted by start
                if start < slot_end and slot_start < end:
                    start = slot_end
                    end = start + task.duration_minutes

            # Tasks that spill past the end of the day are dropped unless they
            # are essential (those run regardless, late if need be).
            if end > window_end and not task.essential:
                self.skipped.append(task)
                skipped_reasons.append(
                    f"{task.title}: would end at {to_hhmm(end)}, past the "
                    f"{self.constraints.day_end} cut-off."
                )
                continue

            placed.append(Scheduler(task, to_hhmm(start), to_hhmm(end)))
            cursor = end
            reasons.append(self._reason_for(task, start, end))

        # 5. Present the schedule in clock order.
        placed.sort(key=lambda item: to_minutes(item.start_time))
        self.scheduled = placed

        # 6. Summarize the run for the UI.
        total_tasks = len(self.scheduled) + len(self.skipped)
        self.explanation = Explanation(
            summary=(
                f"Planned {len(self.scheduled)} of {total_tasks} tasks "
                f"({self.total_minutes()} min of care) for {self.pet.name}."
            ),
            strategy=(
                "Essential tasks (feeding, meds) are scheduled first and never "
                "dropped. Remaining tasks are added by weighted priority (higher "
                "tiers first, shorter tasks breaking near-ties) "
                f"while the {self.constraints.available_minutes}-min budget and "
                f"{self.constraints.day_start}-{self.constraints.day_end} window allow."
            ),
            reasons=reasons,
            skipped_reasons=skipped_reasons,
        )

    @staticmethod
    def _overlaps(start: int, end: int, intervals: list[tuple[int, int]]) -> bool:
        """Whether ``[start, end)`` overlaps any of the given intervals."""
        return any(start < slot_end and slot_start < end for slot_start, slot_end in intervals)

    def _earliest_start(self, task: Responsibility, window_start: int) -> int:
        """Earliest minute a flexible ``task`` may start, ignoring the cursor.

        Honors an owner preference like ``{"walk_time": "afternoon"}`` by not
        starting a matching task before its preferred part of the day."""
        preferred = self.owner.preferences.get(f"{task.category}_time")
        return _TIME_OF_DAY_START.get(preferred, window_start) if preferred else window_start

    def _reason_for(self, task: Responsibility, start: int, end: int) -> str:
        """One-line justification for placing ``task`` at the given slot."""
        why = "essential" if task.essential else f"{task.priority} priority"
        slot = f"{to_hhmm(start)}-{to_hhmm(end)}"
        return f"{task.title} ({task.category}, {why}) scheduled {slot}."

    def total_minutes(self) -> int:
        """Total minutes of scheduled work."""
        return sum(item.responsibility.duration_minutes for item in self.scheduled)

    def detect_conflicts(self) -> str:
        """Check the schedule for overlapping time slots.

        Returns a human-readable warning message listing any overlaps, or an
        empty string when the schedule is clean. This is intentionally
        non-fatal: it surfaces problems (e.g. two essential tasks pinned to the
        same time, which ``build`` keeps regardless) as a warning rather than
        raising, so callers can show it and carry on."""
        # Work in clock order, then compare every slot against each earlier one.
        # Checking all earlier slots (not just the immediate neighbor) catches a
        # long task that overlaps a later one with a short task nested between.
        ordered = Scheduler.sort_by_time(self.scheduled)
        overlaps: list[str] = []
        for i in range(len(ordered)):
            later = ordered[i]
            for j in range(i):
                earlier = ordered[j]
                # They overlap when the later task starts before the earlier ends.
                if later.start_minutes() < to_minutes(earlier.end_time):
                    overlaps.append(
                        f"'{earlier.responsibility.title}' "
                        f"({earlier.start_time}-{earlier.end_time}) overlaps "
                        f"'{later.responsibility.title}' "
                        f"({later.start_time}-{later.end_time})"
                    )
        if not overlaps:
            return ""
        return "Warning - schedule conflict: " + "; ".join(overlaps) + "."

    def as_rows(self) -> list[dict]:
        """Schedule as table rows for the Streamlit display (reads ``scheduled``)."""
        return [
            {
                "Start": item.start_time,
                "End": item.end_time,
                "Task": item.responsibility.title,
                "Category": item.responsibility.category,
                "Priority": item.responsibility.priority,
                "Minutes": item.responsibility.duration_minutes,
            }
            for item in self.scheduled
        ]
