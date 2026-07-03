# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- **Sort tasks by time of day** — View every task in chronological order so your day reads top to bottom. Tasks without a set time are grouped neatly at the end.
- **Filter by pet and status** — Narrow the task list to a single pet, to only what's still pending, or to what's already done — or combine both to focus on exactly what needs attention.
- **Conflict detection** — Get clear warnings when two tasks are scheduled for the same time, including whether the clash is for the same pet or across different pets. Warnings never block you — you stay in control of the final call.
- **Recurring tasks** — Mark a task as daily or weekly and PawPal+ automatically generates the next occurrence when you complete it, so routine care stays on the calendar without re-entering it. Completing the same task twice never creates a duplicate.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# Daily plan for Alice — 2026-06-28
#  08:00-08:10  Feed Whiskers (10 min) [high]
#  08:10-08:25  Feed Buddy (15 min) [high]
#  08:25-08:55  Walk Buddy (30 min) [high]

# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite: my tests cover mostly everything in the scheduler sorting, filtering, recurring and conflicts 
pyhton -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```
========================================= test session start =========================================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\kerouat\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 34 items                                                                                                                                                                                                                

tests\test_pawpal.py ..................................                                                                                                                                                                     [100%]

========================================= 34 passed in 0.26s =========================================

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature           | Method(s)         | Notes                             |
|-------------------|-------------------|-----------------------------------|
| Task sorting      | sort_by_time      | e.g., by priority, duration       |
| Filtering         | tasks_by_status   | e.g., skip tasks if time runs out |
| Conflict handling | detect_conflicts  | e.g., overlapping time slots      |
| Recurring tasks   | _next_occurence   | e.g., daily vs. weekly            |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
