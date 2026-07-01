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


### Sample test output:

```bash

$ python -m pytest
=============================== test session starts ===============================
platform win32 -- Python 3.13.14, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\varve\python\codepath\ai110\module-2\week-2\pawpal
plugins: anyio-4.13.0
collected 50 items                                                                 

tests\test_pawpal.py ..................................................      [100%]

=============================== 50 passed in 0.08s ================================

```



## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | sort_by_time() | sorts item by time  |
| Filtering | filter_tasks() | filter tasks by completion status or by pet |
| Conflict handling | detect_conflicts() | checks the schedule and detects overlapping time conflcits |
| Recurring tasks | next_occurrence | it spawns a new task after the one is completed |



## ✨ Features

- **Multi-pet management** — add multiple pets (species, energy level) under one owner, with graceful notices when a duplicate pet name is entered.
- **Rich task modeling** — each task carries a duration, priority, category, recurrence (daily/weekly/once), optional weekday, optional fixed time, and an "essential" flag.
- **Owner preferences** — set a preferred time of day per activity (e.g. walks in the afternoon) that nudges flexible tasks in the schedule.
- **Constraint-aware scheduling** — `build()` plans a day within a time budget and a start/end window: essentials are placed first and never dropped, then remaining tasks fill in by priority (shorter first) while time allows.
- **Fixed-time pinning** — appointments pinned to a clock time are placed exactly, and flexible tasks flow around them.
- **Sorting & filtering** — sort tasks by priority, duration, or title, and filter by pet and completion status (`filter_tasks()`).
- **Recurring tasks** — completing a daily/weekly task auto-enqueues its next occurrence (`mark_complete()` / `next_occurrence()`), and completion is idempotent.
- **Conflict detection** — overlapping time slots are surfaced as a warning both when adding a fixed-time task and after building the schedule (`detect_conflicts()`).
- **Explained plans** — every schedule includes a summary, strategy, per-task reasons, and reasons for anything skipped.
- **Polished Streamlit UI** — filtered/sorted tasks render in a clean table with success/warning status banners.
- **Tested** — a 50-case suite covers scheduling, sorting, filtering, recurrence, and conflict edge cases.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Under the owner section, you list preferences for walk time, feeding time, enrichment time, and grooming time. You can list your preferring time to start each activity.
2. You can then input pet's information. You can put their name, species and energy level. If you enter a duplicate pet, then you will be notified that you have entered a duplicate pet.
3. You can then add tasks to your chosen pet. You can select the task title, the duration of the workout, the priority level of the workout, the category of the workout (walk, grooming, feeding etc), the recurrence of the task (how often that particular tasks take place), if weekly was selected as the recurrence (you can then select which particular day you want), then you can select whether the task is essential and whether it is set to a fixed time. If you pin multiple items to the same fixed time, then you will be notified that an item already has that fixed time.
4. You can then view the current tasks where you can filter by pet, status (completed or not completed). You can also sort by added order, priority level, duration, and title. Finally, you can then mark a task as completed when you are finished. 
5. You can build the schedule for your chosen pet. You can give the time budget, the day of the week you want to generate the tasks, and the start and end time for your pet. Then you can click generate schedule to generate a schedule for the day.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->


## Data persistence
- We added marshmellow schemas:  ResponsibilitySchema, PetSchema, OwnwerSchema. 
- In data.jaon, Owner.save_to_json() and Owner.load_from_json() was added.
- In app.py, on the first load, the data is hydrates from data.json. Also, owner.save_to_json() is called at the end of every rerun, so it is written to disk before the application restarts.