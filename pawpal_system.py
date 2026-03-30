from dataclasses import dataclass, field
from datetime import time, datetime, timedelta
from typing import List, Optional


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Owner:
    name: str
    available_start: time
    available_end: time

    def get_available_window(self) -> tuple:
        """Return the owner's available start and end times as a tuple."""
        return (self.available_start, self.available_end)

    def get_total_available_time(self) -> int:
        """Return the total number of minutes available between start and end times."""
        start_dt = datetime.combine(datetime.today(), self.available_start)
        end_dt = datetime.combine(datetime.today(), self.available_end)
        return int((end_dt - start_dt).total_seconds() // 60)


@dataclass
class Task:
    id: int
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    frequency: str = "once"  # "once", "daily", "weekly"
    preferred_time: Optional[time] = None
    is_completed: bool = False
    pet_name: Optional[str] = None  # set by Pet.add_task() to preserve ownership context

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_completed = True

    def next_occurrence(self, new_id: int) -> Optional["Task"]:
        """Return a fresh, incomplete copy of this task for its next occurrence.

        Returns None for one-time tasks — they don't repeat.
        The new task inherits all settings (duration, priority, preferred_time)
        but starts with is_completed=False so it appears in the next schedule.
        """
        if self.frequency == "once":
            return None
        return Task(
            id=new_id,
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            is_completed=False,
            pet_name=self.pet_name,
        )

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is high."""
        return self.priority == "high"

    def fits_in_window(self, start: time, end: time) -> bool:
        """Return True if the task's duration fits within the given time window."""
        start_dt = datetime.combine(datetime.today(), start)
        end_dt = datetime.combine(datetime.today(), end)
        available_minutes = (end_dt - start_dt).total_seconds() // 60
        return self.duration_minutes <= available_minutes


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet and stamp it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: int):
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    reason: str = ""

    @property
    def end_time(self) -> time:
        """Compute end time from start time and task duration."""
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = start_dt + timedelta(minutes=self.task.duration_minutes)
        return end_dt.time()

    def get_time_range(self) -> tuple:
        """Return the scheduled start and end times as a tuple."""
        return (self.start_time, self.end_time)

    def to_display_string(self) -> str:
        """Return a formatted string showing the time slot, pet, task, and priority."""
        start_str = self.start_time.strftime("%I:%M %p")
        end_str = self.end_time.strftime("%I:%M %p")
        pet = f"{self.task.pet_name}: " if self.task.pet_name else ""
        return f"{start_str} – {end_str} | {pet}{self.task.title} ({self.task.priority} priority)"


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.pets: List[Pet] = []
        self.scheduled_tasks: List[ScheduledTask] = []
        self.skipped_tasks: List[Task] = []
        self._next_task_id: int = 1000  # start high to avoid collisions with user-created IDs

    def complete_task(self, task_id: int) -> Optional[Task]:
        """Mark a task complete and, if it recurs, add the next occurrence to its pet.

        Returns the new Task if one was created, or None for one-time tasks.
        Raises ValueError if no task with the given ID is found.
        """
        all_tasks = self.get_all_tasks()
        task = next((t for t in all_tasks if t.id == task_id), None)
        if task is None:
            raise ValueError(f"No task with id={task_id} found.")

        task.mark_complete()

        next_task = task.next_occurrence(new_id=self._next_task_id)
        if next_task is None:
            return None  # one-time task, nothing more to do

        self._next_task_id += 1

        # Add the next occurrence back to the same pet
        pet = next((p for p in self.pets if p.name == task.pet_name), None)
        if pet:
            pet.add_task(next_task)

        return next_task

    def add_pet(self, pet: Pet):
        """Register a pet with the scheduler."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of all tasks across every registered pet."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def generate_recurring_tasks(self) -> List[Task]:
        """Return the subset of tasks eligible to be scheduled today.

        Rules:
        - "once" tasks that are already completed are excluded — they are done forever.
        - "daily" and "weekly" tasks are always included regardless of completion
          status, because they need to appear in every applicable schedule cycle.
        """
        eligible = []
        for task in self.get_all_tasks():
            if task.frequency == "once" and task.is_completed:
                continue
            eligible.append(task)
        return eligible

    def filter_by_priority(self, priority: str) -> List[Task]:
        """Return all tasks across all pets that match the given priority level.

        Args:
            priority: One of "high", "medium", or "low".
        """
        return [t for t in self.get_all_tasks() if t.priority == priority]

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the named pet.

        Args:
            pet_name: The exact name of the pet as registered with add_pet().
        """
        return [t for t in self.get_all_tasks() if t.pet_name == pet_name]

    def build_schedule(self) -> List[ScheduledTask]:
        """Build today's schedule: filter recurring, sort, assign slots, track skipped."""
        tasks = self._sort_by_priority(self.generate_recurring_tasks())
        self.scheduled_tasks, self.skipped_tasks = self._assign_time_slots(tasks)
        return self.scheduled_tasks

    def _sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered high → medium → low, using preferred_time as a tiebreaker.

        The sort key is a tuple (priority_rank, preferred_time). Python sorts
        tuples left to right, so priority is always the primary criterion.
        Tasks with no preferred_time are treated as time(23, 59) and drift
        to the end within their priority band.
        """
        def sort_key(t: Task):
            priority_rank = PRIORITY_ORDER.get(t.priority, 99)
            time_rank = t.preferred_time if t.preferred_time else time(23, 59)
            return (priority_rank, time_rank)
        return sorted(tasks, key=sort_key)

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Args:
            pet_name:  If provided, only return tasks belonging to this pet.
            completed: If True, return only completed tasks.
                       If False, return only incomplete tasks.
                       If None, completion status is not filtered.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.is_completed == completed]
        return tasks

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by preferred_time, earliest first.

        Useful for displaying a time-ordered view independently of how the
        greedy scheduler placed tasks. The sort key is a tuple so that tasks
        sharing the same preferred_time are further ordered by priority.

        Tasks with no preferred_time are placed at the end (sorted as time.max).

        Args:
            tasks: Any list of Task objects — need not belong to this scheduler.
        """
        return sorted(tasks, key=lambda t: (
            t.preferred_time or time.max,
            PRIORITY_ORDER.get(t.priority, 99),
        ))

    def _assign_time_slots(self, tasks: List[Task]):
        """Greedily assign start times to tasks within the owner's available window.

        Iterates tasks in the order given (caller is responsible for pre-sorting).
        Each task is placed immediately after the previous one. If a task would
        push past available_end it is added to the skipped list instead.

        Returns:
            A tuple of (scheduled, skipped) — both are lists, never None.
        """
        scheduled = []
        skipped = []
        current_dt = datetime.combine(datetime.today(), self.owner.available_start)
        end_dt = datetime.combine(datetime.today(), self.owner.available_end)

        for task in tasks:
            task_end_dt = current_dt + timedelta(minutes=task.duration_minutes)
            if task_end_dt > end_dt:
                skipped.append(task)
                continue

            freq_note = f" (recurring: {task.frequency})" if task.frequency != "once" else ""
            reason = (
                f"Scheduled at {current_dt.strftime('%I:%M %p')} — "
                f"{task.priority} priority, fits in remaining window{freq_note}."
            )
            scheduled.append(ScheduledTask(task=task, start_time=current_dt.time(), reason=reason))
            current_dt = task_end_dt

        return scheduled, skipped

    def check_conflicts(self, task: Task, proposed_start: time) -> bool:
        """Return True if placing task at proposed_start overlaps any already-scheduled task."""
        new_start_dt = datetime.combine(datetime.today(), proposed_start)
        new_end_dt = new_start_dt + timedelta(minutes=task.duration_minutes)

        for st in self.scheduled_tasks:
            existing_start = datetime.combine(datetime.today(), st.start_time)
            existing_end = datetime.combine(datetime.today(), st.end_time)
            if new_start_dt < existing_end and new_end_dt > existing_start:
                return True
        return False

    def get_all_conflicts(self) -> List[dict]:
        """Scan all scheduled tasks pairwise and return every overlapping pair.

        Each conflict is a dict with:
          - 'task_a', 'task_b': the two ScheduledTask objects
          - 'same_pet': True if both tasks belong to the same pet
          - 'overlap_minutes': how many minutes the two slots overlap
        """
        today = datetime.today()
        conflicts = []

        for i, a in enumerate(self.scheduled_tasks):
            a_start = datetime.combine(today, a.start_time)
            a_end = datetime.combine(today, a.end_time)

            for b in self.scheduled_tasks[i + 1:]:
                b_start = datetime.combine(today, b.start_time)
                b_end = datetime.combine(today, b.end_time)

                overlap_start = max(a_start, b_start)
                overlap_end = min(a_end, b_end)

                if overlap_start < overlap_end:
                    conflicts.append({
                        "task_a": a,
                        "task_b": b,
                        "same_pet": a.task.pet_name == b.task.pet_name,
                        "overlap_minutes": int((overlap_end - overlap_start).total_seconds() // 60),
                    })

        return conflicts

    def warn_conflicts(self) -> List[str]:
        """Return a list of human-readable warning strings for every scheduling conflict.

        Returns an empty list when there are no conflicts — callers can treat
        a falsy result as "all clear" without any exception handling.
        """
        if not self.scheduled_tasks:
            return []

        warnings = []
        for c in self.get_all_conflicts():
            a, b = c["task_a"], c["task_b"]
            scope = "same pet" if c["same_pet"] else "different pets"
            warnings.append(
                f"WARNING: '{a.task.title}' ({a.task.pet_name}) and "
                f"'{b.task.title}' ({b.task.pet_name}) overlap by "
                f"{c['overlap_minutes']} min ({scope})."
            )

        return warnings

    def find_next_slot(self, task: Task) -> Optional[time]:
        """Return the earliest start time within the owner's window where task fits gap-free.

        Unlike the greedy builder, which only appends to the end of the current
        schedule, this method scans every gap in the existing schedule and returns
        the first opening wide enough to hold the task's duration — including gaps
        between already-scheduled tasks, not just the tail.

        Algorithm (gap-scan):
          1. Collect the occupied intervals from scheduled_tasks and sort by start.
          2. Build a list of candidate start times:
               - available_start  (the gap before the first task)
               - each task's end_time  (the gap immediately after each task)
          3. For each candidate in chronological order:
               a. Skip it if it falls before available_start.
               b. Compute the deadline for this gap: the start of the next occupied
                  task, or available_end if there is no next task.
               c. If candidate + task.duration <= deadline, this gap fits — return it.
          4. Return None if no gap in the window is large enough.

        Args:
            task: The task whose duration_minutes must fit in the returned slot.

        Returns:
            A time object for the earliest fitting start, or None if no slot exists.
        """
        today = datetime.today()
        window_start = datetime.combine(today, self.owner.available_start)
        window_end   = datetime.combine(today, self.owner.available_end)

        # Sort occupied intervals by start time
        occupied = sorted(
            self.scheduled_tasks,
            key=lambda st: datetime.combine(today, st.start_time),
        )

        # Candidate start times: beginning of window + immediately after each task
        candidates = [window_start] + [
            datetime.combine(today, st.end_time) for st in occupied
        ]

        # The "wall" after each candidate: the next task's start, or the window end
        walls = [
            datetime.combine(today, occupied[i].start_time) if i < len(occupied) else window_end
            for i in range(len(candidates))
        ]

        for candidate, wall in zip(candidates, walls):
            if candidate < window_start:
                continue
            task_end = candidate + timedelta(minutes=task.duration_minutes)
            if task_end <= wall and task_end <= window_end:
                return candidate.time()

        return None


if __name__ == "__main__":
    owner = Owner(name="Jordan", available_start=time(8, 0), available_end=time(20, 0))

    luna = Pet(name="Luna", species="dog", age=3)
    luna.add_task(Task(id=1, title="Morning Walk",    duration_minutes=30, priority="high"))
    luna.add_task(Task(id=2, title="Evening Walk",    duration_minutes=30, priority="high"))
    luna.add_task(Task(id=3, title="Grooming",        duration_minutes=20, priority="low"))

    milo = Pet(name="Milo", species="cat", age=5)
    milo.add_task(Task(id=4, title="Feeding",         duration_minutes=10, priority="high"))
    milo.add_task(Task(id=5, title="Enrichment Play", duration_minutes=15, priority="medium"))

    scheduler = Scheduler(owner=owner)
    scheduler.add_pet(luna)
    scheduler.add_pet(milo)

    print(f"Owner: {owner.name}")
    print(f"Available: {owner.available_start.strftime('%I:%M %p')} – {owner.available_end.strftime('%I:%M %p')}")
    print(f"Total available time: {owner.get_total_available_time()} minutes\n")

    schedule = scheduler.build_schedule()
    print("=== Daily Schedule ===")
    for st in schedule:
        print(f"  {st.to_display_string()}")
        print(f"    Reason: {st.reason}")
