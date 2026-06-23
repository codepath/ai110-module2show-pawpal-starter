"""
Specific Edge Case Tests for PawPal+ Scheduler

Tests for:
1. Sorting Correctness - Verify tasks are returned in chronological order
2. Recurrence Logic - Confirm that marking a daily task complete creates a new task for the following day
3. Conflict Detection - Verify that the Scheduler flags duplicate times
"""

import unittest
from datetime import date, timedelta

from pawpal_system import Owner, Pet, Plan, ScheduledTask, Scheduler, Task


class TestSortingCorrectness(unittest.TestCase):
    """Verify tasks are returned in chronological order."""

    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner("Test Owner", 180)
        self.pet = Pet("TestPet", "dog", 3, "medium")
        self.scheduler = Scheduler(self.owner, self.pet)

    def test_tasks_returned_in_chronological_order(self):
        """Verify that generated schedule has tasks in chronological order."""
        # Add tasks in random order to test sorting
        task1 = Task("Late Task", "playtime", 20, 3)
        task2 = Task("First Task", "feeding", 15, 5)
        task3 = Task("Second Task", "walk", 30, 4)

        # Add in reverse order
        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)
        self.scheduler.add_task(task3)

        # Generate schedule
        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Verify tasks are in chronological order
        for i in range(len(scheduled) - 1):
            current_time = scheduled[i].get_start_time()
            next_time = scheduled[i + 1].get_start_time()

            # Convert times to comparable format (HH:MM)
            self.assertLessEqual(
                current_time,
                next_time,
                f"Task at {current_time} should not come after task at {next_time}",
            )

    def test_single_task_chronological(self):
        """Verify single task is trivially in order."""
        task = Task("Only Task", "walk", 30, 5)
        self.scheduler.add_task(task)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Single task is always in order
        self.assertEqual(len(scheduled), 1)

    def test_empty_schedule_chronological(self):
        """Verify empty schedule has no order issues."""
        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        self.assertEqual(len(scheduled), 0)

    def test_tasks_with_time_windows_chronological(self):
        """Verify tasks with time windows maintain chronological order."""
        # Task with specific time window
        early_task = Task("Early Walk", "walk", 30, 5)
        early_task.set_time_window("08:00", "09:00")

        late_task = Task("Late Play", "playtime", 20, 4)
        late_task.set_time_window("17:00", "18:00")

        # Add in reverse order
        self.scheduler.add_task(late_task)
        self.scheduler.add_task(early_task)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Verify order
        self.assertGreaterEqual(len(scheduled), 1)
        for i in range(len(scheduled) - 1):
            current_time = scheduled[i].get_start_time()
            next_time = scheduled[i + 1].get_start_time()
            self.assertLessEqual(current_time, next_time)

    def test_mandatory_tasks_chronological_with_regular(self):
        """Verify mandatory and regular tasks mix in chronological order."""
        mandatory = Task("Mandatory Meds", "meds", 5, 10)
        mandatory.set_mandatory(True)

        regular1 = Task("First Regular", "feeding", 15, 5)
        regular2 = Task("Second Regular", "walk", 30, 4)

        # Add in reverse order
        self.scheduler.add_task(regular2)
        self.scheduler.add_task(mandatory)
        self.scheduler.add_task(regular1)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # All scheduled tasks should be in order
        for i in range(len(scheduled) - 1):
            current_time = scheduled[i].get_start_time()
            next_time = scheduled[i + 1].get_start_time()
            self.assertLessEqual(current_time, next_time)

    def test_dependency_tasks_chronological(self):
        """Verify tasks with dependencies maintain chronological order."""
        task_a = Task("Task A", "feeding", 15, 5)
        task_b = Task("Task B", "walk", 30, 4)
        task_b.add_prerequisite(task_a)

        task_c = Task("Task C", "playtime", 20, 3)
        task_c.add_prerequisite(task_b)

        # Add in random order
        self.scheduler.add_task(task_c)
        self.scheduler.add_task(task_a)
        self.scheduler.add_task(task_b)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Verify all were scheduled
        self.assertEqual(len(scheduled), 3)

        # Verify order
        task_names = [st.get_task().get_name() for st in scheduled]
        self.assertEqual(task_names, ["Task A", "Task B", "Task C"])


