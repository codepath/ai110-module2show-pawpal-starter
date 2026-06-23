import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

def priority_badge(p: str) -> str:
    return PRIORITY_BADGE.get(p, p)

# ---------------------------------------------------------------------------
# Session state — initialise Owner and Pet exactly once per browser session
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        preferences={"morning": True, "evening": False},
        available_minutes=120,
    )

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name="Mochi", species="dog", age=None)
    st.session_state.owner.add_pet(st.session_state.pet)

if "original_minutes" not in st.session_state:
    st.session_state.original_minutes = st.session_state.owner.available_minutes

# Convenience aliases
owner: Owner = st.session_state.owner
pet: Pet = st.session_state.pet

# ---------------------------------------------------------------------------
# Owner & Pet setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
    owner.available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=480, value=owner.available_minutes
    )
with col2:
    pet.name = st.text_input("Pet name", value=pet.name)
    pet.species = st.selectbox(
        "Species",
        ["dog", "cat", "other"],
        index=["dog", "cat", "other"].index(pet.species)
        if pet.species in ["dog", "cat", "other"] else 2,
    )

st.caption(
    f"Caring for: **{pet.name}** the {pet.species}  |  "
    f"Owner: **{owner.name}**  |  Time budget: **{owner.available_minutes} min**"
)

st.divider()

# ---------------------------------------------------------------------------
# Add tasks
# ---------------------------------------------------------------------------

st.subheader("Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    recurrence_choice = st.selectbox("Recurrence", ["none", "daily", "weekly", "weekdays"])
with col5:
    earliest = st.text_input("Earliest start (HH:MM)", value="")
with col6:
    latest = st.text_input("Latest end (HH:MM)", value="")

if st.button("Add task"):
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        task_type="manual",
        required=True,
        earliest_start=earliest.strip() or None,
        latest_end=latest.strip() or None,
        recurrence=None if recurrence_choice == "none" else recurrence_choice,
    )
    pet.add_task(new_task)
    label = f"**{task_title}** — {duration} min, {priority_badge(priority)}"
    if recurrence_choice != "none":
        label += f", recurs {recurrence_choice}"
    st.success(f"Task added: {label}")

st.divider()

# ---------------------------------------------------------------------------
# Scheduler instance — shared for filter, sort, conflict, and schedule
# ---------------------------------------------------------------------------

scheduler = Scheduler(owner=owner)
all_tasks = owner.all_tasks()

# ---------------------------------------------------------------------------
# Conflict warnings — shown prominently before the task list
# ---------------------------------------------------------------------------

warnings = scheduler.conflict_warnings()
if warnings:
    st.subheader("⚠️ Scheduling Conflicts")
    st.caption(
        "The tasks below have overlapping time windows. "
        "Your schedule will still be built, but you may need to be in two places at once. "
        "Consider shortening a window or staggering start times."
    )
    for w in warnings:
        # conflict_warnings() tags each message with [same pet (...)] or [cross-pet: ...]
        if "cross-pet" in w:
            st.error(w)   # cross-pet = harder to resolve; needs coordinating two animals
        else:
            st.warning(w) # same-pet = easier fix; just reschedule one task for that pet
    st.divider()

# ---------------------------------------------------------------------------
# Task list — filter, sort, mark complete
# ---------------------------------------------------------------------------

st.subheader("Tasks")

pet_names = [p.name for p in owner.pets]
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names)
with col_f2:
    filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
with col_f3:
    sort_option = st.radio(
        "Sort by",
        ["Default", "Start time", "Urgency score"],
        index=0,
        horizontal=True,
    )

filtered_tasks = scheduler.filter_tasks(
    all_tasks,
    pet_name=filter_pet if filter_pet != "All" else None,
    completed={"Pending": False, "Completed": True}.get(filter_status),
)

if sort_option == "Start time":
    filtered_tasks = scheduler.sort_tasks_by_time(filtered_tasks)
elif sort_option == "Urgency score":
    filtered_tasks = scheduler.rank_by_urgency(filtered_tasks)

