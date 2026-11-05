from ai.gemini_client import ask_gemini
from ai.planner import propose_care_plan
from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task
from persistence import load_owner, save_owner


def load_saved_data() -> None:
    """Replace session data only after a complete successful load."""
    try:
        restored = load_owner()
    except (OSError, ValueError) as error:
        st.session_state.storage_notice = ("error", f"Could not load saved data: {error}")
        return
    # Old widget selections and editor references belong to the previous objects.
    st.session_state.clear()
    st.session_state.owner = restored
    st.session_state.storage_notice = ("success", "Loaded saved pets, tasks, and settings.")


def complete_task_today(pet: Pet, task: Task) -> None:
    """Complete a task once, clear the old plan, and save a success message."""
    if task.completed:
        return
    next_task = pet.complete_task(task, on_date=date.today())
    st.session_state.pop("plan", None)
    message = f"Completed {pet.name}: {task.name}."
    if next_task is not None:
        message += f" Next {next_task.recurrence} occurrence is due {next_task.due_date}."
    st.session_state.completion_notice = message


def load_task_editor(task: Task) -> None:
    """Load a task's saved values, discarding the previous editor draft."""
    st.session_state.edit_title = task.name
    st.session_state.edit_duration = task.duration_minutes
    st.session_state.edit_priority = task.priority
    st.session_state.edit_recurrence = task.recurrence
    st.session_state.edit_scheduled_time = task.scheduled_time or ""
    st.session_state.edit_due_date = task.due_date
    st.session_state.edit_loaded_task = task


def save_pending_task(pet: Pet, task: Task) -> None:
    """Validate and save the rendered task in place before the app redraws."""
    owner = st.session_state.owner
    if (
        task.completed
        or not any(existing is pet for existing in owner.pets)
        or not any(existing is task for existing in pet.tasks)
    ):
        st.session_state.edit_notice = (
            "error", "This task is completed or no longer available. Select a pending task."
        )
        return

    changes = {
        "name": st.session_state.edit_title.strip(),
        "duration_minutes": st.session_state.edit_duration,
        "priority": st.session_state.edit_priority,
        "recurrence": st.session_state.edit_recurrence,
        "scheduled_time": st.session_state.edit_scheduled_time.strip() or None,
        "due_date": st.session_state.edit_due_date,
    }
    changed = any(getattr(task, field) != value for field, value in changes.items())
    try:
        # None means "leave unchanged" to the backend, not an empty duration.
        if changes["duration_minutes"] is None:
            raise ValueError("Task duration must be a positive whole number of minutes.")
        task.update_details(**changes)
    except ValueError as error:
        st.session_state.edit_notice = ("error", str(error))
        return

    if changed:
        st.session_state.pop("plan", None)
        st.session_state.edit_notice = ("success", f"Saved changes to {pet.name}: {task.name}.")
    else:
        st.session_state.edit_notice = ("info", "No changes to save. Your current plan is unchanged.")
    load_task_editor(task)


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=30)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner = st.session_state.owner
scheduler = st.session_state.scheduler

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Add your pets and care tasks, then build a daily plan
that fits your available time.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

Use Save data at the bottom to keep your pets and tasks between runs.
Use Load saved data to restore your last save into this session.
"""
    )

with st.expander("How to use PawPal+", expanded=True):
    st.markdown(
        """
- Add your pets and select a pet when adding a task.
- Set each task's duration, priority, and recurrence; optionally add a time and due date.
- Browse tasks by time, filter by pet or completion status, and review same-time warnings.
- Mark tasks complete today; daily and weekly tasks create their next occurrence automatically.
- Choose your available time and generate a plan for all your pets.
- Review selected tasks and explanations for anything skipped.
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value=owner.name, key="owner_name")
if owner_name.strip():
    owner.name = owner_name.strip()
else:
    st.warning("Enter an owner name before generating a schedule.")

pet_name = st.text_input("Pet name", value="Mochi", key="pet_name")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species")

if st.button("Add pet", key="add_pet"):
    if not pet_name.strip():
        st.error("Pet name must not be empty.")
    else:
        try:
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state.pop("plan", None)
            st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.write("Your pets:")
    st.table([{"Pet": pet.name, "Species": pet.species} for pet in owner.pets])
else:
    st.info("No pets yet. Add a pet above to start adding care tasks.")

