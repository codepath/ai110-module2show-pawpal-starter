"""
Advanced Features Test Suite for PawPal+
Tests for time-windows, task dependencies, and dynamic priority adjustment.
"""

import unittest
from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


class TestTimeWindowConstraints(unittest.TestCase):
    """Test cases for Feature 1: Time-Window Constraints."""

    def test_set_and_get_time_window(self):
        """Test setting and retrieving time window."""
        task = Task("Morning Walk", "walk", 30, 5)
        task.set_time_window("08:00", "10:00")

        start, end = task.get_time_window()
        self.assertEqual(start, "08:00")
        self.assertEqual(end, "10:00")

    def test_has_time_window(self):
        """Test checking if task has a time window."""
        task1 = Task("Anytime Task", "playtime", 20, 5)
        self.assertFalse(task1.has_time_window())

        task2 = Task("Morning Only", "walk", 30, 5)
        task2.set_time_window("08:00", "10:00")
        self.assertTrue(task2.has_time_window())

    def test_can_schedule_at_time_within_window(self):
        """Test that task can be scheduled within its time window."""
        task = Task("Breakfast", "feeding", 15, 8)
        task.set_time_window("07:00", "09:00")

        self.assertTrue(task.can_schedule_at_time("07:00"))
        self.assertTrue(task.can_schedule_at_time("08:00"))
        self.assertTrue(task.can_schedule_at_time("09:00"))

    def test_can_schedule_at_time_outside_window(self):
        """Test that task cannot be scheduled outside its time window."""
        task = Task("Morning Meds", "meds", 5, 10)
        task.set_time_window("08:00", "09:00")

        self.assertFalse(task.can_schedule_at_time("06:00"))
        self.assertFalse(task.can_schedule_at_time("10:00"))
        self.assertFalse(task.can_schedule_at_time("15:00"))

    def test_no_time_window_allows_any_time(self):
        """Test that tasks without time windows can be scheduled anytime."""
        task = Task("Flexible Play", "playtime", 30, 5)

        self.assertTrue(task.can_schedule_at_time("00:00"))
        self.assertTrue(task.can_schedule_at_time("12:00"))
        self.assertTrue(task.can_schedule_at_time("23:59"))

    def test_scheduler_respects_time_windows(self):
        """Test that scheduler respects time window constraints."""
        owner = Owner("Test Owner", 180)
        pet = Pet("TestPet", "dog", 3, "medium")
        scheduler = Scheduler(owner, pet)

        # Task that must happen in morning
        morning_task = Task("Morning Walk", "walk", 30, 8)
        morning_task.set_time_window("08:00", "10:00")

        # Task that can happen anytime
        anytime_task = Task("Play", "playtime", 20, 7)

        scheduler.add_task(morning_task)
        scheduler.add_task(anytime_task)

        plan = scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Morning walk should be scheduled within its window
        for st in scheduled:
            if st.get_task().get_name() == "Morning Walk":
                start_time = st.get_start_time()
                self.assertTrue(morning_task.can_schedule_at_time(start_time))

    def test_impossible_time_window_excludes_task(self):
        """Test that task with impossible time window gets excluded."""
        owner = Owner("Test Owner", 60)
        pet = Pet("TestPet", "cat", 2, "small")
        scheduler = Scheduler(owner, pet)

        # Task with time window before scheduler starts (08:00)
        early_task = Task("Pre-dawn Walk", "walk", 30, 8)
        early_task.set_time_window("06:00", "07:00")

        scheduler.add_task(early_task)
        plan = scheduler.generate_plan()

        # Task should be excluded
        excluded = plan.get_excluded_tasks()
        self.assertEqual(len(excluded), 1)
        self.assertIn("time window", plan.get_explanation().lower())


