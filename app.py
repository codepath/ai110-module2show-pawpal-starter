"""PawPal+ Streamlit app — connects the UI to pawpal_system.py logic."""

import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling for busy owners.")

# ---------------------------------------------------------------------------
# Session state — initialize once, persist across reruns
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ---------------------------------------------------------------------------
# Sidebar — Owner + Pet setup
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Setup")

    owner_name = st.text_input("Your name", value="Jordan")
    if st.button("Set owner"):
        st.session_state.owner = Owner(owner_name)
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.success(f"Owner set: {owner_name}")

    st.divider()
    st.subheader("Add a pet")

    pet_name    = st.text_input("Pet name",  value="Mochi")
    pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])

    if st.button("Add pet"):
        if st.session_state.owner is None:
            st.error("Set an owner first.")
        else:
            existing = [p.name.lower() for p in st.session_state.owner.pets]
            if pet_name.lower() in existing:
                st.warning(f"{pet_name} is already in the system.")
            else:
                st.session_state.owner.add_pet(Pet(pet_name, pet_species))
                st.success(f"Added {pet_name} ({pet_species})")

    if st.session_state.owner and st.session_state.owner.pets:
        st.divider()
        st.subheader("Your pets")
        for p in st.session_state.owner.pets:
            st.write(f"- **{p.name}** ({p.species})")

# ---------------------------------------------------------------------------
# Guard — require owner
# ---------------------------------------------------------------------------

if st.session_state.owner is None:
    st.info("Enter your name in the sidebar and click **Set owner** to get started.")
    st.stop()

owner     = st.session_state.owner
scheduler = st.session_state.scheduler

# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------

tab_add, tab_schedule, tab_conflicts = st.tabs(["Add Task", "Today's Schedule", "Conflicts"])

# ---- Add Task ---------------------------------------------------------------

with tab_add:
    st.subheader("Schedule a new task")

    if not owner.pets:
        st.warning("Add at least one pet from the sidebar first.")
    else:
        pet_options = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Choose pet", pet_options)
        task_desc     = st.text_input("Task description", value="Morning walk")
        task_time     = st.time_input("Time", value=None)
        task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=30)
        task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        task_freq     = st.selectbox("Frequency", ["once", "daily", "weekly"])
        task_date     = st.date_input("Due date", value=date.today())

        if st.button("Add task"):
            time_str = task_time.strftime("%H:%M") if task_time else "08:00"
            new_task = Task(
                description=task_desc,
                time=time_str,
                duration_minutes=int(task_duration),
                priority=task_priority,
                frequency=task_freq,
                due_date=task_date,
            )
            pet_obj = next(p for p in owner.pets if p.name == selected_pet_name)
            pet_obj.add_task(new_task)
            st.success(f"Added '{task_desc}' for {selected_pet_name} at {time_str}.")

# ---- Today's Schedule -------------------------------------------------------

with tab_schedule:
    st.subheader(f"Schedule for {date.today().strftime('%A, %B %d %Y')}")

    sort_mode = st.radio("Sort by", ["Time", "Priority"], horizontal=True)

    if sort_mode == "Time":
        tasks = scheduler.sort_by_time()
    else:
        tasks = scheduler.sort_by_priority()

    if not tasks:
        st.info("No tasks scheduled for today. Add some from the 'Add Task' tab.")
    else:
        for pet, task in tasks:
            col1, col2 = st.columns([3, 1])
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            status_icon   = "✅" if task.completed else "⬜"
            with col1:
                st.markdown(
                    f"{status_icon} **{task.time}** &nbsp; {priority_icon} &nbsp; "
                    f"`{pet.name}` — {task.description} "
                    f"({task.duration_minutes} min, {task.frequency})"
                )
            with col2:
                btn_key = f"complete_{pet.name}_{task.description}_{task.time}"
                if not task.completed and st.button("Done", key=btn_key):
                    next_task = scheduler.mark_task_complete(pet, task)
                    msg = f"'{task.description}' marked complete."
                    if next_task:
                        msg += f" Next on {next_task.due_date}."
                    st.success(msg)
                    st.rerun()

# ---- Conflicts --------------------------------------------------------------

with tab_conflicts:
    st.subheader("Conflict Detection")
    warnings = scheduler.detect_conflicts()
    if not warnings:
        st.success("No scheduling conflicts detected!")
    else:
        for w in warnings:
            st.warning(w)

    st.divider()
    st.subheader("Next available slot")
    if owner.pets:
        slot_pet  = st.selectbox("Pet", [p.name for p in owner.pets], key="slot_pet")
        slot_date = st.date_input("Date", value=date.today(), key="slot_date")
        if st.button("Find slot"):
            slot = scheduler.get_next_available_slot(slot_pet, slot_date)
            st.info(f"Next free 30-min slot for {slot_pet} on {slot_date}: **{slot}**")
