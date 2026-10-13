# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code (Claude Opus 5.5) in the Claude desktop app. I asked it to clone the repo, set up the environment, run the app, and then "start on the PawPal logic": design the classes, implement the scheduler, test it, and connect it to the Streamlit UI.

**What did the agent do?**

1. Created a `.venv`, installed `requirements.txt` (Streamlit, pytest), and confirmed the app started.
2. Read `README.md`, `app.py`, `diagrams/uml.mmd`, and `reflection.md` to understand the requirements.
3. Proposed a design (`Task`, `Pet`, `Owner`, `Scheduler`, `DailyPlan`, `ScheduledItem`) and wrote it in `pawpal_system.py`.
4. Ran `python pawpal_system.py` on sample data to check the output (a 60-min task was correctly skipped when only 10 min were left).
5. Wrote 11 pytest tests in `tests/test_pawpal_system.py` plus a `pytest.ini`; all passed.
6. Replaced the placeholder UML in `diagrams/uml.mmd` with the real classes.
7. Updated `app.py`: added a time-budget input, a preferred-time option per task, a Clear tasks button, and connected Generate schedule to the scheduler.
8. Opened the app in a browser, added a task, clicked Generate schedule, and confirmed the plan table appeared.

Along the way it hit two environment problems and worked around them on its own:
- Port 8501 was already in use by my StudySync app, so it ran PawPal on port 8502 instead of stopping my other app.
- The built-in terminal panel failed to start, so it ran the app as a background process instead.

**What did you have to verify or fix manually?**

<!-- TODO (write this yourself after checking): e.g. did you run `pytest` and the app yourself? Did the scheduling rules match what YOU think a pet owner needs (e.g. should "shorter tasks first" really break ties)? Did you change anything? -->

Things to double-check:
- The agent's tests pass, but it wrote both the code and the tests, so the tests only check the rules it chose.
- I should confirm the scheduling rules make sense for a real pet owner.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Code agent (Claude Opus 5.5) | Claude Code agent (Claude Opus 5.5), same model, separate copy of the project |
| **Prompt** | Vague, one line: "Add conflict handling to the PawPal+ scheduler." | Detailed, 9 numbered requirements: add a `fixed_time` field; when fixed tasks overlap the higher priority wins (tie: first listed); move flexible tasks out of the way; add a `DailyPlan.conflicts` list; list the exact tests to write; update `app.py` and the UML; match the existing style. |
| **Response summary** | Had to decide for itself what "conflict" means. It added `fixed_time`, resolves fixed-task overlaps (tie: earlier start wins), moves flexible tasks to the first free gap, and also counts a task pushed out of its preferred part of the day as a conflict. It also edited the README. About 320 lines added; 21 tests pass. | Did what was specified and little more. It added `fixed_time`, resolves overlaps (tie: first listed wins), pushes flexible tasks past fixed ones, and adds a `conflicts` list. About 150 lines added; 18 tests pass. |
| **What was useful** | Thought of cases I didn't ask for: the "pushed out of its preferred part of the day" conflict, back-to-back tasks not counting as overlap, and a dropped task not using up time budget. Its demo shows an actual conflict (a groomer drop-off overlapping the vet visit). | Predictable and easy to review, because every change matched a requirement. About half as much code. It also pointed out a gap on its own: `"8:00"` is accepted as a valid time. |
| **Problems noticed** | Twice as much code to review. It changed more than asked (README) and wrote a temporary script outside the folder it was told to stay in (then deleted it). The tie-break rule (earlier start wins) was its own choice, not mine. Its report said 10 existing tests when there were 11. | Requirement 3 in my prompt was a garbled sentence. The agent guessed the meaning correctly, but only because it guessed. A dropped fixed task still uses up time budget (I asked for that, but it's a weaker design than A's). Its demo has no actual fixed-vs-fixed conflict. |
| **Decision** | Not used directly; borrowed one idea (resolve fixed-time conflicts *before* the time budget). | **Used** as the base implementation. |

**Which approach did you use in your final implementation and why?**

I used Option B (the detailed prompt) as the base and added one idea from Option A.

**Why B:** every change B made traced back to a requirement I wrote, so I could review it line by line and know what it would do. It was also about half as much code as A. A made several design decisions on its own, like what counts as a conflict and how ties are broken. Some were good, but I would have had to check each one before trusting it. A also edited files I hadn't asked about (the README) and wrote a file outside the folder it was told to use.

**What I took from A:** A resolved fixed-time conflicts *before* applying the time budget, so a task that loses a conflict doesn't use up minutes. B did it the other way, because my prompt told it to "keep it simple." That meant a dropped task could still crowd out a task that would have fit. I merged A's approach into B and added a test (`test_dropped_fixed_task_does_not_use_up_time_budget`). The test fails on B's original code and passes on the merged version.

**What I learned:** the vague prompt was more creative, and the detailed prompt was more predictable. But the detailed prompt is only as good as what I write in it. One of my requirements was a garbled sentence, and B only got it right by guessing. Next time I'd write the spec carefully and still ask the AI what edge cases I missed.
