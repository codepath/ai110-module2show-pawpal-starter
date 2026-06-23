"""
Unit tests for PawPal+ System
Tests the core scheduling logic and class behaviors.
"""

import unittest
from datetime import date

from pawpal_system import Owner, Pet, Plan, ScheduledTask, Scheduler, Task


class TestOwner(unittest.TestCase):
    """Test cases for the Owner class."""

    def test_owner_creation(self):
        """Test creating an owner with basic info."""
        owner = Owner("Alice", 120)
        self.assertEqual(owner.get_name(), "Alice")
        self.assertEqual(owner.get_available_time(), 120)

    def test_set_available_time(self):
        """Test updating available time."""
        owner = Owner("Bob", 60)
        owner.set_available_time(180)
        self.assertEqual(owner.get_available_time(), 180)

    def test_preferences(self):
        """Test adding and retrieving preferences."""
        owner = Owner("Carol", 90)
        owner.add_preference("morning_person", True)
        owner.add_preference("prefer_outdoor", False)
        prefs = owner.get_preferences()
        self.assertEqual(prefs["morning_person"], True)
        self.assertEqual(prefs["prefer_outdoor"], False)


class TestPet(unittest.TestCase):
    """Test cases for the Pet class."""

    def test_pet_creation(self):
        """Test creating a pet with basic info."""
        pet = Pet("Max", "dog", 3, "medium")
        self.assertEqual(pet.get_name(), "Max")
        self.assertEqual(pet.get_species(), "dog")
        self.assertEqual(pet.get_age(), 3)
        self.assertEqual(pet.get_size(), "medium")

    def test_special_needs(self):
        """Test adding special needs."""
        pet = Pet("Fluffy", "cat", 5, "small")
        pet.add_special_need("diabetes medication")
        pet.add_special_need("sensitive stomach")
        needs = pet.get_special_needs()
        self.assertEqual(len(needs), 2)
        self.assertIn("diabetes medication", needs)
        self.assertIn("sensitive stomach", needs)


