import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Initialize session state for Owner and Pet
if "owner" not in st.session_state:
    owner_name = "Jordan"
    st.session_state.owner = Owner(name=owner_name, available_time=480)
else:
    owner_name = st.session_state.owner.name

# ========== OWNER SETTINGS SECTION ==========
st.markdown("## 👤 Owner Settings")

# Owner Info Section - Allow user to change their name (in expander)
with st.expander("👤 Owner's Information", expanded=False):
    st.caption("Update your details here.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_owner_name = st.text_input("Your name", value=st.session_state.owner.name, key="owner_name_input")
    
    with col2:
        if st.button("✅ Update Name", key="update_name_btn"):
            if new_owner_name.strip():
                st.session_state.owner.name = new_owner_name.strip()
                st.success(f"✅ Name updated to '{new_owner_name.strip()}'!")
                st.rerun()
            else:
                st.error("Name cannot be empty!")

# Owner Availability Section (in expander)
with st.expander("⏰ Owner Availability", expanded=False):
    st.caption("Set your total available time and how it's split between morning and afternoon.")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_time = st.number_input(
            "Total available time (minutes)", 
            min_value=1, 
            max_value=1440, 
            value=st.session_state.owner.available_time,
            key="availability_total"
        )

    with col2:
        morning_time = st.number_input(
            "Morning slot (minutes)",
            min_value=0,
            max_value=1440,
            value=st.session_state.owner.available_time_morning,
            key="availability_morning"
        )

    with col3:
        afternoon_time = st.number_input(
            "Afternoon slot (minutes)",
            min_value=0,
            max_value=1440,
            value=st.session_state.owner.available_time_afternoon,
            key="availability_afternoon"
        )

    # Validate and update availability
    if st.button("Update Availability", key="update_availability_btn"):
        try:
            # Check if time slots add up correctly
            if morning_time + afternoon_time != total_time:
                st.error(
                    f"⚠️ Time slot mismatch! Morning ({morning_time}) + Afternoon ({afternoon_time}) = {morning_time + afternoon_time}, "
                    f"but total is {total_time}. They must be equal."
                )
            else:
                st.session_state.owner.available_time = total_time
                st.session_state.owner.available_time_morning = morning_time
                st.session_state.owner.available_time_afternoon = afternoon_time
                
                # Show warnings if imbalanced
                if morning_time < 30 or afternoon_time < 30:
                    st.warning("⚠️ One of your time slots is very short (<30 min). You may struggle to fit tasks!")
                
                if total_time > 0:
                    morning_pct = (morning_time / total_time) * 100
                    afternoon_pct = (afternoon_time / total_time) * 100
                    if morning_pct > 70 or afternoon_pct > 70:
                        st.warning(f"⚠️ Your time is imbalanced: {morning_pct:.0f}% morning, {afternoon_pct:.0f}% afternoon")
                
                st.success("✅ Availability updated!")
        except ValueError as e:
            st.error(f"Invalid availability: {e}")

    # Display current availability summary
    st.info(
        f"📊 Current: {st.session_state.owner.available_time} min total | {st.session_state.owner.available_time_morning} min (morning) + {st.session_state.owner.available_time_afternoon} min (afternoon)"
    )

st.divider()

# ========== PETS & TASKS SECTION ==========
st.markdown("## 🐾 Pets & Tasks")

# initialize pets list from owner
if "current_pet" not in st.session_state:
    if st.session_state.owner.pets:
        st.session_state.current_pet = st.session_state.owner.pets[0]
    else:
        # Create a default pet for demo purposes
        default_pet = Pet(name="Mochi", pet_type="dog", age=3)
        st.session_state.owner.add_pet(default_pet)
        st.session_state.current_pet = default_pet

# Display owner name (read from session state)
st.write(f"**Owner**: {st.session_state.owner.name}")

st.markdown("### Manage Your Pets")

# Show all pets owned
if st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox(
        "Select a pet to manage",
        pet_names,
        index=pet_names.index(st.session_state.current_pet.name) if st.session_state.current_pet.name in pet_names else 0
    )
    # Update current pet
    for pet in st.session_state.owner.pets:
        if pet.name == selected_pet_name:
            st.session_state.current_pet = pet
            break

# Add new pet form
with st.expander("➕ Add a New Pet", expanded=False):
    st.caption("Fill in the details below to add a new pet.")

    col1, col2, col3 = st.columns(3)

    with col1:
        new_pet_name = st.text_input("Pet name", value="")
    with col2:
        new_pet_type = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        new_pet_age = st.number_input("Age (years)", min_value=0, max_value=50, value=1, step=1)

    if st.button("Add Pet"):
        if not new_pet_name.strip():
            st.error("Pet name cannot be empty!")
        else:
            try:
                # CREATE: Instance of Pet with UI input
                new_pet = Pet(name=new_pet_name, pet_type=new_pet_type, age=int(new_pet_age))
                # WIRE: Call Owner.add_pet() - business logic method
                st.session_state.owner.add_pet(new_pet)
                # UPDATE: Switch to the newly added pet
                st.session_state.current_pet = new_pet
                st.success(f"✅ Pet '{new_pet_name}' added successfully!")
                st.rerun()  # Refresh UI to show new pet in dropdown
            except ValueError as e:
                st.error(f"Cannot add pet: {e}")

# Remove pet form
with st.expander("🗑️ Remove a Pet", expanded=False):
    st.caption("Select a pet to remove from your collection.")
    
    if len(st.session_state.owner.pets) > 0:
        pet_names_remove = [pet.name for pet in st.session_state.owner.pets]
        pet_to_remove = st.selectbox("Select pet to remove:", pet_names_remove, key="remove_pet_select")
        
        if st.button("🗑️ Remove Pet", key="remove_pet_btn"):
            # Find and remove the pet
            for pet in st.session_state.owner.pets:
                if pet.name == pet_to_remove:
                    st.session_state.owner.remove_pet(pet.name)
                    
                    # If we removed the current pet, switch to another one
                    if st.session_state.current_pet.name == pet_to_remove:
                        if st.session_state.owner.pets:
                            st.session_state.current_pet = st.session_state.owner.pets[0]
                        else:
                            # Create a default pet if none remain
                            default_pet = Pet(name="Mochi", pet_type="dog", age=3)
                            st.session_state.owner.add_pet(default_pet)
                            st.session_state.current_pet = default_pet
                    
                    st.success(f"✅ Pet '{pet_to_remove}' removed successfully!")
                    st.rerun()
                    break
    else:
        st.info("No pets to remove.")

st.divider()

if st.session_state.current_pet is not None:
    st.markdown(f"### Tasks for {st.session_state.current_pet.name}")
    st.caption("Add tasks to your pet's care plan. These persist in the session.")

    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        prefered_time = st.selectbox("Preferred Time", ["Morning", "Afternoon", "Flexible"], index=2)
    with col5:
        frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"], index=0)

    if st.button("Add task"):
        # Convert priority to numeric (1-3, where 1 is highest priority)
        priority_map = {"high": 1, "medium": 2, "low": 3}
        prefered_time_lower = prefered_time.lower() if prefered_time != "Flexible" else None
        frequency_lower = frequency.lower()
        
        new_task = Task(
            task_name=task_title,
            duration=int(duration),
            priority=priority_map[priority],
            prefered_time=prefered_time_lower,
            frequency=frequency_lower
        )
        try:
            st.session_state.current_pet.add_task(new_task)
            st.session_state.tasks.append(
                {"title": task_title, "duration_minutes": int(duration), "priority": priority, "prefered_time": prefered_time, "frequency": frequency, "task_id": new_task.task_id}
            )
            st.success(f"Task '{task_title}' added for {st.session_state.current_pet.name}!")
        except ValueError as e:
            st.error(f"Error adding task: {e}")

    if st.session_state.current_pet.tasks:
        st.write(f"**{st.session_state.current_pet.name}'s tasks:**")
        task_data = [
            {
                "Task": t.task_name, 
                "Duration (min)": t.duration, 
                "Priority": ["High", "Medium", "Low"][t.priority-1],
                "Preferred Time": t.prefered_time.capitalize() if t.prefered_time else "Flexible",
                "Frequency": t.frequency.capitalize(),
                "Status": t.status.capitalize()
            }
            for t in st.session_state.current_pet.tasks
        ]
        st.table(task_data)
        st.info(f"Total duration: {st.session_state.current_pet.get_total_duration()} minutes")
    else:
        st.info(f"No tasks yet for {st.session_state.current_pet.name}. Add one above.")
else:
    st.info("ℹ️ Add a pet first to start managing tasks.")

if st.session_state.current_pet is not None:
    # Edit Task Section
    with st.expander("✏️ Edit Task", expanded=False):
        st.caption("Select a task to edit, modify the information, and confirm the update.")

        if "update_success" not in st.session_state:
            st.session_state.update_success = False

        if st.session_state.current_pet.tasks:
            task_options = [f"{i+1}. {t.task_name} ({t.duration} min, {t.frequency})" for i, t in enumerate(st.session_state.current_pet.tasks)]
            selected_task_idx = st.selectbox("Select a task to edit:", range(len(st.session_state.current_pet.tasks)), format_func=lambda i: task_options[i], key="edit_task_select")
            
            # Show edit form only after selection
            if selected_task_idx is not None:
                selected_task = st.session_state.current_pet.tasks[selected_task_idx]
                
                # Show current task info in a nice format
                priority_label = ["🔴 High", "🟡 Medium", "🟢 Low"][selected_task.priority - 1]
                pref_time_label = selected_task.prefered_time.capitalize() if selected_task.prefered_time else "Flexible"
                
                st.info(
                    f"**Editing Task:** {selected_task.task_name}\n\n"
                    f"⏱️ Duration: {selected_task.duration} min | "
                    f"{priority_label} | "
                    f"🕐 {pref_time_label} | "
                    f"📅 {selected_task.frequency.capitalize()}"
                )
                
                st.markdown("**Modify the fields below:**")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    edit_task_title = st.text_input("Task name", value=selected_task.task_name, key=f"edit_name_{selected_task_idx}")
                with col2:
                    edit_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=selected_task.duration, key=f"edit_duration_{selected_task_idx}")
                with col3:
                    priority_map_reverse = {1: "high", 2: "medium", 3: "low"}
                    current_priority = priority_map_reverse[selected_task.priority]
                    current_priority_idx = ["low", "medium", "high"].index(current_priority)
                    edit_priority = st.selectbox("Priority", ["low", "medium", "high"], index=current_priority_idx, key=f"edit_priority_{selected_task_idx}")
                with col4:
                    # Get current preferred time as capitalied version or "Flexible"
                    current_pref_time = selected_task.prefered_time.capitalize() if selected_task.prefered_time else "Flexible"
                    pref_time_options = ["Morning", "Afternoon", "Flexible"]
                    current_pref_idx = pref_time_options.index(current_pref_time)
                    edit_prefered_time = st.selectbox("Preferred Time", pref_time_options, index=current_pref_idx, key=f"edit_pref_time_{selected_task_idx}")
                with col5:
                    freq_map_reverse = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}
                    current_freq = freq_map_reverse[selected_task.frequency]
                    current_freq_idx = ["Daily", "Weekly", "Monthly"].index(current_freq)
                    edit_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"], index=current_freq_idx, key=f"edit_frequency_{selected_task_idx}")
                
                # Validation
                is_valid = True
                validation_messages = []
                
                if not edit_task_title.strip():
                    is_valid = False
                    validation_messages.append("❌ Task name cannot be empty")
                
                if edit_duration <= 0 or edit_duration > 480:
                    is_valid = False
                    validation_messages.append("❌ Duration must be between 1-480 minutes")
                
                # Display validation messages
                if validation_messages:
                    for msg in validation_messages:
                        st.warning(msg)
                
                # Update button (only enabled if valid)
                if st.button("✅ Confirm Update Task", disabled=not is_valid, key=f"confirm_update_btn_{selected_task_idx}"):
                    try:
                        priority_map = {"high": 1, "medium": 2, "low": 3}
                        prefered_time_lower = edit_prefered_time.lower() if edit_prefered_time != "Flexible" else None
                        frequency_lower = edit_frequency.lower()
                        
                        success = selected_task.update(
                            name=edit_task_title,
                            duration=int(edit_duration),
                            priority=priority_map[edit_priority],
                            prefered_time=prefered_time_lower,
                            frequency=frequency_lower
                        )
                        
                        if success:
                            st.balloons()
                            st.success(f"🎉 ¡Task '{edit_task_title}' actualizado exitosamente! 🎉", icon="✨")
                            st.info("✅ Los cambios han sido guardados. Task actualizado correctamente.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update task. Check your inputs.")
                            
                    except Exception as e:
                        st.error(f"❌ Error updating task: {e}")
        else:
            st.info("No tasks to edit. Add some tasks first!")

    # Update Task Status Section
    with st.expander("📊 Update Task Status", expanded=False):
        st.caption("Change the status of a task (Pending → In-Progress → Completed). When completed, recurring tasks auto-create the next occurrence.")

        if st.session_state.current_pet.tasks:
            status_task_options = [f"{i+1}. {t.task_name} ({t.status.capitalize()})" for i, t in enumerate(st.session_state.current_pet.tasks)]
            status_task_idx = st.selectbox("Select a task to update status:", range(len(st.session_state.current_pet.tasks)), format_func=lambda i: status_task_options[i], key="status_task_select")
            
            if status_task_idx is not None:
                status_task = st.session_state.current_pet.tasks[status_task_idx]
                
                st.info(f"**Task:** {status_task.task_name} | **Current Status:** {status_task.status.capitalize()}")
                
                new_status = st.selectbox(
                    "New Status",
                    ["pending", "in-progress", "completed"],
                    index=["pending", "in-progress", "completed"].index(status_task.status),
                    format_func=lambda s: s.capitalize(),
                    key=f"new_status_{status_task_idx}"
                )
                
                if st.button("✅ Update Status", key=f"update_status_btn_{status_task_idx}"):
                    try:
                        next_task = st.session_state.current_pet.update_task_status(status_task.task_id, new_status)
                        
                        if new_status == "completed" and next_task:
                            st.balloons()
                            st.success(f"✅ Task marked as completed! Next occurrence created automatically.", icon="✨")
                            st.info(f"📅 New task '{next_task.task_name}' scheduled for {next_task.due_date.strftime('%Y-%m-%d')}")
                        else:
                            st.success(f"✅ Task status updated to '{new_status.capitalize()}'!")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating status: {e}")
        else:
            st.info("No tasks to update. Add some tasks first!")

    st.divider()

    # ========== TASK FILTERING SECTION ==========
    st.markdown("## 🔍 Filter & Analyze Tasks")

    if st.session_state.current_pet.tasks:
        scheduler = Scheduler(st.session_state.owner, st.session_state.current_pet)
        
        with st.expander("📊 Filter by Status", expanded=False):
            st.caption("View tasks grouped by their current status")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🟡 Pending Tasks", key="pending_btn"):
                    pending = scheduler.filter_by_status("pending")
                    if pending:
                        st.success(f"Found {len(pending)} pending task(s)")
                        pending_data = [
                            {
                                "Task": t.task_name,
                                "Duration (min)": t.duration,
                                "Priority": ["🔴 High", "🟡 Medium", "🟢 Low"][t.priority-1],
                                "Frequency": t.frequency.capitalize()
                            }
                            for t in pending
                        ]
                        st.table(pending_data)
                    else:
                        st.info("No pending tasks!")
            
            with col2:
                if st.button("🔵 In-Progress Tasks", key="inprogress_btn"):
                    inprogress = scheduler.filter_by_status("in-progress")
                    if inprogress:
                        st.success(f"Found {len(inprogress)} in-progress task(s)")
                        inprogress_data = [
                            {
                                "Task": t.task_name,
                                "Duration (min)": t.duration,
                                "Priority": ["🔴 High", "🟡 Medium", "🟢 Low"][t.priority-1],
                                "Frequency": t.frequency.capitalize()
                            }
                            for t in inprogress
                        ]
                        st.table(inprogress_data)
                    else:
                        st.info("No in-progress tasks!")
            
            with col3:
                if st.button("✅ Completed Tasks", key="completed_btn"):
                    completed = scheduler.filter_by_status("completed")
                    if completed:
                        st.success(f"Found {len(completed)} completed task(s)")
                        completed_data = [
                            {
                                "Task": t.task_name,
                                "Duration (min)": t.duration,
                                "Priority": ["🔴 High", "🟡 Medium", "🟢 Low"][t.priority-1],
                                "Frequency": t.frequency.capitalize()
                            }
                            for t in completed
                        ]
                        st.table(completed_data)
                    else:
                        st.info("No completed tasks!")
        
        with st.expander("⏰ Filter by Time Slot", expanded=False):
            st.caption("View tasks organized by preferred time of day")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🌅 Morning Tasks", key="morning_btn"):
                    morning = scheduler.filter_by_time_slot("morning")
                    if morning:
                        total_duration = sum(t.duration for t in morning)
                        st.success(f"Found {len(morning)} morning task(s) - Total: {total_duration} min")
                        if total_duration > st.session_state.owner.available_time_morning:
                            st.warning(f"⚠️ Exceeds morning availability ({st.session_state.owner.available_time_morning} min)")
                        morning_data = [
                            {
                                "Task": t.task_name,
                                "Duration (min)": t.duration,
                                "Priority": ["🔴 High", "🟡 Medium", "🟢 Low"][t.priority-1]
                            }
                            for t in morning
                        ]
                        st.table(morning_data)
                    else:
                        st.info("No morning tasks!")
            
            with col2:
                if st.button("🌤️ Afternoon Tasks", key="afternoon_btn"):
                    afternoon = scheduler.filter_by_time_slot("afternoon")
                    if afternoon:
                        total_duration = sum(t.duration for t in afternoon)
                        st.success(f"Found {len(afternoon)} afternoon task(s) - Total: {total_duration} min")
                        if total_duration > st.session_state.owner.available_time_afternoon:
                            st.warning(f"⚠️ Exceeds afternoon availability ({st.session_state.owner.available_time_afternoon} min)")
                        afternoon_data = [
                            {
                                "Task": t.task_name,
                                "Duration (min)": t.duration,
                                "Priority": ["🔴 High", "🟡 Medium", "🟢 Low"][t.priority-1]
                            }
                            for t in afternoon
                        ]
                        st.table(afternoon_data)
                    else:
                        st.info("No afternoon tasks!")
            
            with col3:
                if st.button("🔄 Flexible Tasks", key="flexible_btn"):
                    flexible = scheduler.filter_by_time_slot("flexible")
                    if flexible:
                        st.success(f"Found {len(flexible)} flexible task(s)")
                        flexible_data = [
                            {
                                "Task": t.task_name,
                                "Duration (min)": t.duration,
                                "Priority": ["🔴 High", "🟡 Medium", "🟢 Low"][t.priority-1]
                            }
                            for t in flexible
                        ]
                        st.table(flexible_data)
                    else:
                        st.info("No flexible tasks!")
    else:
        st.info("ℹ️ Add tasks to your pet to see filtering options.")

    st.divider()

    st.subheader("Build Schedule")
    st.caption("Generate a daily schedule for your pet based on priorities and constraints.")

    # Show current session state information
    with st.expander("📊 Session State Information", expanded=False):
        st.markdown("**Session state** persists data while you navigate the app. Think of it as a persistent dictionary:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Owner:** {st.session_state.owner.name}")
            st.markdown(f"**Available time:** {st.session_state.owner.available_time} min")
            st.markdown(f"  - Morning: {st.session_state.owner.available_time_morning} min")
            st.markdown(f"  - Afternoon: {st.session_state.owner.available_time_afternoon} min")
        with col2:
            st.markdown(f"**Current Pet:** {st.session_state.current_pet.name} ({st.session_state.current_pet.pet_type})")
            st.markdown(f"**Pet tasks:** {len(st.session_state.current_pet.tasks)}")
        st.markdown(f"**Total pets owned:** {len(st.session_state.owner.pets)}")

    if st.button("Generate schedule"):
        try:
            # Validate that pet has tasks
            if not st.session_state.current_pet.tasks:
                st.error("❌ Cannot generate schedule: No tasks assigned to this pet. Add some tasks first!")
            else:
                # Create scheduler and generate plan
                scheduler = Scheduler(st.session_state.owner, st.session_state.current_pet)
                plan = scheduler.generate_plan()
                
                # Get explanation
                explanation = scheduler.explain_plan()
                
                # Display results
                st.success("✅ Schedule generated successfully!")
                st.divider()
                
                # Display explanation in an expander
                with st.expander("📋 Schedule Explanation (click to expand)", expanded=True):
                    st.text(explanation)
                
                # Display plan summary in table format if tasks were scheduled
                if plan:
                    st.markdown("### 📅 Scheduled Tasks Summary")
                    plan_data = [
                        {
                            "Task": t.task_name,
                            "Duration (min)": t.duration,
                            "Priority": ["🔴 High", "🟡 Medium", "🟢 Low"][t.priority-1],
                            "Preferred Time": t.prefered_time.capitalize() if t.prefered_time else "Flexible",
                            "Frequency": t.frequency.capitalize()
                        }
                        for t in plan
                    ]
                    st.table(plan_data)
                else:
                    st.warning("⚠️ No tasks could be scheduled. Check conflicts above.")
                
                # Save generated schedule to session state
                st.session_state.generated_schedule = {
                    "plan": plan,
                    "explanation": explanation,
                    "conflicts": scheduler.detect_conflicts()
                }
                
        except ValueError as e:
            st.error(f"❌ Error generating schedule: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.info("Make sure all your tasks have valid durations, priorities, and preferred times.")
