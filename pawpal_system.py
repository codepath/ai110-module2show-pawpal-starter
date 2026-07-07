"""Class skeletons for the PawPal+ system, based on diagrams/uml_draft.mmd.

No logic is implemented yet -- method bodies are stubs.
"""

from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    weight: float
    color: str
    breed: str

    def snack_time(self, weight):
        pass

    def accommodations(self, breed):
        pass

    def get_daily_needs(self):
        pass


@dataclass
class Task:
    info: dict
    duration: int
    priority: str

    def set_priority(self, priority):
        pass

    def estimate_duration(self):
        pass

    def is_high_priority(self):
        pass


class Owner:
    def __init__(self, info: dict, pet: Pet, tasks: list[Task] = None):
        self.info = info
        self.pet = pet
        self.tasks = tasks if tasks is not None else []

    def add_pet_info(self, pet):
        pass

    def add_task(self, task):
        pass

    def remove_task(self, task):
        pass

    def update_preferences(self, preferences):
        pass


class Scheduler:
    def __init__(self, constraints: dict = None, priorities: dict = None):
        self.constraints = constraints if constraints is not None else {}
        self.priorities = priorities if priorities is not None else {}

    def daily_plan(self, constraint):
        pass

    def sort_tasks(self):
        pass

    def check_conflicts(self):
        pass

    def explain_plan(self):
        pass