class TestTask(unittest.TestCase):
    """Test cases for the Task class."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task("Morning Walk", "walk", 30, 5)
        self.assertEqual(task.get_name(), "Morning Walk")
        self.assertEqual(task.get_task_type(), "walk")
        self.assertEqual(task.get_duration(), 30)
        self.assertEqual(task.get_priority(), 5)
        self.assertIsNotNone(task.get_task_id())
        self.assertFalse(task.is_mandatory())

    def test_set_priority(self):
        """Test changing task priority."""
        task = Task("Feeding", "feeding", 15, 3)
        task.set_priority(8)
        self.assertEqual(task.get_priority(), 8)

    def test_set_mandatory(self):
        """Test marking task as mandatory."""
        task = Task("Medicine", "meds", 5, 10)
        task.set_mandatory(True)
        self.assertTrue(task.is_mandatory())

    def test_set_description(self):
        """Test setting task description."""
        task = Task("Grooming", "grooming", 45, 3)
        task.set_description("Brush fur and trim nails")
        self.assertEqual(task.get_description(), "Brush fur and trim nails")

    def test_set_frequency(self):
        """Test setting task frequency."""
        task = Task("Vet Visit", "medical", 60, 10)
        task.set_frequency("monthly")
        # Note: frequency is set but we don't have a getter in the current implementation


class TestScheduledTask(unittest.TestCase):
    """Test cases for the ScheduledTask class."""

    def test_scheduled_task_creation(self):
        """Test creating a scheduled task."""
        task = Task("Walk", "walk", 30, 5)
        scheduled = ScheduledTask(task, "08:00", "08:30", 1)
        self.assertEqual(scheduled.get_task(), task)
        self.assertEqual(scheduled.get_start_time(), "08:00")
        self.assertEqual(scheduled.get_end_time(), "08:30")
        self.assertEqual(scheduled.get_order(), 1)


class TestPlan(unittest.TestCase):
    """Test cases for the Plan class."""

    def test_plan_creation(self):
        """Test creating an empty plan."""
        plan = Plan()
        self.assertEqual(len(plan.get_scheduled_tasks()), 0)
        self.assertEqual(plan.get_total_time(), 0)
        self.assertIsInstance(plan.get_plan_date(), date)

    def test_add_scheduled_task(self):
        """Test adding tasks to a plan."""
        plan = Plan()
        task1 = Task("Walk", "walk", 30, 5)
        task2 = Task("Feed", "feeding", 10, 8)

        scheduled1 = ScheduledTask(task1, "08:00", "08:30", 1)
        scheduled2 = ScheduledTask(task2, "08:30", "08:40", 2)

        plan.add_scheduled_task(scheduled1)
        plan.add_scheduled_task(scheduled2)

        self.assertEqual(len(plan.get_scheduled_tasks()), 2)
        self.assertEqual(plan.get_total_time(), 40)

    def test_explanation(self):
        """Test setting and getting plan explanation."""
        plan = Plan()
        explanation = "Prioritized mandatory tasks first."
        plan.set_explanation(explanation)
        self.assertEqual(plan.get_explanation(), explanation)

    def test_excluded_tasks(self):
        """Test tracking excluded tasks."""
        plan = Plan()
        task1 = Task("Long grooming", "grooming", 120, 2)
        task2 = Task("Training", "training", 60, 3)

        plan.add_excluded_task(task1)
        plan.add_excluded_task(task2)

        excluded = plan.get_excluded_tasks()
        self.assertEqual(len(excluded), 2)
        self.assertIn(task1, excluded)
        self.assertIn(task2, excluded)


class TestScheduler(unittest.TestCase):
    """Test cases for the Scheduler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner("Test Owner", 120)
        self.pet = Pet("TestPet", "dog", 2, "medium")
        self.scheduler = Scheduler(self.owner, self.pet)

    def test_scheduler_creation(self):
        """Test creating a scheduler."""
        self.assertEqual(len(self.scheduler.get_tasks()), 0)

    def test_add_task(self):
        """Test adding tasks to scheduler."""
        task1 = Task("Walk", "walk", 30, 5)
        task2 = Task("Feed", "feeding", 15, 8)

        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)

        tasks = self.scheduler.get_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertIn(task1, tasks)
        self.assertIn(task2, tasks)

    def test_remove_task(self):
        """Test removing a task from scheduler."""
        task1 = Task("Walk", "walk", 30, 5)
        task2 = Task("Feed", "feeding", 15, 8)

        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)

        task_id = task1.get_task_id()
        self.scheduler.remove_task(task_id)

        tasks = self.scheduler.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertNotIn(task1, tasks)
        self.assertIn(task2, tasks)

    def test_generate_empty_plan(self):
        """Test generating a plan with no tasks."""
        plan = self.scheduler.generate_plan()
        self.assertEqual(len(plan.get_scheduled_tasks()), 0)
        self.assertIn("No tasks", plan.get_explanation())

    def test_generate_simple_plan(self):
        """Test generating a plan with tasks that fit."""
        task1 = Task("Feed", "feeding", 15, 8)
        task2 = Task("Walk", "walk", 30, 5)

        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)

        plan = self.scheduler.generate_plan()

        # Both tasks should fit (15 + 30 = 45 < 120)
        self.assertEqual(len(plan.get_scheduled_tasks()), 2)
        self.assertEqual(plan.get_total_time(), 45)
        self.assertEqual(len(plan.get_excluded_tasks()), 0)

    def test_priority_ordering(self):
        """Test that higher priority tasks are scheduled first."""
        task_low = Task("Grooming", "grooming", 20, 2)
        task_high = Task("Medicine", "meds", 10, 10)

        self.scheduler.add_task(task_low)
        self.scheduler.add_task(task_high)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # High priority task should be scheduled first
        self.assertEqual(scheduled[0].get_task().get_name(), "Medicine")

    def test_mandatory_tasks_first(self):
        """Test that mandatory tasks are prioritized over optional ones."""
        task_optional_high = Task("Play", "playtime", 20, 10)
        task_mandatory_low = Task("Meds", "meds", 10, 1)
        task_mandatory_low.set_mandatory(True)

        self.scheduler.add_task(task_optional_high)
        self.scheduler.add_task(task_mandatory_low)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Mandatory task should be first even with lower priority
        self.assertEqual(scheduled[0].get_task().get_name(), "Meds")

    def test_time_constraint_exclusion(self):
        """Test that tasks exceeding time limit are excluded."""
        self.owner.set_available_time(40)

        task1 = Task("Walk", "walk", 30, 10)
        task2 = Task("Grooming", "grooming", 20, 8)
        task3 = Task("Play", "playtime", 15, 5)

        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)
        self.scheduler.add_task(task3)

        plan = self.scheduler.generate_plan()

        # Only first two tasks should fit (30 + 20 = 50 > 40, so only 30 fits, then 20 doesn't)
        # Actually: Walk (30) fits, then Grooming (20) would make 50 > 40, so excluded
        scheduled = plan.get_scheduled_tasks()
        excluded = plan.get_excluded_tasks()

        total = plan.get_total_time()
        self.assertLessEqual(total, 40)
        self.assertGreater(len(excluded), 0)

    def test_task_type_optimization(self):
        """Test that task types are ordered logically."""
        # Add tasks in random order
        walk = Task("Walk", "walk", 30, 5)
        feed = Task("Feed", "feeding", 15, 5)
        meds = Task("Meds", "meds", 5, 5)

        self.scheduler.add_task(walk)
        self.scheduler.add_task(feed)
        self.scheduler.add_task(meds)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Feeding should come before meds, meds before walk
        task_names = [s.get_task().get_name() for s in scheduled]
        feed_idx = task_names.index("Feed")
        meds_idx = task_names.index("Meds")
        walk_idx = task_names.index("Walk")

        self.assertLess(feed_idx, meds_idx)
        self.assertLess(meds_idx, walk_idx)

    def test_scheduled_task_timing(self):
        """Test that scheduled tasks have proper time slots."""
        task = Task("Walk", "walk", 30, 5)
        self.scheduler.add_task(task)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()[0]

        # Should start at 08:00 (480 minutes from midnight)
        self.assertEqual(scheduled.get_start_time(), "08:00")
        self.assertEqual(scheduled.get_end_time(), "08:30")
        self.assertEqual(scheduled.get_order(), 1)

    def test_plan_explanation_includes_key_info(self):
        """Test that plan explanation contains important information."""
        task = Task("Walk", "walk", 30, 5)
        self.scheduler.add_task(task)

        plan = self.scheduler.generate_plan()
        explanation = plan.get_explanation()

        # Check that explanation includes key details
        self.assertIn(self.pet.get_name(), explanation)
        self.assertIn(self.owner.get_name(), explanation)
        self.assertIn("Scheduled", explanation)


if __name__ == "__main__":
    unittest.main()
