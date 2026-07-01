import streamlit as st
from pawpal_system import PetTask, Constraints, Pet, Owner

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

st.subheader("Owner & Pets")

# Persist the Owner across reruns (created once per session).
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", Constraints(available_minutes=240))
owner = st.session_state.owner

owner.name = st.text_input("Owner name", value=owner.name)

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))

if owner.pets:
    st.write("Pets:", ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks to a pet. These feed into the scheduler below.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

pet_names = [p.name for p in owner.pets]
target_pet = st.selectbox("Assign to pet", pet_names) if pet_names else None

if st.button("Add task"):
    if target_pet is None:
        st.warning("Add a pet first.")
    else:
        owner.get_pet(target_pet).add_task(PetTask(task_title, int(duration), priority))

all_tasks = owner.all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
                "status": t.status,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan from all pets' tasks under the owner's constraints.")

if st.button("Generate schedule"):
    plan = owner.build_plan()
    st.write(f"**Daily plan for {owner.name} — {plan.day}**")
    if plan.scheduled:
        st.table(
            [
                {"start": start, "end": end, "task": task.title, "priority": task.priority}
                for start, end, task in plan.scheduled
            ]
        )
    else:
        st.info("Nothing could be scheduled within the available time.")
    if plan.skipped:
        st.write("Skipped:", ", ".join(t.title for t in plan.skipped))
    st.caption(plan.explain())
