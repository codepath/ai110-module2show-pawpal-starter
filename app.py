import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

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

st.subheader("Owner and Pet")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Time available for pet care today (minutes)", min_value=5, max_value=720, value=120
)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed into the scheduler below.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time = st.selectbox("Preferred time", ["any", "morning", "afternoon", "evening"])
fixed_time = st.text_input("Fixed time (HH:MM)", value="", help="Leave blank for a flexible task.")

if st.button("Add task"):
    st.session_state.tasks.append(
        {
            "title": task_title,
            "duration_minutes": int(duration),
            "priority": priority,
            "preferred_time": preferred_time,
            "fixed_time": fixed_time.strip(),
        }
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
    if st.button("Clear tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Picks the most important tasks that fit your time, then places them across the day.")

if st.button("Generate schedule"):
    owner = Owner(owner_name, available_minutes=int(available_minutes))
    pet = Pet(pet_name, species)
    owner.add_pet(pet)
    try:
        for t in st.session_state.tasks:
            pet.add_task(
                Task(
                    t["title"],
                    t["duration_minutes"],
                    t["priority"],
                    None if t["preferred_time"] == "any" else t["preferred_time"],
                    t.get("fixed_time") or None,
                )
            )
    except ValueError as e:
        st.error(f"Invalid task **{t['title']}**: {e}")
        st.stop()

    plan = Scheduler(owner, pet).build_plan()

    for conflict in plan.conflicts:
        st.error(f"Conflict: {conflict}")

    if plan.items:
        st.success(
            f"Scheduled {len(plan.items)} task(s) for {pet.name}, "
            f"{plan.total_minutes} of {owner.available_minutes} min used."
        )
        st.table(
            [
                {
                    "Time": item.time_range(),
                    "Task": item.task.title,
                    "Minutes": item.task.duration_minutes,
                    "Priority": item.task.priority,
                    "Why": item.reason,
                }
                for item in plan.items
            ]
        )
    else:
        st.info("Nothing to schedule. Add some tasks above.")

    for task, reason in plan.skipped:
        st.warning(f"Skipped **{task.title}**: {reason}")

    with st.expander("Plain-text plan"):
        st.code(plan.explain(), language=None)
