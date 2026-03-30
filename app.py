import streamlit as st
from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_start=time(8, 0),
        available_end=time(20, 0),
    )

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

# --- Page header ---
st.title("🐾 PawPal+")
st.caption(
    f"Owner: {st.session_state.owner.name} | "
    f"Available: {st.session_state.owner.available_start.strftime('%I:%M %p')} – "
    f"{st.session_state.owner.available_end.strftime('%I:%M %p')} "
    f"({st.session_state.owner.get_total_available_time()} min)"
)

st.divider()

# ── Add a Pet ─────────────────────────────────────────────────────────────────
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Luna")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)

if st.button("Add Pet"):
    existing_names = [p.name for p in st.session_state.scheduler.pets]
    if pet_name in existing_names:
        st.warning(f"A pet named '{pet_name}' is already registered.")
    else:
        new_pet = Pet(name=pet_name, species=species, age=age)
        st.session_state.scheduler.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}!")

if st.session_state.scheduler.pets:
    st.markdown("**Registered pets:**")
    for pet in st.session_state.scheduler.pets:
        st.write(f"- {pet.name} ({pet.species}, age {pet.age})")
else:
    st.info("No pets added yet.")

st.divider()

# ── Add a Task ────────────────────────────────────────────────────────────────
st.subheader("Add a Task")

if not st.session_state.scheduler.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    pet_options = [p.name for p in st.session_state.scheduler.pets]

    col1, col2 = st.columns(2)
    with col1:
        selected_pet_name = st.selectbox("Assign to pet", pet_options)
    with col2:
        task_title = st.text_input("Task title", value="Morning Walk")

    col3, col4, col5 = st.columns(3)
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col5:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add Task"):
        target_pet = next(
            (p for p in st.session_state.scheduler.pets if p.name == selected_pet_name), None
        )
        if target_pet is None:
            st.error("Could not find the selected pet. Please try again.")
        else:
            new_task = Task(
                id=st.session_state.next_task_id,
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
            )
            target_pet.add_task(new_task)
            st.session_state.next_task_id += 1
            st.success(f"Added '{task_title}' ({frequency}) to {selected_pet_name}.")

    # ── Task list with filters ─────────────────────────────────────────────────
    all_tasks = st.session_state.scheduler.get_all_tasks()
    if all_tasks:
        st.markdown("**Current tasks:**")

        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            filter_pet = st.selectbox(
                "Filter by pet", ["All"] + pet_options, key="filter_pet"
            )
        with filter_col2:
            filter_status = st.selectbox(
                "Filter by status", ["All", "Pending", "Completed"], key="filter_status"
            )
        with filter_col3:
            sort_mode = st.selectbox(
                "Sort by", ["Priority", "Preferred time"], key="sort_mode"
            )

        # Apply filters via Scheduler.filter_tasks()
        pet_arg = None if filter_pet == "All" else filter_pet
        completed_arg = None
        if filter_status == "Pending":
            completed_arg = False
        elif filter_status == "Completed":
            completed_arg = True

        filtered = st.session_state.scheduler.filter_tasks(
            pet_name=pet_arg, completed=completed_arg
        )

        # Apply sort
        if sort_mode == "Preferred time":
            display_tasks = st.session_state.scheduler.sort_by_time(filtered)
        else:
            display_tasks = st.session_state.scheduler._sort_by_priority(filtered)

        if display_tasks:
            rows = [
                {
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                    "Status": "Done" if t.is_completed else "Pending",
                }
                for t in display_tasks
            ]
            st.table(rows)
        else:
            st.info("No tasks match the selected filters.")

st.divider()

# ── Generate Schedule ─────────────────────────────────────────────────────────
st.subheader("Generate Schedule")

if st.button("Build Schedule"):
    all_tasks = st.session_state.scheduler.get_all_tasks()
    if not all_tasks:
        st.warning("Add at least one task before building a schedule.")
    else:
        schedule = st.session_state.scheduler.build_schedule()
        skipped = st.session_state.scheduler.skipped_tasks

        # ── Conflict warnings — shown first so the owner sees them immediately ──
        conflict_warnings = st.session_state.scheduler.warn_conflicts()
        if conflict_warnings:
            st.error(
                f"**{len(conflict_warnings)} scheduling conflict(s) detected.** "
                "Review the warnings below before following this schedule."
            )
            for msg in conflict_warnings:
                st.warning(msg)
        else:
            st.success(
                f"Scheduled {len(schedule)} of {len(all_tasks)} tasks — no conflicts."
            )

        # ── Skipped tasks ──────────────────────────────────────────────────────
        if skipped:
            st.warning(
                f"{len(skipped)} task(s) could not fit in your available window today:"
            )
            for t in skipped:
                st.caption(f"- {t.pet_name}: {t.title} ({t.duration_minutes} min, {t.priority} priority)")

        # ── Schedule table ─────────────────────────────────────────────────────
        st.markdown("### Today's Schedule")
        for st_task in schedule:
            priority = st_task.task.priority
            if priority == "high":
                indicator = "🔴"
            elif priority == "medium":
                indicator = "🟡"
            else:
                indicator = "🟢"

            freq_badge = (
                f" _{st_task.task.frequency}_" if st_task.task.frequency != "once" else ""
            )
            st.markdown(
                f"{indicator} **{st_task.to_display_string()}**{freq_badge}"
            )
            st.caption(f"↳ {st_task.reason}")
