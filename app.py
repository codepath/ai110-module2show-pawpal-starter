import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from persistence import save_pets, load_pets
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+! Plan your pet care tasks with ease.
"""
)

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = None
if "schedule_output" not in st.session_state:
    st.session_state.schedule_output = ""

# Auto-load saved pets on first run
if "pets" not in st.session_state:
    st.session_state.pets = load_pets()

st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan", key="owner_name")
col1, col2 = st.columns(2)
with col1:
    available_hours = st.number_input("Available hours", min_value=0, max_value=24, value=2, step=1, key="available_hours")
with col2:
    available_minutes = st.number_input("Available minutes", min_value=0, max_value=55, value=0, step=5, key="available_minutes")

available_time = available_hours * 60 + available_minutes
if available_time == 0:
    st.warning("Available time is zero; please select at least 5 minutes")

st.subheader("Pet Setup")

pet_name = st.text_input("Pet name", value="Mochi", key="pet_name")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species")
age = st.number_input("Age", min_value=1, max_value=30, value=3, key="age")

if st.button("Add pet", key="add_pet"):
    pet_id = f"pet{len(st.session_state.pets)+1}"
    new_pet = Pet(id=pet_id, name=pet_name, species=species, age=age)
    st.session_state.pets.append(new_pet)

if st.session_state.pets:
    st.write("Current pets:")
    st.table([{"id": p.id, "name": p.name, "species": p.species, "age": p.age} for p in st.session_state.pets])
    selected_pet = st.selectbox("Assign task to pet", [p.id + ": " + p.name for p in st.session_state.pets], key="selected_pet")
    selected_pet_id = selected_pet.split(":")[0]
else:
    st.info("Add at least one pet first.")
    selected_pet_id = None

st.subheader("Tasks")
col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=20, step=5, key="duration")
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="task_priority")
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], index=0, key="task_frequency")

if st.button("Add task", key="add_task"):
    if selected_pet_id:
        target_pet = next((p for p in st.session_state.pets if p.id == selected_pet_id), None)
        if target_pet:
            task_id = f"task{sum(len(p.tasks) for p in st.session_state.pets) + 1}"
            new_task = Task(id=task_id, description=task_title, duration_min=int(duration), priority=priority, frequency=frequency)
            target_pet.add_task(new_task)
    else:
        st.error("Please add and select a pet first before adding tasks.")

all_tasks = [{"pet": p.name, "task": t.description, "duration_min": t.duration_min, "priority": t.priority, "frequency": t.frequency} for p in st.session_state.pets for t in p.tasks]
if all_tasks:
    st.write("Current tasks:")
    st.table(all_tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

if st.button("Save my pets & tasks", key="save_data"):
    save_pets(st.session_state.pets)
    st.success("Saved! Your pets and tasks will be here next time you open the app.")

st.divider()

st.subheader("Build Schedule")
if "scheduler_result" not in st.session_state:
    st.session_state.scheduler_result = None

if st.button("Generate schedule", key="generate_schedule"):
    if not st.session_state.pets:
        st.error("Add at least one pet before generating a schedule.")
    elif available_time == 0:
        st.error("Set your available time before generating a schedule.")
    else:
        owner = Owner(id="owner1", name=owner_name, available_time_min=available_time)
        for pet_obj in st.session_state.pets:
            owner.add_pet(pet_obj)

        scheduler = Scheduler(owner=owner, date=date.today())
        scheduler.build_daily_plan()
        st.session_state.scheduler_result = scheduler
        st.session_state.schedule_owner = owner
        st.success("Schedule generated!")

if st.session_state.scheduler_result:
    scheduler = st.session_state.scheduler_result
    owner = st.session_state.schedule_owner

    # Conflict warnings
    conflicts = scheduler.warn_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(warning)

    # Sorted timeline table
    st.subheader("Today's Timeline")
    sorted_entries = scheduler.sort_by_time()
    if sorted_entries:
        st.table([
            {
                "Start": e.start.strftime("%H:%M"),
                "End": e.end.strftime("%H:%M"),
                "Pet": e.pet.name,
                "Task": e.task.description,
                "Priority": e.task.priority,
                "Frequency": e.task.frequency,
            }
            for e in sorted_entries
        ])
    else:
        st.info("No tasks were scheduled. Check that your tasks fit within your available time.")

    # Per-pet breakdown
    st.subheader("Per-Pet Summary")
    for p in owner.pets:
        pet_entries = [e for e in sorted_entries if e.pet == p]
        if pet_entries:
            st.markdown(f"**{p.name}** ({p.species})")
            for e in pet_entries:
                st.markdown(f"- {e.start.strftime('%H:%M')}–{e.end.strftime('%H:%M')} · {e.task.description} ({e.task.priority})")
        else:
            st.markdown(f"**{p.name}** — no tasks scheduled today")

    # Overflow tasks
    if scheduler.overflow_tasks:
        st.subheader("Could Not Fit")
        st.warning(
            f"{len(scheduler.overflow_tasks)} task(s) could not be scheduled within your available time:"
        )
        st.table([
            {
                "Task": t.description,
                "Duration (min)": t.duration_min,
                "Priority": t.priority,
            }
            for t in scheduler.overflow_tasks
        ])

