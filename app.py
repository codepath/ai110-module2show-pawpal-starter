"""
PawPal — Streamlit UI

Run with:
    streamlit run app.py

The Owner object lives in st.session_state so it survives re-runs
without being reset to an empty state on every button click.
"""

import streamlit as st
from datetime import datetime

from pawpal_system import Appointment, Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Step 1 & 2: Import classes and set up persistent session state
# ---------------------------------------------------------------------------

def init_session() -> None:
    """
    Bootstrap the session vault.

    st.session_state is a dictionary-like object that persists across
    Streamlit re-runs within the same browser session.  We check for the
    key before creating so the Owner is only built once — not every time
    a widget fires and Streamlit reruns this script from the top.
    """
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name="Pet Parent", email="")
    if "scheduler" not in st.session_state:
        st.session_state.scheduler = Scheduler(owner=st.session_state.owner)


# ---------------------------------------------------------------------------
# Page sections
# ---------------------------------------------------------------------------

def section_owner_profile() -> None:
    """Edit the Owner's basic profile."""
    st.header("Owner Profile")
    owner: Owner = st.session_state.owner

    with st.form("owner_form"):
        name = st.text_input("Your name", value=owner.name)
        email = st.text_input("Email", value=owner.email)
        phone = st.text_input("Phone", value=owner.phone)
        if st.form_submit_button("Save profile"):
            owner.name = name
            owner.email = email
            owner.phone = phone
            st.success(f"Profile saved for {owner.name}.")


