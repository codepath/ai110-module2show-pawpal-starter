# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to implement the 'next available slot' scheduling feature (PR 18 stretch goal). This feature must find the earliest time slot of a given duration during waking hours (07:00 to 21:00) where a task can be scheduled without overlapping any existing pending tasks across all pets in the household.

**What did the agent do?**

The agent autonomously performed the following actions:

1. Configured waking hours `DAY_START` ("07:00") and `DAY_END` ("21:00") constants and conversion utilities `_to_minutes` / `_to_hhmm` in `pawpal_system.py`.
2. Wrote the sorting and interval checking algorithm inside `Scheduler.find_next_available_slot(duration_minutes, day)`.
3. Integrated the feature into `main.py` (CLI demo) and the Streamlit UI `app.py` under a new "Find a free slot" section.
4. Added test coverage: unit tests in `tests/test_pawpal.py` and UI e2e tests in `tests/test_app_ui.py`.
5. Updated `CHANGELOG.md` and `README.md` to reflect the new feature and output.

I reviewed the slot-scanning algorithm for edge cases around waking-hour boundaries. The test `test_next_available_slot_respects_day_end_boundary_with_late_task` was added to verify that tasks scheduled after `DAY_END` (e.g., at 22:00) don't allow the algorithm to return invalid slots that would extend past waking hours. The algorithm correctly clamps all gap scanning to the `DAY_END` boundary.

---

## Prompt Comparison (SF11)

> Two design approaches were considered for the `reschedule_task(task, new_time, new_date)` method.

|                      | Option A                                                                                                                                                                                                                                         | Option B                                                                                                                                                                                                                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Approach**         | AI agent (direct instruction)                                                                                                                                                                                                                    | AI agent (open-ended design question)                                                                                                                                                                                                                                                                         |
| **Prompt**           | Write a `reschedule_task(task, new_time, new_date)` method on the Scheduler class. It should mutate the task's time and date attributes, and run `detect_conflicts()` returning the list of warnings. Completed tasks should raise a ValueError. | Design a reschedule_task method on Scheduler. Should rescheduling return a new Task object (immutable style) or mutate the existing one? Implement the best pattern and check for conflicts at the new position.                                                                                              |
| **Response summary** | Provided a simple implementation that directly updates `task.time = new_time` and `task.date = new_date`, runs conflict detection, and returns warnings. Raises `ValueError` if `task.completed`.                                                | Suggested that since Task objects are dataclasses, mutating them directly might break references. Proposed returning a new `replace(task, time=new_time, date=new_date)` instance, updating the list in the `Pet` object, running `detect_conflicts()`, and reverting if conflicts exist (transaction-style). |
| **What was useful**  | Simple, minimal code footprint, fits perfectly with the existing mutable design where `mark_complete()` modifies `completed = True` in-place.                                                                                                    | Showed a robust transaction-like pattern: copy, replace, check conflicts, commit. Very safe for concurrent execution or database-backed engines.                                                                                                                                                              |
| **Problems noticed** | Risk of corrupting scheduler state if conflicts exist (the change is committed instantly even if there's a conflict warning, which is acceptable in our advisory conflict design but could be problematic).                                      | Overly complex for the current simple local in-memory structure; replacing task objects in the Pet's task list requires searching and mutating list indices, which is verbose in pure Python without an ORM.                                                                                                  |
| **Decision**         | Selected Option A (Direct Mutation) for simplicity, aligning with the project's existing state modification style (e.g., `task.mark_complete()`), but adjusted to return the conflict warnings without raising errors, keeping it advisory.      | Selected Option A (Direct Mutation) for simplicity, aligning with the project's existing state modification style.                                                                                                                                                                                            |

**Which approach did you use in your final implementation and why?**

I used Option A (Direct Mutation). Mutating the existing Task instance attributes (`task.time` and `task.date`) is direct, easy to test, and matches how completing tasks modifies `task.completed = True` in-place. Given that conflicts in our system are purely advisory warnings and do not crash or prevent tasks from existing, there was no need to implement a complex database-like rollback transaction or list-index replacements for immutable dataclass copies. This choice kept the codebase clean, lean, and highly maintainable.
