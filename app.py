from datetime import time

import streamlit as st
from marshmallow import ValidationError

from pawpal_system import (
    Pet,
    Owner,
    Responsibility,
    Constraints,
    Plan,
    Scheduler,
    to_minutes,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet care planning assistant. Add your pets and their care tasks,
set your daily constraints, and PawPal+ builds an explained, time-ordered schedule —
placing essential tasks first, honoring fixed times and your preferences, and warning
about any conflicts.
"""
)

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
CATEGORIES = ["walk", "feeding", "meds", "enrichment", "grooming", "general"]
# Categories a time-of-day preference makes sense for (flexible, non-pinned work).
PREFERENCE_CATEGORIES = ["walk", "feeding", "enrichment", "grooming"]
TIME_OF_DAY = ["No preference", "morning", "afternoon", "evening"]

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
PawPal+ helps a pet owner plan care tasks for their pet(s) based on constraints like
time budget, priority, fixed appointments, and preferences. Essential tasks (feeding,
meds) are scheduled first and never dropped; the rest are filled in by priority while
the day's budget and window allow.
"""
    )

# --------------------------------------------------------------------------- #
# Session state: a single Owner persists across reruns; pets and their tasks
# live on that owner, so every widget below reads/writes the same object graph.
# On first load we hydrate that owner from data.json (written by save below) so
# pets and tasks survive page refreshes and application restarts; if the file is
# missing/unreadable we start fresh.
# --------------------------------------------------------------------------- #
if "owner" not in st.session_state:
    try:
        st.session_state.owner = Owner.load_from_json()
    except (FileNotFoundError, OSError, ValidationError, ValueError):
        st.session_state.owner = Owner(name="Jordan")
owner = st.session_state.owner

st.divider()

# --------------------------------------------------------------------------- #
# Owner + preferences
# --------------------------------------------------------------------------- #
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

with st.expander("Preferences (preferred time of day per activity)"):
    st.caption(
        "Nudges *flexible* (non-fixed) tasks of a category so they aren't placed "
        "before their preferred part of the day. Fixed-time tasks ignore this."
    )
    for category in PREFERENCE_CATEGORIES:
        key = f"{category}_time"
        current = owner.preferences.get(key, "No preference")
        choice = st.selectbox(
            f"{category.capitalize()} time",
            TIME_OF_DAY,
            index=TIME_OF_DAY.index(current) if current in TIME_OF_DAY else 0,
            key=f"pref_{category}",
        )
        if choice == "No preference":
            owner.preferences.pop(key, None)
        else:
            owner.preferences[key] = choice

st.divider()

# --------------------------------------------------------------------------- #
# Pets — support multiple so filtering by pet is meaningful.
# --------------------------------------------------------------------------- #
st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        new_pet_name = st.text_input("Name", value="Mochi")
    with pc2:
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
    with pc3:
        new_energy = st.selectbox("Energy level", ["low", "medium", "high"], index=1)
    if st.form_submit_button("Add pet"):
        name = new_pet_name.strip()
        if not name:
            st.warning("Please enter a pet name.")
        elif any(pet.name.lower() == name.lower() for pet in owner.pets):
            st.warning(f"A pet named '{name}' already exists — not added.")
        else:
            owner.add_pet(Pet(name=name, species=new_species, energy_level=new_energy))
            st.success(f"Added {name}.")

if not owner.pets:
    owner.save_to_json()  # persist owner name/preferences before the early exit
    st.info("Add a pet above to get started.")
    st.stop()

