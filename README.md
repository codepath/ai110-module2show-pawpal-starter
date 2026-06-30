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

```bash
==================================================
Today's Schedule for Justin
==================================================

Rex (dog)
--------------------------------------------------
  08:00-08:30  Morning walk (walk, high)
  08:30-08:40  Breakfast (feeding, high)
  18:00-18:30  Evening walk (walk, medium)
  Total: 70 min of care

Mittens (cat)
--------------------------------------------------
  07:30-07:40  Morning feeding (feeding, high)
  12:00-12:15  Litter box cleaning (grooming, medium)
  19:00-19:20  Play time (enrichment, low)
  Total: 45 min of care

```
## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```bash

tests\test_pawpal.py ..                                                       [100%]

================================ 2 passed in 0.05s =================================

```

## Tradeoffs
One tradeoff is that in detect_conflicts() function, is we use a nested loop to go through items in each section, so it is O(n^2) instead of O(n). So I traded a slower space complexity in order for simpler and easier-to-understand code.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | sort_by_time() | sorts item by time  |
| Filtering | filter_tasks() | filter tasks by completion status or by pet |
| Conflict handling | detect_conflicts() | checks the schedule and detects overlapping time conflcits |
| Recurring tasks | next_occurrence | it spawns a new task after the one is completed |



## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
