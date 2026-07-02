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

> Compare two different prompts (or two different models) on the same task.

|                       | Option A | Option B |
| --------------------- | -------- | -------- |
| **Model / tool used** |          |          |
| **Prompt**            |          |          |
| **Response summary**  |          |          |
| **What was useful**   |          |          |
| **Problems noticed**  |          |          |
| **Decision**          |          |          |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