pet_names = [pet.name for pet in owner.pets]
st.caption("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

st.divider()

# --------------------------------------------------------------------------- #
# Tasks — full Responsibility form (category, recurrence, weekday, fixed time,
# essential), attached to the chosen pet via add_responsibility.
# --------------------------------------------------------------------------- #
st.subheader("Tasks")
active_pet_name = st.selectbox("Add tasks to", pet_names, key="task_pet")
active_pet = next(pet for pet in owner.pets if pet.name == active_pet_name)

with st.form("add_task", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        t_title = st.text_input("Task title", value="Morning walk")
    with c2:
        t_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with c3:
        t_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    c4, c5, c6 = st.columns(3)
    with c4:
        t_category = st.selectbox("Category", CATEGORIES)
    with c5:
        t_recurrence = st.selectbox("Recurrence", ["daily", "weekly", "once"])
    with c6:
        t_weekday = st.selectbox("Weekday (weekly only)", WEEKDAYS)

    c7, c8, c9 = st.columns(3)
    with c7:
        t_essential = st.checkbox("Essential (never dropped)")
    with c8:
        t_pin = st.checkbox("Pin to a fixed time")
    with c9:
        t_fixed = st.time_input("Fixed time", value=time(8, 0))

    if st.form_submit_button("Add task"):
        title = t_title.strip()
        if not title:
            st.warning("Please enter a task title.")
        else:
            new_task = Responsibility(
                title=title,
                duration_minutes=int(t_duration),
                priority=t_priority,
                category=t_category,
                recurrence=t_recurrence,
                weekday=t_weekday if t_recurrence == "weekly" else None,
                fixed_time=t_fixed.strftime("%H:%M") if t_pin else None,
                essential=t_essential,
            )
            # Warn about pinned tasks whose time overlaps another pinned task on
            # the same pet. Flexible (non-fixed) tasks flow around each other, so
            # only fixed-time tasks can truly collide at add time.
            clashes = []
            if new_task.fixed_time:
                new_start = to_minutes(new_task.fixed_time)
                new_end = new_start + new_task.duration_minutes
                for existing in active_pet.responsibilities:
                    if existing.completed or not existing.fixed_time:
                        continue
                    ex_start = to_minutes(existing.fixed_time)
                    ex_end = ex_start + existing.duration_minutes
                    if new_start < ex_end and ex_start < new_end:
                        clashes.append(existing)
            active_pet.add_responsibility(new_task)
            if clashes:
                names = ", ".join(f"'{c.title}' ({c.fixed_time})" for c in clashes)
                st.warning(
                    f"Added '{title}', but its {new_task.fixed_time} slot overlaps {names}. "
                    "Essentials are kept and flagged as a conflict; a non-essential task "
                    "may be dropped when you build the schedule."
                )
            else:
                st.success(f"Added '{title}'.")

# --------------------------------------------------------------------------- #
# Current tasks — filter (Owner.filter_tasks), sort, and mark complete
# (Responsibility.mark_complete auto-enqueues the next occurrence).
# --------------------------------------------------------------------------- #
st.markdown("### Current tasks")
fc1, fc2, fc3 = st.columns(3)
with fc1:
    filter_pet = st.selectbox("Filter by pet", ["All pets"] + pet_names)
with fc2:
    filter_status = st.selectbox("Filter by status", ["All", "Not completed", "Completed"])
with fc3:
    sort_choice = st.selectbox(
        "Sort by",
        ["Added order", "Priority (high → low)", "Duration (short → long)", "Title (A → Z)"],
    )

tasks = owner.filter_tasks(
    pet_name=None if filter_pet == "All pets" else filter_pet,
    completed=None if filter_status == "All" else (filter_status == "Completed"),
)

if sort_choice == "Priority (high → low)":
    tasks = sorted(tasks, key=lambda t: (-t.priority_weight(), t.duration_minutes))
elif sort_choice == "Duration (short → long)":
    tasks = sorted(tasks, key=lambda t: t.duration_minutes)
elif sort_choice == "Title (A → Z)":
    tasks = sorted(tasks, key=lambda t: t.title.lower())

if not tasks:
    st.info("No tasks match the current filter.")
else:
    # Summary banners: a green success line for what's done, an amber warning
    # for what's still outstanding.
    done = [t for t in tasks if t.completed]
    pending = [t for t in tasks if not t.completed]
    if pending:
        essential_left = sum(1 for t in pending if t.essential)
        note = f" ({essential_left} essential)" if essential_left else ""
        st.warning(f"⬜ {len(pending)} task{'s' if len(pending) != 1 else ''} still to do{note}.")
    if done:
        st.success(f"✅ {len(done)} of {len(tasks)} task{'s' if len(tasks) != 1 else ''} complete.")

    def when(task):
        if task.fixed_time:
            return f"📌 {task.fixed_time}"
        if task.recurrence == "weekly":
            return f"weekly · {task.weekday}"
        return task.recurrence

    st.table(
        [
            {
                "Status": "✅ Done" if task.completed else "⬜ To do",
                "Task": f"{task.title}{' ⭐' if task.essential else ''}",
                "Pet": task.pet.name if task.pet else "—",
                "Priority": task.priority,
                "Min": task.duration_minutes,
                "Category": task.category,
                "When": when(task),
            }
            for task in tasks
        ]
    )

    # A table can't carry per-row buttons, so completing a task is a compact
    # picker + button. mark_complete() auto-enqueues recurring tasks' next run.
    if pending:
        lookup: dict[str, Responsibility] = {}
        for index, task in enumerate(pending):
            label = f"{task.title} ({task.pet.name})" if task.pet else task.title
            if label in lookup:  # disambiguate identical titles on the same pet
                label = f"{label} #{index + 1}"
            lookup[label] = task
        mc1, mc2 = st.columns([3, 1])
        with mc1:
            choice = st.selectbox("Mark a task complete", list(lookup), key="mark_choice")
        with mc2:
            st.write("")  # nudge the button down to align with the selectbox
            if st.button("Mark done"):
                lookup[choice].mark_complete()
                st.rerun()

st.divider()

# --------------------------------------------------------------------------- #
# Build schedule — Constraints (budget + window + weekday), Plan.build,
# detect_conflicts, total_minutes, as_rows, and the explanation.
# --------------------------------------------------------------------------- #
st.subheader("Build schedule")

sc1, sc2, sc3 = st.columns(3)
with sc1:
    sched_pet_name = st.selectbox("Pet to schedule", pet_names, key="sched_pet")
with sc2:
    budget = st.number_input("Time budget (minutes)", min_value=0, max_value=1440, value=240)
with sc3:
    day_of_week = st.selectbox("Day of week", WEEKDAYS)

wc1, wc2 = st.columns(2)
with wc1:
    day_start = st.time_input("Day start", value=time(7, 0))
with wc2:
    day_end = st.time_input("Day end", value=time(21, 0))

schedule_order = st.radio(
    "Schedule order",
    ["Clock time", "Priority (high → low)"],
    horizontal=True,
    help=(
        "Clock time lists tasks as they occur through the day; "
        "Priority lists the highest-priority tasks first (time breaks ties)."
    ),
)

sched_pet = next(pet for pet in owner.pets if pet.name == sched_pet_name)

if st.button("Generate schedule"):
    constraints = Constraints(
        available_minutes=int(budget),
        day_start=day_start.strftime("%H:%M"),
        day_end=day_end.strftime("%H:%M"),
        day_of_week=day_of_week,
    )
    plan = Plan(owner=owner, pet=sched_pet, constraints=constraints)
    plan.build()

    conflict = plan.detect_conflicts()
    if conflict:
        st.warning(conflict)

    if plan.scheduled:
        order = "priority" if schedule_order.startswith("Priority") else "time"
        st.write(f"Schedule for {sched_pet.name} — {plan.total_minutes()} min of care:")
        st.table(plan.as_rows(order=order))
    else:
        st.info("Nothing scheduled for these constraints.")

    st.markdown(plan.explanation.as_text())

# --------------------------------------------------------------------------- #
# Persist the current owner/pet/task graph on every rerun so all edits made
# this session (added pets and tasks, completed tasks, preference changes)
# survive a page refresh or restart. The derived plan/schedule is not saved.
# --------------------------------------------------------------------------- #
owner.save_to_json()