def section_add_pet() -> None:
    """
    Step 3 — Wire the 'Add a Pet' form to Owner.add_pet().

    When the form is submitted the Owner method is called directly,
    so the new Pet is appended to owner.pets inside session_state.
    Streamlit will re-run and the updated list is immediately visible.
    """
    st.header("Add a Pet")
    owner: Owner = st.session_state.owner

    with st.form("add_pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
        breed = st.text_input("Breed (optional)")
        age = st.number_input("Age (years)", min_value=0.0, step=0.5)

        if st.form_submit_button("Add pet"):
            if not pet_name.strip():
                st.warning("Please enter a pet name.")
            else:
                new_pet = Pet(
                    name=pet_name.strip(),
                    species=species,
                    owner_id=owner.owner_id,
                    breed=breed.strip(),
                    age=age,
                )
                owner.add_pet(new_pet)   # Step 3: call the class method
                st.success(f"{new_pet.name} added!")


def section_pet_list() -> None:
    """Display the owner's current pets."""
    st.header("My Pets")
    owner: Owner = st.session_state.owner

    if not owner.pets:
        st.info("No pets yet — add one above.")
        return

    for pet in owner.pets:
        with st.expander(f"{pet.name} ({pet.species})"):
            st.write(f"**Breed:** {pet.breed or '—'}  |  **Age:** {pet.age} yrs")
            summary = pet.get_care_summary()
            incomplete = summary["incomplete_tasks"]
            overdue = summary["overdue_tasks"]
            st.write(f"Incomplete tasks: **{len(incomplete)}**  |  Overdue: **{len(overdue)}**")


def section_add_task() -> None:
    """
    Step 3 — Wire the 'Schedule a Task' form to Pet.add_task().

    The selected pet is looked up from session_state, then the Task
    object is passed to pet.add_task() so owner → pet → tasks stays
    in sync without any manual list manipulation in the UI layer.
    """
    st.header("Schedule a Task")
    owner: Owner = st.session_state.owner

    if not owner.pets:
        st.info("Add a pet first before scheduling tasks.")
        return

    pet_names = [p.name for p in owner.pets]

    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Pet", pet_names)
        title = st.text_input("Task title (e.g. Morning walk)")
        description = st.text_area("Notes (optional)")
        due_date = st.date_input("Due date", value=datetime.today())
        due_time = st.time_input("Due time", value=datetime.now().time())
        recurrence = st.selectbox("Recurrence", ["None", "daily", "weekly"])

        if st.form_submit_button("Add task"):
            if not title.strip():
                st.warning("Please enter a task title.")
            else:
                pet = next(p for p in owner.pets if p.name == selected_pet_name)
                due_datetime = datetime.combine(due_date, due_time)
                new_task = Task(
                    title=title.strip(),
                    pet_id=pet.pet_id,
                    due_date=due_datetime,
                    description=description.strip(),
                    recurrence=None if recurrence == "None" else recurrence,
                )
                pet.add_task(new_task)   # Step 3: call the class method
                st.success(f"Task '{new_task.title}' added for {pet.name}.")


def section_add_appointment() -> None:
    """Wire the 'Schedule an Appointment' form to Pet.schedule_appointment()."""
    st.header("Schedule an Appointment")
    owner: Owner = st.session_state.owner

    if not owner.pets:
        st.info("Add a pet first before scheduling appointments.")
        return

    pet_names = [p.name for p in owner.pets]

    with st.form("add_appt_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Pet", pet_names, key="appt_pet")
        appt_type = st.selectbox("Type", ["Vet checkup", "Vaccination", "Grooming", "Other"])
        provider = st.text_input("Provider name")
        location = st.text_input("Location")
        appt_date = st.date_input("Date", key="appt_date")
        appt_time = st.time_input("Time", key="appt_time")

        if st.form_submit_button("Add appointment"):
            if not provider.strip():
                st.warning("Please enter a provider name.")
            else:
                pet = next(p for p in owner.pets if p.name == selected_pet_name)
                appt_datetime = datetime.combine(appt_date, appt_time)
                new_appt = Appointment(
                    pet_id=pet.pet_id,
                    appointment_type=appt_type,
                    provider_name=provider.strip(),
                    location=location.strip(),
                    date_time=appt_datetime,
                )
                pet.schedule_appointment(new_appt)
                st.success(f"Appointment with {new_appt.provider_name} added for {pet.name}.")


def section_task_dashboard() -> None:
    """
    Show a metrics summary, sorted/filtered task table, conflict warnings,
    and per-task actions. Uses Scheduler methods for all data operations.
    """
    st.header("Task Dashboard")
    owner: Owner = st.session_state.owner
    scheduler: Scheduler = st.session_state.scheduler

    all_tasks = scheduler.all_tasks()
    if not all_tasks:
        st.info("No tasks scheduled yet. Add tasks from the **Add Task** tab.")
        return

    # --- Metrics row ---
    total     = len(all_tasks)
    overdue   = sum(1 for t in all_tasks if t.is_overdue())
    complete  = sum(1 for t in all_tasks if t.is_complete)
    pending   = total - complete
    upcoming_appts = sum(
        len(pet.get_care_summary()["upcoming_appointments"])
        for pet in owner.pets
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total tasks",    total)
    m2.metric("Pending",        pending)
    m3.metric("Overdue",        overdue,   delta=overdue  if overdue  else None, delta_color="inverse")
    m4.metric("Upcoming appts", upcoming_appts)

    st.divider()

    # --- Filter controls ---
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox(
            "Filter by pet",
            ["All"] + [p.name for p in owner.pets],
        )
    with col2:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Incomplete", "Complete"],
        )

    # Apply Scheduler filters then sort
    filtered = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All" else pet_filter,
        completed=None if status_filter == "All" else (status_filter == "Complete"),
    )
    sorted_tasks = scheduler.sort_by_time(filtered)

    if not sorted_tasks:
        st.info("No tasks match the current filters.")
        return

    # --- Conflict warnings (surface prominently above the table) ---
    conflicts = scheduler.detect_conflicts(sorted_tasks)
    if conflicts:
        st.subheader(f"⚠ {len(conflicts)} scheduling conflict(s) detected")
        for warning in conflicts:
            st.warning(warning)
        st.divider()

    # --- Summary table (read-only, quick overview) ---
    pet_lookup = {p.pet_id: p.name for p in owner.pets}
    table_rows = []
    for task in sorted_tasks:
        table_rows.append({
            "Status":    "✅ Done" if task.is_complete else ("🔴 Overdue" if task.is_overdue() else "🔵 Pending"),
            "Task":      task.title,
            "Pet":       pet_lookup.get(task.pet_id, "—"),
            "Due":       task.due_date.strftime("%b %d  %H:%M"),
            "Repeats":   task.recurrence or "—",
        })
    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    st.divider()

    # --- Per-task action expanders ---
    st.subheader("Actions")
    for task in sorted_tasks:
        pet_name  = pet_lookup.get(task.pet_id, "Unknown")
        status_icon = "✅" if task.is_complete else ("🔴" if task.is_overdue() else "🔵")
        label = f"{status_icon} **{task.title}** — {pet_name} — {task.due_date.strftime('%b %d %H:%M')}"
        if task.recurrence:
            label += f" _(repeats {task.recurrence})_"

        with st.expander(label):
            if task.description:
                st.caption(task.description)
            if not task.is_complete:
                if st.button("Mark complete", key=f"complete_{task.task_id}"):
                    pet_obj = next((p for p in owner.pets if p.pet_id == task.pet_id), None)
                    if pet_obj:
                        next_task = scheduler.mark_task_complete(task, pet_obj)
                        if next_task:
                            st.success(
                                f"Done! Next **{task.title}** auto-scheduled "
                                f"for {next_task.due_date.strftime('%b %d at %H:%M')}."
                            )
                        else:
                            st.success("Task marked complete.")
                        st.rerun()
            else:
                st.success(f"Completed {task.completed_at.strftime('%b %d at %H:%M') if task.completed_at else ''}")


# ---------------------------------------------------------------------------
# Main app entry point
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title="PawPal", page_icon="🐾", layout="wide")
    st.title("🐾 PawPal — Pet Care Scheduler")

    init_session()

    tab_pets, tab_tasks, tab_appts, tab_dashboard, tab_profile = st.tabs([
        "My Pets", "Add Task", "Add Appointment", "Dashboard", "Profile"
    ])

    with tab_pets:
        section_add_pet()
        section_pet_list()

    with tab_tasks:
        section_add_task()

    with tab_appts:
        section_add_appointment()

    with tab_dashboard:
        section_task_dashboard()

    with tab_profile:
        section_owner_profile()


if __name__ == "__main__":
    main()
