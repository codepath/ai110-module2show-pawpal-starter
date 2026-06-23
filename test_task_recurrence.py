"""
Task Recurrence Test Suite for PawPal+
Tests automatic task recurrence functionality.
"""

import unittest
from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


class TestTaskRecurrence(unittest.TestCase):
    """Test cases for task recurrence functionality."""

    def test_set_and_get_recurs(self):
        """Test setting and getting recurrence flag."""
        task = Task("Daily Walk", "walk", 30, 5)

        # Default should be True (recurs)
        self.assertTrue(task.get_recurs())

        # Set to False
        task.set_recurs(False)
        self.assertFalse(task.get_recurs())

        # Set back to True
        task.set_recurs(True)
        self.assertTrue(task.get_recurs())

    def test_daily_task_recurrence(self):
        """Test that daily task creates next occurrence for tomorrow."""
        task = Task("Daily Feeding", "feeding", 15, 8)
        task.set_frequency("daily")

        # Complete task and get next occurrence
        next_task = task.complete_and_recur()

        # Should create new task
        self.assertIsNotNone(next_task)

        # Original task should be completed
        self.assertTrue(task.is_completed())

        # New task should not be completed
        self.assertFalse(next_task.is_completed())

        # New task should have same properties
        self.assertEqual(next_task.get_name(), "Daily Feeding")
        self.assertEqual(next_task.get_task_type(), "feeding")
        self.assertEqual(next_task.get_duration(), 15)
        self.assertEqual(next_task.get_priority(), 8)
        self.assertEqual(next_task.get_frequency(), "daily")

        # New task should have next occurrence date set
        expected_date = date.today() + timedelta(days=1)
        self.assertEqual(next_task.get_next_occurrence(), expected_date)

    def test_weekly_task_recurrence(self):
        """Test that weekly task creates next occurrence for next week."""
        task = Task("Weekly Grooming", "grooming", 45, 6)
        task.set_frequency("weekly")

        # Complete and get next occurrence
        next_task = task.complete_and_recur()

        # Should create new task
        self.assertIsNotNone(next_task)

        # Check next occurrence is 7 days from now
        expected_date = date.today() + timedelta(weeks=1)
        self.assertEqual(next_task.get_next_occurrence(), expected_date)
        self.assertEqual(next_task.get_frequency(), "weekly")

    def test_monthly_task_recurrence(self):
        """Test that monthly task creates next occurrence for next month."""
        task = Task("Monthly Vet Checkup", "medical", 60, 10)
        task.set_frequency("monthly")

        # Complete and get next occurrence
        next_task = task.complete_and_recur()

        # Should create new task
        self.assertIsNotNone(next_task)

        # Check next occurrence is ~30 days from now
        expected_date = date.today() + timedelta(days=30)
        self.assertEqual(next_task.get_next_occurrence(), expected_date)
        self.assertEqual(next_task.get_frequency(), "monthly")

    def test_non_recurring_task(self):
        """Test that non-recurring task returns None."""
        task = Task("One-Time Bath", "grooming", 45, 5)
        task.set_recurs(False)

        # Complete task
        next_task = task.complete_and_recur()

        # Should NOT create new task
        self.assertIsNone(next_task)

        # Original task should be completed
        self.assertTrue(task.is_completed())

    def test_recurring_task_inherits_time_window(self):
        """Test that recurring task inherits time window constraints."""
        task = Task("Morning Medication", "meds", 5, 10)
        task.set_frequency("daily")
        task.set_time_window("08:00", "09:00")

        # Complete and get next occurrence
        next_task = task.complete_and_recur()

        # New task should have same time window
        self.assertTrue(next_task.has_time_window())
        start, end = next_task.get_time_window()
        self.assertEqual(start, "08:00")
        self.assertEqual(end, "09:00")

    def test_recurring_task_inherits_mandatory_flag(self):
        """Test that recurring task inherits mandatory status."""
        task = Task("Critical Medication", "meds", 5, 10)
        task.set_mandatory(True)
        task.set_frequency("daily")

        # Complete and get next occurrence
        next_task = task.complete_and_recur()

        # New task should be mandatory
        self.assertTrue(next_task.is_mandatory())

    def test_recurring_task_inherits_description(self):
        """Test that recurring task inherits description."""
        task = Task("Special Meal", "feeding", 15, 8)
        task.set_description("Grain-free kibble with supplements")
        task.set_frequency("daily")

        # Complete and get next occurrence
        next_task = task.complete_and_recur()

        # New task should have same description
        self.assertEqual(
            next_task.get_description(), "Grain-free kibble with supplements"
        )

    def test_recurring_task_has_different_id(self):
        """Test that new task instance has different ID."""
        task = Task("Daily Task", "walk", 30, 5)
        task.set_frequency("daily")

        # Complete and get next occurrence
        next_task = task.complete_and_recur()

        # Should have different task IDs
        self.assertNotEqual(task.get_task_id(), next_task.get_task_id())

    def test_recurring_task_updates_last_completed(self):
        """Test that completing task updates last_completed date."""
        task = Task("Daily Walk", "walk", 30, 7)
        task.set_frequency("daily")

        # Initially no completion date
        self.assertIsNone(task.get_last_completed())

        # Complete task
        next_task = task.complete_and_recur()

        # Original task should have today as last completed
        self.assertEqual(task.get_last_completed(), date.today())

        # New task should also have today as last completed (for tracking)
        self.assertEqual(next_task.get_last_completed(), date.today())

    def test_multiple_completions_chain(self):
        """Test completing same task multiple times creates chain."""
        task1 = Task("Daily Feeding", "feeding", 15, 8)
        task1.set_frequency("daily")

        # First completion
        task2 = task1.complete_and_recur()
        self.assertIsNotNone(task2)
        self.assertTrue(task1.is_completed())
        self.assertFalse(task2.is_completed())

        # Second completion
        task3 = task2.complete_and_recur()
        self.assertIsNotNone(task3)
        self.assertTrue(task2.is_completed())
        self.assertFalse(task3.is_completed())

        # All should have different IDs
        self.assertNotEqual(task1.get_task_id(), task2.get_task_id())
        self.assertNotEqual(task2.get_task_id(), task3.get_task_id())


