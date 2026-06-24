"""PawPal+ object model (skeleton).

Mirrors diagrams/uml_draft.mmd. Attributes are fully defined; methods are
stubs (``raise NotImplementedError``) to be implemented in a later step.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Pet:
    """The animal being cared for."""

    name: str
    species: str = "dog"  # "dog" | "cat" | "other"
    energy_level: str = "medium"  # "low" | "medium" | "high"
    notes: str = ""


@dataclass
class Owner:
    """The person doing the caring. Scheduling limits live in ``Constraints``."""

    name: str
    pets: list[Pet] = field(default_factory=list)

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
    fixed_time: str | None = None  # e.g. "08:00" for meds pinned to a time
    essential: bool = False  # meds/feeding that must never be dropped

    def priority_weight(self) -> int:
        """Numeric weight for sorting (high=3, medium=2, low=1)."""
        raise NotImplementedError


@dataclass
class Constraints:
    """The day's context and limits handed to the plan."""

    available_minutes: int
    day_start: str = "07:00"
    day_end: str = "21:00"
    day_of_week: str = "Monday"
    preferences: dict = field(default_factory=dict)  # e.g. {"walk_time": "morning"}

    def has_time_for(self, remaining_minutes: int, duration: int) -> bool:
        """Whether ``duration`` still fits within the remaining budget."""
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
class Plan:
    """The daily plan: holds the inputs it was built from and the schedule it
    produces. Construct from a pet + responsibilities + constraints, then call
    :meth:`build`."""

    pet: Pet
    responsibilities: list[Responsibility]
    constraints: Constraints
    date: str = ""

    # Results, populated by build().
    # Each scheduled entry is a dict: {responsibility, start_time, end_time}.
    scheduled: list[dict] = field(default_factory=list)
    skipped: list[Responsibility] = field(default_factory=list)
    explanation: Explanation = field(default_factory=Explanation)

    def build(self) -> None:
        """Run the scheduling logic, populating ``scheduled``, ``skipped`` and
        ``explanation``."""
        raise NotImplementedError

    def total_minutes(self) -> int:
        """Total minutes of scheduled work."""
        raise NotImplementedError

    def as_rows(self) -> list[dict]:
        """Schedule as table rows for the Streamlit display (reads ``scheduled``)."""
        raise NotImplementedError