class TestTaskDependencies(unittest.TestCase):
    """Test cases for Feature 2: Task Dependencies."""

    def test_add_prerequisite(self):
        """Test adding a prerequisite task."""
        task1 = Task("Feed", "feeding", 10, 8)
        task2 = Task("Medicine", "meds", 5, 9)

        task2.add_prerequisite(task1)

        self.assertTrue(task2.has_prerequisites())
        self.assertIn(task1.get_task_id(), task2.get_prerequisites())

    def test_multiple_prerequisites(self):
        """Test adding multiple prerequisites."""
        task1 = Task("Feed", "feeding", 10, 8)
        task2 = Task("Walk", "walk", 30, 7)
        task3 = Task("Medicine after food and exercise", "meds", 5, 10)

        task3.add_prerequisite(task1)
        task3.add_prerequisite(task2)

        prereqs = task3.get_prerequisites()
        self.assertEqual(len(prereqs), 2)
        self.assertIn(task1.get_task_id(), prereqs)
        self.assertIn(task2.get_task_id(), prereqs)

    def test_no_prerequisites(self):
        """Test task without prerequisites."""
        task = Task("Simple Task", "playtime", 20, 5)
        self.assertFalse(task.has_prerequisites())
        self.assertEqual(len(task.get_prerequisites()), 0)

    def test_prerequisites_met(self):
        """Test checking if prerequisites are met."""
        task1 = Task("Feed", "feeding", 10, 8)
        task2 = Task("Walk", "walk", 30, 7)
        task3 = Task("Medicine", "meds", 5, 10)

        task3.add_prerequisite(task1)
        task3.add_prerequisite(task2)

        # Prerequisites not met
        self.assertFalse(task3.are_prerequisites_met([]))
        self.assertFalse(task3.are_prerequisites_met([task1.get_task_id()]))

        # Prerequisites met
        self.assertTrue(
            task3.are_prerequisites_met([task1.get_task_id(), task2.get_task_id()])
        )

    def test_scheduler_enforces_dependencies(self):
        """Test that scheduler enforces task dependencies."""
        owner = Owner("Test Owner", 120)
        pet = Pet("TestPet", "dog", 4, "large")
        scheduler = Scheduler(owner, pet)

        # Create tasks with dependencies
        feeding = Task("Breakfast", "feeding", 15, 5)
        meds = Task("Morning Medicine", "meds", 5, 10)
        meds.add_prerequisite(feeding)  # Medicine after feeding

        # Add in reverse order to test dependency enforcement
        scheduler.add_task(meds)
        scheduler.add_task(feeding)

        plan = scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Both should be scheduled
        self.assertEqual(len(scheduled), 2)

        # Feeding should come before medicine
        task_names = [st.get_task().get_name() for st in scheduled]
        feeding_index = task_names.index("Breakfast")
        meds_index = task_names.index("Morning Medicine")
        self.assertLess(feeding_index, meds_index)

    def test_unmet_dependency_excludes_task(self):
        """Test that task with unmet dependencies gets excluded."""
        owner = Owner("Test Owner", 30)
        pet = Pet("TestPet", "cat", 2, "small")
        scheduler = Scheduler(owner, pet)

        # Create tasks where dependency won't fit
        long_task = Task("Long Grooming", "grooming", 60, 3)
        dependent_task = Task("Post-Grooming Treat", "feeding", 5, 8)
        dependent_task.add_prerequisite(long_task)

        scheduler.add_task(long_task)
        scheduler.add_task(dependent_task)

        plan = scheduler.generate_plan()

        # Long task won't fit, so dependent task should be excluded
        excluded = plan.get_excluded_tasks()
        excluded_names = [t.get_name() for t in excluded]
        self.assertIn("Post-Grooming Treat", excluded_names)

    def test_chain_of_dependencies(self):
        """Test a chain of task dependencies (A -> B -> C)."""
        owner = Owner("Test Owner", 180)
        pet = Pet("TestPet", "dog", 5, "medium")
        scheduler = Scheduler(owner, pet)

        task_a = Task("Feed", "feeding", 15, 5)
        task_b = Task("Walk", "walk", 30, 6)
        task_c = Task("Rest", "enrichment", 20, 4)

        task_b.add_prerequisite(task_a)  # Walk after feeding
        task_c.add_prerequisite(task_b)  # Rest after walk

        # Add in random order
        scheduler.add_task(task_c)
        scheduler.add_task(task_a)
        scheduler.add_task(task_b)

        plan = scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # All should be scheduled in correct order
        task_names = [st.get_task().get_name() for st in scheduled]
        self.assertEqual(task_names[0], "Feed")
        self.assertEqual(task_names[1], "Walk")
        self.assertEqual(task_names[2], "Rest")


