"""
Simple tests for PawPal+ system
Tests basic functionality for task completion and pet task counting.
"""

import os
import sys
import unittest

# Add parent directory to path so we can import pawpal_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Pet, Task


class TestTaskCompletion(unittest.TestCase):
    """Test that mark_complete() changes task status."""

    def test_mark_complete_changes_task_status(self):
        """Verify that mark_complete() actually changes the task's completed status."""
        # Create a task
        task = Task("Walk the dog", "walk", 30, 5)

        # Initially, task should not be completed
        self.assertFalse(task.is_completed())

        # Mark the task as complete
        task.mark_complete()

        # Now the task should be completed
        self.assertTrue(task.is_completed())


class TestPetTaskCount(unittest.TestCase):
    """Test that adding tasks to a pet increases the task count."""

    def test_adding_task_increases_pet_task_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Create a pet
        pet = Pet("Buddy", "dog", 3, "medium")

        # Initially, pet should have 0 tasks
        self.assertEqual(pet.get_task_count(), 0)

        # Add first task
        task1 = Task("Morning Walk", "walk", 30, 8)
        pet.add_task(task1)

        # Pet should now have 1 task
        self.assertEqual(pet.get_task_count(), 1)

        # Add second task
        task2 = Task("Feeding", "feeding", 15, 10)
        pet.add_task(task2)

        # Pet should now have 2 tasks
        self.assertEqual(pet.get_task_count(), 2)

        # Add third task
        task3 = Task("Playtime", "playtime", 20, 6)
        pet.add_task(task3)

        # Pet should now have 3 tasks
        self.assertEqual(pet.get_task_count(), 3)


if __name__ == "__main__":
    unittest.main()
