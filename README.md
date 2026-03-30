# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

``A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

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

---

# PawPal+ Manual

## Overview

PawPal+ is a pet care scheduling assistant built with Python and Streamlit. It helps an owner manage pets, define care tasks, and generate a daily schedule that respects fixed appointments and prioritizes flexible work.

This manual describes the system design, installation, usage, and the algorithms implemented in the current version.

## Architecture

The app is composed of three main layers:

- `pawpal_system.py` — core domain model and scheduling engine
- `app.py` — Streamlit interface and session-state management
- `tests/test_pawpal.py` — automated unit tests for core behaviors

### Key objects

- `OwnerInfo` — stores the owner name and a collection of `Pet` objects
- `Pet` — stores the pet profile and a list of assigned `Task` objects
- `Task` — abstract base class for all tasks, with common fields like name, description, duration, priority, and completion state
- `FlexibleTask` — movable tasks that can be scheduled around other items
- `StaticTask` — fixed-time tasks with a locked time slot
- `Scheduler` — produces a daily schedule, detects conflicts, and filters by completion

## Installation

1. Open a terminal in the project folder:
   `C:\Users\Anato\Downloads\PawPEp\ai110-module2-forked`
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
3. Activate the environment:
   ```powershell
   .\.venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Running the application

Start the Streamlit app with:

```powershell
streamlit run app.py
```

Open the browser window that Streamlit launches, then use the UI to:

- enter the owner name
- add one or more pets
- add flexible or static tasks for a selected pet
- generate a schedule
- review the generated task list and completion state

## Using the app

### Add a pet

Use the `Add a Pet` section to register a pet with:

- name
- birthday
- species

Each added pet appears in the owner roster and contributes to the pet count.

### Add a task

In the `Tasks` section, choose a task type and provide:

- title
- description
- duration
- priority (numeric)
- ideal time for flexible tasks
- fixed time for static tasks

The app stores tasks per selected pet. Flexible tasks are movable, while static tasks remain locked to their fixed time.

### Generate a schedule

Press `Generate schedule` to build a plan for all pets.

The schedule generator does the following:

- assigns static tasks to their fixed time slots
- places flexible tasks into available time slots, ordered by priority and ideal time
- resolves conflicts by shifting same-priority flexible tasks to the next available minutes
- warns when a pet has multiple static tasks at the same date, fixed time, and priority

## Design behavior

### Owner / Pet relationship

- `OwnerInfo` owns a collection of `Pet` objects
- each `Pet` owns a list of `Task` objects
- pet and task counts are exposed as properties for quick summary

### Task lifecycle

- every task has `name`, `description`, `duration`, `ideal_time`, `priority`, `date`, and `completed`
- tasks are initialized as incomplete
- `Task.mark_complete()` marks the task completed
- daily tasks can clone themselves into the next day automatically when marked complete

### Scheduling algorithm

The scheduler is responsible for generating a real schedule:

- static tasks are scheduled first at their locked `fixed_time`
- flexible tasks are sorted by descending priority and ideal time
- flexible tasks are assigned the earliest free time slot that does not conflict with already scheduled tasks
- the final schedule is sorted by date, assigned time, and priority

## Testing

Run the unit tests with:

```powershell
pytest
```

The test suite covers:

- marking tasks complete
- pet task count updates
- schedule generation and chronology
- static task conflict detection

## File reference

- `app.py` — Streamlit UI and session state
- `pawpal_system.py` — domain classes and scheduling engine
- `tests/test_pawpal.py` — unit tests
- `main.py` — standalone script with example owner/pet/task setup

## Features

- Owner / Pet management with count tracking
- Per-pet task assignment
- Abstract `Task` base class with completion state
- Numeric priority for task ordering
- `FlexibleTask` scheduling that shifts tasks when conflicts occur
- `StaticTask` locking to fixed times
- Schedule generation by date and assigned time
- Conflict warnings for same-pet static tasks sharing date, fixed time, and priority
- Schedule filtering by completed or pending tasks
- Daily task replication for repeated tasks when marked complete
 