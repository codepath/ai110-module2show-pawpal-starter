"""
PawPal+ — Streamlit UI
Connects the Owner / Pet / Task / Scheduler backend to an interactive web app.
"""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session-state initialisation
# Streamlit re-runs the whole script on every interaction.
# We store the Owner object in st.session_state so it survives those re-runs.
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant — powered by your own scheduler.")
st.divider()


# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------

st.subheader("1. Who's caring today?")

with st.form("owner_form"):
    col_name, col_start, col_end = st.columns(3)
    with col_name:
        owner_name  = st.text_input("Your name", value="Jordan")
    with col_start:
        avail_start = st.text_input("Available from", value="08:00")
    with col_end:
        avail_end   = st.text_input("Available until", value="20:00")
    submitted_owner = st.form_submit_button("Set owner")

if submitted_owner:
    st.session_state.owner     = Owner(name=owner_name, available_start=avail_start, available_end=avail_end)
    st.session_state.scheduler = None
    st.success(f"Owner set: {owner_name} ({avail_start}–{avail_end})")

if st.session_state.owner is None:
    st.info("Fill in your name and availability above to get started.")
    st.stop()

owner: Owner = st.session_state.owner


# ---------------------------------------------------------------------------
# Section 2 — Add a pet
# ---------------------------------------------------------------------------

st.divider()
st.subheader("2. Register a pet")

with st.form("pet_form"):
    col_pet, col_species, col_age = st.columns(3)
    with col_pet:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col_species:
        species  = st.selectbox("Species", ["dog", "cat", "other"])
    with col_age:
        age      = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    load_defaults = st.checkbox("Load species default tasks", value=True)
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    if owner.get_pet(pet_name):
        st.warning(f"{pet_name} is already registered.")
    else:
        new_pet = Pet(name=pet_name, species=species, age=age)
        if load_defaults:
            new_pet.load_default_tasks()
        owner.add_pet(new_pet)
        st.session_state.scheduler = None
        st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.markdown("**Registered pets:**")
    for pet in owner.pets:
        pending = len(pet.get_pending_tasks())
        total   = len(pet.tasks)
        st.markdown(f"- **{pet.name}** ({pet.species}, age {pet.age}) — {pending}/{total} tasks pending")
else:
    st.info("No pets yet. Add one above.")


# ---------------------------------------------------------------------------
# Section 3 — Add a task to a pet
# ---------------------------------------------------------------------------

st.divider()
st.subheader("3. Add a care task")

if not owner.pets:
    st.info("Register at least one pet before adding tasks.")
else:
    with st.form("task_form"):
        pet_options       = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Assign to pet", pet_options)
        col_t, col_d, col_p, col_f = st.columns(4)
        with col_t:
            task_title = st.text_input("Task", value="Evening walk")
        with col_d:
            duration   = st.number_input("Minutes", min_value=1, max_value=240, value=30)
        with col_p:
            priority   = st.selectbox("Priority", ["high", "medium", "low"])
        with col_f:
            frequency  = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        owner.get_pet(selected_pet_name).add_task(Task(task_title, int(duration), priority, frequency))
        st.session_state.scheduler = None
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    all_pairs = owner.get_all_tasks()
    if all_pairs:
        st.markdown("**All tasks:**")
        st.table([
            {
                "Pet":       pet.name,
                "Task":      task.title,
                "Minutes":   task.duration_minutes,
                "Priority":  task.priority,
                "Frequency": task.frequency,
                "Done":      "✓" if task.completed else "",
            }
            for pet, task in all_pairs
        ])


# ---------------------------------------------------------------------------
# Section 4 — Generate and display schedule
# ---------------------------------------------------------------------------

st.divider()
st.subheader("4. Build today's schedule")

if not owner.get_all_pending_tasks():
    st.info("Add at least one pending task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        sched = Scheduler(owner=owner)
        sched.build_schedule()
        st.session_state.scheduler = sched

    if st.session_state.scheduler:
        sched: Scheduler = st.session_state.scheduler

        # ── Summary ──────────────────────────────────────────────────────────
        total = len(sched.schedule)
        done  = sum(1 for i in sched.schedule if i.task.completed)
        st.markdown(
            f"**{owner.name}'s plan** — "
            f"{owner.available_start}–{owner.available_end} · "
            f"{done}/{total} completed"
        )

        # ── Conflict warnings ─────────────────────────────────────────────────
        conflicts = sched.detect_conflicts()
        if conflicts:
            st.error("**Schedule conflicts detected** — two or more tasks overlap:")
            for w in conflicts:
                st.warning(w)

        # ── View toggle ───────────────────────────────────────────────────────
        view = st.radio(
            "View",
            ["All tasks", "Sorted by time", "Pending only", "Completed only"],
            horizontal=True,
        )

        view_map = {
            "All tasks":      sched.schedule,
            "Sorted by time": sched.sort_by_time(),
            "Pending only":   sched.filter_tasks(completed=False),
            "Completed only": sched.filter_tasks(completed=True),
        }
        items_to_show = view_map[view]

        # ── Filter by pet ─────────────────────────────────────────────────────
        pet_options = ["All pets"] + [p.name for p in owner.pets]
        chosen_pet  = st.selectbox("Filter by pet", pet_options)
        if chosen_pet != "All pets":
            items_to_show = [i for i in items_to_show if i.pet.name == chosen_pet]

        # ── Schedule table ────────────────────────────────────────────────────
        if items_to_show:
            ICONS = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            st.table([
                {
                    "Time":     f"{item.start_time}–{item.end_time}",
                    "Pet":      item.pet.name,
                    "Task":     item.task.title,
                    "Priority": ICONS.get(item.task.priority, "") + " " + item.task.priority,
                    "Min":      item.task.duration_minutes,
                    "Freq":     item.task.frequency,
                    "Done":     "✓" if item.task.completed else "○",
                    "Why":      item.reason,
                }
                for item in items_to_show
            ])
        else:
            st.info("No tasks match the current view.")

        # ── Mark complete ─────────────────────────────────────────────────────
        pending_titles = [i.task.title for i in sched.get_todays_tasks()]
        if pending_titles:
            with st.form("complete_form"):
                to_complete = st.selectbox("Mark as completed", pending_titles)
                if st.form_submit_button("✓ Done"):
                    sched.mark_complete(to_complete)
                    st.rerun()
        else:
            st.success("All tasks for today are complete! 🎉")

        # ── Skipped tasks ─────────────────────────────────────────────────────
        if sched.skipped:
            with st.expander(f"⚠ {len(sched.skipped)} task(s) didn't fit in the window"):
                for pet, task in sched.skipped:
                    st.markdown(
                        f"- **[{pet.name}]** {task.title} "
                        f"({task.duration_minutes} min, {task.priority} priority)"
                    )
                st.caption("Tip: extend your available window or remove lower-priority tasks to fit these in.")
