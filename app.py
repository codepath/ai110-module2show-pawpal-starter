import streamlit as st
from pawpal_system import PetTask, Constraints, Pet, Owner, DailyPlan

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ app — a pet care planning assistant. Manage multiple owners,
add pets and care tasks, track what's done, and generate an explained daily plan.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** helps pet owners plan care tasks for their pet(s) based on constraints
like time available, priority, and preferences. Each owner keeps their own pets,
tasks, and daily plan.
"""
    )

# Visual badges keep the tables scannable at a glance.
PRIORITY_BADGE = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
STATUS_BADGE = {"pending": "⏳ pending", "completed": "✅ completed"}


# --------------------------------------------------------------------------
# Owners — each owner has its own pets, tasks, and daily plan.
# --------------------------------------------------------------------------
if "owners" not in st.session_state:
    st.session_state.owners = {
        "Jordan": Owner("Jordan", Constraints(available_minutes=240))
    }

st.sidebar.header("👤 Owners")

owner_names = list(st.session_state.owners.keys())
active_name = st.sidebar.selectbox("Active owner", owner_names)
owner = st.session_state.owners[active_name]

with st.sidebar.form("new_owner", clear_on_submit=True):
    st.caption("Add a new owner")
    new_name = st.text_input("Owner name")
    new_minutes = st.number_input(
        "Daily care budget (minutes)", min_value=15, max_value=1440, value=240, step=15
    )
    if st.form_submit_button("Create owner"):
        if not new_name.strip():
            st.sidebar.warning("Enter an owner name.")
        elif new_name in st.session_state.owners:
            st.sidebar.warning(f"{new_name} already exists.")
        else:
            st.session_state.owners[new_name] = Owner(
                new_name, Constraints(available_minutes=int(new_minutes))
            )
            st.sidebar.success(f"Created owner {new_name}.")
            st.rerun()

# Let the user tune the active owner's daily budget (drives the schedule).
owner.constraints.available_minutes = st.sidebar.number_input(
    f"{owner.name}'s daily budget (min)",
    min_value=15,
    max_value=1440,
    value=owner.constraints.available_minutes,
    step=15,
)

st.divider()
st.subheader(f"Owner & Pets — {owner.name}")

# --- Add a pet ------------------------------------------------------------
p1, p2, p3 = st.columns([3, 2, 2])
with p1:
    pet_name = st.text_input("Pet name", value="Mochi")
with p2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with p3:
    st.write("")
    st.write("")
    if st.button("Add pet"):
        before = len(owner.pets)
        owner.add_pet(Pet(pet_name, species))
        if len(owner.pets) > before:
            st.success(f"Added {pet_name} ({species}).")
        else:
            st.warning(f"{pet_name} is already registered.")

if owner.pets:
    st.table([{"Pet": p.name, "Species": p.species, "Tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

# --- Add a task -----------------------------------------------------------
st.markdown("### Tasks")
st.caption("Add tasks to a pet. These feed into the scheduler below.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    time_str = st.text_input("Time (HH:MM, optional)", value="")

fcol, freq_col = st.columns(2)
with fcol:
    pet_names = [p.name for p in owner.pets]
    target_pet = st.selectbox("Assign to pet", pet_names) if pet_names else None
with freq_col:
    freq_choice = st.selectbox("Repeat", ["none", "daily", "weekly"])

if st.button("Add task"):
    if target_pet is None:
        st.warning("Add a pet first.")
    else:
        owner.get_pet(target_pet).add_task(
            PetTask(
                task_title,
                int(duration),
                priority,
                time=time_str.strip() or None,
                frequency=None if freq_choice == "none" else freq_choice,
            )
        )
        st.success(f"Added “{task_title}” for {target_pet}.")


# --------------------------------------------------------------------------
# Task list — sortable, filterable, and interactive (status + remove).
# --------------------------------------------------------------------------
all_tasks = owner.all_tasks()
if all_tasks:
    st.markdown("#### Task list")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total tasks", len(all_tasks))
    m2.metric("Pending", len(owner.tasks_by_status("pending")))
    m3.metric("Completed", len(owner.tasks_by_status("completed")))

    f1, f2 = st.columns(2)
    with f1:
        pet_filter = st.selectbox("Filter by pet", ["All pets"] + pet_names)
    with f2:
        status_filter = st.selectbox("Filter by status", ["All", "pending", "completed"])

    status = None if status_filter == "All" else status_filter

    # Build (pet, task) pairs so each row knows which pet to act on.
    pairs = [(pet, task) for pet in owner.pets for task in pet.tasks]
    if pet_filter != "All pets":
        pairs = [(p, t) for p, t in pairs if p.name == pet_filter]
    if status is not None:
        pairs = [(p, t) for p, t in pairs if t.status == status]

    # Sort by time of day, untimed tasks last (same ordering as sort_by_time).
    pairs.sort(key=lambda pt: (pt[1].time is None, pt[1].time or ""))

    st.caption(f"Showing {len(pairs)} task(s), ordered by time of day.")

    if pairs:
        # Header row.
        h = st.columns([1.3, 3, 1.6, 1.6, 1.6, 1.4, 1.2])
        for col, label in zip(h, ["Time", "Task", "Duration", "Priority", "Status", "", ""]):
            col.markdown(f"**{label}**")

        for i, (pet, task) in enumerate(pairs):
            row = st.columns([1.3, 3, 1.6, 1.6, 1.6, 1.4, 1.2])
            row[0].write(task.time or "--:--")
            row[1].write(f"{task.title}  \n*{pet.name}*")
            row[2].write(f"{task.duration_minutes} min")
            row[3].write(PRIORITY_BADGE.get(task.priority, task.priority))
            row[4].write(STATUS_BADGE.get(task.status, task.status))

            key = f"{pet.name}-{task.title}-{i}"
            if task.status == "pending":
                if row[5].button("Mark done", key=f"done-{key}"):
                    next_task = task.mark_complete()
                    if next_task is not None:
                        pet.add_task(next_task)
                        st.toast(f"Next {task.frequency} occurrence scheduled for {next_task.due_date}.")
                    st.rerun()
            else:
                if row[5].button("Reopen", key=f"open-{key}"):
                    task.status = "pending"
                    st.rerun()

            if row[6].button("🗑 Remove", key=f"rm-{key}"):
                pet.tasks.remove(task)
                st.rerun()
    else:
        st.info("No tasks match the current filters.")

    conflicts = DailyPlan.detect_conflicts(owner.pets)
    if conflicts:
        st.warning(f"⚠️ {len(conflicts)} schedule conflict(s) detected:")
        for warning in conflicts:
            st.markdown(f"- {warning}")
    else:
        st.success("✅ No schedule conflicts — every timed task has a clear slot.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --------------------------------------------------------------------------
# Daily plan — generated per owner.
# --------------------------------------------------------------------------
st.subheader(f"Build Schedule — {owner.name}")
st.caption("Generates today's plan from all of this owner's tasks under their constraints.")

if st.button("Generate schedule"):
    plan = owner.build_plan()
    st.markdown(f"#### Daily plan for {owner.name} — {plan.day}")
    if plan.scheduled:
        st.success(f"Scheduled {len(plan.scheduled)} task(s).")
        st.table(
            [
                {
                    "Start": start,
                    "End": end,
                    "Task": task.title,
                    "Priority": PRIORITY_BADGE.get(task.priority, task.priority),
                }
                for start, end, task in plan.scheduled
            ]
        )
        s1, s2 = st.columns(2)
        s1.metric("Scheduled tasks", len(plan.scheduled))
        s2.metric("Total scheduled time", f"{plan.total_minutes()} min")
    else:
        st.info("Nothing could be scheduled within the available time.")
    if plan.skipped:
        st.warning("Skipped: " + ", ".join(t.title for t in plan.skipped))
    st.caption(plan.explain())
