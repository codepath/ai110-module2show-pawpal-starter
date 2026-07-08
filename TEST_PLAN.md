# PawPal+ Core Behavior Test Plan

## 1. Task completion and recurrence
### Happy path
- Mark a pending task complete and confirm the `completed` flag becomes `True`.
- Mark a completed task incomplete and confirm the flag flips back to `False`.
- Toggle a task twice and confirm it returns to its original state.
- Complete a daily or weekly task and confirm the scheduler creates the next occurrence with the correct due date.

### Edge cases
- Complete a task with `frequency="once"` and confirm no next occurrence is created.
- Confirm tasks without a due date still behave safely and do not crash.

## 2. Owner and pet management
### Happy path
- Add multiple pets to an owner and confirm each pet is stored correctly.
- Add tasks to pets and to the owner directly, then confirm `get_all_tasks()` returns both sets.
- Remove a pet and confirm its tasks are no longer part of the owner’s combined task list.

### Edge cases
- Create an owner with no pets and confirm task collection stays empty until items are added.
- Remove a task that is not present and confirm the list remains unchanged.

## 3. Scheduler planning and constraints
### Happy path
- Build a daily plan from pending tasks and confirm high-priority tasks are prioritized.
- Apply a `max_tasks` constraint and confirm the plan is truncated correctly.
- Filter tasks by pet name and confirm only the requested pet’s tasks are returned.

### Edge cases
- Request a plan for a pet that has no tasks and confirm the filtered result is empty.
- Include two tasks scheduled at the exact same time and confirm the scheduler reports a conflict.
- Use invalid times and confirm the lightweight conflict check returns a warning rather than crashing.
