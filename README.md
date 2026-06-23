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

## 📸 Demo

<a href="/course_images/ai110/pawpal_1.png" target="_blank"><img src='/course_images/ai110/pawpal_1.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/pawpal_feed.png" target="_blank"><img src='/course_images/ai110/pawpal_feed.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## Features

### Core scheduling
- **Priority-based task ordering** — required tasks always schedule before optional ones; within each group tasks are sorted high → medium → low priority so the most critical care is never crowded out by enrichment activities.
- **Time-budget enforcement** — the owner declares available minutes for the day; the scheduler only accepts tasks that fit within the remaining budget and raises an error if the budget is ever exceeded.
- **Greedy allocation** — tasks are assigned in priority order until time runs out, producing a realistic plan rather than an aspirational one.

### Smart algorithms
- **Sorting by time** — `sort_tasks_by_time()` orders any task list chronologically by `earliest_start` using a lambda key that converts `HH:MM` strings to `datetime` objects. Tasks with no time window always sink to the end.
- **Filter by pet or status** — `filter_tasks()` narrows a task list by pet name and/or completion status. Filters can be combined (e.g., "Buddy's pending tasks only"). Pet matching uses object identity to avoid false matches between similarly-named tasks across different pets.
- **Conflict detection** — `detect_conflicts()` scans all tasks that have defined time windows and flags every pair whose windows overlap using the interval condition `a_start < b_end AND b_start < a_end`.
- **Conflict warnings** — `conflict_warnings()` wraps raw conflict pairs into plain-English messages that distinguish same-pet clashes (reschedule one task) from cross-pet clashes (owner must be in two places). Warnings surface in the UI before the schedule is built; the schedule is always produced regardless.

### Recurring tasks
- **Daily recurrence** — completing a daily task automatically creates the next occurrence dated `today + timedelta(days=1)`.
- **Weekly recurrence** — next occurrence is `today + timedelta(weeks=1)`.
- **Weekdays recurrence** — advances one day at a time and skips Saturday and Sunday until a Mon–Fri date is reached.
- **Auto-attach** — `complete_and_reschedule()` marks the original task done, calculates the next date, and attaches the new task to the correct pet in one step.

### UI
- Task list with per-row completion checkboxes, priority emoji badges (🔴/🟡/🟢), and inline time windows.
- Filter controls (by pet, by status) and a sort-by-time toggle wired directly to the Scheduler methods.
- Conflict warnings rendered as `st.error` (cross-pet) or `st.warning` (same-pet) with a plain-English fix suggestion.
- Schedule output as a `st.dataframe` table plus `st.metric` tiles for tasks scheduled, minutes used, and minutes remaining.
- Skipped required tasks flagged explicitly after schedule generation so nothing is silently dropped.

---

## Urgency-Weighted Scoring (Agent Mode Feature)

### What it does

`Task.weighted_score()` computes a composite numeric score for any task by combining four independent signals:

| Component | Value |
|---|---|
| Base priority | low = 10, medium = 20, high = 30 |
| Required bonus | +20 if `required=True` |
| Care type bonus | +12 if `task_type == "medication"` |
| Deadline urgency | +15 if ≤ 60 min remaining (or overdue), +8 if ≤ 120 min, +3 if ≤ 240 min, +0 otherwise |

Maximum achievable score: **77** (high + required + medication + imminent/overdue deadline).

`Scheduler.rank_by_urgency(tasks, current_time)` sorts any task list by this score descending — highest urgency first. The UI exposes it as a third sort option ("Urgency score") alongside "Default" and "Start time", and displays each task's numeric score in a dedicated column when this sort is active.

### Why urgency scoring goes beyond basic priority

The existing `order_tasks()` uses a binary required/priority sort: required tasks always beat optional ones, then high beats medium beats low. That's static — it doesn't change as the day progresses.

Urgency scoring is dynamic. A low-priority feeding task due in 20 minutes scores higher than a high-priority grooming task with no deadline at all (`10 + 15 = 25` vs `30 + 0 = 30` — close, and as time runs out the gap only grows). This reflects real pet-owner decision-making: urgency is a function of both importance *and* time pressure.

### How Agent Mode was used to implement this

This feature was designed and implemented using Agent Mode in Claude Code:

1. **Architecture planning** — Agent Mode was prompted with the existing codebase context and asked to design a composite scoring algorithm that fit the existing `Task`/`Scheduler` separation of concerns. It identified a critical datetime epoch mismatch bug upfront: `datetime.now()` returns a full timestamp (`2026-03-30 14:35:00`) while `Task._parse_time("14:35")` returns a `1900-01-01` epoch datetime — subtracting them would raise a `TypeError`. The fix (`datetime.strptime(datetime.now().strftime(TIME_FORMAT), TIME_FORMAT)`) was part of the design before a single line was written.

2. **Test-first specification** — Agent Mode produced a complete test matrix (9 test cases covering all urgency tiers, the overdue boundary, mutation safety, and the empty-list edge case) before implementation, which locked down the exact expected values for each score component.

3. **UI wiring** — Agent Mode specified replacing the `st.checkbox` sort toggle with `st.radio` (three mutually exclusive options) and conditionally rendering a "Score" column only when urgency sort is active — keeping the default view uncluttered.

The implementation was verified by running all 33 tests (`python -m pytest tests/ -q`) and confirming 0 failures before committing.

---

## Smarter Scheduling

Four algorithmic improvements were added to make the scheduler more useful for real pet-owner workflows:

### Sort by time
`Scheduler.sort_tasks_by_time(tasks)` orders any task list chronologically by `earliest_start`. Tasks without a time window sink to the end of the list. A lambda key function converts each `HH:MM` string into a comparable `datetime` object so the sort is accurate even across midnight boundaries.

### Filter by pet or status
`Scheduler.filter_tasks(tasks, pet_name, completed)` narrows a task list to exactly what the owner needs to see. Filters can be used independently or combined — e.g., "show only Luna's pending tasks." Pet matching uses object identity rather than string comparison, so two pets with similar task names are never confused.

### Recurring tasks
Tasks accept a `recurrence` field (`"daily"`, `"weekly"`, or `"weekdays"`). When a recurring task is completed, `Scheduler.complete_and_reschedule(task)` automatically creates the next occurrence and attaches it to the correct pet. Next dates are calculated with Python's `timedelta`: daily adds 1 day, weekly adds 7, and weekdays advances to the next Mon–Fri, skipping Saturday and Sunday.

### Conflict detection
`Scheduler.detect_conflicts()` scans all tasks with defined time windows and flags any pair whose windows overlap using the condition `a_start < b_end AND b_start < a_end`. `Scheduler.conflict_warnings()` wraps the raw pairs into plain-English strings that identify whether the clash is within the same pet or across different pets. Warnings are printed automatically at the start of `generate_schedule()` — the schedule is still produced, so no task is silently dropped.

---

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
