from datetime import date, time

import streamlit as st
from typing import cast

from pawpal_system import (
    Owner,
    Pet,
    Scheduler,
    Task,
    TaskStatusFilter,
    detect_plan_conflicts,
    detect_preferred_time_conflicts,
    filter_tasks_with_pets,
    sort_pairs_by_preferred_time,
    sort_pairs_by_urgency,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

The sections below use your **Phase 2** classes: `Owner` in `st.session_state`, `Pet` / `Task`
on the model, and `Scheduler.generateOptimizedSchedule()` for the day plan.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner()

owner = st.session_state.owner


def _clock(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"


st.subheader("Add a pet")
st.caption("Appends a `Pet` to `Owner.pets` (same structure as `main.py`).")

pc1, pc2, pc3 = st.columns(3)
with pc1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pc2:
    species = st.selectbox("Species", ["dog", "cat", "other"], key="add_pet_species")
with pc3:
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=2)

if st.button("Add pet"):
    name = (pet_name or "").strip() or "Unnamed"
    owner.pets.append(Pet(name=name, species=species, age=int(age)))
    st.success(f"Added **{name}**.")

if owner.pets:
    st.markdown("**Your pets**")
    for p in owner.pets:
        st.markdown(f"- **{p.name}** ({p.species}, age {p.age}) — {len(p.tasks)} task(s)")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a task")
st.caption("Appends a `Task` to the chosen pet (`Pet.tasks`), using urgency, buffers, and optional preferred time in the scheduler.")

if not owner.pets:
    st.warning("Add at least one pet before adding tasks.")
else:
    pet_for_task = st.selectbox(
        "Pet for this task",
        owner.pets,
        format_func=lambda p: f"{p.name} ({p.species})",
    )

    tc1, tc2 = st.columns(2)
    with tc1:
        description = st.text_input("Task description", value="Morning walk")
    with tc2:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"])

    weekly_day: int | None = None
    if frequency == "weekly":
        _day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        weekly_day = _day_names.index(
            st.selectbox(
                "Weekly on",
                _day_names,
                index=date.today().weekday(),
                key="task_weekly_day",
            )
        )

    ac1, ac2 = st.columns(2)
    with ac1:
        duration_minutes = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=30
        )
    with ac2:
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        _priority_value = {"low": 1, "medium": 2, "high": 3}[priority_label]

    use_pref = st.checkbox("Preferred start time (minutes from midnight, for scheduling)")
    pref_minutes: int | None = None
    if use_pref:
        pref_time = st.time_input("Preferred start", value=time(8, 0))
        pref_minutes = pref_time.hour * 60 + pref_time.minute

    if st.button("Add task"):
        pet_for_task.tasks.append(
            Task(
                description=description,
                time_minutes=pref_minutes,
                frequency=frequency,
                duration_minutes=int(duration_minutes),
                priority=_priority_value,
                weekly_weekday=weekly_day,
            )
        )
        st.success(f"Task added for **{pet_for_task.name}**.")

    st.markdown("#### Task list (filter & sort)")
    _f1, _f2, _f3 = st.columns(3)
    with _f1:
        filter_pet_opt = st.selectbox(
            "Pet filter",
            ["All pets"] + [p.name for p in owner.pets],
            key="task_filter_pet",
        )
    with _f2:
        filter_status = st.selectbox(
            "Status",
            ["all", "open", "done"],
            format_func=lambda x: {"all": "All", "open": "Open only", "done": "Done only"}[x],
            key="task_filter_status",
        )
    with _f3:
        sort_mode = st.selectbox(
            "Sort by",
            ["preferred_time", "urgency", "description"],
            format_func=lambda x: {
                "preferred_time": "Preferred time",
                "urgency": "Urgency (priority)",
                "description": "Description (A–Z)",
            }[x],
            key="task_sort_mode",
        )

    _pet_filter: Pet | None = None
    if filter_pet_opt != "All pets":
        _pet_filter = next(p for p in owner.pets if p.name == filter_pet_opt)

    _pairs = filter_tasks_with_pets(
        owner, pet=_pet_filter, status=cast(TaskStatusFilter, filter_status)
    )
    if sort_mode == "preferred_time":
        _pairs = sort_pairs_by_preferred_time(_pairs)
    elif sort_mode == "urgency":
        _pairs = sort_pairs_by_urgency(_pairs)
    else:
        _pairs = sorted(_pairs, key=lambda pt: pt[1].description.lower())

    _pref_conflicts = detect_preferred_time_conflicts(owner)
    if _pref_conflicts:
        st.warning(
            f"**Preferred time conflicts** ({len(_pref_conflicts)}): overlapping windows among tasks with a preferred start."
        )
        for c in _pref_conflicts:
            st.markdown(
                f"- **{c.pet_a}** — {c.task_a} ({_clock(c.start_a)}–{_clock(c.end_a)}) "
                f"vs **{c.pet_b}** — {c.task_b} ({_clock(c.start_b)}–{_clock(c.end_b)})"
            )

    if not _pairs:
        st.caption("No tasks match the current filters.")
    else:
        _day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        st.table(
            [
                {
                    "pet": pet.name,
                    "description": task.description,
                    "status": "done" if task.completed else "open",
                    "duration_min": task.duration_minutes,
                    "priority": task.priority,
                    "frequency": task.frequency,
                    "weekly_on": _day_names[task.weekly_weekday]
                    if task.frequency.lower() == "weekly" and task.weekly_weekday is not None
                    else "—",
                    "preferred": _clock(task.time_minutes)
                    if task.time_minutes is not None
                    else "—",
                }
                for pet, task in _pairs
            ]
        )

    with st.expander("Mark a task complete"):
        _mp = st.selectbox("Pet", owner.pets, format_func=lambda p: p.name, key="mark_pet")
        _open_on_pet = [t for t in _mp.tasks if not t.completed]
        if not _open_on_pet:
            st.caption("No open tasks for this pet.")
        else:
            _mt = st.selectbox(
                "Open task",
                _open_on_pet,
                format_func=lambda t: t.description,
                key="mark_task",
            )
            if st.button("Mark complete", key="mark_done_btn"):
                _mt.mark_complete()
                st.success("Marked complete. Use **Status** filter to see done tasks.")
                st.rerun()