if filtered_tasks:
    st.caption(f"Showing **{len(filtered_tasks)}** task(s)")

    show_score = sort_option == "Urgency score"

    # Column headers
    if show_score:
        h1, h2, h3, h4, h5, h6, h7 = st.columns([3, 2, 2, 2, 2, 1, 1])
        with h7: st.markdown("**Score**")
    else:
        h1, h2, h3, h4, h5, h6 = st.columns([3, 2, 2, 2, 2, 1])
    with h1: st.markdown("**Task**")
    with h2: st.markdown("**Duration**")
    with h3: st.markdown("**Priority**")
    with h4: st.markdown("**Pet**")
    with h5: st.markdown("**Recurs**")
    with h6: st.markdown("**Done**")

    st.markdown("---")

    for i, task in enumerate(filtered_tasks):
        if show_score:
            col_a, col_b, col_c, col_d, col_e, col_f, col_g = st.columns([3, 2, 2, 2, 2, 1, 1])
        else:
            col_a, col_b, col_c, col_d, col_e, col_f = st.columns([3, 2, 2, 2, 2, 1])
        title_display = f"~~{task.title}~~" if task.completed else f"**{task.title}**"
        window = f" `{task.earliest_start}–{task.latest_end}`" if task.earliest_start else ""
        with col_a:
            st.markdown(title_display + window)
        with col_b:
            st.write(f"{task.duration_minutes} min")
        with col_c:
            st.write(priority_badge(task.priority))
        with col_d:
            st.write(task.pet_name or "—")
        with col_e:
            st.write(task.recurrence or "once")
        with col_f:
            done = st.checkbox(
                "Done",
                value=task.completed,
                key=f"done_{task.title}_{i}",
                label_visibility="collapsed",
            )
            if done and not task.completed:
                task.mark_complete()
            elif not done and task.completed:
                task.completed = False
        if show_score:
            with col_g:
                st.write(f"{task.weighted_score():.0f}")
else:
    st.info("No tasks match the current filter — add one above or adjust the filter.")

# ---------------------------------------------------------------------------
# Recurring tasks summary
# ---------------------------------------------------------------------------

recurring = scheduler.recurring_tasks()
if recurring:
    with st.expander(f"🔁 Recurring tasks ({len(recurring)})"):
        st.dataframe(
            [
                {
                    "Task": t.title,
                    "Pet": t.pet_name or "—",
                    "Recurrence": t.recurrence,
                    "Duration (min)": t.duration_minutes,
                    "Priority": priority_badge(t.priority),
                }
                for t in recurring
            ],
            use_container_width=True,
            hide_index=True,
        )

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not owner.all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner.available_minutes = st.session_state.original_minutes
        sched_runner = Scheduler(owner=owner)
        # generate_schedule() prints conflict warnings to stdout; UI already shows them above
        pending = [t for t in owner.all_tasks() if not t.completed]
        selected = sched_runner.select_tasks()
        ordered = sched_runner.order_tasks(selected)
        schedule = sched_runner.allocate_time(ordered)
        sched_runner.validate_schedule(schedule)

        if schedule:
            st.success(f"Schedule ready — {len(schedule)} task(s) planned")

            # Display as a clean table
            st.dataframe(
                [
                    {
                        "Task": entry["title"],
                        "Duration (min)": entry["duration_minutes"],
                        "Priority": priority_badge(entry["priority"]),
                        "Type": entry["task_type"],
                        "Required": "Yes" if entry["required"] else "No",
                    }
                    for entry in schedule
                ],
                use_container_width=True,
                hide_index=True,
            )

            # Remaining time as a metric
            remaining = sched_runner.owner.remaining_availability()
            total = st.session_state.original_minutes
            used = total - remaining
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Tasks scheduled", len(schedule))
            col_m2.metric("Minutes used", used)
            col_m3.metric("Minutes remaining", remaining)

            # Flag any required tasks that didn't make it in
            scheduled_titles = {e["title"] for e in schedule}
            skipped_required = [
                t for t in owner.all_tasks()
                if t.required and not t.completed and t.title not in scheduled_titles
            ]
            if skipped_required:
                st.warning(
                    "**Required tasks that couldn't fit in the time budget:**\n"
                    + "\n".join(f"- {t.title} ({t.duration_minutes} min)" for t in skipped_required)
                )
        else:
            st.warning(
                "No tasks could be scheduled. "
                "Try increasing available minutes or reducing task durations."
            )

# Keep original_minutes in sync when the user changes the time budget
st.session_state.original_minutes = owner.available_minutes
