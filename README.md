# PawPal+ (Module 2 Project)

[![Test](https://github.com/Inventrohyder/ai110-module2show-pawpal-starter/actions/workflows/test.yml/badge.svg)](https://github.com/Inventrohyder/ai110-module2show-pawpal-starter/actions/workflows/test.yml)
[![Trunk Check](https://github.com/Inventrohyder/ai110-module2show-pawpal-starter/actions/workflows/trunk-check.yml/badge.svg)](https://github.com/Inventrohyder/ai110-module2show-pawpal-starter/actions/workflows/trunk-check.yml)

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

This project uses [uv](https://docs.astral.sh/uv/) for dependency management (see `docs/decisions/0001-use-uv.md`):

```bash
uv sync                        # installs runtime + dev dependencies from uv.lock
uv run streamlit run app.py    # launch the app
uv run python main.py          # run the CLI demo
uv run pytest                  # run the tests
```

<details>
<summary>Prefer plain pip? (requirements.txt is generated from uv.lock)</summary>

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

</details>

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Captured from a real run of `uv run python main.py`:

```text
PawPal+ demo — household of Jordan: Mochi the dog, Whiskers the cat

Today's Schedule (as entered)
-----------------------------
08:00  Mochi (dog)  Morning walk  [30 min, daily, pending]
18:30  Mochi (dog)  Evening walk  [30 min, daily, pending]
09:00  Whiskers (cat)  Feeding  [10 min, daily, pending]
20:00  Whiskers (cat)  Litter box cleanup  [15 min, once, pending]

Today's Schedule (sorted by time)
---------------------------------
08:00  Mochi (dog)  Morning walk  [30 min, daily, pending]
09:00  Whiskers (cat)  Feeding  [10 min, daily, pending]
18:30  Mochi (dog)  Evening walk  [30 min, daily, pending]
20:00  Whiskers (cat)  Litter box cleanup  [15 min, once, pending]

Mochi only (filter_by_pet)
--------------------------
08:00  Mochi (dog)  Morning walk  [30 min, daily, pending]
18:30  Mochi (dog)  Evening walk  [30 min, daily, pending]

Still pending (filter_by_status)
--------------------------------
08:00  Mochi (dog)  Morning walk  [30 min, daily, pending]
18:30  Mochi (dog)  Evening walk  [30 min, daily, pending]
20:00  Whiskers (cat)  Litter box cleanup  [15 min, once, pending]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```text
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature           | Method(s)                                                   | Notes                                                 |
| ----------------- | ----------------------------------------------------------- | ----------------------------------------------------- |
| Task sorting      | `Scheduler.sort_by_time()`                                  | Chronological "HH:MM" ordering across **all** pets    |
| Filtering         | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Narrow any view to pending/done tasks or a single pet |
| Conflict handling |                                                             | _lands with `detect_conflicts()`_                     |
| Recurring tasks   |                                                             | _lands with `complete_task()` recurrence_             |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
