"""
PawPal+ Streamlit UI.

Four tabs map one-to-one to the architecture:
  1. Schedule      — original Module-2 scheduler (Owner / Pet / Task / Scheduler)
  2. Ask PawPal    — RAG-grounded Q&A over the curated knowledge base
  3. Review Agent  — plan→act→check agent that audits today's schedule
  4. Reliability   — runs the offline evaluator and shows a pass/fail report
"""
from __future__ import annotations

import os
from datetime import date, timedelta

import streamlit as st

from ai_agent import ScheduleReviewAgent, answer_question
from evaluator import run_all
from knowledge_base import all_topics, corpus_size
from logger_setup import GuardrailError, get_logger
from pawpal_system import Owner, Pet, Scheduler, Task

log = get_logger("pawpal.app")

st.set_page_config(page_title="PawPal+ Applied AI", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+ — Applied AI System")
st.caption(
    "Pet-care scheduler, RAG knowledge assistant, review agent, and reliability dashboard."
)

# ── Session state bootstrap ────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None


# ── Sidebar: owner & pets ──────────────────────────────────────────────────
with st.sidebar:
    st.header("Owner Setup")
    owner_name = st.text_input("Owner name", value="Jordan")
    if st.button("Set / Reset Owner"):
        st.session_state.owner = Owner(name=owner_name)
        st.success(f"Owner set to {owner_name}")

    if st.session_state.owner:
        st.divider()
        st.header("Add a Pet")
        pet_name = st.text_input("Pet name", key="pet_name")
        species = st.selectbox("Species", ["dog", "cat", "bird", "other"], key="species")
        if st.button("Add Pet"):
            if pet_name.strip():
                st.session_state.owner.add_pet(Pet(name=pet_name.strip(), species=species))
                st.success(f"Added {pet_name} ({species})")
            else:
                st.error("Pet name cannot be empty.")

    st.divider()
    st.header("AI Key")
    key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))
    st.write(("🟢 ANTHROPIC_API_KEY detected" if key_present else
              "🔴 No ANTHROPIC_API_KEY — Q&A and agent tabs disabled"))

    st.divider()
    st.caption(f"Knowledge base: **{corpus_size()}** snippets")


# ── Guard: require owner ───────────────────────────────────────────────────
if st.session_state.owner is None:
    st.info("Set an owner name in the sidebar to get started.")
    st.stop()

owner: Owner = st.session_state.owner

tab_schedule, tab_ask, tab_agent, tab_rel = st.tabs(
    ["📅 Schedule", "💬 Ask PawPal (RAG)", "🧠 Review Agent", "🧪 Reliability"]
)


