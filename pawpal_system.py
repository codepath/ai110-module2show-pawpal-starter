"""PawPal+ object model (skeleton).

Mirrors diagrams/uml_draft.mmd. Attributes are fully defined; methods are
stubs (``raise NotImplementedError``) to be implemented in a later step.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def to_minutes(hhmm: str) -> int:
    """Convert a ``"HH:MM"`` clock string to minutes since midnight (e.g.
    ``"08:30"`` -> ``510``)."""
    raise NotImplementedError


def to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight back to a ``"HH:MM"`` string (e.g.
    ``510`` -> ``"08:30"``)."""
    raise NotImplementedError


@dataclass
class Pet:
    """The animal being cared for. Owns the care tasks it needs."""

    name: str
    species: str = "dog"  # "dog" | "cat" | "other"
    energy_level: str = "medium"  # "low" | "medium" | "high"
    notes: str = ""
    responsibilities: list[Responsibility] = field(default_factory=list)


@dataclass
class Owner:
    """The person doing the caring. Holds durable preferences; the day's
    budget and window live in ``Constraints``."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)  # e.g. {"walk_time": "morning"}

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        raise NotImplementedError


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

    def priority_weight(self) -> int:
        """Numeric weight for sorting (high=3, medium=2, low=1)."""
        raise NotImplementedError


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
        raise NotImplementedError

    def window_minutes(self) -> int:
        """Length of the clock window (``day_end`` - ``day_start``) in minutes."""
        raise NotImplementedError


@dataclass
class Explanation:
    """The reasoning behind the whole plan."""

    summary: str = ""
    strategy: str = ""
    reasons: list[str] = field(default_factory=list)
    skipped_reasons: list[str] = field(default_factory=list)

    def as_text(self) -> str:
        """Render the explanation as markdown for the UI."""
        raise NotImplementedError


@dataclass
class ScheduledItem:
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
    scheduled: list[ScheduledItem] = field(default_factory=list)
    skipped: list[Responsibility] = field(default_factory=list)
    explanation: Explanation = field(default_factory=Explanation)

    def build(self) -> None:
        """Run the scheduling logic, populating ``scheduled``, ``skipped`` and
        ``explanation``.

        Reads tasks from ``self.pet.responsibilities`` and applies
        ``self.owner.preferences``. Essential responsibilities are scheduled
        first and are never dropped, even if doing so exceeds the budget;
        non-essential tasks are filled in by priority while time remains."""
        raise NotImplementedError

    def total_minutes(self) -> int:
        """Total minutes of scheduled work."""
        raise NotImplementedError

    def as_rows(self) -> list[dict]:
        """Schedule as table rows for the Streamlit display (reads ``scheduled``)."""
        raise NotImplementedError
