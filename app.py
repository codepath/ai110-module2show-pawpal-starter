"""PawPal+ Streamlit UI.

Thin presentation layer over the logic in `pawpal_system.py`. The Owner object is
kept in st.session_state so pets and tasks survive Streamlit's top-to-bottom reruns.
"""

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, VALID_FREQUENCIES

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Persistent "memory": one Owner lives in the session vault -------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner: Owner = st.session_state.owner

st.title("🐾 PawPal+")
st.caption("A smart pet-care scheduler. Add pets, add tasks, and generate a conflict-aware daily plan.")

# --- Owner ------------------------------------------------------------------
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Add a pet --------------------------------------------------------------
st.subheader("➕ Add a pet")
with st.form("add_pet", clear_on_submit=True):
    col1, col2 = st.columns(2)
    pet_name = col1.text_input("Pet name", value="")
    species = col2.selectbox("Species", ["dog", "cat", "bird", "other"])
    if st.form_submit_button("Add pet") and pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species))
        st.success(f"Added {pet_name.strip()} the {species}.")

if not owner.pets:
    st.info("No pets yet. Add one above to get started.")
    st.stop()

# --- Add a task -------------------------------------------------------------
st.subheader("📝 Add a care task")
with st.form("add_task", clear_on_submit=True):
    pet_names = [p.name for p in owner.pets]
    col1, col2 = st.columns(2)
    target_pet = col1.selectbox("For which pet?", pet_names)
    description = col2.text_input("Task", value="Morning walk")
    col3, col4 = st.columns(2)
    task_time = col3.time_input("Time").strftime("%H:%M")
    frequency = col4.selectbox("Frequency", list(VALID_FREQUENCIES))
    if st.form_submit_button("Add task") and description.strip():
        pet = next(p for p in owner.pets if p.name == target_pet)
        pet.add_task(Task(description.strip(), task_time, frequency))
        st.success(f"Added '{description.strip()}' at {task_time} for {target_pet}.")

st.divider()

# --- Today's schedule -------------------------------------------------------
st.subheader("📅 Today's schedule")
scheduler = Scheduler(owner)

pairs = sorted(
    ((pet, task) for pet in owner.pets for task in pet.tasks),
    key=lambda pt: pt[1].time,
)

if not pairs:
    st.info("No tasks scheduled yet. Add a task above.")
else:
    rows = [
        {
            "Time": task.time,
            "Task": task.description,
            "Pet": pet.name,
            "Frequency": task.frequency,
            "Done": "✅" if task.completed else "⬜",
        }
        for pet, task in pairs
    ]
    st.table(rows)

    # Conflict warnings, presented clearly to the owner.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")
    else:
        st.success("No scheduling conflicts. 🎉")

    # Let the owner complete a task (recurring tasks auto-roll to the next day).
    st.markdown("#### Mark a task complete")
    labels = [f"{t.time} · {t.description} ({p.name})" for p, t in pairs]
    choice = st.selectbox("Task", labels)
    if st.button("Mark complete"):
        _, task = pairs[labels.index(choice)]
        follow_up = scheduler.complete_task(task)
        st.success(f"Completed '{task.description}'.")
        if follow_up:
            st.info(f"🔁 Recurring task — next occurrence created for {follow_up.due_date}.")
        st.rerun()
