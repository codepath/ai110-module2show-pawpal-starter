# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I gave Claude the starter Streamlit file and asked it to fix it up and finish the missing scheduling logic. From there I kept handing it more pieces one at a time: a CLI demo file that imported a backend module I hadn't written yet, then my real backend module once I had it, then asked it to fill in my README and reflection docs based on the actual code.


**What did the agent do?**

Rewrote the starter Streamlit app (pawpal_app.py) and added a working scheduler, since the original file was just a UI shell
Wrote a pawpal_system.py backend from scratch to unblock my CLI demo (main.py), since that file referenced a module that didn't exist yet
When I gave it my actual pawpal_system.py, it replaced its placeholder version and re-ran main.py to confirm everything still worked with the real one
Wrote a full test file (test_pawpal_system.py) covering sorting, filtering, conflicts, and recurrence, and actually ran the tests rather than just describing them
Filled in my README and reflection with real output pulled from actually running the code

**What did you have to verify or fix manually?**

I read through the generated backend logic myself to make sure the conflict detection and recurrence rules matched what I actually wanted (same time + same day counts as a conflict, daily tasks roll to the next day). I also checked that the test file's assertions were testing the right thing and not just trivially passing. When it swapped my placeholder backend for the real one, I confirmed on my own that the CLI output still made sense rather than trusting it just because the tests passed.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude| Claude |
| **Prompt** |"Write a Python function that checks if any tasks overlap in time." | "Write a Python function that takes tasks with a time string and duration_minutes, and returns a conflict warning for any two tasks whose time windows overlap on the same day — but only if they belong to different pets."|
| **Response summary** | Loops over all pairs and flags them only if their start times are exactly equal.|Converts times to minutes, checks real interval overlap (start < other_end and other_start < end), and skips pairs that belong to the same pet. |
| **What was useful** |Simple, short, easy to read. |Actually catches back-to-back overlaps , which is the realistic case for a busy owner. |
| **Problems noticed** |Misses real conflicts, two tasks at 08:00 and 08:15 with a 30-min duration clearly overlap, but A reports nothing unless the start times match exactly. |More code to review, and the "different pets only" rule is a judgment call, a real owner also can't do two tasks with the same pet at once, so that exclusion could hide a conflict too. |
| **Decision** |Not used as final. |Used, but I removed the same-pet exclusion after testing, since it hid same-pet double-bookings. |

**Which approach did you use in your final implementation and why?**
Neither one exactly as written, I used Option B's overlap logic (checking real time windows, not just exact matches) since it catches conflicts A misses, but I dropped the "different pets only" rule since same-pet double-booking is still a real conflict for the owner.
