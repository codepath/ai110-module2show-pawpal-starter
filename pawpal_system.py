"""PawPal+ object model.

Mirrors diagrams/uml_draft.mmd. The scheduling logic lives in :meth:`Plan.build`,
which reads the pet's responsibilities and the owner's preferences and produces a
time-ordered schedule plus a human-readable explanation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Numeric weight per priority label; used for sorting tasks.
_PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}

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
        """Add a care task to this pet."""
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

    def priority_weight(self) -> int:
        """Numeric weight for sorting (high=3, medium=2, low=1)."""
        return _PRIORITY_WEIGHTS.get(self.priority, 2)

    def mark_complete(self) -> None:
        """Mark this task as done for the day."""
        self.completed = True


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
        non-essential tasks are filled in by priority while time remains."""
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

        # 2. Order non-essential tasks by priority (high first), shorter first to
        #    fit more in. Essential tasks are handled separately and always kept.
        essential = [t for t in eligible if t.essential]
        optional = sorted(
            (t for t in eligible if not t.essential),
            key=lambda t: (-t.priority_weight(), t.duration_minutes),
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
                "dropped. Remaining tasks are added by priority while the "
                f"{self.constraints.available_minutes}-min budget and "
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
