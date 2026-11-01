from dataclasses import dataclass, field
from datetime import date, timedelta

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
VALID_RECURRENCES = {"daily", "weekly", "once"}
RECURRENCE_INTERVAL = {"daily": timedelta(days=1), "weekly": timedelta(days=7)}


# -----------------------------------
# CLASS 1: Owner
# -----------------------------------

@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list["Pet"] = field(default_factory=list)

    def update_preferences(self, preferences):
        """Replace preferences with a cleaned, de-duplicated list (e.g. ["walk", "grooming"])."""
        cleaned = []
        for pref in preferences:
            pref = pref.strip().lower()
            if pref and pref not in cleaned:
                cleaned.append(pref)
        self.preferences = cleaned

    def set_available_time(self, minutes):
        """Set how many minutes the owner has today for pet care."""
        if minutes < 0:
            raise ValueError("Available minutes cannot be negative.")
        self.available_minutes = minutes

    def add_pet(self, pet):
        """Add a pet to this owner if not already present."""
        if pet not in self.pets:
            self.pets.append(pet)


# -----------------------------------
# CLASS 2: Pet
# -----------------------------------

@dataclass
class Pet:
    name: str
    species: str
    care_tasks: list["CareTask"] = field(default_factory=list)

    def add_task(self, task):
        """Add a valid task to this pet; duplicates are ignored."""
        if not task.is_valid():
            raise ValueError(f"Invalid task: {task}")
        if task not in self.care_tasks:
            self.care_tasks.append(task)

    def remove_task(self, task):
        """Remove a task if present. Returns True if something was removed."""
        if task in self.care_tasks:
            self.care_tasks.remove(task)
            return True
        return False


# -----------------------------------
# CLASS 3: CareTask
# -----------------------------------

@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: str = "medium"
    recurrence: str = "daily"
    last_completed: date | None = field(default=None, compare=False)

    def update_details(self, title=None, duration_minutes=None, priority=None, recurrence=None):
        """Update any provided fields; rolls back if the result would be invalid."""
        previous = (self.title, self.duration_minutes, self.priority, self.recurrence)
        if title is not None:
            self.title = title
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority.lower()
        if recurrence is not None:
            self.recurrence = recurrence.lower()

        if not self.is_valid():
            self.title, self.duration_minutes, self.priority, self.recurrence = previous
            raise ValueError("Updated task details are invalid.")

    def is_valid(self):
        """Return True if title, duration, priority, and recurrence are all valid."""
        return (
            bool(self.title.strip())
            and self.duration_minutes > 0
            and self.priority in PRIORITY_RANK
            and self.recurrence in VALID_RECURRENCES
        )

    @property
    def priority_rank(self):
        """Return a numeric rank for priority (high=3, medium=2, low=1)."""
        return PRIORITY_RANK.get(self.priority, 0)

    def mark_complete(self, on=None):
        """Record that this task was completed on the given date (default: today)."""
        self.last_completed = on or date.today()

    def next_due_date(self):
        """Return the first date the task is due again, or None if a one-time task is done."""
        if self.last_completed is None:
            return date.min
        if self.recurrence == "once":
            return None
        return self.last_completed + RECURRENCE_INTERVAL[self.recurrence]

    def is_due(self, on=None):
        """Return True if the task should be scheduled on the given date (default: today)."""
        due = self.next_due_date()
        return due is not None and due <= (on or date.today())


# -----------------------------------
# CLASS 4: DailySchedule
# -----------------------------------

@dataclass
class DailySchedule:
    pet: Pet
    tasks: list[CareTask] = field(default_factory=list)
    scheduled_tasks: list[CareTask] = field(default_factory=list)
    remaining_minutes: int = 0
    reasons: dict[str, str] = field(default_factory=dict)
    skipped_tasks: list[CareTask] = field(default_factory=list)
    schedule_date: date = field(default_factory=date.today)

    def generate(self, owner):
        """Build the plan for schedule_date: filter by due date, sort, then fit into the owner's time."""
        # 1. Collect valid tasks without duplicates.
        candidates = []
        for task in self.pet.care_tasks + self.tasks:
            if task.is_valid() and task not in candidates:
                candidates.append(task)
        self.tasks = candidates

        self.scheduled_tasks = []
        self.skipped_tasks = []
        self.reasons = {}
        self.remaining_minutes = owner.available_minutes

        # 2. Filter out tasks that are not due (completed this period or one-time and done).
        eligible = []
        for task in candidates:
            if task.is_due(self.schedule_date):
                eligible.append(task)
            else:
                self.skipped_tasks.append(task)
                self.reasons[task.title] = f"Skipped: {self._not_due_reason(task)}"

        # 3. Sort: highest priority, shortest duration, preference match, original order.
        order = {id(task): i for i, task in enumerate(candidates)}
        eligible.sort(
            key=lambda t: (
                -t.priority_rank,
                t.duration_minutes,
                not self._matches_preference(t, owner),
                order[id(t)],
            )
        )

        # 4. Greedily add tasks that fit in the remaining time.
        for task in eligible:
            preferred = " and matches your preferences" if self._matches_preference(task, owner) else ""
            if task.duration_minutes <= self.remaining_minutes:
                self.scheduled_tasks.append(task)
                self.remaining_minutes -= task.duration_minutes
                self.reasons[task.title] = (
                    f"Scheduled: {task.priority} priority{preferred}, "
                    f"fits in the time left ({task.duration_minutes} min)."
                )
            else:
                self.skipped_tasks.append(task)
                self.reasons[task.title] = (
                    f"Skipped: needs {task.duration_minutes} min but only "
                    f"{self.remaining_minutes} min were left."
                )

        return self.scheduled_tasks

    def add_task(self, task):
        """Add an extra task to consider the next time generate() runs."""
        if not task.is_valid():
            raise ValueError(f"Invalid task: {task}")
        if task not in self.tasks:
            self.tasks.append(task)

    def explain_task(self, task):
        """Return why a task was scheduled or skipped."""
        return self.reasons.get(task.title, f"'{task.title}' has not been considered yet; run generate() first.")

    def get_summary(self):
        """Return a readable summary of scheduled tasks, skipped tasks, and time left."""
        lines = [f"Daily plan for {self.pet.name} ({self.pet.species}):"]
        if not self.scheduled_tasks:
            lines.append("  No tasks scheduled.")
        for task in self.scheduled_tasks:
            lines.append(f"  - {task.title} ({task.duration_minutes} min) [priority: {task.priority}]")

        if self.skipped_tasks:
            lines.append("Skipped:")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.title}: {self.explain_task(task).removeprefix('Skipped: ')}")

        lines.append(f"Time remaining: {self.remaining_minutes} min")
        return "\n".join(lines)

    @staticmethod
    def _not_due_reason(task):
        """Return why a completed task is not due on this schedule's date."""
        if task.recurrence == "once":
            return f"one-time task already completed on {task.last_completed}."
        if task.recurrence == "daily":
            return f"already completed on {task.last_completed}."
        return f"completed on {task.last_completed}; next due {task.next_due_date()}."

    @staticmethod
    def _matches_preference(task, owner):
        """Return True if any owner preference appears in the task title."""
        title = task.title.lower()
        return any(pref in title for pref in owner.preferences)