class TestDynamicPriorityAdjustment(unittest.TestCase):
    """Test cases for Feature 3: Dynamic Priority Adjustment."""

    def test_set_and_get_last_completed(self):
        """Test setting and retrieving last completion date."""
        task = Task("Daily Walk", "walk", 30, 5)
        completion_date = date.today() - timedelta(days=3)

        task.set_last_completed(completion_date)
        self.assertEqual(task.get_last_completed(), completion_date)

    def test_days_since_completion(self):
        """Test calculating days since last completion."""
        task = Task("Walk", "walk", 30, 5)

        # Task completed 5 days ago
        completion_date = date.today() - timedelta(days=5)
        task.set_last_completed(completion_date)

        self.assertEqual(task.get_days_since_completion(), 5)

    def test_never_completed_task(self):
        """Test that never-completed task has high days count."""
        task = Task("New Task", "playtime", 20, 5)

        # Never completed
        days = task.get_days_since_completion()
        self.assertEqual(days, 999)

    def test_dynamic_priority_increases_with_time(self):
        """Test that priority increases as task gets older."""
        task = Task("Walk", "walk", 30, 5)

        # Just completed - no boost
        task.set_last_completed(date.today())
        self.assertEqual(task.get_dynamic_priority(), 5)

        # 1 day old - small boost
        task.set_last_completed(date.today() - timedelta(days=1))
        self.assertEqual(task.get_dynamic_priority(), 6)

        # 3 days old - medium boost
        task.set_last_completed(date.today() - timedelta(days=3))
        self.assertEqual(task.get_dynamic_priority(), 7)

        # 7 days old - high boost
        task.set_last_completed(date.today() - timedelta(days=7))
        self.assertEqual(task.get_dynamic_priority(), 8)

    def test_dynamic_priority_capped_at_10(self):
        """Test that dynamic priority doesn't exceed 10."""
        task = Task("High Priority Task", "meds", 5, 9)

        # Very old task
        task.set_last_completed(date.today() - timedelta(days=30))

        # Should be capped at 10
        self.assertEqual(task.get_dynamic_priority(), 10)

    def test_apply_dynamic_priority(self):
        """Test applying dynamic priority to task."""
        task = Task("Walk", "walk", 30, 5)

        # Make task 4 days old
        task.set_last_completed(date.today() - timedelta(days=4))

        # Apply dynamic priority
        task.apply_dynamic_priority()

        # Priority should now be adjusted
        self.assertEqual(task.get_priority(), 7)

    def test_reset_to_base_priority(self):
        """Test resetting task to original priority."""
        task = Task("Walk", "walk", 30, 5)

        # Boost priority
        task.set_last_completed(date.today() - timedelta(days=7))
        task.apply_dynamic_priority()
        self.assertEqual(task.get_priority(), 8)

        # Reset to base
        task.reset_to_base_priority()
        self.assertEqual(task.get_priority(), 5)

    def test_scheduler_uses_dynamic_priority(self):
        """Test that scheduler uses dynamic priority for task ordering."""
        owner = Owner("Test Owner", 120)
        pet = Pet("TestPet", "dog", 3, "medium")
        scheduler = Scheduler(owner, pet)

        # Two tasks with same base priority
        task1 = Task("Recent Task", "walk", 30, 5)
        task1.set_last_completed(date.today())  # Just done

        task2 = Task("Old Task", "walk", 30, 5)
        task2.set_last_completed(date.today() - timedelta(days=7))  # Week old

        scheduler.add_task(task1)
        scheduler.add_task(task2)

        plan = scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Old task should be scheduled first due to higher dynamic priority
        self.assertEqual(scheduled[0].get_task().get_name(), "Old Task")
        self.assertEqual(scheduled[1].get_task().get_name(), "Recent Task")


class TestIntegratedFeatures(unittest.TestCase):
    """Test cases for all three features working together."""

    def test_all_features_combined(self):
        """Test time windows, dependencies, and dynamic priority together."""
        owner = Owner("Test Owner", 180)
        pet = Pet("TestPet", "dog", 4, "medium")
        scheduler = Scheduler(owner, pet)

        # Task 1: Morning feeding (time window + old task = high priority)
        feeding = Task("Morning Feeding", "feeding", 15, 6)
        feeding.set_time_window("08:00", "09:00")
        feeding.set_last_completed(date.today() - timedelta(days=5))

        # Task 2: Medicine (depends on feeding + mandatory)
        meds = Task("Medicine", "meds", 5, 8)
        meds.set_mandatory(True)
        meds.add_prerequisite(feeding)

        # Task 3: Walk (old task gets priority boost)
        walk = Task("Morning Walk", "walk", 30, 4)
        walk.set_last_completed(date.today() - timedelta(days=8))

        # Task 4: Play (recent, lower priority)
        play = Task("Playtime", "playtime", 20, 5)
        play.set_last_completed(date.today())

        scheduler.add_task(walk)
        scheduler.add_task(play)
        scheduler.add_task(meds)
        scheduler.add_task(feeding)

        plan = scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # All tasks should fit
        self.assertEqual(len(scheduled), 4)

        # Check explanation mentions advanced features
        explanation = plan.get_explanation()
        self.assertIn("Dynamic priority", explanation)
        self.assertIn("Time-window", explanation)
        self.assertIn("dependencies", explanation)

    def test_complex_scenario_with_exclusions(self):
        """Test complex scenario where some tasks get excluded."""
        owner = Owner("Busy Owner", 60)  # Only 1 hour
        pet = Pet("TestPet", "cat", 2, "small")
        scheduler = Scheduler(owner, pet)

        # Mandatory task with time window
        meds = Task("Morning Meds", "meds", 5, 10)
        meds.set_mandatory(True)
        meds.set_time_window("08:00", "08:30")

        # Task with unmet dependency
        grooming = Task("Grooming", "grooming", 45, 6)
        post_grooming = Task("Brushing", "grooming", 15, 5)
        post_grooming.add_prerequisite(grooming)

        # Old task with high dynamic priority
        play = Task("Play Session", "enrichment", 25, 4)
        play.set_last_completed(date.today() - timedelta(days=10))

        scheduler.add_task(meds)
        scheduler.add_task(grooming)
        scheduler.add_task(post_grooming)
        scheduler.add_task(play)

        plan = scheduler.generate_plan()

        # Should have some scheduled and some excluded
        self.assertGreater(len(plan.get_scheduled_tasks()), 0)
        self.assertGreater(len(plan.get_excluded_tasks()), 0)

        # Mandatory task should be scheduled
        scheduled_names = [
            st.get_task().get_name() for st in plan.get_scheduled_tasks()
        ]
        self.assertIn("Morning Meds", scheduled_names)


if __name__ == "__main__":
    unittest.main()
