import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

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

st.subheader("Owner & Pet Setup")
owner_name = st.text_input("Owner name", value="Jordan")

# Initialize session state for Owner and pets if they don't already exist
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    new_pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added {pet_name} the {species} to {st.session_state.owner.name}'s profile!")

if st.session_state.owner.pets:
    st.write("**Pets:**", ", ".join(p.name for p in st.session_state.owner.pets))
else:
    st.info("No pets added yet. Add one above.")

st.divider()
st.subheader("Owner Preferences")
st.caption("These constraints limit how the daily schedule is built.")
col1, col2 = st.columns(2)
with col1:
    max_tasks = st.number_input("Max tasks per day", min_value=1, max_value=20, value=5, key="pref_max_tasks")
with col2:
    available_minutes = st.number_input("Available time (minutes)", min_value=10, max_value=480, value=90, key="pref_minutes")
st.session_state.owner.set_preferences({
    'max_tasks_per_day': int(max_tasks),
    'available_minutes': int(available_minutes),
})

st.divider()
st.markdown("### Tasks")
st.caption("Select a pet and add tasks to their schedule.")

if st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Assign task to pet", pet_names)
    selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)

    col1, col2 = st.columns(2)
    with col1:
        task_description = st.text_input("Task description", value="Morning walk")
    with col2:
        task_frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly", "once"])

    col3, col4 = st.columns(2)
    with col3:
        task_duration = st.number_input("Duration (minutes)", min_value=0, max_value=300, value=30, key="task_duration")
    with col4:
        task_priority = st.selectbox("Priority", ["high", "medium", "low"], index=1, key="task_priority")

    col5, col6 = st.columns(2)
    with col5:
        use_time = st.checkbox("Set a start time?", value=False, key="task_use_time")
    with col6:
        task_time_input = st.time_input("Start time", value=None, key="task_time") if use_time else None

    if st.button("Add Task"):
        task_time = None
        if use_time and task_time_input is not None:
            task_time = datetime.combine(datetime.today().date(), task_time_input)
        new_task = Task(description=task_description, frequency=task_frequency, duration=int(task_duration), priority=task_priority, time=task_time)
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_description}' to {selected_pet.name}'s tasks!")

    for pet in st.session_state.owner.pets:
        tasks = pet.get_tasks()
        if tasks:
            st.write(f"**{pet.name}'s tasks:**")
            st.table([
                {
                    "Description": t.description,
                    "Priority": t.priority,
                    "Duration": f"{t.duration} min" if t.duration else "—",
                    "Frequency": t.frequency,
                    "Status": "✅ Done" if t.completed else "⏳ Pending",
                }
                for t in tasks
            ])
else:
    st.info("Add a pet first to start adding tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan ordered by priority, capped by your time and task limits.")

if st.button("Generate Schedule"):
    scheduler = Scheduler(st.session_state.owner)

    # Conflict warnings
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.error(f"⚠️ {len(conflicts)} scheduling conflict{'s' if len(conflicts) > 1 else ''} detected!")
        with st.expander("View conflicts", expanded=True):
            for conflict in conflicts:
                st.warning(conflict)
    else:
        st.success("✅ No scheduling conflicts found.")

    # Generate the prioritized, constraint-aware plan
    schedule = scheduler.generate_schedule()

    if schedule:
        total_duration = sum(task.duration for _, task, _ in schedule)
        prefs = st.session_state.owner.preferences

        st.success("Today's Schedule")
        m1, m2, m3 = st.columns(3)
        m1.metric("Tasks Selected", len(schedule))
        m2.metric("Total Time", f"{total_duration} min")
        m3.metric("Time Budget", f"{prefs.get('available_minutes', 90)} min")

        rows = []
        for pet, task, reason in schedule:
            rows.append({
                "Pet": pet.name,
                "Task": task.description,
                "Priority": task.priority,
                "Duration": f"{task.duration} min" if task.duration else "—",
                "Time": task.time.strftime("%H:%M") if task.time else "—",
                "Frequency": task.frequency,
                "Why": reason,
            })
        st.dataframe(rows, use_container_width=True)

        with st.expander("📋 Plan explanation", expanded=False):
            st.text(scheduler.explain_plan())
    else:
        st.warning("No tasks selected. Add tasks to your pets or adjust preferences.")