class TestSchedulerRecurrence(unittest.TestCase):
    """Test cases for Scheduler's recurrence handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner("Test Owner", 120)
        self.pet = Pet("TestPet", "dog", 3, "medium")
        self.scheduler = Scheduler(self.owner, self.pet)

    def test_scheduler_complete_task(self):
        """Test Scheduler's complete_task method."""
        task = Task("Daily Walk", "walk", 30, 7)
        task.set_frequency("daily")
        self.scheduler.add_task(task)

        # Complete task through scheduler
        next_task = self.scheduler.complete_task(task.get_task_id())

        # Should return new task
        self.assertIsNotNone(next_task)

        # New task should be in scheduler's task list
        tasks = self.scheduler.get_tasks()
        self.assertIn(next_task, tasks)

    def test_scheduler_complete_non_recurring_task(self):
        """Test completing non-recurring task through scheduler."""
        task = Task("One-Time Event", "training", 45, 6)
        task.set_recurs(False)
        self.scheduler.add_task(task)

        # Complete task
        next_task = self.scheduler.complete_task(task.get_task_id())

        # Should return None
        self.assertIsNone(next_task)

        # Original task should be completed
        self.assertTrue(task.is_completed())

    def test_scheduler_complete_invalid_task_id(self):
        """Test completing task with invalid ID."""
        result = self.scheduler.complete_task("invalid-task-id")

        # Should return None
        self.assertIsNone(result)

    def test_scheduler_get_recurring_tasks(self):
        """Test getting all recurring tasks from scheduler."""
        task1 = Task("Daily Walk", "walk", 30, 7)
        task1.set_frequency("daily")

        task2 = Task("One-Time Bath", "grooming", 45, 5)
        task2.set_recurs(False)

        task3 = Task("Weekly Grooming", "grooming", 30, 6)
        task3.set_frequency("weekly")

        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)
        self.scheduler.add_task(task3)

        # Get recurring tasks
        recurring = self.scheduler.get_recurring_tasks()

        # Should have 2 recurring tasks
        self.assertEqual(len(recurring), 2)
        self.assertIn(task1, recurring)
        self.assertIn(task3, recurring)
        self.assertNotIn(task2, recurring)

    def test_scheduler_get_completed_tasks(self):
        """Test getting all completed tasks from scheduler."""
        task1 = Task("Task 1", "walk", 30, 7)
        task2 = Task("Task 2", "feeding", 15, 8)
        task3 = Task("Task 3", "playtime", 20, 5)

        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)
        self.scheduler.add_task(task3)

        # Mark some tasks as completed
        task1.mark_complete()
        task3.mark_complete()

        # Get completed tasks
        completed = self.scheduler.get_completed_tasks()

        # Should have 2 completed tasks
        self.assertEqual(len(completed), 2)
        self.assertIn(task1, completed)
        self.assertIn(task3, completed)
        self.assertNotIn(task2, completed)

    def test_recurring_task_count_increases(self):
        """Test that completing recurring task increases task count."""
        task = Task("Daily Feeding", "feeding", 15, 8)
        task.set_frequency("daily")
        self.scheduler.add_task(task)

        # Initial count
        initial_count = len(self.scheduler.get_tasks())

        # Complete task
        self.scheduler.complete_task(task.get_task_id())

        # Count should increase by 1 (old task still there, new task added)
        new_count = len(self.scheduler.get_tasks())
        self.assertEqual(new_count, initial_count + 1)

    def test_multiple_daily_tasks_recurrence(self):
        """Test multiple daily tasks recurring independently."""
        task1 = Task("Morning Feeding", "feeding", 15, 8)
        task1.set_frequency("daily")

        task2 = Task("Evening Feeding", "feeding", 15, 8)
        task2.set_frequency("daily")

        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)

        # Complete both tasks
        next1 = self.scheduler.complete_task(task1.get_task_id())
        next2 = self.scheduler.complete_task(task2.get_task_id())

        # Both should create new instances
        self.assertIsNotNone(next1)
        self.assertIsNotNone(next2)

        # Should have 4 tasks total (2 original + 2 new)
        self.assertEqual(len(self.scheduler.get_tasks()), 4)

        # Original tasks completed
        self.assertTrue(task1.is_completed())
        self.assertTrue(task2.is_completed())

        # New tasks not completed
        self.assertFalse(next1.is_completed())
        self.assertFalse(next2.is_completed())


