import streamlit as st

from pawpal_system import (
    Pet,
    Owner,
    Responsibility,
    Constraints,
    Plan,
    Scheduler,
    Explanation,
)

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

# Adding a Pet: create the pet and register it with the owner.
if "pet" not in st.session_state:
    pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(pet)
    st.session_state.pet = pet

owner = st.session_state.owner
pet = st.session_state.pet

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

# Scheduling a Task: create a Responsibility and attach it to the pet.
if st.button("Add task"):
    pet.add_responsibility(
        Responsibility(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
        )
    )

if pet.responsibilities:
    st.write("Current tasks:")
    st.table(
        [
            {
                "Task": task.title,
                "Minutes": task.duration_minutes,
                "Priority": task.priority,
            }
            for task in pet.responsibilities
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    constraints = Constraints(available_minutes=240)
    plan = Plan(owner=owner, pet=pet, constraints=constraints)
    plan.build()

    if plan.scheduled:
        st.write(f"Schedule for {pet.name}:")
        st.table(plan.as_rows())
    st.markdown(plan.explanation.as_text())

