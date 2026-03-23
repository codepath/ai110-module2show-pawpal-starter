from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import List, Optional, Dict


@dataclass
class Pet:
	"""Simple Pet dataclass."""
	name: str


@dataclass
class Task:
	"""Task dataclass representing a scheduled action for pets."""
	name: str
	priority: str
	date: date
	start_time: Optional[time] = None
	end_time: Optional[time] = None
	assigned_pets: List[Pet] = field(default_factory=list)

	def get_duration(self) -> Optional[timedelta]:
		"""Return duration between start_time and end_time, or None if unavailable."""
		if self.start_time is None or self.end_time is None:
			return None
		start_dt = datetime.combine(self.date, self.start_time)
		end_dt = datetime.combine(self.date, self.end_time)
		return end_dt - start_dt


class Owner:
	"""Owner holds pets and preferences."""

	def __init__(self, name: str, pets: Optional[List[Pet]] = None, preferences: Optional[Dict] = None):
		self.name = name
		self.pets: List[Pet] = pets if pets is not None else []
		self.preferences: Dict = preferences if preferences is not None else {}

	def add_pet(self, pet: Pet) -> None:
		"""Add a Pet to this owner's collection."""
		self.pets.append(pet)


class Schedule:
	"""Schedule contains tasks for a given date (defaults to today)."""

	def __init__(self, date_: Optional[date] = None, tasks: Optional[List[Task]] = None):
		self.date: date = date_ or date.today()
		self.tasks: List[Task] = tasks if tasks is not None else []

	def add_task(self, task: Task) -> None:
		"""Add a Task to the schedule."""
		self.tasks.append(task)

	def get_tasks_for_date(self, date_: date) -> List[Task]:
		"""Return tasks scheduled for the given date."""
		return [t for t in self.tasks if t.date == date_]