class TestRecurrenceEdgeCases(unittest.TestCase):
    """Test edge cases for recurrence functionality."""

    def test_completing_already_completed_task(self):
        """Test completing a task that's already completed."""
        task = Task("Daily Task", "walk", 30, 5)
        task.set_frequency("daily")

        # Complete once
        next1 = task.complete_and_recur()
        self.assertIsNotNone(next1)

        # Try to complete again
        next2 = task.complete_and_recur()

        # Should still return a new task
        self.assertIsNotNone(next2)

        # But they should be different instances
        self.assertNotEqual(next1.get_task_id(), next2.get_task_id())

    def test_unknown_frequency_defaults_to_daily(self):
        """Test that unknown frequency defaults to daily recurrence."""
        task = Task("Custom Task", "playtime", 20, 5)
        task.set_frequency("custom_frequency")

        # Complete task
        next_task = task.complete_and_recur()

        # Should create new task with daily interval
        expected_date = date.today() + timedelta(days=1)
        self.assertEqual(next_task.get_next_occurrence(), expected_date)

    def test_recurring_task_with_dependencies_preserved(self):
        """Test that task dependencies are preserved in recurring tasks."""
        task1 = Task("Feeding", "feeding", 15, 8)
        task2 = Task("Medication", "meds", 5, 10)
        task2.add_prerequisite(task1)
        task2.set_frequency("daily")

        # Complete task2
        next_task = task2.complete_and_recur()

        # New task should still have the prerequisite
        self.assertTrue(next_task.has_prerequisites())
        prereqs = next_task.get_prerequisites()
        self.assertIn(task1.get_task_id(), prereqs)

    def test_recurrence_with_zero_duration(self):
        """Test edge case of task with zero duration."""
        task = Task("Quick Check", "enrichment", 0, 3)
        task.set_frequency("daily")

        # Should still work
        next_task = task.complete_and_recur()
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.get_duration(), 0)

    def test_recurrence_with_very_high_priority(self):
        """Test recurrence with maximum priority value."""
        task = Task("Critical Task", "meds", 5, 10)
        task.set_frequency("daily")

        next_task = task.complete_and_recur()

        # Priority should be preserved
        self.assertEqual(next_task.get_priority(), 10)


if __name__ == "__main__":
    unittest.main()