st.markdown("### Tasks")
st.caption("Select a pet and add a care task. Leave the time or due date blank when not needed.")
completion_notice = st.session_state.pop("completion_notice", None)
if completion_notice:
    st.success(completion_notice)
if owner.pets and st.session_state.get("selected_pet") is None:
    st.session_state.selected_pet = 0
selected_pet_index = st.selectbox(
    "Task's pet",
    options=list(range(len(owner.pets))),
    format_func=lambda index: f"{index + 1}. {owner.pets[index].name} ({owner.pets[index].species})",
    disabled=not owner.pets,
    key="selected_pet",
)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
with col2:
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20, key="duration"
    )
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="priority")

col1, col2, col3 = st.columns(3)
with col1:
    scheduled_time = st.text_input(
        "Scheduled time (optional)", placeholder="HH:MM", key="scheduled_time",
        help="Use 24-hour time, such as 09:05 or 18:30. Leave blank for an untimed task.",
    )
with col2:
    recurrence = st.selectbox("Recurrence", ["once", "daily", "weekly"], key="recurrence")
with col3:
    due_date = st.date_input(
        "Due date (optional)", value=None, key="due_date",
        help="Future tasks are skipped in today's plan. Undated pending tasks are eligible today.",
    )

if st.button("Add task", disabled=selected_pet_index is None, key="add_task"):
    try:
        task = Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            scheduled_time=scheduled_time.strip() or None,
            recurrence=recurrence,
            due_date=due_date,
        )
        owner.pets[selected_pet_index].add_task(task)
    except ValueError as error:
        st.error(str(error))
    else:
        st.session_state.pop("plan", None)
        st.success(f"Added {task.name} for {owner.pets[selected_pet_index].name}.")

task_pairs = owner.get_all_tasks()
st.markdown("### Edit a pending task")
st.caption(
    "Choose from all pending tasks, regardless of browse filters. Changes apply only when "
    "you save; selecting another task discards unsaved edits."
)
edit_notice = st.session_state.pop("edit_notice", None)
if edit_notice:
    notice_type, notice_text = edit_notice
    if notice_type == "success":
        st.success(notice_text)
    elif notice_type == "error":
        st.error(notice_text)
    else:
        st.info(notice_text)