class TestRecurrenceLogic(unittest.TestCase):
    """Confirm that marking a daily task complete creates a new task for the following day."""

    def test_daily_task_creates_next_day_occurrence(self):
        """Verify daily task completion creates tomorrow's task."""
        task = Task("Morning Feeding", "feeding", 15, 8)
        task.set_frequency("daily")

        # Complete the task
        next_task = task.complete_and_recur()

        # Verify new task was created
        self.assertIsNotNone(next_task)

        # Verify next occurrence is tomorrow
        expected_date = date.today() + timedelta(days=1)
        self.assertEqual(next_task.get_next_occurrence(), expected_date)

    def test_weekly_task_creates_next_week_occurrence(self):
        """Verify weekly task completion creates next week's task."""
        task = Task("Weekly Grooming", "grooming", 60, 6)
        task.set_frequency("weekly")

        # Complete the task
        next_task = task.complete_and_recur()

        # Verify new task was created
        self.assertIsNotNone(next_task)

        # Verify next occurrence is next week
        expected_date = date.today() + timedelta(weeks=1)
        self.assertEqual(next_task.get_next_occurrence(), expected_date)

    def test_monthly_task_creates_next_month_occurrence(self):
        """Verify monthly task completion creates next month's task."""
        task = Task("Monthly Vet Checkup", "medical", 60, 10)
        task.set_frequency("monthly")

        # Complete the task
        next_task = task.complete_and_recur()

        # Verify new task was created
        self.assertIsNotNone(next_task)

        # Verify next occurrence is approximately next month
        expected_date = date.today() + timedelta(days=30)
        self.assertEqual(next_task.get_next_occurrence(), expected_date)

    def test_non_recurring_task_creates_no_new_task(self):
        """Verify non-recurring task completion does not create new task."""
        task = Task("One-Time Event", "training", 45, 5)
        task.set_recurs(False)

        # Complete the task
        next_task = task.complete_and_recur()

        # Verify no new task was created
        self.assertIsNone(next_task)

        # Original should be marked complete
        self.assertTrue(task.is_completed())

    def test_daily_task_properties_preserved(self):
        """Verify new daily task inherits all properties from original."""
        original = Task("Morning Walk", "walk", 30, 7)
        original.set_frequency("daily")
        original.set_description("Park walk with ball")
        original.set_mandatory(True)
        original.set_time_window("08:00", "09:00")

        # Complete the task
        next_task = original.complete_and_recur()

        # Verify properties are preserved
        self.assertEqual(next_task.get_name(), "Morning Walk")
        self.assertEqual(next_task.get_task_type(), "walk")
        self.assertEqual(next_task.get_duration(), 30)
        self.assertEqual(next_task.get_priority(), 7)
        self.assertEqual(next_task.get_description(), "Park walk with ball")
        self.assertTrue(next_task.is_mandatory())
        self.assertTrue(next_task.has_time_window())

        start, end = next_task.get_time_window()
        self.assertEqual(start, "08:00")
        self.assertEqual(end, "09:00")

    def test_daily_task_new_id_created(self):
        """Verify new daily task has different ID than original."""
        task = Task("Daily Task", "playtime", 20, 5)
        task.set_frequency("daily")

        # Complete the task
        next_task = task.complete_and_recur()

        # Verify different IDs
        self.assertNotEqual(task.get_task_id(), next_task.get_task_id())

    def test_original_marked_complete(self):
        """Verify original task is marked as completed."""
        task = Task("Daily Feeding", "feeding", 15, 8)
        task.set_frequency("daily")

        # Initially not complete
        self.assertFalse(task.is_completed())

        # Complete the task
        next_task = task.complete_and_recur()

        # Verify now complete
        self.assertTrue(task.is_completed())

        # Verify last completed date set
        self.assertEqual(task.get_last_completed(), date.today())

    def test_multiple_daily_completions_chain(self):
        """Verify multiple completions create chain of tasks."""
        task1 = Task("Daily Task", "enrichment", 15, 6)
        task1.set_frequency("daily")

        # First completion
        task2 = task1.complete_and_recur()
        self.assertIsNotNone(task2)

        # Second completion
        task3 = task2.complete_and_recur()
        self.assertIsNotNone(task3)

        # Third completion
        task4 = task3.complete_and_recur()
        self.assertIsNotNone(task4)

        # Verify chain
        self.assertTrue(task1.is_completed())
        self.assertTrue(task2.is_completed())
        self.assertTrue(task3.is_completed())
        self.assertFalse(task4.is_completed())

        # Verify different IDs
        self.assertNotEqual(task1.get_task_id(), task2.get_task_id())
        self.assertNotEqual(task2.get_task_id(), task3.get_task_id())
        self.assertNotEqual(task3.get_task_id(), task4.get_task_id())

    def test_scheduler_completion_creates_new_task(self):
        """Verify completing task through scheduler creates next occurrence."""
        owner = Owner("Test Owner", 120)
        pet = Pet("TestPet", "cat", 2, "small")
        scheduler = Scheduler(owner, pet)

        task = Task("Daily Feeding", "feeding", 15, 8)
        task.set_frequency("daily")
        scheduler.add_task(task)

        # Initial state
        initial_count = len(scheduler.get_tasks())

        # Complete through scheduler
        next_task = scheduler.complete_task(task.get_task_id())

        # Verify new task created
        self.assertIsNotNone(next_task)
        self.assertEqual(len(scheduler.get_tasks()), initial_count + 1)

        # Verify it's in the scheduler
        self.assertIn(next_task, scheduler.get_tasks())


