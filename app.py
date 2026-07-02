"""PawPal+ Streamlit UI — a thin view over the pawpal_system logic layer."""

from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planner: add pets, schedule tasks, and see an organized day.")

# The Owner lives in session_state so data survives Streamlit's rerun-per-click model.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- Save & Load Sidebar ---------------------------------------------------
with st.sidebar:
    st.header("Save & Load Data")
    save_path = st.text_input(
        "Data file path", value="pawpal_data.json", key="save_path"
    )

    col_save, col_load = st.columns(2)
    with col_save:
        if st.button("Save Data", key="save_btn"):
            from pawpal_system import save_to_json

            try:
                save_to_json(owner, save_path)
                st.success("Saved!")
            except Exception as e:
                st.error(f"Error saving: {e}")
    with col_load:
        if st.button("Load Data", key="load_btn"):
            import os

            from pawpal_system import load_from_json

            if os.path.exists(save_path):
                try:
                    loaded_owner = load_from_json(save_path)
                    st.session_state.owner = loaded_owner
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading: {e}")
            else:
                st.error("File not found!")

# --- Household -------------------------------------------------------------
st.header("Household")

owner.name = st.text_input("Owner name", value=owner.name, key="owner_name")

col_name, col_species = st.columns(2)
with col_name:
    new_pet_name = st.text_input("Pet name", key="pet_name")
with col_species:
    new_pet_species = st.selectbox(
        "Species", ["dog", "cat", "other"], key="pet_species"
    )

if st.button("Add pet", key="add_pet") and new_pet_name.strip():
    if owner.get_pet(new_pet_name.strip()) is None:
        owner.add_pet(Pet(name=new_pet_name.strip(), species=new_pet_species))
        st.success(f"Added {new_pet_name.strip()} the {new_pet_species}.")
    else:
        st.warning(f"{new_pet_name.strip()} is already in the household.")

if owner.pets:
    st.write("Pets: " + ", ".join(f"{pet.name} ({pet.species})" for pet in owner.pets))
else:
    st.info("No pets yet — add one above to start scheduling.")

# --- Schedule a task -------------------------------------------------------
st.header("Schedule a task")

if owner.pets:
    task_pet = st.selectbox("Pet", [pet.name for pet in owner.pets], key="task_pet")
    task_description = st.text_input("Task", key="task_description")
    col_time, col_duration, col_frequency, col_priority = st.columns(4)
    with col_time:
        task_time = st.time_input("Time", key="task_time")
    with col_duration:
        task_duration = st.number_input(
            "Duration (min)", min_value=1, max_value=240, value=15, key="task_duration"
        )
    with col_frequency:
        task_frequency = st.selectbox(
            "Repeats", ["once", "daily", "weekly"], key="task_frequency"
        )
    with col_priority:
        task_priority = st.selectbox(
            "Priority", ["low", "medium", "high"], index=1, key="task_priority"
        )

    if st.button("Add task", key="add_task") and task_description.strip():
        owner.get_pet(task_pet).add_task(
            Task(
                description=task_description.strip(),
                time=task_time,
                date=date.today(),
                duration_minutes=int(task_duration),
                frequency=task_frequency,
                priority=task_priority,
            )
        )
        st.success(f"Scheduled '{task_description.strip()}' for {task_pet}.")
else:
    st.caption("Add a pet first, then schedule tasks here.")

# --- Today's schedule ------------------------------------------------------
st.header("Today's schedule")

for conflict in scheduler.detect_conflicts():
    st.warning(f"⚠️ {conflict}")

col_show, col_order = st.columns(2)
with col_show:
    status_filter = st.radio(
        "Show", ["All", "Pending", "Done"], horizontal=True, key="status_filter"
    )
with col_order:
    order_by = st.radio(
        "Order by", ["Time", "Priority"], horizontal=True, key="order_by"
    )

sorted_entries = (
    scheduler.sort_by_time() if order_by == "Time" else scheduler.sort_by_priority()
)
if status_filter == "All":
    entries = sorted_entries
else:
    entries = [
        (pet, task)
        for pet, task in sorted_entries
        if task.completed == (status_filter == "Done")
    ]

if entries:
    st.table(
        [
            {
                "Time": task.time.strftime("%H:%M"),
                "Pet": pet.name,
                "Task": task.description,
                "Duration (min)": task.duration_minutes,
                "Repeats": task.frequency,
                "Priority": task.priority,
                "Status": "✅ done" if task.completed else "⏳ pending",
            }
            for pet, task in entries
        ]
    )
else:
    st.info("Nothing scheduled yet.")

# --- Find a free slot ------------------------------------------------------
st.subheader("Find a free slot")
slot_duration = st.number_input(
    "How long (min)?", min_value=5, max_value=240, value=30, key="slot_duration"
)
if st.button("Find next available slot", key="find_slot"):
    slot = scheduler.find_next_available_slot(int(slot_duration))
    if slot is not None:
        st.info(f"Next free {int(slot_duration)}-minute slot today: **{slot}**")
    else:
        st.info("No free slot that long remains today.")

# --- Complete a task -------------------------------------------------------
pending = scheduler.filter_by_status(completed=False)
if pending:
    st.header("Complete a task")
    labels = {
        f"{task.time.strftime('%H:%M')} — {task.description} ({pet.name})": task
        for pet, task in pending
    }
    picked = st.selectbox("Task to complete", list(labels), key="complete_pick")
    if st.button("Mark complete", key="mark_complete"):
        follow_up = scheduler.complete_task(labels[picked])
        if follow_up is not None:
            st.success(
                f"Done! Recurring task rescheduled for {follow_up.date} at {follow_up.time.strftime('%H:%M')}."
            )
        else:
            st.success("Done!")
        st.rerun()
