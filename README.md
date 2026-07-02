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
08:00  Mochi (dog)  Morning walk  [30 min, daily, medium, pending]
18:30  Mochi (dog)  Evening walk  [30 min, daily, medium, pending]
09:00  Whiskers (cat)  Feeding  [10 min, daily, medium, pending]
20:00  Whiskers (cat)  Litter box cleanup  [15 min, once, medium, pending]

Today's Schedule (sorted by time)
---------------------------------
08:00  Mochi (dog)  Morning walk  [30 min, daily, medium, pending]
09:00  Whiskers (cat)  Feeding  [10 min, daily, medium, pending]
18:30  Mochi (dog)  Evening walk  [30 min, daily, medium, pending]
20:00  Whiskers (cat)  Litter box cleanup  [15 min, once, medium, pending]

Mochi only (filter_by_pet)
--------------------------
08:00  Mochi (dog)  Morning walk  [30 min, daily, medium, pending]
18:30  Mochi (dog)  Evening walk  [30 min, daily, medium, pending]

Still pending (filter_by_status)
--------------------------------
08:00  Mochi (dog)  Morning walk  [30 min, daily, medium, pending]
18:30  Mochi (dog)  Evening walk  [30 min, daily, medium, pending]
20:00  Whiskers (cat)  Litter box cleanup  [15 min, once, medium, pending]

Completed 'Morning walk' (daily) -> next occurrence auto-scheduled for tomorrow at 08:00

Added 'Medication' for Whiskers at 18:30 (same time as Mochi's evening walk):
  ⚠️  Conflict at 18:30 on today: Evening walk (Mochi) overlaps Medication (Whiskers)

Priority view (sort_by_priority: high first, then time)
-------------------------------------------------------
16:00  Mochi (dog)  Vet appointment  [45 min, once, high, pending]
08:00  Mochi (dog)  Morning walk  [30 min, daily, medium, done]
08:00  Mochi (dog)  Morning walk  [30 min, daily, medium, pending]
09:00  Whiskers (cat)  Feeding  [10 min, daily, medium, done]
18:30  Mochi (dog)  Evening walk  [30 min, daily, medium, pending]
18:30  Whiskers (cat)  Medication  [5 min, once, medium, pending]
20:00  Whiskers (cat)  Litter box cleanup  [15 min, once, medium, pending]

Next free 30-minute slot today (find_next_available_slot): 07:00
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

| Feature                       | Method(s)                                                   | Notes                                                                             |
| ----------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Task sorting                  | `Scheduler.sort_by_time()`                                  | Chronological "HH:MM" ordering across **all** pets                                |
| Filtering                     | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Narrow any view to pending/done tasks or a single pet                             |
| Conflict handling             | `Scheduler.detect_conflicts()`                              | Warns (never crashes) on identical date+time collisions, across pets              |
| Recurring tasks               | `Scheduler.complete_task()`, `Task.next_occurrence()`       | Completing a daily/weekly task auto-schedules the next occurrence (+1d/+7d)       |
| Priority ordering (stretch)   | `Scheduler.sort_by_priority()`                              | High > medium > low, ties broken chronologically; "Order by" toggle in the UI     |
| Next available slot (stretch) | `Scheduler.find_next_available_slot()`                      | Finds the earliest free block of a given duration within 07:00–21:00 waking hours |

The "Priority view" block in [Sample Output](#%EF%B8%8F-sample-output) above is the captured CLI demonstration of the priority-based enhancement: the 16:00 high-priority vet appointment outranks every earlier medium-priority task.

## 💾 Persistence

The application supports saving and loading the household scheduling state to and from JSON files using Python's standard library.

### Persistence Workflow

1. **Save Data**: The system serializes the `Owner` object (along with its list of `Pet` objects and their corresponding `Task` lists) into a nested JSON structure. Since `datetime.date` objects are not JSON serializable by default, a custom encoder (`_PawPalEncoder`) translates dates into ISO-formatted strings (`YYYY-MM-DD`).
2. **Load Data**: The system reads the JSON file, parses the nesting, parses date strings back to Python `date` objects, and reconstructs the domain model graph (`Owner` -> `Pet` -> `Task`).
3. **UI Integration**: The Streamlit sidebar provides input for the target file path and buttons to trigger saving and loading. On load, the `st.session_state.owner` is updated and `st.rerun()` is triggered to refresh the UI immediately with the restored household data.

### Files Modified

- [pawpal_system.py](pawpal_system.py): Implements `_PawPalEncoder`, `save_to_json()`, and `load_from_json()`.
- [app.py](app.py): Integrates save and load buttons and state management in the sidebar.
- [main.py](main.py): Demonstrates a save and load round-trip in the CLI demo execution.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
