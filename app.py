import datetime
import streamlit as st

from pawpal.pawpal_system import (
    AvailabilityWindow,
    DailySchedule,
    Owner,
    Pet,
    Priority,
    RecurrenceScope,
    Task,
    TaskType,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session State Initialization – keeps data alive across Streamlit reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# 1. Owner Setup
# ---------------------------------------------------------------------------
st.subheader("Owner Setup")

owner_name = st.text_input("Owner name", value="Jordan")

if st.session_state.owner is None or st.session_state.owner.name != owner_name:
    if owner_name:
        st.session_state.owner = Owner(name=owner_name)

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# 2. Availability
# ---------------------------------------------------------------------------
st.subheader("Set Availability")

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

col_day, col_start, col_end = st.columns(3)
with col_day:
    avail_day = st.selectbox("Day", DAYS)
with col_start:
    avail_start = st.time_input("Start time", value=datetime.time(8, 0))
with col_end:
    avail_end = st.time_input("End time", value=datetime.time(12, 0))

if st.button("Set Availability"):
    window = AvailabilityWindow(day=avail_day, start_time=avail_start, end_time=avail_end)
    owner.set_availability(avail_day, [window])
    st.success(f"Availability set for {avail_day}: {avail_start.strftime('%H:%M')} – {avail_end.strftime('%H:%M')}")

if owner.weekly_availability:
    st.write("Current availability:")
    avail_data = [
        {"Day": w.day, "Start": w.start_time.strftime("%H:%M"), "End": w.end_time.strftime("%H:%M")}
        for w in owner.weekly_availability
    ]
    st.table(avail_data)

st.divider()

# ---------------------------------------------------------------------------
# 3. Add a Pet
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

col_pname, col_species, col_age = st.columns(3)
with col_pname:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col_age:
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add Pet"):
    new_pet = Pet(name=pet_name, species=species, age=pet_age)
    owner.add_pet(new_pet)
    st.success(f"Added {pet_name} the {species}!")

if owner._pets:
    st.write("Your pets:")
    pets_data = [{"Name": p.name, "Species": p.species, "Age": p.age} for p in owner._pets]
    st.table(pets_data)
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# 4. Schedule a Task
# ---------------------------------------------------------------------------
st.subheader("Schedule a Task")

if not owner._pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    pet_options = {p.name: p for p in owner._pets}
    selected_pet_name = st.selectbox("Assign to pet", list(pet_options.keys()))
    selected_pet: Pet = pet_options[selected_pet_name]

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        task_type = st.selectbox("Task type", [t.value for t in TaskType])
        priority_choice = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"])
    with col2:
        scope_choice = st.selectbox("Recurrence", [s.value for s in RecurrenceScope])
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        assigned_day = st.selectbox("Assigned day (for weekly/monthly)", ["None"] + DAYS)

    if st.button("Add Task"):
        new_task = Task(
            name=task_title,
            task_type=TaskType(task_type),
            priority=Priority[priority_choice],
            scope=RecurrenceScope(scope_choice),
            duration_minutes=int(duration),
            assigned_day=None if assigned_day == "None" else assigned_day,
        )
        selected_pet.add_task(new_task)
        st.success(f"Task '{task_title}' added to {selected_pet_name}!")

    if selected_pet._tasks:
        st.write(f"Tasks for {selected_pet_name}:")
        task_data = [
            {
                "Name": t.name,
                "Type": t.task_type.value,
                "Priority": t.priority.name,
                "Recurrence": t.scope.value,
                "Duration": f"{t.duration_minutes} min",
                "Done": "✅" if t.completed else "❌",
            }
            for t in selected_pet._tasks
        ]
        st.table(task_data)

st.divider()

# ---------------------------------------------------------------------------
# 5. Generate Daily Schedule
# ---------------------------------------------------------------------------
st.subheader("Generate Daily Schedule")

schedule_date = st.date_input("Date", value=datetime.date.today())

if st.button("Generate Schedule"):
    all_tasks = [t for p in owner._pets for t in p._tasks]
    if not all_tasks:
        st.warning("No tasks to schedule. Add tasks to your pets first.")
    elif not owner.weekly_availability:
        st.warning("Set your availability first so tasks can be scheduled.")
    else:
        schedule = DailySchedule(date=schedule_date)
        schedule.generate(owner, all_tasks)
        st.code(schedule.display())