class TestConflictDetection(unittest.TestCase):
    """Verify that the Scheduler flags duplicate or overlapping times."""

    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner("Test Owner", 180)
        self.pet = Pet("TestPet", "dog", 3, "medium")
        self.scheduler = Scheduler(self.owner, self.pet)

    def test_no_conflicts_for_separate_times(self):
        """Verify no conflicts when tasks have separate times."""
        # Add tasks that fit without overlap
        task1 = Task("Task 1", "feeding", 15, 8)
        task2 = Task("Task 2", "walk", 30, 7)
        task3 = Task("Task 3", "playtime", 20, 6)

        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)
        self.scheduler.add_task(task3)

        plan = self.scheduler.generate_plan()

        # Should have 3 tasks without conflicts
        self.assertEqual(len(plan.get_scheduled_tasks()), 3)

    def test_manual_scheduled_tasks_no_conflicts(self):
        """Verify manually added scheduled tasks don't conflict."""
        owner = Owner("Test Owner", 60)
        pet = Pet("TestPet", "dog", 3, "medium")
        plan = Plan()

        # Manually add two non-overlapping scheduled tasks
        task1 = Task("Task 1", "walk", 20, 5)
        task2 = Task("Task 2", "playtime", 20, 5)

        scheduled1 = ScheduledTask(task1, "08:00", "08:20", 1)
        scheduled2 = ScheduledTask(task2, "08:30", "08:50", 2)

        plan.add_scheduled_task(scheduled1)
        plan.add_scheduled_task(scheduled2)

        # No conflicts
        scheduled = plan.get_scheduled_tasks()
        self.assertEqual(len(scheduled), 2)

    def test_tasks_with_same_priority_no_conflict(self):
        """Verify tasks with same priority don't inherently conflict."""
        # Add multiple tasks with same priority
        for i in range(5):
            task = Task(f"Task {i}", "walk", 20, 5)
            self.scheduler.add_task(task)

        plan = self.scheduler.generate_plan()

        # Should schedule as many as fit
        self.assertGreaterEqual(len(plan.get_scheduled_tasks()), 1)

    def test_mandatory_tasks_time_conflict(self):
        """Verify behavior when mandatory tasks conflict in time."""
        # Create many mandatory tasks
        for i in range(10):
            task = Task(f"Mandatory {i}", "meds", 15, 10)
            task.set_mandatory(True)
            self.scheduler.add_task(task)

        # Generate plan
        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Should schedule as many mandatory as fit
        # Not all 10 will fit in 180 minutes (need 150 min, but scheduling overhead)
        total_time = plan.get_total_time()
        self.assertLessEqual(total_time, 180)

    def test_time_window_constraints_prevent_conflicts(self):
        """Verify time windows help prevent scheduling conflicts."""
        # Task that must be at specific time
        morning_task = Task("Morning Meds", "meds", 5, 10)
        morning_task.set_time_window("08:00", "09:00")

        # Another task that could overlap
        walk_task = Task("Morning Walk", "walk", 60, 5)

        self.scheduler.add_task(morning_task)
        self.scheduler.add_task(walk_task)

        plan = self.scheduler.generate_plan()

        # Meds should be within 08:00-09:00
        for st in plan.get_scheduled_tasks():
            if st.get_task().get_name() == "Morning Meds":
                self.assertTrue(morning_task.can_schedule_at_time(st.get_start_time()))

    def test_dependent_tasks_no_time_conflict(self):
        """Verify dependent tasks are scheduled sequentially, not overlapping."""
        # Create dependent tasks
        feeding = Task("Feeding", "feeding", 15, 8)
        meds = Task("Meds", "meds", 5, 10)
        meds.add_prerequisite(feeding)

        self.scheduler.add_task(meds)
        self.scheduler.add_task(feeding)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Both should be scheduled
        self.assertEqual(len(scheduled), 2)

        # Find positions
        feeding_idx = None
        meds_idx = None
        for i, st in enumerate(scheduled):
            if st.get_task().get_name() == "Feeding":
                feeding_idx = i
            elif st.get_task().get_name() == "Meds":
                meds_idx = i

        # Feeding should come before meds
        self.assertIsNotNone(feeding_idx)
        self.assertIsNotNone(meds_idx)
        self.assertLess(feeding_idx, meds_idx)

    def test_scheduler_returns_excluded_tasks(self):
        """Verify scheduler identifies and reports tasks that don't fit."""
        # Add many tasks
        for i in range(20):
            task = Task(f"Task {i}", "walk", 30, 5)
            self.scheduler.add_task(task)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()
        excluded = plan.get_excluded_tasks()

        # Some should be scheduled, some excluded
        self.assertGreater(len(scheduled), 0)
        self.assertGreater(len(excluded), 0)

        # Total should equal all tasks
        self.assertEqual(len(scheduled) + len(excluded), 20)

    def test_time_based_sorting_prevents_conflicts(self):
        """Verify tasks are sorted by time to prevent conflicts."""
        # Create tasks with different times via time windows
        early_task = Task("Early", "walk", 30, 5)
        early_task.set_time_window("08:00", "09:00")

        late_task = Task("Late", "playtime", 30, 5)
        late_task.set_time_window("17:00", "18:00")

        # Add in reverse order
        self.scheduler.add_task(late_task)
        self.scheduler.add_task(early_task)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # All scheduled tasks should be in time order
        for i in range(len(scheduled) - 1):
            current = scheduled[i].get_start_time()
            next_time = scheduled[i + 1].get_start_time()
            self.assertLessEqual(current, next_time)

    def test_dynamic_priority_does_not_cause_conflicts(self):
        """Verify dynamic priority doesn't introduce scheduling conflicts."""
        # Create tasks with different completion times
        recent_task = Task("Recent", "walk", 30, 5)
        recent_task.set_last_completed(date.today())

        old_task = Task("Old", "grooming", 30, 3)
        old_task.set_last_completed(date.today() - timedelta(days=10))

        self.scheduler.add_task(recent_task)
        self.scheduler.add_task(old_task)

        plan = self.scheduler.generate_plan()
        scheduled = plan.get_scheduled_tasks()

        # Both should be scheduled without conflicts
        # Old task gets priority boost but still scheduled
        self.assertEqual(len(scheduled), 2)

        # Verify order - old task should come first due to boost
        task_names = [st.get_task().get_name() for st in scheduled]
        self.assertEqual(task_names[0], "Old")


if __name__ == "__main__":
    unittest.main()
