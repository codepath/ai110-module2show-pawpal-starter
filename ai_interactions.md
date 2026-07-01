# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->
I asked it to refactor my code to take into account weighted prioritization. So, I wanted it to focus on tasks that are seem as more essential and prioritze scheduling those.

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->
It edited pawpal_system and added a responsibility.priority_schedule, which is designed to give a priority weight to each test. It then added more tests to ensure it works.

**What did you have to verify or fix manually?**
I looked over and decided to re-word my prompt to ensure it focus on essential tasks when prioritizing tasks.

<!-- Describe anything the agent got wrong or that required human review -->

I just reviewed the code to ensure it was Pythonic and readable.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | ChatGPT | GEMINI |
| **Prompt** |   In the responsibility class, refactor the code to be more Pythonic.  |   In the responsibility class, refactor the code to be more Pythonic.  |
| **Response summary** |Use an Enum instead of string literals for priority, category, and recurrence | Leveraging StrEnum: Instead of leaving comments like # "low" | "medium" | "high", we formalize them using Python's built-in Enum system. This gives you IDE autocompletion, type safety, and eliminates the need for a brittle Priority.coerce() fallback helper. |
| **What was useful** | Simplify certain function like mark_complete() using an early return | |
| **Problems noticed** | None | overly complicated |
| **Decision** | none | none |

**Which approach did you use in your final implementation and why?**


<!-- Your conclusion -->
I decided the current code was better, but I noticed ChatGPT offered a simpler and more easy-to-understand explanation. However, I felt my code was not overly complicated, so I stuck with that one.
