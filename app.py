import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, a pet care planning assistant. Add your pets, give them care
tasks, and build a daily plan based on priority and frequency.
"""
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner({"name": "Jordan"})

owner: Owner = st.session_state.owner

owner_name = st.text_input("Owner name", value=owner.info.get("name", "Jordan"))
owner.info["name"] = owner_name

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (lbs)", min_value=0.0, value=8.5, step=0.5)
        color = st.text_input("Color", value="brown")
    with col2:
        breed = st.text_input("Breed", value="labrador")
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    owner.add_pet(Pet(pet_name, weight, color, breed))
    st.success(f"Added {pet_name} to {owner_name}'s pets.")

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": pet.name, "weight": pet.weight, "color": pet.color, "breed": pet.breed}
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_names = [pet.name for pet in owner.pets]
        selected_pet_name = st.selectbox("Pet", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            time = st.text_input("Time", value="08:00")
        with col2:
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)
        task = Task(
            info={"title": task_title, "time": time, "frequency": frequency},
            duration=int(duration),
            priority=priority,
        )
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet_name}.")
else:
    st.info("Add a pet first to start creating tasks.")

def pet_name_for_task(task: Task) -> str:
    for pet in owner.pets:
        if task in pet.get_tasks():
            return pet.name
    return "Unassigned"


def task_rows(tasks: list[Task]) -> list[dict]:
    return [
        {
            "pet": pet_name_for_task(t),
            "description": t.description,
            "time": t.time,
            "frequency": t.frequency,
            "priority": t.priority,
            "duration_minutes": t.duration,
            "completed": "✅" if t.completed else "⏳",
        }
        for t in tasks
    ]


scheduler = Scheduler(owner)

st.write("Current tasks:")
if scheduler.get_all_tasks():
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_filter = st.selectbox("Filter by pet", ["All"] + [pet.name for pet in owner.pets])
    with col2:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Priority & frequency", "Time"])

    completed_arg = {"Pending": False, "Completed": True}.get(status_filter)
    pet_arg = None if pet_filter == "All" else pet_filter
    filtered_tasks = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_arg)

    if sort_by == "Time":
        display_tasks = scheduler.sort_by_time(filtered_tasks)
    else:
        display_tasks = scheduler.sort_tasks(filtered_tasks)

    if display_tasks:
        st.table(task_rows(display_tasks))
        st.success(f"Showing {len(display_tasks)} task(s) matching your filters.")
    else:
        st.info("No tasks match the selected filters.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
max_tasks = st.number_input("Max tasks in plan (0 = no limit)", min_value=0, value=0)

if st.button("Generate schedule"):
    plan_scheduler = Scheduler(owner, constraints={"max_tasks": max_tasks or None})
    plan = plan_scheduler.daily_plan()
    conflicts = plan_scheduler.check_conflicts()

    if plan:
        st.success(f"Today's plan is ready with {len(plan)} task(s).")
        st.table(task_rows(plan))
    else:
        st.info("No pending tasks to schedule.")

    if conflicts:
        st.warning(
            f"⚠️ {len(conflicts)} scheduling conflict(s) found — some pets need care at the same time. "
            "Review the pairings below and consider adjusting one task's time so you're not needed in two places at once."
        )
        conflict_rows = [
            {
                "time": task_a.time,
                "pet 1": pet_name_for_task(task_a),
                "task 1": task_a.description,
                "pet 2": pet_name_for_task(task_b),
                "task 2": task_b.description,
            }
            for task_a, task_b in conflicts
        ]
        st.table(conflict_rows)
    else:
        st.success("No scheduling conflicts detected — your plan is good to go!")
