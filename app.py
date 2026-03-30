import streamlit as st
from pawpal_system import OwnerInfo, Pet, FlexibleTask, StaticTask, Scheduler

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
    st.session_state.owner = OwnerInfo(name="Jordan")
    st.session_state.schedule = []

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
st.session_state.owner.name = owner_name

st.markdown("### Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name")
with col2:
    birthday = st.text_input("Pet birthday", value="2021-01-01", key="pet_birthday")
with col3:
    species = st.selectbox("Species", ["dog", "cat", "other"], index=0, key="pet_species")

if st.button("Add pet"):
    new_pet = Pet(name=pet_name or "Unnamed", birthday=birthday or "unknown", animal=species)
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added pet {new_pet.name}")

st.markdown(f"Owner has {st.session_state.owner.pet_count} pets.")
if st.session_state.owner.pet_count > 0:
    for pet in st.session_state.owner.list_pets():
        st.write(f"- {pet.name} ({pet.animal})")

st.divider()

st.subheader("Tasks")
st.caption("Add a task and attach it to one of your pets.")

selected_pet = None
if st.session_state.owner.pet_count > 0:
    pet_names = [pet.name for pet in st.session_state.owner.list_pets()]
    selected_name = st.selectbox("Select pet for task", pet_names, key="selected_pet")
    selected_pet = next(p for p in st.session_state.owner.list_pets() if p.name == selected_name)
else:
    st.warning("Add a pet first before scheduling tasks.")

if selected_pet is not None:
    task_type = st.selectbox("Task type", ["Flexible", "Static"], index=0, key="task_type")
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
    task_description = st.text_input("Task description", value="Take a short walk", key="task_description")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration")
    priority = st.number_input("Priority", min_value=1, max_value=10, value=5, key="task_priority")

    if task_type == "Static":
        fixed_time = st.text_input("Fixed time (HH:MM)", value="09:00", key="task_fixed_time")
    else:
        ideal_time = st.text_input("Ideal time (HH:MM)", value="08:00", key="task_ideal_time")

    if st.button("Add task to pet"):
        if task_type == "Static":
            task = StaticTask(
                name=task_title,
                description=task_description,
                duration=int(duration),
                ideal_time=fixed_time,
                fixed_time=fixed_time,
                priority=int(priority),
            )
        else:
            task = FlexibleTask(
                name=task_title,
                description=task_description,
                duration=int(duration),
                ideal_time=ideal_time,
                priority=int(priority),
            )

        selected_pet.add_task(task)
        st.success(f"Added {task_type.lower()} task '{task_title}' to {selected_pet.name}")

    if selected_pet.task_count > 0:
        st.markdown(f"### Tasks for {selected_pet.name}")
        rows = [
            {
                "Task": task.name,
                "Type": type(task).__name__,
                "Time": getattr(task, "scheduled_time", getattr(task, "fixed_time", task.ideal_time)),
                "Priority": getattr(task, "priority", 0),
                "Completed": task.completed,
            }
            for task in selected_pet.list_tasks()
        ]
        st.table(rows)

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a sorted schedule for all pets and their tasks.")

if st.session_state.owner.pet_count == 0:
    st.warning("Add at least one pet before generating a schedule.")
else:
    scheduler = Scheduler(st.session_state.owner)
    all_tasks_exist = any(p.task_count > 0 for p in st.session_state.owner.list_pets())

    if not all_tasks_exist:
        st.warning("Add tasks for your pets before generating a schedule.")
    else:
        if st.button("Generate schedule"):
            st.session_state.schedule = scheduler.schedule_tasks()
            st.success("Schedule generated and sorted chronologically.")
            conflict_warnings = scheduler.detect_static_conflicts()
            if conflict_warnings:
                for warning_message in conflict_warnings:
                    st.warning(warning_message)

        if st.session_state.schedule:
            st.markdown("### Today's schedule")
            schedule_rows = [
                {
                    "Pet": pet.name,
                    "Task": task.name,
                    "Type": type(task).__name__,
                    "Time": getattr(task, "scheduled_time", getattr(task, "fixed_time", task.ideal_time)),
                    "Priority": getattr(task, "priority", 0),
                    "Date": task.date.isoformat(),
                    "Completed": "Yes" if task.completed else "No",
                }
                for pet, task in st.session_state.schedule
            ]
            st.table(schedule_rows)

            filter_choice = st.selectbox(
                "Filter schedule",
                ["All tasks", "Pending tasks", "Completed tasks"],
                key="schedule_filter",
            )

            if filter_choice != "All tasks":
                is_completed = filter_choice == "Completed tasks"
                filtered_items = scheduler.filter_tasks_by_completion(is_completed)
                if filtered_items:
                    filtered_rows = [
                        {
                            "Pet": pet.name,
                            "Task": task.name,
                            "Time": getattr(task, "scheduled_time", getattr(task, "fixed_time", task.ideal_time)),
                            "Date": task.date.isoformat(),
                            "Priority": getattr(task, "priority", 0),
                            "Completed": "Yes" if task.completed else "No",
                        }
                        for pet, task in filtered_items
                    ]
                    st.table(filtered_rows)
                    st.success(f"Showing {len(filtered_rows)} {filter_choice.lower()}.")
                else:
                    st.warning(f"No {filter_choice.lower()} found in the current schedule.")

            if st.button("Clear schedule"):
                st.session_state.schedule = []
                st.success("Schedule cleared.")
