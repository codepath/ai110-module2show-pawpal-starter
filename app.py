import streamlit as st
from collections import defaultdict
from datetime import date, time as dt_time
from pawpal_system import Owner, Pet, Task, Scheduler, OwnerRepository


def time_to_minutes(t) -> int:
    """Convert a datetime.time object to minutes from midnight."""
    return t.hour * 60 + t.minute


def minutes_to_time(minutes: int) -> dt_time:
    """Convert minutes from midnight to a datetime.time object."""
    return dt_time(minutes // 60, minutes % 60)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

_repo = OwnerRepository("owner.json")

# ── Owner / Pet setup ────────────────────────────────────────────────────────
st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name_input = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

def find_pet(owner, pet_name):
    """Look up a pet by name within an owner's pet list.

    Centralizes the repeated pattern of searching owner.get_pets() by name
    so callers (edit, delete, mark-complete) don't duplicate the logic.

    Args:
        owner: The Owner instance whose pets will be searched.
        pet_name: The exact name string to match against Pet.name.

    Returns:
        The matching Pet instance, or None if no pet with that name exists.
    """
    return next((p for p in owner.get_pets() if p.name == pet_name), None)

if "owner" not in st.session_state:
    st.session_state.owner = _repo.load() or Owner(owner_name)

# ── Task creation form ────────────────────────────────────────────────────────
st.markdown("### Add a Task")

priority_map = {"low": 1, "medium": 2, "high": 3}
priority_label = {1: "low", 2: "medium", 3: "high"}
priority_badge = {1: "🟢 low", 2: "🟡 medium", 3: "🔴 high"}

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    due_date = st.date_input("Due date", value=date.today())

col5, col6, col7, col8 = st.columns(4)
with col5:
    is_recurring = st.checkbox("Recurring task")
with col6:
    recurrence_interval = st.selectbox(
        "Repeat every",
        ["daily", "weekly"],
        disabled=not is_recurring,
    )
with col7:
    set_preferred = st.checkbox("Set preferred time")
with col8:
    preferred_time_input = st.time_input(
        "Preferred time",
        value=dt_time(8, 0),
        disabled=not set_preferred,
    )

if st.button("Add task"):
    owner = st.session_state.owner
    existing_pet = next((p for p in owner.get_pets() if p.name == pet_name_input), None)
    if existing_pet is None:
        existing_pet = Pet(pet_name_input, species)
        owner.add_pet(existing_pet)
    task = Task(
        name=task_title,
        duration=int(duration),
        priority=priority_map[priority],
        due_time=due_date,
        recurring=is_recurring,
        recurrence_interval=recurrence_interval if is_recurring else None,
        preferred_time=time_to_minutes(preferred_time_input) if set_preferred else None,
    )
    existing_pet.add_task(task)
    _repo.save(owner)

# ── All tasks — with filter + sort ───────────────────────────────────────────
st.markdown("### All Tasks")

owner = st.session_state.owner
pet_names = [p.name for p in owner.get_pets()]

fcol1, fcol2, fcol3 = st.columns(3)
with fcol1:
    filter_pet = st.selectbox("Filter by pet", ["All pets"] + pet_names)
with fcol2:
    filter_status = st.radio("Status", ["all", "incomplete", "completed"], horizontal=True)
with fcol3:
    sort_by = st.selectbox("Sort by", ["priority", "due date", "duration"])

pet_filter = filter_pet if filter_pet != "All pets" else None
status_filter = filter_status if filter_status != "all" else None
filtered_tasks = owner.get_tasks_filtered(pet_name=pet_filter, status=status_filter)

# Apply sort
_sched_helper = Scheduler(available_times=[8 * 60, 20 * 60])
if sort_by == "due date":
    display_tasks = _sched_helper.sort_tasks_by_time(filtered_tasks)
elif sort_by == "duration":
    display_tasks = sorted(filtered_tasks, key=lambda t: t.duration)
else:  # priority (default)
    display_tasks = _sched_helper.sort_tasks_by_priority(filtered_tasks)

if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = None

if display_tasks:
    hcol1, hcol2, hcol3, hcol4, hcol5, hcol6, hcol7, hcol8 = st.columns([3, 2, 2, 1, 1, 2, 1, 1])
    with hcol1:
        st.caption("Task")
    with hcol2:
        st.caption("Pet")
    with hcol3:
        st.caption("Due date")
    with hcol4:
        st.caption("Dur.")
    with hcol5:
        st.caption("Priority")
    with hcol6:
        st.caption("Pref. time")
    st.divider()
    for task in display_tasks:
        is_editing = st.session_state.editing_task_id == task.task_id

        if is_editing:
            with st.form(key=f"edit_form_{task.task_id}"):
                st.markdown(f"**Editing: {task.name}**")
                ecol1, ecol2, ecol3, ecol4 = st.columns(4)
                with ecol1:
                    new_title = st.text_input("Task title", value=task.name)
                with ecol2:
                    new_duration = st.number_input("Duration (min)", min_value=1, max_value=240,
                                                   value=task.duration)
                with ecol3:
                    cur_pri = priority_label[task.priority]
                    new_priority_str = st.selectbox("Priority", ["low", "medium", "high"],
                                                    index=["low", "medium", "high"].index(cur_pri))
                with ecol4:
                    new_due = st.date_input("Due date", value=task.due_time or date.today())
                pcol1, pcol2 = st.columns(2)
                with pcol1:
                    edit_set_pref = st.checkbox(
                        "Set preferred time",
                        value=task.preferred_time is not None,
                    )
                with pcol2:
                    pref_default = minutes_to_time(task.preferred_time) if task.preferred_time else dt_time(8, 0)
                    edit_pref_input = st.time_input(
                        "Preferred time",
                        value=pref_default,
                        disabled=not edit_set_pref,
                    )
                save_clicked = st.form_submit_button("Save")
                cancel_clicked = st.form_submit_button("Cancel")

            if save_clicked:
                updated = Task(
                    name=new_title,
                    duration=int(new_duration),
                    priority=priority_map[new_priority_str],
                    due_time=new_due,
                    recurring=task.recurring,
                    recurrence_interval=task.recurrence_interval,
                    preferred_time=time_to_minutes(edit_pref_input) if edit_set_pref else None,
                    pet_name=task.pet_name,
                    notes=task.notes,
                    task_id=task.task_id,
                    completed=task.completed,
                )
                pet = find_pet(owner, task.pet_name)
                if pet:
                    pet.update_task(task.task_id, updated)
                    _repo.save(owner)
                st.session_state.editing_task_id = None
                st.rerun()
            if cancel_clicked:
                st.session_state.editing_task_id = None
                st.rerun()
        else:
            tcol1, tcol2, tcol3, tcol4, tcol5, tcol6, tcol7, tcol8 = st.columns([3, 2, 2, 1, 1, 2, 1, 1])
            with tcol1:
                label = f"**{task.name}**"
                if task.recurring:
                    label += f" ↻ {task.recurrence_interval}"
                if task.completed:
                    st.markdown(f"~~{label}~~  ✓")
                else:
                    st.markdown(label)
            with tcol2:
                st.write(task.pet_name or "—")
            with tcol3:
                st.write(task.due_time.isoformat() if task.due_time else "—")
            with tcol4:
                st.write(f"{task.duration}m")
            with tcol5:
                st.write(priority_badge[task.priority])
            with tcol6:
                if task.preferred_time is not None:
                    st.write(f"pref: {minutes_to_time(task.preferred_time).strftime('%I:%M %p').lstrip('0')}")
                else:
                    st.write("—")
            with tcol7:
                if st.button("Edit", key=f"edit_{task.task_id}"):
                    st.session_state.editing_task_id = task.task_id
                    st.rerun()
            with tcol8:
                if st.button("Delete", key=f"del_{task.task_id}"):
                    pet = find_pet(owner, task.pet_name)
                    if pet:
                        pet.remove_task(task.task_id)
                        _repo.save(owner)
                    st.rerun()
else:
    st.info("No tasks match the current filter.")

st.divider()

# ── Today's tasks — with Mark Complete + conflict detection ──────────────────
st.subheader("Tasks for Today")
st.caption(f"Incomplete tasks due {date.today().isoformat()}, sorted by priority.")

today_tasks = sorted(
    owner.get_today_tasks(),
    key=lambda t: t.priority,
    reverse=True,
)

if today_tasks:
    # Proactive conflict check: warn when multiple tasks share the same due date
    # for the same pet — the scheduler will pack them sequentially, but the owner
    # should know they have back-to-back tasks for one pet.
    _pet_due_counts: dict = defaultdict(list)
    for _t in today_tasks:
        _pet_due_counts[(_t.pet_name, str(_t.due_time))].append(_t.name)
    _conflict_msgs = [
        f"⚠️ {pet} has {len(names)} tasks due on {due}: {', '.join(names)}"
        for (pet, due), names in _pet_due_counts.items()
        if len(names) > 1
    ]
    if _conflict_msgs:
        for _msg in _conflict_msgs:
            st.warning(_msg)

    # Render each task as a row with a Mark Complete button
    st.markdown("---")
    rh1, rh2, rh3, rh4, rh5 = st.columns([4, 2, 1, 1, 2])
    with rh1:
        st.caption("Task")
    with rh2:
        st.caption("Pet")
    with rh3:
        st.caption("Dur.")
    with rh4:
        st.caption("Priority")
    for task in today_tasks:
        rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns([4, 2, 1, 1, 2])
        with rcol1:
            label = f"**{task.name}**"
            if task.recurring:
                label += f" ↻ {task.recurrence_interval}"
            st.markdown(label)
        with rcol2:
            st.write(task.pet_name or "—")
        with rcol3:
            st.write(f"{task.duration}m")
        with rcol4:
            st.write(priority_badge[task.priority])
        with rcol5:
            btn_key = f"done_{task.task_id}"
            if st.button("✓ Done", key=btn_key):
                next_occurrence = task.mark_complete()
                if next_occurrence is not None:
                    pet = find_pet(owner, next_occurrence.pet_name)
                    if pet:
                        pet.add_task(next_occurrence)
                _repo.save(owner)
                st.rerun()
    st.markdown("---")
else:
    st.info("No incomplete tasks due today.")

# ── Schedule generation ────────────────────────────────────────────────────
if st.button("Generate schedule"):
    if not today_tasks:
        st.warning("No tasks due today to schedule.")
    else:
        window_start = 8 * 60
        window_end = 20 * 60

        total_task_min = sum(t.duration for t in today_tasks)
        total_with_buffers = total_task_min + 10 * max(0, len(today_tasks) - 1)
        available_min = window_end - window_start
        if total_with_buffers > available_min:
            st.warning(
                f"Total task time ({total_with_buffers} min including buffers) exceeds the "
                f"{available_min}-min window. Some tasks will be dropped."
            )

        # Use copies so generate_schedule doesn't mutate live task objects
        schedule_copies = [Task.from_dict(t.to_dict()) for t in today_tasks]
        scheduler = Scheduler(available_times=[window_start, window_end], buffer_minutes=10)
        result = scheduler.generate_schedule(schedule_copies)

        if result["scheduled"]:
            st.success(f"Scheduled {len(result['scheduled'])} task(s):")
            rows = []
            for t in result["scheduled"]:
                start_h, start_m = divmod(t["start_time"], 60)
                end_h, end_m = divmod(t["start_time"] + t["duration"], 60)
                pref = t.get("preferred_time")
                pref_str = minutes_to_time(pref).strftime("%I:%M %p").lstrip("0") if pref else "—"
                honored = (
                    "yes" if pref is not None and t["start_time"] == pref else
                    "no (unavailable)" if pref is not None else "—"
                )
                rows.append({
                    "pet": t.get("pet_name", ""),
                    "task": t["name"],
                    "start": f"{start_h:02d}:{start_m:02d}",
                    "end": f"{end_h:02d}:{end_m:02d}",
                    "duration (min)": t["duration"],
                    "priority": priority_badge[t["priority"]],
                    "preferred": pref_str,
                    "pref honored": honored,
                })
            st.table(rows)

        if result["dropped"]:
            st.warning(f"{len(result['dropped'])} task(s) could not fit:")
            st.table([{"task": t["name"], "duration (min)": t["duration"]} for t in result["dropped"]])
