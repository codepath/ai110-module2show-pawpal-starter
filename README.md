# PawPal+

## Overview

PawPal+ is a pet care planner that helps busy pet owners organize daily tasks like walks, feeding, medication, and grooming. The app builds a practical daily plan based on your available time and task importance, then shows what fits and what needs to wait. It is designed for non-technical users who want a clear, simple way to stay consistent with pet care.

## Features

- Smart daily planning with priorities:
  The scheduler creates a daily plan by sorting pending tasks by priority (highest first), then by shorter duration, then by name. It uses a greedy approach to fit as many important tasks as possible into the owner's available minutes.
- Duration sorting:
  Tasks can also be sorted from shortest to longest duration for quick-win planning.
- Time budget conflict warning in the UI:
  If all pending tasks fit within the day's time budget, PawPal+ shows a success message. If they do not fit, it shows how many minutes over budget you are and lists the low-priority tasks that are overflowing the plan.
- Recurring task support:
  When a daily task is completed, the next occurrence is automatically created for the following day. When a weekly task is completed, the next occurrence is created 7 days later.
- Instant completion workflow:
  Marking a task complete updates the plan immediately. If a recurring task creates a new occurrence, the app shows an info message so you know it was scheduled.
- Task status filtering:
  The scheduler can return pending tasks, completed tasks, or all tasks. It can also filter by pet name.
- Completed task organization:
  Completed tasks are tucked into an expandable section so the main view stays clean and focused on what is still pending.
- Input safety checks:
  The app rejects invalid task values such as non-positive duration, negative priority, or unsupported recurrence frequency.
- Due-date aware tasks:
  Each task stores a due date, and due dates are shown in the tables.
- Backend conflict detection utility:
  The scheduler can detect overlapping task time windows and return warnings for missing or invalid time formats.

## 📸 Demo

<a href="/course_images/ai110/demo1.png" target="_blank"><img src='/course_images/ai110/demo1.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo2.png" target="_blank"><img src='/course_images/ai110/demo2.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo3.png" target="_blank"><img src='/course_images/ai110/demo3.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo4.png" target="_blank"><img src='/course_images/ai110/demo4.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo5.png" target="_blank"><img src='/course_images/ai110/demo5.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo6.png" target="_blank"><img src='/course_images/ai110/demo6.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo7.png" target="_blank"><img src='/course_images/ai110/demo7.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## How to Run

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Streamlit app:

```bash
streamlit run app.py
```

4. Optional: run tests:

```bash
python -m pytest
```

## Project Structure

```text
.
├── app.py
├── pawpal_system.py
├── tests/
│   └── test_pawpal.py
├── requirements.txt
├── main.py
├── reflection.md
└── README.md
```

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