# ══════════════════════════════════════════════════════════════════════════
# Tab 1 — Schedule
# ══════════════════════════════════════════════════════════════════════════
with tab_schedule:
    st.subheader("Add a Task")
    if not owner.pets:
        st.warning("Add at least one pet (sidebar) before scheduling tasks.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            target_pet = st.selectbox("For pet", [p.name for p in owner.pets])
            task_desc = st.text_input("Task description", value="Morning walk")
            task_time = st.text_input("Time (HH:MM)", value="08:00")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
            due = st.date_input("Due date", value=date.today())

        if st.button("Add Task"):
            try:
                h, m = task_time.split(":")
                assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
            except Exception:
                st.error("Time must be in HH:MM format (e.g. 08:30).")
            else:
                new_task = Task(
                    description=task_desc.strip(),
                    time=task_time,
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                    due_date=due,
                )
                for pet in owner.pets:
                    if pet.name == target_pet:
                        pet.add_task(new_task)
                        st.success(f"Task '{task_desc}' added to {target_pet}.")
                        break

    st.divider()
    st.subheader("All Tasks")
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.info("No tasks yet.")
    else:
        rows = [
            {"Pet": p, "Description": t.description, "Time": t.time,
             "Duration": f"{t.duration_minutes}min", "Priority": t.priority,
             "Frequency": t.frequency, "Due": str(t.due_date), "Done": t.completed}
            for p, t in all_tasks
        ]
        st.table(rows)

    if all_tasks:
        st.subheader("Mark Task Complete")
        incomplete = [(p, t) for p, t in all_tasks if not t.completed]
        if incomplete:
            options = {f"{p} — {t.time} {t.description}": (p, t) for p, t in incomplete}
            chosen_label = st.selectbox("Select task to complete", list(options.keys()))
            if st.button("Mark Complete"):
                pet_name, task = options[chosen_label]
                scheduler = Scheduler(owner)
                scheduler.mark_task_complete(pet_name, task)
                if task.frequency in ("daily", "weekly"):
                    delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
                    st.success(f"Done! Next '{task.description}' scheduled for {task.due_date + delta}.")
                else:
                    st.success(f"'{task.description}' marked complete.")
        else:
            st.success("All tasks are complete!")

    st.divider()
    st.subheader("Generate Today's Schedule")
    if st.button("Build Schedule"):
        scheduler = Scheduler(owner)
        schedule = scheduler.get_todays_schedule()
        conflicts = scheduler.detect_conflicts()
        if not schedule:
            st.info("No pending tasks for today.")
        else:
            st.success(f"Schedule built — {len(schedule)} task(s) pending.")
            rows = [
                {"Time": t.time, "Pet": p, "Task": t.description,
                 "Duration": f"{t.duration_minutes}min",
                 "Priority": t.priority, "Frequency": t.frequency}
                for p, t in schedule
            ]
            st.table(rows)
            if conflicts:
                for c in conflicts:
                    st.warning(f"⚠ {c}")
            else:
                st.success("No scheduling conflicts detected.")


# ══════════════════════════════════════════════════════════════════════════
# Tab 2 — RAG Q&A
# ══════════════════════════════════════════════════════════════════════════
with tab_ask:
    st.subheader("Ask a Pet-Care Question")
    st.caption(
        "Answers are grounded in the curated knowledge base "
        f"({corpus_size()} snippets) and include inline citations [n]."
    )
    with st.expander("Topics available in the knowledge base"):
        st.write(", ".join(all_topics()))

    q = st.text_input(
        "Your question",
        placeholder="e.g. How often should I brush a long-haired cat?",
    )
    if st.button("Ask PawPal"):
        if not q.strip():
            st.warning("Enter a question first.")
        else:
            with st.spinner("Retrieving and thinking..."):
                try:
                    result = answer_question(q)
                except GuardrailError as ge:
                    st.error(f"Blocked by guardrail: {ge}")
                    result = None

            if result and result.ok:
                st.markdown("**Answer:**")
                st.info(result.text)
                conf_color = "🟢" if result.confidence >= 0.7 else ("🟡" if result.confidence >= 0.4 else "🔴")
                st.caption(f"{conf_color} Confidence: **{result.confidence:.2f}**")
                if result.sources:
                    st.caption(f"Sources used: {', '.join(result.sources)}")
                with st.expander("Agent trace"):
                    for s in result.steps:
                        st.write(f"• {s}")
            elif result:
                st.error(result.text)


# ══════════════════════════════════════════════════════════════════════════
# Tab 3 — Review Agent
# ══════════════════════════════════════════════════════════════════════════
with tab_agent:
    st.subheader("Schedule Review Agent")
    st.caption(
        "Runs a 3-step loop: plan (retrieve guidance) → act (LLM flags issues) → "
        "check (validate each issue against the real Scheduler state)."
    )
    if not owner.pets or not owner.get_all_tasks():
        st.info("Add at least one pet + one task on the Schedule tab first.")
    elif st.button("Run Review Agent"):
        scheduler = Scheduler(owner)
        agent = ScheduleReviewAgent(scheduler)
        with st.spinner("Agent running plan → act → check..."):
            result = agent.review()

        if result.ok:
            st.markdown("**Agent report:**")
            st.info(result.text)
            conf_color = "🟢" if result.confidence >= 0.7 else ("🟡" if result.confidence >= 0.4 else "🔴")
            st.caption(f"{conf_color} Confidence: **{result.confidence:.2f}**")
            with st.expander("Agent trace"):
                for s in result.steps:
                    st.write(f"• {s}")
            if result.sources:
                st.caption(f"Grounding snippets: {', '.join(result.sources)}")
        else:
            st.error(result.text)


# ══════════════════════════════════════════════════════════════════════════
# Tab 4 — Reliability dashboard
# ══════════════════════════════════════════════════════════════════════════
with tab_rel:
    st.subheader("Reliability Dashboard")
    st.caption(
        "Offline checks over retriever, guardrails, scheduler, and agent JSON "
        "parsing. Runs without network — safe for CI."
    )
    if st.button("Run all reliability checks"):
        with st.spinner("Running checks..."):
            report = run_all()
        colA, colB = st.columns(2)
        colA.metric("Passed", f"{report.passed} / {report.total}")
        colB.metric("Score", f"{report.score:.0%}")
        for r in report.results:
            if r.passed:
                st.success(f"✓ {r.name}" + (f" — {r.detail}" if r.detail else ""))
            else:
                st.error(f"✗ {r.name} — {r.detail}")
