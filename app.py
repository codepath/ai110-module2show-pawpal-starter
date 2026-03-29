import streamlit as st
from pathlib import Path
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", layout="centered")

DATA_FILE = Path(__file__).with_name("data.json")

st.title("PawPal+")

st.markdown(
    """
Welcome to PawPal+. This app helps you plan your pet's daily care.

The logic here is built on some real scheduling algorithms - we detect conflicts,
rank tasks by priority, and respect your time constraints. Nice, right?
"""
)

with st.expander("How This Works", expanded=False):
    st.markdown(
        """
**PawPal+** helps you organize pet care. You tell it:
- Your pets and their tasks
- How much time you have available
- Your preferences

Then it builds a smart schedule that respects your constraints and minimizes conflicts.

The scheduling algorithm handles a lot of the fuzzy stuff - what if two tasks overlap? 
What if you don't have time for everything? How do we rank by importance?
"""
    )

st.divider()

# Create or load a persistent owner object in the session before rendering inputs
if "owner" not in st.session_state:
    if DATA_FILE.exists():
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
        except (ValueError, OSError):
            st.session_state.owner = Owner(name="Ben")
    else:
        st.session_state.owner = Owner(name="Ben")

# Start by setting up who owns what - we need owner and pet info
# before we can create tasks
st.subheader("Your Pet Family")
col1, col2 = st.columns(2)

owner = st.session_state.owner


def priority_badge(priority: str) -> str:
    """Return a visual badge for task priority."""
    normalized = priority.strip().lower()
    if normalized == "high":
        return "🔴 High"
    if normalized == "medium":
        return "🟡 Medium"
    return "🟢 Low"


def status_badge(is_completed: bool) -> str:
    """Return a visual status indicator."""
    return "✅ Completed" if is_completed else "🔵 Pending"


def task_type_badge(task: Task) -> str:
    """Return an emoji label for task type using category/title hints."""
    category = task.category.strip().lower()
    title = task.title.strip().lower()
    combined = f"{category} {title}"

    if any(token in combined for token in ["med", "medicine", "pill"]):
        return "💊 Medication"
    if any(token in combined for token in ["walk", "exercise", "run"]):
        return "🐾 Exercise"
    if any(token in combined for token in ["food", "feed", "meal"]):
        return "🍽️ Feeding"
    if any(token in combined for token in ["groom", "bath", "brush"]):
        return "🧼 Grooming"
    if any(token in combined for token in ["play", "toy", "enrich"]):
        return "🎾 Enrichment"
    if any(token in combined for token in ["train", "practice"]):
        return "🎯 Training"
    return "📌 General"

with col1:
    owner_name = st.text_input("Your name", value=owner.name)
with col2:
    species = st.selectbox("I have a", ["dog", "cat", "other"])

if owner.name != owner_name:
    owner.name = owner_name
    owner.save_to_json(DATA_FILE)

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 1

# Pet management - add/remove pets
col1, col2 = st.columns([2, 1])
with col1:
    pet_name = st.text_input("Pet name", value="Jack")
with col2:
    if st.button("Add pet"):
        try:
            owner.add_pet(Pet(name=pet_name, species=species))
            owner.save_to_json(DATA_FILE)
            st.success(f"Added pet: {pet_name}")
        except ValueError as error:
            st.info(str(error))

pets = owner.get_pets()
pet_names = [pet.name for pet in pets]

if pets:
    st.write("Your pets:")
    st.table([{"name": pet.name, "species": pet.species} for pet in pets])
else:
    st.info("No pets yet. Add one to get started.")

