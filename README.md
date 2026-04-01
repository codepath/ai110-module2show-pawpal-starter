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

## 🎯 Features & Algorithms

PawPal+ implements advanced scheduling algorithms to intelligently organize pet care tasks:

### Core Scheduling Algorithms

- **Priority-Based Greedy Scheduling** (`generate_plan()`) - Creates daily schedules by selecting tasks in priority order (1=highest), ensuring high-priority tasks are always scheduled first while respecting time constraints

- **Conflict Detection** (`detect_conflicts()`) - Automatically warns about:
  - Total task duration exceeding available time
  - Morning tasks overflowing morning time slot
  - Afternoon tasks overflowing afternoon time slot
  - Provides specific recommendations for task reallocation

- **Task Sorting & Organization**:
  - `sort_by_priority()` - Orders tasks by priority level (1→3) with morning tasks prioritized
  - `sort_by_duration()` - Sorts tasks shortest-first or longest-first for flexible scheduling
  - `filter_by_constraints()` - Ensures only feasible tasks make it into the plan

### Filtering & Analysis

- **Status-Based Filtering** (`filter_by_status()`) - Analyze tasks by state:
  - `"pending"` - Tasks not yet started
  - `"in-progress"` - Tasks currently being worked on
  - `"completed"` - Finished tasks
  - Helps identify what needs attention and track completion rates

- **Time-Slot Filtering** (`filter_by_time_slot()`) - Organize by preferred time:
  - `"morning"` - Tasks best done in the morning
  - `"afternoon"` - Tasks best done in the afternoon
  - `"flexible"` - Tasks with no time preference
  - Reveals scheduling conflicts and time slot imbalances

### Automation & Recurrence

- **Recurring Task Automation** (`get_next_occurrence()`) - Automatically creates next occurrence when task marked complete:
  - Daily tasks repeat +1 day
  - Weekly tasks repeat +7 days
  - Monthly tasks repeat +30 days
  - Each occurrence gets unique ID but preserves task properties

- **3-State Status System** - Tasks progress through:
  - Pending → In-Progress → Completed (with recurring task auto-generation)

### Data Validation & Safety

- **Comprehensive Input Validation** - Validates all fields in dataclass `__post_init__`:
  - Task: name, duration (1-480 min), priority (1-3), frequency, status, time preferences
  - Pet: name, type, age
  - Owner: name, time availability, time slot consistency
  
- **Duplicate Prevention** - Prevents duplicate pets and tasks with same properties

- **Multi-Pet Support** - Manage multiple pets per owner with independent task tracking

## Testing PawPal+

Run the automated test suite:

```bash
python -m pytest tests/test_pawpal.py -v
```

**What's Tested:**
- Task status system (pending → in-progress → completed transitions)
- Recurring task logic (daily, weekly, monthly task generation)
- Conflict detection (morning/afternoon time slot overflows)
- Priority sorting and scheduling
- Filtering by status and time slot
- Data validation and edge cases
- Pet duplicate prevention

**Test Coverage:** 34 tests across 11 test classes verify core behaviors.
**Confidence Level:** ⭐⭐⭐⭐⭐ (5/5) - All tests passing with comprehensive coverage of requirements.

## 📸 Demo

Below are screenshots showing the key features of PawPal+:

### Owner Settings & Configuration
<a href="DEMO Pics/OwnersInfo.png" target="_blank"><img src='DEMO Pics/OwnersInfo.png' title='Owner Information Settings' width='800' alt='Owner Information Settings' class='center-block' /></a>

*Owner Settings: Configure availability, time slots, and personal preferences*

### Pets & Tasks Management
<a href="DEMO Pics/PetsAndTasks.png" target="_blank"><img src='DEMO Pics/PetsAndTasks.png' title='Pets and Tasks Management' width='800' alt='Pets and Tasks Management' class='center-block' /></a>

*Pets & Tasks: Add multiple pets, create tasks with priority and frequency settings*

### Task Handling & Editing
<a href="DEMO Pics/TaskHandeling.png" target="_blank"><img src='DEMO Pics/TaskHandeling.png' title='Task Editing and Status Updates' width='800' alt='Task Editing and Status Updates' class='center-block' /></a>

*Task Management: Edit tasks, update status (pending → in-progress → completed), and auto-generate recurring tasks*

### Filtering & Schedule Generation
<a href="DEMO Pics/FilterAndScheduler.png" target="_blank"><img src='DEMO Pics/FilterAndScheduler.png' title='Filtering and Schedule Generation' width='800' alt='Filtering and Schedule Generation' class='center-block' /></a>

*Filtering & Scheduling: Filter by status/time slot and generate intelligent daily schedules with conflict detection*

## 📋 UML Diagram

The system architecture is documented in the UML folder with both the initial design (`uml_initial.mmd`) and final implementation (`uml_final.mmd`) showing the actual class structure, relationships, and methods.