edit_options = {
    f"{number}. {pet.name}: {task.name}": (pet, task)
    for number, (pet, task) in enumerate(task_pairs, start=1)
    if not task.completed
}
if edit_options:
    # Keep the same object selected when its title or collection numbering changes.
    requested_label = st.session_state.get("edit_task")
    previous_label = st.session_state.get("edit_previous_label")
    if requested_label == previous_label or requested_label not in edit_options:
        loaded_task = st.session_state.get("edit_loaded_task")
        st.session_state.edit_task = next(
            (label for label, (_, task) in edit_options.items() if task is loaded_task),
            next(iter(edit_options)),
        )
    selected_label = st.selectbox("Pending task to edit", list(edit_options), key="edit_task")
    edit_pet, edit_task = edit_options[selected_label]
    st.session_state.edit_previous_label = selected_label
    if st.session_state.get("edit_loaded_task") is not edit_task:
        load_task_editor(edit_task)

    with st.form("pending_task_editor"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Edit title", key="edit_title")
        with col2:
            st.number_input("Edit duration (minutes)", min_value=1, step=1, key="edit_duration")
        with col3:
            st.selectbox("Edit priority", ["high", "medium", "low"], key="edit_priority")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.selectbox("Edit recurrence", ["once", "daily", "weekly"], key="edit_recurrence")
        with col2:
            st.text_input(
                "Edit scheduled time", placeholder="HH:MM", key="edit_scheduled_time",
                help="Use 24-hour HH:MM. Clear this field for an untimed task.",
            )
        with col3:
            st.date_input(
                "Edit due date", value=None, key="edit_due_date",
                help="Clear this field to remove the due date.",
            )
        st.form_submit_button(
            "Save changes", key="edit_save", on_click=save_pending_task, args=(edit_pet, edit_task),
        )
else:
    st.session_state.pop("edit_task", None)
    st.session_state.pop("edit_previous_label", None)
    st.session_state.pop("edit_loaded_task", None)
    st.info("No pending tasks to edit. Add a care task or view your completed tasks below.")

st.markdown("### Browse tasks")
col1, col2 = st.columns(2)
with col1:
    pet_filter = st.text_input(
        "Filter by pet name", key="pet_filter",
        help="Leave blank for all pets. Matches the full name, ignoring case.",
    )
with col2:
    status_filter = st.selectbox(
        "Completion status", ["All", "Pending", "Completed"], key="status_filter",
    )
completed_filter = {"All": None, "Pending": False, "Completed": True}[status_filter]
visible_pairs = scheduler.sort_tasks_by_time(
    scheduler.filter_tasks(owner, pet_name=pet_filter.strip() or None, completed=completed_filter)
)
st.caption("Sorted by scheduled time of day; untimed tasks appear last. Filters only affect this list.")
if task_pairs:
    if visible_pairs:
        st.table([
            {
                "Time": task.scheduled_time or "Untimed",
                "Pet": pet.name,
                "Task": task.name,
                "Minutes": task.duration_minutes,
                "Priority": task.priority,
                "Recurrence": task.recurrence,
                "Due date": str(task.due_date) if task.due_date else "No date",
                "Status": "Completed" if task.completed else "Pending",
            }
            for pet, task in visible_pairs
        ])
        pending_pairs = [(pet, task) for pet, task in visible_pairs if not task.completed]
        if pending_pairs:
            with st.expander("Complete a task"):
                st.caption(
                    "Completion is recorded for today. Daily and weekly tasks create one new "
                    "occurrence due one or seven days after completion."
                )
                for pet, task in pending_pairs:
                    # Object identity keeps each button tied to its task after sorting or filtering.
                    st.button(
                        f"Complete today: {pet.name} - {task.name} "
                        f"({task.scheduled_time or 'Untimed'}, due {task.due_date or 'No date'})",
                        key=f"complete_task_{id(task)}",
                        on_click=complete_task_today,
                        args=(pet, task),
                    )
    else:
        st.info("No tasks match these filters.")
else:
    st.info("No tasks yet. Select a pet and add a task above.")

st.markdown("### Same-time conflicts")
st.caption(
    "Checks all pending tasks across pets and dates, regardless of the filters above. "
    "Tasks without a due date use today. Only identical start times on the same date "
    "are checked; overlapping durations with different start times are not detected."
)
conflicts = scheduler.detect_conflicts(task_pairs, on_date=date.today())
for warning in conflicts:
    st.warning(warning)
if task_pairs and not conflicts:
    st.info("No identical-start-time conflicts found.")

st.divider()

st.subheader("Build Schedule")
st.caption("Plan care across all your pets using one shared time budget.")
available_minutes = st.number_input(
    "Available time (minutes)", min_value=0, value=owner.available_minutes, step=5,
    key="available_minutes",
)
prefer_short_tasks = st.checkbox(
    "Prefer shorter tasks when priorities match", value=owner.prefer_short_tasks,
    key="prefer_short_tasks",
)

settings_valid = True
if (available_minutes, prefer_short_tasks) != (owner.available_minutes, owner.prefer_short_tasks):
    try:
        owner.update_settings(
            available_minutes=int(available_minutes), prefer_short_tasks=prefer_short_tasks
        )
    except ValueError as error:
        settings_valid = False
        st.error(str(error))
    else:
        st.session_state.pop("plan", None)

if st.button(
    "Generate schedule", disabled=not owner_name.strip() or not settings_valid,
    key="generate_schedule",
):
    try:
        st.session_state.plan = scheduler.generate_plan(owner)
    except ValueError as error:
        st.session_state.pop("plan", None)
        st.error(str(error))

plan = st.session_state.get("plan")
if plan is not None:
    st.markdown("### Today's Schedule")
    st.write(f"Planned: {plan['total_minutes']} min | Remaining: {plan['remaining_minutes']} min")
    if plan["selected"]:
        st.table([
            {
                "Order": number,
                "Pet": entry["pet"].name,
                "Task": entry["task"].name,
                "Time": entry["task"].scheduled_time or "Untimed",
                "Minutes": entry["task"].duration_minutes,
                "Priority": entry["task"].priority,
                "Why selected": entry["reason"],
            }
            for number, entry in enumerate(plan["selected"], start=1)
        ])
    elif not task_pairs:
        st.info("Add a pet and care tasks to build your first schedule.")
    else:
        st.info("No tasks could be scheduled. Review the skipped tasks below.")

    if plan["skipped"]:
        st.markdown("### Skipped tasks")
        st.table([
            {"Pet": entry["pet"].name, "Task": entry["task"].name, "Reason": entry["reason"]}
            for entry in plan["skipped"]
        ])
else:
    st.info("Generate a schedule after adding tasks or changing your care settings.")

st.divider()
st.subheader("Find a free time")
st.caption(
    "Find space for an additional task across all pets. Pending timed tasks reserve their full "
    "duration; completed and untimed tasks do not. This suggests a time without changing tasks. "
    "Use the returned time and search date when adding or editing a task."
)
with st.form("slot_search"):
    slot_date = st.date_input("Search date", value=date.today(), key="slot_date")
    slot_duration = st.number_input("Minutes needed", min_value=1, value=20, key="slot_duration")
    slot_start = st.text_input("Window start", value="09:00", key="slot_start")
    slot_end = st.text_input("Window end", value="17:00", key="slot_end", help="24:00 means end of day.")
    find_slot = st.form_submit_button("Find next available slot", key="find_slot")
if find_slot:
    try:
        slot = scheduler.next_available_slot(owner, slot_duration, slot_start, slot_end, slot_date)
    except ValueError as error:
        st.error(str(error))
    else:
        if slot is None:
            st.info("No free interval fits within this window.")
        else:
            st.success(f"Next available slot: {slot} on {slot_date} for {slot_duration} minutes.")

st.subheader("Save and load")
st.caption(
    "Save data writes pets, tasks, completion history, and settings to data/pawpal.json. "
    "Load replaces this session with the last save and discards unsaved changes. "
    "Submit task edits before saving. This local file is shared by sessions on this server; "
    "use this feature for a single-owner local app."
)
storage_notice = st.session_state.pop("storage_notice", None)
if storage_notice:
    kind, message = storage_notice
    if kind == "error":
        st.error(message)
    else:
        st.success(message)
if st.button("Save data", key="save_data", disabled=not owner_name.strip() or not settings_valid):
    try:
        save_owner(owner)
    except (OSError, ValueError) as error:
        st.error(f"Could not save data: {error}")
    else:
        st.success("Saved pets, tasks, and settings to data/pawpal.json.")
st.button("Load saved data", key="load_data", on_click=load_saved_data)
st.divider()
st.subheader("🐾 PawPal AI care guide")
st.caption(
    "Ask about general care or request a task proposal for your pets. "
    "AI uses a small local knowledge base; it does not diagnose or change your tasks. "
    "Your request and relevant pet/task names are sent to Gemini only when you submit."
)


def show_ai_sources(sources):
    if sources:
        with st.expander("View cited knowledge sources"):
            for source in sources:
                st.markdown(f"**{source['title']} — {source['chunk_id']}**")
                if source["url"]:
                    st.markdown(f"[Read original source]({source['url']})")
                st.write(source["text"])


with st.form("pawpal_ai_form"):
    ai_question = st.text_area(
        "What would you like to know?",
        placeholder="How can I plan walks and fresh water for my dog?",
        key="ai_question",
    )
    ask_ai = st.form_submit_button("Ask PawPal AI", key="ask_ai")

if ask_ai:
    with st.spinner("Checking care knowledge..."):
        result = ask_gemini(ai_question)
    st.markdown("### AI answer")
    st.write(result["answer"])
    show_ai_sources(result["sources"])

st.markdown("### Suggest care tasks")
st.caption("Proposals are checked against today's shared time budget. Review them and use Add task yourself if useful; nothing is saved automatically.")
with st.form("pawpal_plan_form"):
    planning_request = st.text_area(
        "Care planning request",
        placeholder="Suggest a short walk and water check for my dog within today's plan.",
        key="planning_request",
    )
    request_plan = st.form_submit_button("Suggest tasks", key="suggest_tasks")

if request_plan:
    with st.spinner("Checking knowledge and schedule..."):
        proposal = propose_care_plan(planning_request, owner, scheduler)
    st.write(proposal["message"])
    if proposal["tasks"]:
        st.table(proposal["tasks"])
    show_ai_sources(proposal["sources"])
    with st.expander("Planning steps", expanded=True):
        for number, step in enumerate(proposal["trace"], start=1):
            st.write(f"{number}. {step['step']}: {step['detail']}")
