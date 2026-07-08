"""PawPal+ – smart pet care scheduler."""
from __future__ import annotations

from datetime import date, datetime
import streamlit as st

# ── Logic layer (all backend classes live in pawpal_system.py) ────────────────
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    PRIORITIES, FREQUENCIES,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens ──────────────────────────────────────────────────────────────
C_AMBER    = "#E8850A"
C_TEAL     = "#4A7C6F"
C_NAVY     = "#1E2A35"
C_BG       = "#F2F0EC"
C_CARD     = "#FFFFFF"
C_MUTED    = "#6B7A8D"
C_BORDER   = "#DDD9D0"
C_CRITICAL = "#C53030"
C_HIGH     = "#B45309"
C_MEDIUM   = "#1D4ED8"
C_LOW      = "#374151"
C_OPTIONAL = "#9CA3AF"

PRIORITY_COLORS = {
    "critical": C_CRITICAL,
    "high":     C_HIGH,
    "medium":   C_MEDIUM,
    "low":      C_LOW,
    "optional": C_OPTIONAL,
}

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background: {C_BG}; }}
  section[data-testid="stSidebar"] {{ background: {C_NAVY}; }}
  section[data-testid="stSidebar"] * {{ color: #E8E8E0 !important; }}
  h1,h2,h3 {{ color: {C_NAVY}; font-family: system-ui, -apple-system, sans-serif; }}
  .task-card {{
    background: {C_CARD}; border-radius: 10px;
    border-left: 5px solid {C_AMBER}; padding: 14px 18px;
    margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.07);
  }}
  .task-card.done {{  border-left-color: {C_TEAL}; opacity: .6; }}
  .task-title {{ font-size: 1.05rem; font-weight: 600; color: {C_NAVY}; margin: 0 0 4px 0; }}
  .task-meta  {{ font-size: .82rem; color: {C_MUTED}; margin: 0 0 4px 0; }}
  .badge {{
    display: inline-block; border-radius: 4px; font-size: .72rem;
    font-weight: 700; letter-spacing: .04em; padding: 2px 7px;
    text-transform: uppercase; margin-right: 5px;
  }}
  .time-chip {{
    font-size: 1rem; font-weight: 700; color: {C_AMBER}; margin-right: 10px;
  }}
  .empty-state {{ text-align: center; padding: 48px 0; color: {C_MUTED}; }}
  .sidebar-header {{ font-size: 1.3rem; font-weight: 700; color: {C_AMBER} !important; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _badge(text: str, color: str) -> str:
    return (
        f'<span class="badge" style="background:{color}20;'
        f'color:{color};border:1px solid {color}60">{text}</span>'
    )


def _priority_badge(priority: str) -> str:
    color = PRIORITY_COLORS.get(priority.lower(), C_MUTED)
    return _badge(priority.upper(), color)


def _freq_label(f: str) -> str:
    return {"once": "One-time", "daily": "Daily", "weekly": "Weekly"}.get(f, f)


# ── Session state — one Owner object persists across Streamlit reruns ──────────
# st.session_state acts as the app's "memory vault". We check for the Owner
# key before creating it so the object isn't reset on every page interaction.

if "owner" not in st.session_state:
    st.session_state.owner = Owner.load()
if "active_pet_idx" not in st.session_state:
    st.session_state.active_pet_idx = 0
if "show_add_pet" not in st.session_state:
    st.session_state.show_add_pet = False

owner: Owner = st.session_state.owner
scheduler    = Scheduler(owner)          # stateless — safe to rebuild each render


def _save() -> None:
    owner.save()


def _active_pet() -> Pet | None:
    if not owner.pets:
        return None
    return owner.pets[min(st.session_state.active_pet_idx, len(owner.pets) - 1)]


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-header">🐾 PawPal+</div>', unsafe_allow_html=True)
    st.caption("Smart pet care scheduler")
    st.divider()

    # Owner name
    new_name = st.text_input("Your name", value=owner.name, key="s_owner_name")
    if new_name != owner.name:
        owner.name = new_name
        _save()

    st.divider()

    # Pet selector
    st.markdown("**Active pet**")
    if owner.pets:
        pet_labels = [f"{p.name} ({p.species})" for p in owner.pets]
        idx = st.selectbox(
            "Select pet", range(len(owner.pets)),
            format_func=lambda i: pet_labels[i],
            index=min(st.session_state.active_pet_idx, len(owner.pets) - 1),
            label_visibility="collapsed",
        )
        st.session_state.active_pet_idx = idx
    else:
        st.info("No pets yet — add one in Pet Setup.")

    if st.button("+ Add new pet", use_container_width=True):
        st.session_state.show_add_pet = not st.session_state.show_add_pet

    if st.session_state.show_add_pet:
        with st.form("sidebar_add_pet_form", clear_on_submit=True):
            st.markdown("**New pet**")
            p_name    = st.text_input("Name *")
            p_species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
            p_breed   = st.text_input("Breed (optional)")
            p_age     = st.number_input("Age (years)", 0.0, 30.0, 1.0, step=0.5)
            p_weight  = st.number_input("Weight (kg)", 0.0, 100.0, 5.0, step=0.5)
            p_conds   = st.text_input("Conditions (comma-sep.)")
            if st.form_submit_button("Save pet", use_container_width=True):
                if not p_name.strip():
                    st.error("Name is required.")
                else:
                    conds = [c.strip() for c in p_conds.split(",") if c.strip()]
                    owner.add_pet(Pet(
                        name=p_name.strip(),
                        species=p_species,
                        breed=p_breed.strip(),
                        age_years=float(p_age),
                        weight_kg=float(p_weight),
                        medical_conditions=conds,
                    ))
                    st.session_state.active_pet_idx = len(owner.pets) - 1
                    st.session_state.show_add_pet = False
                    _save()
                    st.rerun()

    st.divider()
    st.caption(f"Today: {date.today().strftime('%A, %B %d')}")


# ── Main tabs ──────────────────────────────────────────────────────────────────

tab_plan, tab_tasks, tab_setup = st.tabs(["Today's Plan", "Manage Tasks", "Pet Setup"])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 – Today's Plan
# ════════════════════════════════════════════════════════════════════════════════

with tab_plan:
    pet = _active_pet()
    if pet is None:
        st.markdown(
            '<div class="empty-state"><h3>No pet set up yet</h3>'
            '<p>Head to <b>Pet Setup</b> to add your pet.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.subheader(f"Care plan for {pet.name} — {date.today().strftime('%A, %B %d')}")

        # ── Conflict warnings (Scheduler.detect_conflicts) ────────────────────
        pet_tasks = scheduler.filter_by_pet(pet.name)
        conflicts = scheduler.detect_conflicts(tasks=pet_tasks)
        for c in conflicts:
            st.warning(c)

        # ── Today's schedule (Scheduler.todays_schedule) ──────────────────────
        plan = [t for t in scheduler.todays_schedule(date.today())
                if t.pet_name == pet.name]

        col_h, col_btn = st.columns([4, 1])
        with col_btn:
            if st.button("Refresh plan", use_container_width=True):
                st.rerun()

        if not plan:
            # Check if there are simply no tasks due today vs. all done
            all_done = all(t.completed for t in pet_tasks)
            msg = ("Nothing due today — all tasks are caught up! 🎉"
                   if all_done else "No tasks scheduled for today.")
            st.markdown(
                f'<div class="empty-state"><h3>{msg}</h3></div>',
                unsafe_allow_html=True,
            )
        else:
            for task in plan:
                icon = {"Walk": "🦮", "Feeding": "🍖", "Medication": "💊",
                        "Enrichment": "🧩", "Grooming": "✂️"}.get(
                    next((w for w in ["Walk","Feeding","Medication","Enrichment","Grooming"]
                          if w.lower() in task.name.lower()), ""), "🐾")
                pbadge = _priority_badge(task.priority)
                fbadge = _badge(_freq_label(task.frequency), C_TEAL)

                card_col, btn_col = st.columns([5, 1])
                with card_col:
                    st.markdown(
                        f'<div class="task-card">'
                        f'  <div class="task-title">'
                        f'    <span class="time-chip">{task.time}</span>{icon} {task.name}'
                        f'  </div>'
                        f'  <div class="task-meta">{pbadge}{fbadge}'
                        f'    &nbsp;{task.duration_minutes} min'
                        f'  </div>'
                        f'  {f"<div class=task-meta>{task.notes}</div>" if task.notes else ""}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with btn_col:
                    if st.button("✓ Done", key=f"done_{task.id}", use_container_width=True):
                        next_task = scheduler.mark_task_complete(task)
                        _save()
                        if next_task:
                            st.success(
                                f"Done! '{task.name}' rescheduled → {next_task.due_date} at {next_task.time}."
                            )
                        st.rerun()

        # ── Completed tasks for today ─────────────────────────────────────────
        done_today = [t for t in pet_tasks if t.completed and t.due_date == date.today()]
        if done_today:
            with st.expander(f"✓ {len(done_today)} task(s) completed today"):
                for task in done_today:
                    st.markdown(
                        f'<div class="task-card done">'
                        f'  <div class="task-title">'
                        f'    <span class="time-chip">{task.time}</span>{task.name}'
                        f'  </div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 – Manage Tasks
# ════════════════════════════════════════════════════════════════════════════════

with tab_tasks:
    pet = _active_pet()
    if pet is None:
        st.info("Add a pet first in the **Pet Setup** tab.")
    else:
        st.subheader(f"Tasks for {pet.name}")

        # ── Add task form ─────────────────────────────────────────────────────
        with st.expander("＋ Add new task", expanded=False):
            with st.form("add_task_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    t_name     = st.text_input("Task name *")
                    t_time     = st.text_input("Scheduled time (HH:MM) *", value="08:00",
                                               help="24-hour format, e.g. 07:30 or 20:00")
                    t_duration = st.number_input("Duration (min)", 1, 240, 30)
                with c2:
                    t_priority = st.selectbox("Priority", PRIORITIES, index=1)
                    t_frequency = st.selectbox("Frequency", FREQUENCIES,
                                               format_func=_freq_label, index=1)
                    t_notes    = st.text_input("Notes (optional)")

                if st.form_submit_button("Add task", use_container_width=True):
                    if not t_name.strip():
                        st.error("Task name is required.")
                    elif len(t_time) != 5 or t_time[2] != ":":
                        st.error("Time must be in HH:MM format (e.g. 08:00).")
                    else:
                        pet.add_task(Task(
                            name=t_name.strip(),
                            time=t_time.strip(),
                            priority=t_priority,
                            frequency=t_frequency,
                            pet_name=pet.name,
                            duration_minutes=int(t_duration),
                            notes=t_notes.strip(),
                            due_date=date.today(),
                        ))
                        _save()
                        st.rerun()

        st.divider()

        # ── Task list ─────────────────────────────────────────────────────────
        if not pet.tasks:
            st.markdown(
                '<div class="empty-state"><h3>No tasks yet</h3>'
                '<p>Use the form above to add care tasks.</p></div>',
                unsafe_allow_html=True,
            )
        else:
            active_tasks   = [t for t in pet.tasks if not t.completed]
            completed_tasks = [t for t in pet.tasks if t.completed]

            for task in scheduler.sort_by_time(active_tasks):
                pbadge  = _priority_badge(task.priority)
                fbadge  = _badge(_freq_label(task.frequency), C_TEAL)
                card_c, done_c, del_c = st.columns([5, 1, 1])
                with card_c:
                    st.markdown(
                        f'<div class="task-card" style="margin-bottom:6px">'
                        f'  <div class="task-title">'
                        f'    <span class="time-chip">{task.time}</span>{task.name}'
                        f'  </div>'
                        f'  <div class="task-meta">{pbadge}{fbadge}'
                        f'    &nbsp;{task.duration_minutes} min'
                        f'    &nbsp;·&nbsp; due {task.due_date}'
                        f'  </div>'
                        f'  {f"<div class=task-meta>{task.notes}</div>" if task.notes else ""}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with done_c:
                    if st.button("✓ Done", key=f"tl_done_{task.id}", use_container_width=True):
                        next_task = scheduler.mark_task_complete(task)
                        _save()
                        if next_task:
                            st.success(f"Rescheduled → {next_task.due_date}")
                        st.rerun()
                with del_c:
                    if st.button("Remove", key=f"tl_del_{task.id}", use_container_width=True):
                        pet.tasks.remove(task)
                        _save()
                        st.rerun()

            if completed_tasks:
                with st.expander(f"Completed tasks ({len(completed_tasks)})"):
                    for task in completed_tasks:
                        st.markdown(
                            f'<div class="task-card done">'
                            f'  <div class="task-title">'
                            f'    <span class="time-chip">{task.time}</span>{task.name} ✓'
                            f'  </div>'
                            f'  <div class="task-meta">Completed on {task.due_date}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )


# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 – Pet Setup
# ════════════════════════════════════════════════════════════════════════════════

with tab_setup:
    st.subheader("Pet Setup")

    # ── Add pet form ──────────────────────────────────────────────────────────
    if st.session_state.show_add_pet or not owner.pets:
        with st.form("add_pet_form"):
            st.markdown("**Add a new pet**")
            c1, c2 = st.columns(2)
            with c1:
                p_name    = st.text_input("Pet name *")
                p_species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
                p_breed   = st.text_input("Breed (optional)")
            with c2:
                p_age    = st.number_input("Age (years)", 0.0, 30.0, 1.0, step=0.5)
                p_weight = st.number_input("Weight (kg)", 0.0, 100.0, 5.0, step=0.5)
                p_conds  = st.text_input("Medical conditions (comma-separated)")

            if st.form_submit_button("Save pet", use_container_width=True):
                if not p_name.strip():
                    st.error("Pet name is required.")
                else:
                    conds = [c.strip() for c in p_conds.split(",") if c.strip()]
                    owner.add_pet(Pet(
                        name=p_name.strip(),
                        species=p_species,
                        breed=p_breed.strip(),
                        age_years=float(p_age),
                        weight_kg=float(p_weight),
                        medical_conditions=conds,
                    ))
                    st.session_state.active_pet_idx = len(owner.pets) - 1
                    _save()
                    st.session_state.show_add_pet = False
                    st.rerun()

    # ── Existing pets ──────────────────────────────────────────────────────────
    if owner.pets:
        st.divider()
        st.markdown("**Your pets**")
        for i, p in enumerate(owner.pets):
            label = f"{p.name} · {p.species}{f' ({p.breed})' if p.breed else ''}"
            with st.expander(label):
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Age",    f"{p.age_years:.1f} yr")
                    st.metric("Weight", f"{p.weight_kg:.1f} kg")
                with c2:
                    st.metric("Tasks", len(p.tasks))
                    if p.medical_conditions:
                        st.markdown("**Conditions:** " + ", ".join(p.medical_conditions))
                    else:
                        st.caption("No medical conditions noted.")
                if st.button(f"Remove {p.name}", key=f"del_pet_{p.id}"):
                    owner.pets.pop(i)
                    st.session_state.active_pet_idx = max(0, i - 1)
                    _save()
                    st.rerun()
