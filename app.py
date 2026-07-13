from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

import streamlit as st

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str

    def __post_init__(self):
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"Invalid priority: {self.priority}")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be positive")


@dataclass
class Pet:
    name: str
    species: str


@dataclass
class Owner:
    name: str
    available_minutes: int
    day_start: str = "08:00"


@dataclass
class ScheduledItem:
    task: Task
    start_time: str
    end_time: str
    reason: str


@dataclass
class SkippedItem:
    task: Task
    reason: str


@dataclass
class SchedulePlan:
    scheduled: List[ScheduledItem] = field(default_factory=list)
    skipped: List[SkippedItem] = field(default_factory=list)

    @property
    def total_minutes_used(self) -> int:
        return sum(item.task.duration_minutes for item in self.scheduled)


class CareScheduler:
    def __init__(self, owner: Owner, tasks: List[Task]):
        self.owner = owner
        self.tasks = tasks

    def _sorted_tasks(self) -> List[Task]:
        return sorted(self.tasks, key=lambda t: (PRIORITY_RANK[t.priority], t.duration_minutes))

    def build_plan(self) -> SchedulePlan:
        plan = SchedulePlan()
        remaining = self.owner.available_minutes
        current_time = datetime.strptime(self.owner.day_start, "%H:%M")

        for task in self._sorted_tasks():
            if task.duration_minutes <= remaining:
                start = current_time
                end = current_time + timedelta(minutes=task.duration_minutes)
                reason = f"Placed because it's {task.priority}-priority and fits in the {remaining} minutes left."
                plan.scheduled.append(
                    ScheduledItem(task, start.strftime("%H:%M"), end.strftime("%H:%M"), reason)
                )
                current_time = end
                remaining -= task.duration_minutes
            else:
                reason = f"Skipped: only {remaining} minutes remained, but this task needs {task.duration_minutes}."
                plan.skipped.append(SkippedItem(task, reason))

        return plan


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

st.markdown(
    "Welcome to **PawPal+**. Add your pet's care tasks below, set a time budget for "
    "the day, and PawPal+ will build an ordered, explainable schedule for you."
)

st.divider()
st.subheader("Owner & Pet")

col_a, col_b, col_c = st.columns(3)
with col_a:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_b:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_c:
    species = st.selectbox("Species", ["dog", "cat", "other"])

col_d, col_e = st.columns(2)
with col_d:
    day_start = st.time_input("Day start time", value=datetime.strptime("08:00", "%H:%M").time())
with col_e:
    available_minutes = st.number_input("Available time today (minutes)", min_value=15, max_value=1440, value=90, step=5)

st.divider()
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

add_col, clear_col = st.columns(2)
with add_col:
    if st.button("➕ Add task", use_container_width=True):
        if task_title.strip():
            st.session_state.tasks.append(
                {"title": task_title.strip(), "duration_minutes": int(duration), "priority": priority}
            )
        else:
            st.warning("Give the task a title first.")
with clear_col:
    if st.button("🗑️ Clear all tasks", use_container_width=True):
        st.session_state.tasks = []

if st.session_state.tasks:
    st.write("Current tasks:")
    for i, t in enumerate(st.session_state.tasks):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        c1.write(t["title"])
        c2.write(f"{t['duration_minutes']} min")
        c3.write(t["priority"])
        if c4.button("✕", key=f"remove_{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()
st.subheader("Build Schedule")

if st.button("📅 Generate schedule", type="primary"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(owner_name, int(available_minutes), day_start.strftime("%H:%M"))
        pet = Pet(pet_name, species)
        tasks = [Task(**t) for t in st.session_state.tasks]

        plan = CareScheduler(owner, tasks).build_plan()

        st.success(f"Schedule built for **{pet.name}** the {pet.species} ({owner.name}'s day, starting {owner.day_start}).")

        st.markdown("#### ✅ Scheduled")
        if plan.scheduled:
            for item in plan.scheduled:
                st.markdown(f"**{item.start_time}–{item.end_time}** · {item.task.title} _( {item.task.priority} priority, {item.task.duration_minutes} min )_")
                st.caption(item.reason)
        else:
            st.write("Nothing scheduled.")

        if plan.skipped:
            st.markdown("#### ⏭️ Skipped")
            for item in plan.skipped:
                st.markdown(f"**{item.task.title}** _( {item.task.priority} priority, {item.task.duration_minutes} min )_")
                st.caption(item.reason)

        st.markdown(f"**Time used:** {plan.total_minutes_used} / {owner.available_minutes} minutes")
