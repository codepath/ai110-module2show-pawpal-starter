import streamlit as st
from datetime import date, time
from pawpal_system import Priority, TimeWindow, Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("Pet care planning assistant")

# ============================================================
# Session State vault — Owner persists across every rerun
# ============================================================
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        availability_windows=[TimeWindow(time(7, 0), time(21, 0))],
    )
if "schedule" not in st.session_state:
    st.session_state.schedule = None

owner: Owner = st.session_state.owner
scheduler = Scheduler()

# ============================================================
# Sidebar — owner settings + Add Pet form
# ============================================================
with st.sidebar:
    st.header("⚙️ Owner Settings")

    new_name = st.text_input("Owner name", value=owner.name)
    if new_name.strip() and new_name.strip() != owner.name:
        owner.name = new_name.strip()

    st.subheader("Availability")
    c1, c2 = st.columns(2)
    with c1:
        avail_start = st.time_input("From", value=owner.availability_windows[0].start)
    with c2:
        avail_end = st.time_input("To", value=owner.availability_windows[0].end)
    if (avail_start != owner.availability_windows[0].start
            or avail_end != owner.availability_windows[0].end):
        owner.availability_windows = [TimeWindow(avail_start, avail_end)]

    st.divider()
    st.subheader("➕ Add a Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        pet_name    = st.text_input("Pet name",    placeholder="e.g. Mochi")
        pet_species = st.selectbox("Species",      ["dog", "cat", "other"])
        pet_breed   = st.text_input("Breed",       placeholder="e.g. Shiba Inu")
        pet_age     = st.number_input("Age (yrs)", min_value=0.0, step=0.5, value=1.0)
        if st.form_submit_button("Add Pet") and pet_name.strip():
            owner.add_pet(Pet(pet_name.strip(), pet_species, pet_breed, pet_age))
            st.success(f"Added {pet_name.strip()}!")
            st.rerun()

# ============================================================
# Guard — nothing to show yet
# ============================================================
pets = owner.get_pets()
if not pets:
    st.info("No pets yet. Use the sidebar to add your first pet.")
    st.stop()

# ============================================================
# Tab layout
# ============================================================
tab_pets, tab_view, tab_schedule = st.tabs(["🐾 Pets & Tasks", "🔍 Sort & Filter", "📅 Schedule"])

# ============================================================
# Tab 1 — Pets & Tasks
# ============================================================
with tab_pets:
    for pet in pets:
        label = (f"{pet.name}  ({pet.species}"
                 + (f", {pet.breed}" if pet.breed else "")
                 + f", {pet.age_years:.0f} yrs)  — {len(pet.get_tasks())} task(s)")
        with st.expander(label, expanded=True):
            if pet.get_tasks():
                for task in pet.get_tasks():
                    icon = "✅" if task.completed else "○"
                    rec  = f" · _{task.recurrence}_" if task.recurrence else ""
                    due  = f" · next due {task.next_due}" if task.next_due else ""
                    st.markdown(
                        f"{icon} **{task.title}** · {task.priority.value} "
                        f"· {task.duration_minutes} min{rec}{due}"
                    )
            else:
                st.caption("No tasks yet — add one below.")

            with st.form(f"add_task_{pet.id}", clear_on_submit=True):
                st.markdown(f"**Add a task for {pet.name}**")
                fc1, fc2 = st.columns(2)
                with fc1:
                    t_title    = st.text_input("Title",       placeholder="e.g. Morning walk", key=f"tt_{pet.id}")
                    t_desc     = st.text_input("Description", placeholder="e.g. Leash walk",   key=f"td_{pet.id}")
                    t_priority = st.selectbox("Priority", ["high", "medium", "low"],            key=f"tpri_{pet.id}")
                with fc2:
                    t_duration   = st.number_input("Duration (min)", min_value=1, value=15,     key=f"tdur_{pet.id}")
                    t_recurrence = st.text_input("Recurrence", placeholder="daily / weekly",    key=f"trec_{pet.id}")
                    t_earliest   = st.time_input("Earliest start (optional)", value=time(7, 0), key=f"tes_{pet.id}")
                    t_use_earliest = st.checkbox("Set earliest start", key=f"tues_{pet.id}")

                if st.form_submit_button(f"Add task to {pet.name}") and t_title.strip():
                    pet.add_task(Task(
                        title=t_title.strip(),
                        description=t_desc,
                        duration_minutes=int(t_duration),
                        priority=t_priority,
                        recurrence=t_recurrence.strip() or None,
                        earliest_start=t_earliest if t_use_earliest else None,
                    ))
                    st.success(f"Added '{t_title.strip()}' to {pet.name}!")
                    st.rerun()

# ============================================================
# Tab 2 — Sort & Filter view
# ============================================================
with tab_view:
    st.subheader("Sort tasks by time")
    all_tasks = owner.all_tasks()
    if all_tasks:
        sorted_tasks = scheduler.sort_by_time(all_tasks)
        rows = []
        for t in sorted_tasks:
            pet_match = next((p for p in pets if t.required_pet_id == p.id), None)
            rows.append({
                "Earliest start": t.earliest_start.strftime("%H:%M") if t.earliest_start else "anytime",
                "Task":           t.title,
                "Pet":            pet_match.name if pet_match else "—",
                "Priority":       t.priority.value,
                "Duration (min)": t.duration_minutes,
                "Recurring":      t.recurrence or "—",
                "Status":         "✅ done" if t.completed else "○ pending",
            })
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No tasks yet.")

    st.divider()
    st.subheader("Filter tasks")
    fc1, fc2 = st.columns(2)
    with fc1:
        pet_options = ["All pets"] + [p.name for p in pets]
        chosen_pet = st.selectbox("Pet", pet_options)
    with fc2:
        status_options = {"All": None, "Pending only": False, "Completed only": True}
        chosen_status_label = st.selectbox("Status", list(status_options.keys()))

    chosen_pet_name   = None if chosen_pet == "All pets" else chosen_pet
    chosen_status     = status_options[chosen_status_label]
    filtered = scheduler.filter_tasks(owner, pet_name=chosen_pet_name, completed=chosen_status)

    if filtered:
        filter_rows = []
        for t in filtered:
            pet_match = next((p for p in pets if t.required_pet_id == p.id), None)
            filter_rows.append({
                "Task":     t.title,
                "Pet":      pet_match.name if pet_match else "—",
                "Priority": t.priority.value,
                "Duration": f"{t.duration_minutes} min",
                "Status":   "✅ done" if t.completed else "○ pending",
            })
        st.success(f"{len(filter_rows)} task(s) matched")
        st.table(filter_rows)
    else:
        st.warning("No tasks match that filter.")

# ============================================================
# Tab 3 — Schedule
# ============================================================
with tab_schedule:
    pending = owner.all_pending_tasks()
    if not pending:
        st.warning("No pending tasks to schedule. Add tasks in the Pets & Tasks tab.")
    else:
        dc1, dc2 = st.columns([3, 1])
        with dc1:
            target_date = st.date_input("Schedule for", value=date.today())
        with dc2:
            st.metric("Pending tasks", len(pending))

        if st.button("Generate schedule", type="primary"):
            schedule = scheduler.generate_daily_plan(owner, target_date)
            st.session_state.schedule = schedule

    if st.session_state.schedule:
        sched = st.session_state.schedule

        # ── Summary banner ──────────────────────────────────────
        st.success(
            f"Scheduled **{len(sched.slots)} tasks** — "
            f"**{sched.total_minutes_scheduled} minutes** total"
        )

        # ── Conflict warnings ────────────────────────────────────
        conflicts = scheduler.detect_conflicts(sched)
        if conflicts:
            st.error("⚠️ Scheduling conflicts detected — two or more tasks overlap in time:")
            for w in conflicts:
                st.warning(w)
        else:
            st.success("✓ No time conflicts detected")

        # ── Scheduled plan ───────────────────────────────────────
        if sched.slots:
            st.markdown("### Today's Plan")
            plan_rows = []
            for slot in sched.slots:
                pet   = owner.get_pet(slot.pet_id)
                plan_rows.append({
                    "Time":     f"{slot.start.strftime('%I:%M %p')} – {slot.end.strftime('%I:%M %p')}",
                    "Task":     slot.title,
                    "Pet":      pet.name if pet else "—",
                    "Duration": f"{slot.duration()} min",
                    "Status":   "✅" if slot.status == "completed" else "🕐 scheduled",
                    "Why":      slot.reason,
                })
            st.table(plan_rows)

        # ── Skipped tasks ────────────────────────────────────────
        if sched.skipped_tasks:
            st.markdown("### ⚠️ Tasks that couldn't be scheduled")
            for t in sched.skipped_tasks:
                st.warning(
                    f"**{t.title}** ({t.duration_minutes} min · {t.priority.value} priority) "
                    f"— couldn't fit inside your availability window. "
                    f"Try expanding your available hours or shortening the task."
                )

        # ── Collapsible extras ───────────────────────────────────
        with st.expander("📋 Owner summary"):
            st.text(scheduler.summary(owner))

        with st.expander("📤 Export as JSON"):
            st.code(sched.persist(), language="json")
