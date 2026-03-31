import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def parse_csv(value: str) -> list[str]:
    """Convert comma-separated text into a clean list."""
    return [item.strip() for item in value.split(",") if item.strip()]


st.title("🐾 PawPal+")
st.markdown("Use the forms below to add an owner, add a pet, schedule tasks, and generate a daily plan.")

if "owner" not in st.session_state or "pet" not in st.session_state:
    st.session_state.owner = Owner(
        owner_name="Jordan",
        constraints=["Morning availability"],
        priorities=["Health", "Exercise"],
    )
    st.session_state.pet = Pet(
        pet_name="Mochi",
        pet_desc="cat",
        pet_height=25.0,
        pet_weight=4.5,
    )
    st.session_state.owner.add_pet(st.session_state.pet)

current_desc = st.session_state.pet.getPetDesc()
if current_desc not in ["dog", "cat", "other"]:
    current_desc = "other"

st.divider()
st.subheader("Add an Owner + Pet")

with st.form("owner_pet_form"):
    owner_name = st.text_input("Owner name", value=st.session_state.owner.getOwnerName())
    constraints_text = st.text_input(
        "Constraints (comma-separated)",
        value=", ".join(st.session_state.owner.getConstraints()),
    )
    priorities_text = st.text_input(
        "Priorities (comma-separated)",
        value=", ".join(st.session_state.owner.getPriorities()),
    )

    pet_name = st.text_input("Pet name", value=st.session_state.pet.pet_name)
    pet_desc = st.selectbox("Species", ["dog", "cat", "other"], index=["dog", "cat", "other"].index(current_desc))
    pet_height = st.number_input("Pet height", min_value=0.0, value=float(st.session_state.pet.getPetHeight()), step=1.0)
    pet_weight = st.number_input("Pet weight", min_value=0.0, value=float(st.session_state.pet.getPetWeight()), step=0.1)

    save_profile = st.form_submit_button("Save owner and pet")

if save_profile:
    existing_tasks = st.session_state.pet.get_tasks()

    owner = Owner(
        owner_name=owner_name,
        constraints=parse_csv(constraints_text),
        priorities=parse_csv(priorities_text),
    )
    pet = Pet(
        pet_name=pet_name,
        pet_desc=pet_desc,
        pet_height=float(pet_height),
        pet_weight=float(pet_weight),
    )
    for task in existing_tasks:
        pet.add_task(task)
    owner.add_pet(pet)

    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Saved {owner.getOwnerName()}'s pet: {pet.pet_name} ({pet.getPetDesc()})")

st.info(
    f"Owner: {st.session_state.owner.getOwnerName()} | Constraints: {', '.join(st.session_state.owner.getConstraints()) or 'None'} | Priorities: {', '.join(st.session_state.owner.getPriorities()) or 'None'}"
)

st.divider()
st.subheader("Schedule a Task")

with st.form("task_form"):
    task_name = st.text_input("Task name", value="Morning walk")
    task_description = st.text_input("Task description", value="A quick walk around the block")
    due_time = st.text_input("Due time", value="08:00")
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly", "monthly"], index=1)
    duration_minutes = st.number_input("Duration (minutes)", min_value=5, value=30, step=5)
    category = st.selectbox(
        "Category",
        ["feeding", "exercise", "meds", "grooming", "enrichment", "general"],
        index=1,
    )

    schedule_task = st.form_submit_button("Add task")

if schedule_task:
    task = Task(
        title=task_name,
        frequency=frequency,
        duration_minutes=int(duration_minutes),
        category=category,
    )
    task.editTask(
        name=task_name,
        description=task_description,
        due_time=due_time,
        priority=priority,
        duration_minutes=int(duration_minutes),
        category=category,
    )
    st.session_state.pet.add_task(task)
    st.success(f"Scheduled '{task.getTask()}' for {st.session_state.pet.pet_name}.")

current_tasks = st.session_state.pet.get_tasks()
if current_tasks:
    st.write("Current tasks:")
    st.table([task.get_task_info() for task in current_tasks])
else:
    st.info("No tasks yet. Add one above.")

st.divider()
st.subheader("Generate Daily Plan")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    plan = scheduler.generatePlan(
        st.session_state.owner,
        st.session_state.pet,
        st.session_state.pet.get_tasks(),
    )
    daily_tasks = plan.getPlan()

    if daily_tasks:
        st.success(f"Plan for {plan.date}")
        st.caption(f"Constraints used: {', '.join(plan.constraints) or 'None'}")
        st.caption(f"Priorities used: {', '.join(plan.priorities) or 'None'}")
        if plan.conflicts:
            st.warning("Potential conflicts: " + " | ".join(plan.conflicts))
        for task in daily_tasks:
            st.markdown(
                f"- **{task.time or 'Any time'}** — **{task.getTask()}** (`{task.priority}` / {task.frequency} / {task.category} / {task.duration_minutes} min)"
            )
            if task.description:
                st.caption(task.description)
    else:
        st.info("No tasks available to schedule yet.")
