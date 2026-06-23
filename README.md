# PawPal+ (Module 2 Project)

**PawPal+** is a small Python backend plus a Streamlit shell that helps a pet owner plan care tasks (walks, feeding, meds, enrichment) under time and priority constraints.

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

## Project layout

| Path | Purpose |
|------|---------|
| `pawpal_system.py` | Domain model (`Task`, `Pet`, `Owner`) and `Scheduler` (priority sort + day packing) |
| `main.py` | CLI demo: sample pets/tasks, prints an optimized schedule |
| `app.py` | Streamlit UI starter (wire your scheduler here when ready) |
| `tests/` | `pytest` tests for core behaviors |
| `uml.mmd` | UML source (Mermaid) |

## Backend overview

- **`Task`** — Care item: description, optional preferred time (`time_minutes` from midnight), frequency, duration, priority, and `completed`. Urgency scoring drives ordering; `mark_complete()` sets done.
- **`Pet`** — Name, species, age, and a list of `Task` instances. Species/age inform recommended care hints and health notes.
- **`Owner`** — Holds `Pet` list; exposes flat views of all tasks (with or without pet pairing).
- **`Scheduler`** — Given an `Owner`, considers only incomplete tasks, sorts by urgency/priority, then assigns non-overlapping start times within a day window (default 07:00–22:00), respecting preferred times when they fit.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the CLI demo

```bash
python main.py
```

Prints a sorted daily plan for the sample pets defined in `main.py`.

### Run the Streamlit app

```bash
streamlit run app.py
```

### Run tests

```bash
pytest tests/ -v
```

## Suggested workflow

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
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
