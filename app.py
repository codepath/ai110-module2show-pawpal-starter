import streamlit as st
from pawpal_system import CareTask, DailySchedule, Owner, Pet

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
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
    st.session_state.owner = Owner(
        name="Jordan",
        available_minutes=60,
    )

owner = st.session_state.owner

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    available = st.number_input(
        "Available minutes today", min_value=0, max_value=1440, value=owner.available_minutes
    )
    owner.set_available_time(int(available))

preferences_text = st.text_input(
    "Preferences (comma-separated keywords, e.g. walk, grooming)",
    value=", ".join(owner.preferences),
)
owner.update_preferences(preferences_text.split(","))

st.divider()

st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Pet name cannot be empty.")
    elif any(p.name == pet_name.strip() for p in owner.pets):
        st.warning(f"{pet_name.strip()} is already added.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species))
        st.success(f"Added {pet_name.strip()} the {species}.")

if not owner.pets:
    st.info("No pets yet. Add one above.")
    st.stop()

pet_names = [p.name for p in owner.pets]
selected_name = st.selectbox("Select a pet to manage", pet_names)
pet = owner.pets[pet_names.index(selected_name)]

st.divider()

st.subheader(f"Tasks for {pet.name}")


def task_status(task):
    """Describe whether a task is due today or when it is next due."""
    if task.is_due():
        return "due" if task.last_completed is None else f"due (last done {task.last_completed})"
    next_due = task.next_due_date()
    if next_due is None:
        return f"done {task.last_completed} (one-time)"
    return f"done {task.last_completed}, next due {next_due}"


col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    recurrence = st.selectbox("Recurrence", ["daily", "weekly", "once"])

if st.button("Add task"):
    try:
        pet.add_task(
            CareTask(
                title=task_title.strip(),
                duration_minutes=int(duration),
                priority=priority,
                recurrence=recurrence,
            )
        )
    except ValueError as e:
        st.error(str(e))

if pet.care_tasks:
    st.table(
        [
            {
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
                "recurrence": t.recurrence,
                "status": task_status(t),
            }
            for t in pet.care_tasks
        ]
    )
    col1, col2 = st.columns(2)
    with col1:
        to_complete = st.selectbox("Mark a task complete", [t.title for t in pet.care_tasks])
        if st.button("Mark complete"):
            task = next(t for t in pet.care_tasks if t.title == to_complete)
            task.mark_complete()
            st.rerun()
    with col2:
        to_remove = st.selectbox("Remove a task", [t.title for t in pet.care_tasks])
        if st.button("Remove task"):
            task = next(t for t in pet.care_tasks if t.title == to_remove)
            pet.remove_task(task)
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(f"Plans {pet.name}'s day within {owner.name}'s {owner.available_minutes} available minutes.")

if st.button("Generate schedule"):
    schedule = DailySchedule(pet=pet)
    scheduled = schedule.generate(owner)

    col1, col2 = st.columns(2)
    col1.metric("Scheduled minutes", owner.available_minutes - schedule.remaining_minutes)
    col2.metric("Remaining minutes", schedule.remaining_minutes)

    if scheduled:
        st.success(f"Scheduled {len(scheduled)} task(s) for {schedule.schedule_date}.")
        st.table(
            [
                {
                    "order": i,
                    "title": t.title,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                    "why": schedule.explain_task(t),
                }
                for i, t in enumerate(scheduled, start=1)
            ]
        )
    else:
        st.warning("No tasks fit in the available time.")

    not_due = [t for t in schedule.skipped_tasks if not t.is_due(schedule.schedule_date)]
    no_time = [t for t in schedule.skipped_tasks if t not in not_due]
    if not_due:
        st.markdown("**Filtered out (not due)**")
        for t in not_due:
            st.write(f"- {t.title}: {schedule.explain_task(t).removeprefix('Skipped: ')}")
    if no_time:
        st.markdown("**Skipped (not enough time)**")
        for t in no_time:
            st.write(f"- {t.title}: {schedule.explain_task(t).removeprefix('Skipped: ')}")

    with st.expander("Text summary"):
        st.code(schedule.get_summary(), language="text")
