from datetime import date, datetime, time

import streamlit as st
from Pawpal_system import Pet, Task, Owner, Scheduler

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

st.subheader("Owner")

# Streamlit reruns this script on every interaction, so the Owner is kept in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)

col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value="Jordan", key="owner_name")
with col2:
    owner.available_minutes = int(
        st.number_input("Available minutes today", min_value=10, max_value=1440, value=120, key="available_minutes")
    )
preferences = st.text_input("Preferences (comma-separated, e.g. walk, play)", value="walk", key="preferences")
owner.preferences = [pref.strip() for pref in preferences.split(",") if pref.strip()]

st.markdown("### Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=40, value=3)

    if st.form_submit_button("Add pet"):
        pet_name = pet_name.strip()
        if not pet_name:
            st.warning("Please enter a pet name.")
        elif any(pet.name.lower() == pet_name.lower() for pet in owner.pets):
            st.warning(f"{pet_name} is already in your pet list.")
        else:
            owner.add_pet(Pet(pet_name, species, int(age)))
            st.success(f"Added {pet_name}!")

if owner.pets:
    st.table([{"name": pet.name, "species": pet.species, "age": pet.age} for pet in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if not owner.pets:
    st.caption("Add a pet before adding tasks.")
else:
    with st.form("add_task_form"):
        col1, col2 = st.columns(2)
        with col1:
            pet_choice = st.selectbox("Pet", [pet.name for pet in owner.pets])
            task_title = st.text_input("Task title", value="Morning walk")
            task_time = st.time_input("Time", value=time(8, 0))
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["Once", "Daily", "Weekly"])

        if st.form_submit_button("Add task"):
            task = Task(
                description=task_title.strip() or "Untitled task",
                due_time=datetime.combine(date.today(), task_time),
                duration_mins=int(duration),
                priority=priority,
                frequency=frequency,
            )
            if scheduler.check_conflicts(task):
                st.warning(f"'{task.description}' overlaps another task, so the schedule may skip one of them.")
            next(pet for pet in owner.pets if pet.name == pet_choice).add_task(task)
            st.success(f"Added '{task.description}' for {pet_choice}.")

upcoming = scheduler.get_upcoming_tasks()
if upcoming:
    st.write("Upcoming tasks:")
    st.table(
        [
            {
                "pet": pet_name,
                "task": task.description,
                "time": f"{task.due_time:%H:%M}",
                "duration (min)": task.duration_mins,
                "priority": task.priority,
                "frequency": task.frequency,
            }
            for pet_name, task in upcoming
        ]
    )
elif owner.pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Picks tasks by priority that fit your available time without overlapping.")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if plan:
        st.table(
            [
                {
                    "time": f"{item.start_time:%H:%M}",
                    "pet": item.pet_name,
                    "task": item.task.description,
                    "duration (min)": item.task.duration_mins,
                    "priority": item.task.priority,
                }
                for item in plan
            ]
        )
    st.text(scheduler.explain_plan(plan))
