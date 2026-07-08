# AI Interactions Log

---

## Agent Workflow (SF7)

**What task did you give the agent?**

I asked Claude Code (running as an autonomous agent in VS Code) to design and build the complete PawPal+ system from scratch. The prompt was: *"Design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI. Include tests for the most important scheduling behaviors."*

**What did the agent do?**

1. Explored the starter folder to understand the structure (read `app.py`, `README.md`, `reflection.md`, `requirements.txt`, `diagrams/uml.mmd`)
2. Designed the full class hierarchy: `Pet`, `Task`, `OwnerPreferences`, `DailyPlan`, `ScheduledTask`, plus three enums (`TaskType`, `Priority`, `Frequency`) and a `scheduler` module
3. Created `models.py` — all dataclasses with `is_due()`, `hours_overdue()`, and `next_due_at()` methods on `Task`
4. Created `scheduler.py` — `score_task()` function and `generate_plan()` algorithm (greedy fill with scoring formula: priority × 20 + min(overdue × 1.5, 60) + 10 if never done)
5. Created `storage.py` — JSON persistence to `~/.pawpal/` with full serialisation round-trips
6. Wrote `tests/test_scheduler.py` — 15 test cases grouped into `TestScoring` and `TestPlanGeneration`
7. Replaced the starter `app.py` with the full Streamlit UI (three tabs: Today's Plan, Manage Tasks, Pet Setup) including a custom CSS layer, time budget progress bar, per-task reasoning display, and ✓ Done buttons
8. Added `conftest.py` to wire up the test path
9. Updated `diagrams/uml.mmd` with the real Mermaid class diagram
10. Ran the test suite — 18/19 passed on the first run; identified and fixed the failing test

**What did I have to verify or fix manually?**

One test (`test_multiple_daily_due_after_interval`) failed because the test was anchoring `last_done` relative to `datetime.now()` (8 AM) while `generate_plan()` internally evaluates tasks at midnight of the plan date. The agent had written `NOW - timedelta(hours=9)` but the correct reference was `MIDNIGHT - timedelta(hours=9)`. I reviewed the failure, understood the mismatch, and confirmed the fix made the test logically correct — not just passing.

I also reviewed the scoring formula manually with a few sample inputs (see the scoring table in the UML diagram) to confirm that critical overdue tasks always outrank optional just-due tasks and that the overdue cap of 60 points prevents runaway scores.

---

## Prompt Comparison (SF11)

> Comparing two prompts for the scoring formula design.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Code (Sonnet 4.6) | Claude Code (Sonnet 4.6) |
| **Prompt** | "Write a scheduling algorithm that picks tasks by priority" | "Score each task as: priority × 20 (range 20–100) + min(hours_overdue × 1.5, 60) + 10 if never done. Sort by score descending, then greedy-fill the time budget. Tie-break by shorter duration first." |
| **Response summary** | Returned a simple sort by priority enum value, no overdue weighting, no tie-breaking | Implemented exactly the formula specified, including the overdue cap and the secondary sort key |
| **What was useful** | Got working code quickly | Got code that matched the intended behavior with no rework |
| **Problems noticed** | Tasks that were chronically skipped but low-priority would never get scheduled; no tie-breaking meant non-deterministic order | None — matched spec exactly |
| **Decision** | Rejected; produced a plan that would permanently neglect low-priority tasks that were weeks overdue | Used this version in the final implementation |

**Which approach did you use in your final implementation and why?**

Option B. The specific prompt produced a scheduler that actually solves the problem — a pet owner shouldn't have to worry that their dog's weekly grooming gets skipped indefinitely because it's "low priority." The overdue bonus makes sure every task eventually gets its turn. Vague prompts produce generic code; precise prompts produce code that fits the use case.