with st.expander("Your Schedule & Preferences", expanded=True):
    st.caption("Tell us about your available time and preferences. This helps us build a realistic schedule.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # How much actual time can you spend on pet care today?
        available_time = st.slider(
            "Available time per day (minutes)",
            min_value=5,
            max_value=480,
            value=owner.available_minutes_per_day,
            step=5,
        )
        owner.update_available_time(available_time)
        owner.save_to_json(DATA_FILE)
    
    with col2:
        # What's too many tasks? When do scheduled tasks start to feel overwhelming?
        max_tasks = st.slider(
            "Max tasks per day (feeling overwhelmed after... tasks?)",
            min_value=1,
            max_value=20,
            value=owner.max_tasks_per_day,
            step=1,
        )
        owner.max_tasks_per_day = max_tasks
        owner.save_to_json(DATA_FILE)
    
    # When are you most likely to have time?
    col1, col2 = st.columns(2)
    with col1:
        preferred_time = st.selectbox(
            "When do you usually have time?",
            ["morning", "afternoon", "evening", "anytime"],
            index=0 if owner.preferred_schedule == "morning" else 3,
        )
        owner.preferred_schedule = preferred_time
        owner.save_to_json(DATA_FILE)
    
    with col2:
        st.markdown("**What types of tasks matter most?**")
        pref_input = st.text_input("Your preferences (comma-separated)", value=", ".join(owner.task_preferences))
        if pref_input:
            prefs = [p.strip() for p in pref_input.split(",")]
            owner.set_preferences(prefs)
            owner.save_to_json(DATA_FILE)
    
    # Summary of what we know about the owner
    st.markdown("**Current settings:**")
    st.json({
        "Available Time": f"{owner.available_minutes_per_day} min/day",
        "Max Tasks": owner.max_tasks_per_day,
        "Preferred Schedule": owner.preferred_schedule,
        "Task Preferences": owner.task_preferences if owner.task_preferences else "None",
        "Pets": len(owner.get_pets()),
        "Total Tasks": len(owner.get_all_tasks()),
    })

st.markdown("### Add Tasks")
st.caption("Create tasks for your pet(s). The scheduler will figure out when to fit them in.")

# Select which pet gets this task
selected_pet_name = st.selectbox("Who is this task for?", pet_names, disabled=not pet_names)

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("What needs to happen?", value="Morning walk")
with col2:
    duration = st.number_input("How long? (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("How important?", ["low", "medium", "high"], index=2)
with col4:
    task_time = st.text_input("Time? (HH:MM)", value="", placeholder="e.g., 09:30")

# Advanced options - frequency and other attributes
with st.expander("More options"):
    col1, col2, col3 = st.columns(3)
    with col1:
        frequency = st.selectbox("How often?", ["once", "daily", "weekly"], index=0)
    with col2:
        is_required = st.checkbox("Must-do task? (don't skip this)", value=False)
    with col3:
        category = st.text_input("Category", value="general")

if st.button("Add task", disabled=not pet_names):
    pet = owner.get_pet(selected_pet_name)
    if pet is None:
        st.error("Hmm, couldn't find that pet.")
    else:
        # Generate a unique ID for this task
        task_id = f"task-{st.session_state.task_counter}"
        st.session_state.task_counter += 1
        try:
            pet.add_task(
                Task(
                    task_id=task_id,
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                    time=task_time if task_time else "",
                    frequency=frequency,
                    is_required=is_required,
                    category=category,
                )
            )
            owner.save_to_json(DATA_FILE)
            st.success(f"Added '{task_title}' for {pet.name}")
        except ValueError as error:
            st.error(f"Error: {str(error)}")

all_tasks = []
for pet in owner.get_pets():
    for task in pet.get_tasks():
        all_tasks.append(
            {
                "Pet": pet.name,
                "Task": task.title,
                "Type": task_type_badge(task),
                "Duration": f"{task.duration_minutes} min",
                "Priority": priority_badge(task.priority),
                "Status": status_badge(task.is_completed),
                "Time": task.time if task.time else "Anytime",
                "Frequency": task.frequency,
                "Required": "Yes" if task.is_required else "No",
                "Category": task.category,
            }
        )

if all_tasks:
    st.write("Current tasks:")
    st.table(all_tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# Before we schedule, let's give users a chance to explore and organize their tasks
st.subheader("View Your Tasks")
st.caption("Organize your tasks by time or filter to see what's coming up.")

if owner.get_all_tasks():
    tab1, tab2 = st.tabs(["By Time", "By Pet/Status"])
    
    # Create a scheduler instance just for sorting/filtering
    scheduler_preview = Scheduler(owner)
    
    with tab1:
        st.markdown("#### Tasks Sorted by Time")
        st.caption("Tasks ordered chronologically (HH:MM). Unscheduled tasks appear at the end.")
        
        sorted_by_time = scheduler_preview.sort_by_time()
        
        if sorted_by_time:
            time_display = []
            for task in sorted_by_time:
                pet_name = scheduler_preview.task_pet_lookup.get(task.task_id, "Unknown")
                time_str = task.time if task.time else "(no time set)"
                time_display.append({
                    "Time": time_str,
                    "Pet": pet_name,
                    "Task": task.title,
                    "Type": task_type_badge(task),
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": priority_badge(task.priority),
                    "Status": status_badge(task.is_completed),
                })
            st.dataframe(time_display, use_container_width=True, hide_index=True)
        else:
            st.info("No tasks yet.")
    
    with tab2:
        st.markdown("#### Filter Tasks")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Let users focus on one pet at a time
            filter_pet = st.selectbox("Show tasks for", ["All pets"] + [pet.name for pet in owner.get_pets()])
            pet_to_filter = None if filter_pet == "All pets" else filter_pet
        
        with col2:
            # It's helpful to see pending vs completed
            filter_status = st.selectbox("Status", ["all", "pending", "completed"])
        
        scheduler_preview.refresh_inputs()
        filtered_tasks = scheduler_preview.filter_by(pet_name=pet_to_filter, status=filter_status)
        
        if filtered_tasks:
            filter_display = []
            for task in filtered_tasks:
                pet_name = scheduler_preview.task_pet_lookup.get(task.task_id, "Unknown")
                status = "Completed" if task.is_completed else "Pending"
                filter_display.append({
                    "Pet": pet_name,
                    "Task": task.title,
                    "Type": task_type_badge(task),
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": priority_badge(task.priority),
                    "Status": status_badge(task.is_completed),
                })
            st.dataframe(filter_display, use_container_width=True, hide_index=True)
        else:
            st.info(f"No {filter_status} tasks found.")

st.divider()

if st.button("Generate schedule", type="primary", use_container_width=True):
    if not owner.get_pets():
        st.warning("Add at least one pet first.")
    elif not owner.get_all_tasks():
        st.warning("Add some tasks before making a schedule.")
    else:
        # Run the scheduling algorithm
        scheduler = Scheduler(owner)
        scheduled_tasks = scheduler.generate_schedule()
        
        # Check for conflicts - if tasks overlap, we need to warn the user
        all_owner_tasks = owner.get_all_tasks()
        conflicts = scheduler.detect_conflicts(all_owner_tasks)
        conflict_warnings = scheduler.get_conflict_warnings(all_owner_tasks)
        
        if conflict_warnings:
            st.warning("Scheduling Conflicts Detected")
            st.markdown("""
Some of your tasks overlap in time - they can't both happen. 
The scheduler resolved these conflicts by prioritizing important tasks and moving others around.
""")
            for i, warning in enumerate(conflict_warnings, 1):
                st.markdown(f"**{i}.** {warning}")
            st.markdown("---")
        
        # Show the generated schedule
        if scheduled_tasks:
            st.success(f"Schedule ready ({len(scheduled_tasks)} task(s))")
            
            st.markdown("### Your Daily Schedule")
            
            # Sort by time for a natural flow
            sorted_tasks = scheduler.sort_by_time(scheduled_tasks)
            
            schedule_display = []
            for task in sorted_tasks:
                pet_name = scheduler.task_pet_lookup.get(task.task_id, "Unknown")
                time_display = task.time if task.time else "(anytime)"
                selection_reason = scheduler.selection_reasons.get(task.task_id, "Selected")
                
                schedule_display.append({
                    "Time": time_display,
                    "Pet": pet_name,
                    "Task": task.title,
                    "Type": task_type_badge(task),
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": priority_badge(task.priority),
                    "Status": "✅ Scheduled",
                    "Why": selection_reason,
                })
            
            st.dataframe(
                schedule_display,
                use_container_width=True,
                hide_index=True,
            )
            
            # Summary metrics - give users a quick sense of the schedule
            col1, col2, col3 = st.columns(3)
            with col1:
                total_time = sum(task.duration_minutes for task in scheduled_tasks)
                remaining = owner.available_minutes_per_day - total_time
                st.metric("Time Used", f"{total_time} min", f"{remaining} min free")
            with col2:
                high_priority_count = sum(1 for task in scheduled_tasks if task.is_high_priority())
                st.metric("High Priority", high_priority_count)
            with col3:
                st.metric("Total Tasks", len(scheduled_tasks))
        else:
            st.info("No tasks could fit into today's schedule with your constraints.")
        
        # Show tasks that didn't make the cut
        if scheduler.unscheduled_tasks:
            st.markdown("### Couldn't Schedule")
            st.caption("These tasks didn't fit. Check your available time or priorities.")
            
            unscheduled_display = []
            for task in scheduler.unscheduled_tasks:
                pet_name = scheduler.task_pet_lookup.get(task.task_id, "Unknown")
                reason = scheduler.selection_reasons.get(task.task_id, "Not scheduled")
                
                unscheduled_display.append({
                    "Pet": pet_name,
                    "Task": task.title,
                    "Type": task_type_badge(task),
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": priority_badge(task.priority),
                    "Status": "⛔ Skipped",
                    "Why Not": reason,
                })
            
            st.dataframe(
                unscheduled_display,
                use_container_width=True,
                hide_index=True,
            )
        
        # Let users see the logic behind scheduling decisions
        st.markdown("### How We Built This Schedule")
        with st.expander("View the scheduling reasoning"):
            st.text(scheduler.explain_schedule())
            st.markdown("Structured schedule table")
            st.code(scheduler.explain_schedule_table(), language="text")
        
        # Show the constraints that shaped the schedule
        st.markdown("### Your Constraints (Applied)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Available", f"{owner.available_minutes_per_day} min/day")
        with col2:
            st.metric("Max Tasks", f"{owner.max_tasks_per_day}/day")
        with col3:
            st.metric("Preferred", owner.preferred_schedule)