st.divider()

st.subheader("Build schedule")
st.caption(
    "Uses `Scheduler.generateOptimizedSchedule(weekday=…)` so **weekly** tasks only appear on their day; "
    "open tasks are ordered by urgency inside the scheduler."
)

_use_today = st.checkbox("Schedule for today’s weekday (recurring filter)", value=True, key="sched_use_today")
_sched_weekday: int | None = date.today().weekday() if _use_today else None
if _use_today:
    st.caption(f"Today is **{date.today().strftime('%A')}** — only daily / as-needed / matching weekly tasks are included.")

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task first.")
    else:
        scheduler = Scheduler(owner=owner)
        plan = scheduler.generateOptimizedSchedule(weekday=_sched_weekday)
        plan.sort(key=lambda row: row[2])
        _plan_conflicts = detect_plan_conflicts(plan)
        if _plan_conflicts:
            st.error(
                "Unexpected **schedule overlaps** (report if you see this after generation): "
                + "; ".join(
                    f"{c.pet_a}/{c.task_a} vs {c.pet_b}/{c.task_b}" for c in _plan_conflicts
                )
            )
        if not plan:
            st.info("No tasks fit in the day window, all tasks are complete, or none apply on this weekday.")
        else:
            rows = []
            for pet, task, slot_start in plan:
                need = task.total_block_minutes()
                slot_end = slot_start + need
                rows.append(
                    {
                        "start": _clock(slot_start),
                        "end": _clock(slot_end),
                        "pet": pet.name,
                        "task": task.description,
                    }
                )
            st.success("Schedule generated.")
            st.table(rows)
