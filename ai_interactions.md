# AI Interactions Log

## AI110 final-project interaction (November 5, 2026 UTC)

The final-project request asked the agent to preserve PawPal+ scheduling, complete the AI110 requirements and four bonus features, and test real results without claiming a guaranteed grade. The agent inspected the branch and staged AI files, consulted AVMA/ASPCA guidance, added attributed retrieval, grounded JSON responses, a review-only care planner, a deterministic evaluation subset, and documentation. The first planner syntax check found an unclosed schema dictionary; it was fixed before evaluation.

**Real baseline/RAG comparison:** The same question, “How should I plan dog exercise and fresh water on a warm day?”, was sent once directly to `gemini-3.1-flash-lite` and once through PawPal+'s retrieval path. The direct response gave timing and pavement advice without local citations and was truncated by the 200-token cap. The grounded response advised cooler walks, breaks, shade, water, and veterinary consultation before a new exercise program, citing `dog_care:0` and `dog_care:1`. The complete observed outputs and source URLs are in [the comparison record](docs/ai_live_comparison.json). This single example shows the difference in grounding and citations; it does not establish overall accuracy.

**Real planning trace:** With one demo dog named Mochi, no existing tasks, and a 30-minute budget, the live request asked for a short exercise and water routine. The recorded trace shows: interpret accepted → retrieve 4 chunks → inspect 1 pet and 0 tasks → receive 3 model candidates with valid source IDs → validate task fields and source terms → Scheduler selected 3 of 3 within the budget → present for review. The suggested walk (20 minutes), water/shade check (5), and hydration break (5) were never added to the owner's tasks. See the full trace in the same JSON record. This is an observable action log, not the model's private reasoning.

**Evaluation separation:** `python -m ai.evaluate` passed 23 mocked cases for successful answers, failure paths, citations, safety, UI wiring, and planning validation. Live results above were separate provider calls. The first full pytest attempt hit an existing Windows temporary-directory permission issue during 21 fixture setups; a fresh temporary-directory run is reported in the AI110 section of the README.

---

This log records the agent workflow and prompt-comparison work completed for PawPal+.

---

## Agent Workflow (SF7)

### Bonus algorithm and persistence follow-up

**Requested task:** After correcting the five bonus categories, I asked Codex to complete the remaining achievable work and commit/push it. The agent scoped a third algorithmic capability, next-available-slot search, along with JSON persistence and explicit formatting documentation. This work followed the original prompt comparison; it was not part of either frozen candidate.

**Completed work:** Codex added `Scheduler.next_available_slot()` to sort occupied intervals across pets and scan for the first sufficient gap, including overlapping/nested reservations, touching endpoints and previous-day spillover. It exposed this through a Streamlit form and a CLI demo. It added validated, versioned JSON Save/Load with atomic file replacement and editor-state reset after loading. The four domain classes remain intact. It documented the existing formatting APIs and added 34 tests, including a separate-process load and an independent minute-by-minute search oracle. The full suite passed 150 cases, including all original 97 and frozen 19 cases.

**Files added/modified:** `pawpal_system.py` (slot search), `persistence.py` (new storage functions), `app.py` (search and Save/Load controls), `main.py` (CLI example), `tests/test_bonus_features.py` (new tests), `.gitignore` (exclude local saves), `README.md`, `reflection.md`, this log, `diagrams/uml.mmd`, `diagrams/uml_final.mmd`, `docs/bonus_verification.md`, and historical-report pointers in `docs/submission_readiness.md` and `docs/prompt_comparison.md`. No dependencies or frozen evidence were changed.

**Corrections and review:** My manual correction was supplying the actual five bonus categories. I did not manually repair the new code. The agent's first test run had 31 passes and three failures caused by its new AppTest helper checking the clicked Button instead of the returned AppTest. The agent corrected that helper; all 34 new tests then passed, followed by all 150 tests. Automated UI verification is not a manual browser or accessibility review. Persistence requires explicit Save/Load, uses a single local file, and has no multi-user conflict resolution. Search suggests a slot without assigning it or changing the existing priority-plan algorithm.

### Earlier pending-task editor workflow

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked Codex to implement a pending-task editor while preserving the four-class backend, the original 97 tests, task identity, atomic validation, and existing scheduling behavior. I used two isolated candidates with frozen prompts and 19 shared acceptance tests, then authorized evaluation and integration separately.

**What did the agent do?**

Codex inspected the existing code, implemented each candidate in app.py, and ran the baseline, acceptance, and combined pytest suites, the CLI demo, syntax checks, and Git diff checks. It preserved the prompts, patches, actual available transcripts and results, independently reran the checks, and documented a tie. After my approval, it integrated Strategy A's form editor and the frozen acceptance tests, updated the documentation, and reran all 116 tests. The backend and original test file stayed unchanged.

**What did you have to verify or fix manually?**

I reviewed the comparison and chose Strategy A because I preferred editing fields together in a form. No manual candidate code repair was required by the frozen tests. I also requested a final cleanup of tracked bytecode, outdated documentation and personal paths in the submission evidence. The experiment's unequal prior context remains a limitation. I have not claimed a full manual browser review; the reported UI checks are automated AppTest runs.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Codex CLI 0.155.1; session metadata records `gpt-6-astra`, high reasoning effort. Exact served model build unavailable. | Same recorded configuration; exact served model build unavailable. |
| **Prompt** | [Frozen Strategy A: direct implementation](docs/prompt_comparison/preparation/prompt_a.txt) | [Frozen Strategy B: staged inspection, plan, implementation and review](docs/prompt_comparison/preparation/prompt_b.txt) |
| **Response summary** | Added a pending-task editor using a form, identity-safe selection and atomic backend saves. Only `app.py` changed: +116 / -0 lines. | Added a pending-task editor with a separate rendering helper, identity-safe selection and atomic backend saves. Only `app.py` changed: +98 / -0 lines. |
| **What was useful** | Form batches drafts until Save; explicit field help and validation mapping. Original and evaluator runs each passed 97 baseline, 19 acceptance and 116 combined tests. | Smaller diff and grouped rendering logic; explicit Pet/Task target and broad date bounds. Original and evaluator runs each passed 97 baseline, 19 acceptance and 116 combined tests. |
| **Problems noticed** | More top-level UI code and selection-label state; default date bounds. This run retained preparation context, so conditions were not fully controlled. No browser review. | Every widget event reruns the app; fewer field hints and change detection using `vars(task)`. Separate first-task session verified from logs; launch-directory/permission conditions differed. No browser review. |
| **Decision** | Experimental tie; subsequently selected for integration because the form batches edits until Save. No candidate repair needed or made. | Experimental tie; retained as evidence and not integrated. No candidate repair needed or made. |

I compared the actual patches and kept the original prompts, visible Codex transcripts, tool results and environment records separate from fresh evaluator checks. Both implementations preserved task identity, rejected the tested invalid edits atomically and avoided duplicate tasks. A's form and B's rendering helper are different strengths; the evidence did not establish an overall winner. The unequal prior context means I cannot attribute the differences only to prompt strategy. This was one run per strategy, not a general model-performance finding.

See [the full comparison and acceptance review](docs/prompt_comparison.md) and [evidence index](docs/prompt_comparison/README.md). The evaluator reran all eight frozen commands for each candidate on October 11, 2026; all exited successfully. Additional AppTest observations are labeled separately and are not browser verification. Neither candidate received a human repair.

**Which approach did you use in your final implementation and why?**

I selected Strategy A for integration because I prefer its form-based editing experience: users change task fields together and submit them with **Save changes**. Both candidates passed the same checks, so this choice does not turn the experimental tie into a claim that Strategy A or direct prompting is generally better. After my approval, the preserved A implementation and the unchanged 19 frozen acceptance tests were copied into main's working tree. The backend, original 97 tests, evidence archive and both candidate worktrees were preserved during that integration. The final project was subsequently committed and pushed as `7013138f8599520c275fd9cf47a59f329e346bfc`. The bonus work documented above extends main separately; it does not change the frozen candidates or the experimental tie. No manual browser verification is claimed.
