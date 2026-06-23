"""
PawPal+ - Pet Care Scheduling Assistant
A Streamlit application for planning daily pet care tasks.
"""

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

# Page configuration
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")


def init_session_state():
    """Initialize all session state variables."""
    if "owner" not in st.session_state:
        st.session_state.owner = None

    if "pets" not in st.session_state:
        st.session_state.pets = []

    if "selected_pet_index" not in st.session_state:
        st.session_state.selected_pet_index = 0

    if "tasks" not in st.session_state:
        st.session_state.tasks = {}  # {pet_name: [Task objects]}

    if "current_plan" not in st.session_state:
        st.session_state.current_plan = None

    if "view" not in st.session_state:
        st.session_state.view = "setup"


def get_current_pet():
    """Get the currently selected pet."""
    if st.session_state.pets and st.session_state.selected_pet_index < len(
        st.session_state.pets
    ):
        return st.session_state.pets[st.session_state.selected_pet_index]
    return None


def get_tasks_for_pet(pet_name):
    """Get all tasks for a specific pet."""
    return st.session_state.tasks.get(pet_name, [])


def render_sidebar():
    """Render the sidebar with navigation and current status."""
    with st.sidebar:
        st.title("🐾 PawPal+")

        # Show owner info
        if st.session_state.owner:
            st.success(f"👤 {st.session_state.owner.get_name()}")
            st.caption(f"⏰ {st.session_state.owner.get_available_time()} min/day")
        else:
            st.info("👤 No owner profile")

        st.divider()

        # Navigation
        st.subheader("Navigation")

        if st.button("🏠 Setup", use_container_width=True):
            st.session_state.view = "setup"
            st.rerun()

        if st.button(
            "🐾 Pets", use_container_width=True, disabled=not st.session_state.owner
        ):
            st.session_state.view = "pets"
            st.rerun()

        if st.button(
            "📋 Tasks", use_container_width=True, disabled=not st.session_state.pets
        ):
            st.session_state.view = "tasks"
            st.rerun()

        if st.button(
            "📅 Schedule", use_container_width=True, disabled=not st.session_state.pets
        ):
            st.session_state.view = "schedule"
            st.rerun()

        st.divider()

        # Quick stats
        if st.session_state.owner:
            st.subheader("Quick Stats")
            st.metric("Pets", len(st.session_state.pets))

            total_tasks = sum(len(tasks) for tasks in st.session_state.tasks.values())
            st.metric("Total Tasks", total_tasks)

        st.divider()

        # Reset button
        if st.button("🔄 Reset All", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_setup_view():
    """Render the owner setup view."""
    st.header("🏠 Owner Setup")

    if st.session_state.owner:
        st.success(f"✅ Owner profile created for {st.session_state.owner.get_name()}")

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Name:** {st.session_state.owner.get_name()}")
        with col2:
            st.info(
                f"**Available Time:** {st.session_state.owner.get_available_time()} minutes/day"
            )

        if st.button("Edit Owner Profile"):
            st.session_state.owner = None
            st.rerun()

    else:
        st.markdown("""
        Welcome to **PawPal+**! Let's start by creating your owner profile.
        This helps us understand how much time you have available for pet care each day.
        """)

        with st.form("owner_form"):
            st.subheader("Create Your Profile")

            owner_name = st.text_input(
                "Your Name",
                placeholder="Enter your name",
                help="This is how we'll address you in the app",
            )

            available_time = st.slider(
                "Available Time (minutes per day)",
                min_value=30,
                max_value=480,
                value=120,
                step=15,
                help="How many minutes can you dedicate to pet care daily?",
            )

            col1, col2 = st.columns([1, 3])
            with col1:
                submitted = st.form_submit_button(
                    "Create Profile", type="primary", use_container_width=True
                )

            if submitted:
                if owner_name.strip():
                    st.session_state.owner = Owner(owner_name.strip(), available_time)
                    st.success(f"✅ Welcome, {owner_name}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Please enter your name")


def render_pets_view():
    """Render the pets management view."""
    st.header("🐾 Manage Pets")

    # Show existing pets
    if st.session_state.pets:
        st.subheader("Your Pets")

        cols = st.columns(min(len(st.session_state.pets), 3))
        for idx, pet in enumerate(st.session_state.pets):
            with cols[idx % 3]:
                with st.container(border=True):
                    species_emoji = {
                        "dog": "🐕",
                        "cat": "🐱",
                        "bird": "🐦",
                        "rabbit": "🐰",
                        "fish": "🐠",
                        "other": "🐾",
                    }
                    st.markdown(
                        f"### {species_emoji.get(pet.get_species(), '🐾')} {pet.get_name()}"
                    )
                    st.caption(
                        f"{pet.get_species().title()} • {pet.get_size().title()} • Age {pet.get_age()}"
                    )

                    if pet.get_special_needs():
                        with st.expander("Special Needs"):
                            for need in pet.get_special_needs():
                                st.write(f"• {need}")

                    task_count = len(get_tasks_for_pet(pet.get_name()))
                    st.metric("Tasks", task_count)

                    if st.button(f"Remove {pet.get_name()}", key=f"remove_pet_{idx}"):
                        st.session_state.pets.pop(idx)
                        if pet.get_name() in st.session_state.tasks:
                            del st.session_state.tasks[pet.get_name()]
                        if st.session_state.selected_pet_index >= len(
                            st.session_state.pets
                        ):
                            st.session_state.selected_pet_index = max(
                                0, len(st.session_state.pets) - 1
                            )
                        st.rerun()

        st.divider()

    # Add new pet form
    st.subheader("Add a New Pet")

    with st.form("add_pet_form"):
        col1, col2 = st.columns(2)

        with col1:
            pet_name = st.text_input("Pet Name", placeholder="e.g., Buddy, Whiskers")
            species = st.selectbox(
                "Species", ["dog", "cat", "bird", "rabbit", "fish", "other"]
            )

        with col2:
            age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
            size = st.selectbox("Size", ["small", "medium", "large"])

        special_needs = st.text_area(
            "Special Needs (optional)",
            placeholder="Enter any special care requirements, one per line",
            help="e.g., medication, dietary restrictions, allergies",
        )

        submitted = st.form_submit_button(
            "Add Pet", type="primary", use_container_width=True
        )

        if submitted:
            if pet_name.strip():
                # Create pet
                new_pet = Pet(pet_name.strip(), species, age, size)

                # Add special needs if provided
                if special_needs.strip():
                    for need in special_needs.strip().split("\n"):
                        if need.strip():
                            new_pet.add_special_need(need.strip())

                st.session_state.pets.append(new_pet)
                st.session_state.tasks[new_pet.get_name()] = []
                st.success(f"✅ Added {pet_name}!")
                st.rerun()
            else:
                st.error("Please enter a pet name")


def render_tasks_view():
    """Render the tasks management view."""
    st.header("📋 Manage Tasks")

    if not st.session_state.pets:
        st.warning("⚠️ Please add at least one pet first!")
        return

    # Pet selector
    pet_names = [pet.get_name() for pet in st.session_state.pets]
    selected_pet_name = st.selectbox(
        "Select Pet", pet_names, index=st.session_state.selected_pet_index
    )

    # Update selected pet index
    st.session_state.selected_pet_index = pet_names.index(selected_pet_name)
    current_pet = get_current_pet()

    if not current_pet:
        return

    st.divider()

    # Show existing tasks
    tasks = get_tasks_for_pet(current_pet.get_name())

    if tasks:
        st.subheader(f"Tasks for {current_pet.get_name()}")

        for idx, task in enumerate(tasks):
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])

                with col1:
                    st.markdown(f"**{task.get_name()}**")
                    if task.get_description():
                        st.caption(task.get_description())

                with col2:
                    st.write(f"🏷️ {task.get_task_type()}")

                with col3:
                    st.write(f"⏱️ {task.get_duration()} min")

                with col4:
                    priority_color = (
                        "🔴"
                        if task.get_priority() >= 8
                        else "🟡"
                        if task.get_priority() >= 5
                        else "🟢"
                    )
                    st.write(f"{priority_color} {task.get_priority()}")

                with col5:
                    if task.is_mandatory():
                        st.write("⭐")
                    if st.button("🗑️", key=f"delete_task_{idx}_{task.get_task_id()}"):
                        tasks.pop(idx)
                        st.rerun()

        st.divider()

    # Add new task form
    st.subheader(f"Add Task for {current_pet.get_name()}")

    with st.form("add_task_form"):
        col1, col2 = st.columns(2)

        with col1:
            task_name = st.text_input("Task Name", placeholder="e.g., Morning Walk")

            task_type = st.selectbox(
                "Task Type",
                [
                    "feeding",
                    "walk",
                    "meds",
                    "enrichment",
                    "grooming",
                    "training",
                    "playtime",
                ],
            )

            duration = st.number_input(
                "Duration (minutes)", min_value=5, max_value=180, value=30, step=5
            )

        with col2:
            priority = st.slider(
                "Priority",
                min_value=1,
                max_value=10,
                value=5,
                help="1 = Low priority, 10 = High priority",
            )

            is_mandatory = st.checkbox(
                "Mandatory Task", help="Mandatory tasks are always scheduled first"
            )

            description = st.text_area(
                "Description (optional)", placeholder="Add any additional details..."
            )

        submitted = st.form_submit_button(
            "Add Task", type="primary", use_container_width=True
        )

        if submitted:
            if task_name.strip():
                # Create task
                new_task = Task(task_name.strip(), task_type, duration, priority)
                new_task.set_mandatory(is_mandatory)
                if description.strip():
                    new_task.set_description(description.strip())

                # Add to current pet's tasks
                if current_pet.get_name() not in st.session_state.tasks:
                    st.session_state.tasks[current_pet.get_name()] = []

                st.session_state.tasks[current_pet.get_name()].append(new_task)
                st.success(f"✅ Added task: {task_name}")
                st.rerun()
            else:
                st.error("Please enter a task name")


def render_schedule_view():
    """Render the schedule generation and display view."""
    st.header("📅 Generate Schedule")

    if not st.session_state.pets:
        st.warning("⚠️ Please add at least one pet first!")
        return

    # Pet selector
    pet_names = [pet.get_name() for pet in st.session_state.pets]

    col1, col2 = st.columns([3, 1])

    with col1:
        selected_pet_name = st.selectbox(
            "Select Pet to Schedule",
            pet_names,
            index=st.session_state.selected_pet_index,
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        generate_button = st.button(
            "🚀 Generate Schedule", type="primary", use_container_width=True
        )

    # Update selected pet index
    st.session_state.selected_pet_index = pet_names.index(selected_pet_name)
    current_pet = get_current_pet()

    if not current_pet:
        return

    # Get tasks for selected pet
    tasks = get_tasks_for_pet(current_pet.get_name())

    if not tasks:
        st.info(
            f"ℹ️ No tasks added for {current_pet.get_name()} yet. Add some tasks first!"
        )
        return

    # Show task summary before generating
    st.divider()
    st.subheader("Task Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tasks", len(tasks))
    with col2:
        total_time = sum(task.get_duration() for task in tasks)
        st.metric("Total Time", f"{total_time} min")
    with col3:
        mandatory_count = sum(1 for task in tasks if task.is_mandatory())
        st.metric("Mandatory Tasks", mandatory_count)

    # Generate schedule when button is clicked
    if generate_button:
        with st.spinner("Generating optimal schedule..."):
            # Create scheduler
            scheduler = Scheduler(st.session_state.owner, current_pet)

            # Add all tasks
            for task in tasks:
                scheduler.add_task(task)

            # Generate plan
            plan = scheduler.generate_plan()
            st.session_state.current_plan = plan

    # Display the generated plan
    if st.session_state.current_plan:
        st.divider()
        st.subheader(f"📅 Today's Schedule for {current_pet.get_name()}")

        plan = st.session_state.current_plan
        scheduled_tasks = plan.get_scheduled_tasks()

        if scheduled_tasks:
            # Display scheduled tasks
            for scheduled_task in scheduled_tasks:
                task = scheduled_task.get_task()

                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 4, 2, 1])

                    with col1:
                        st.markdown(
                            f"**⏰ {scheduled_task.get_start_time()} - {scheduled_task.get_end_time()}**"
                        )

                    with col2:
                        st.markdown(f"**{task.get_name()}**")
                        if task.get_description():
                            st.caption(task.get_description())

                    with col3:
                        st.write(f"🏷️ {task.get_task_type()}")
                        st.caption(f"⏱️ {task.get_duration()} min")

                    with col4:
                        priority_color = (
                            "🔴"
                            if task.get_priority() >= 8
                            else "🟡"
                            if task.get_priority() >= 5
                            else "🟢"
                        )
                        st.write(f"{priority_color} P{task.get_priority()}")
                        if task.is_mandatory():
                            st.write("⭐ Required")

            # Summary metrics
            st.divider()
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Scheduled Tasks", len(scheduled_tasks))

            with col2:
                st.metric("Total Time", f"{plan.get_total_time()} min")

            with col3:
                time_remaining = (
                    st.session_state.owner.get_available_time() - plan.get_total_time()
                )
                st.metric("Time Remaining", f"{time_remaining} min")

            # Show excluded tasks if any
            excluded = plan.get_excluded_tasks()
            if excluded:
                st.warning(f"⚠️ {len(excluded)} task(s) couldn't fit in the schedule:")
                for task in excluded:
                    st.write(
                        f"• {task.get_name()} ({task.get_duration()} min, priority {task.get_priority()})"
                    )
            else:
                st.success("✅ All tasks scheduled successfully!")

            # Show explanation
            st.divider()
            with st.expander("📝 Scheduling Explanation", expanded=False):
                st.text(plan.get_explanation())

        else:
            st.info("No tasks were scheduled.")


def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()

    # Render sidebar
    render_sidebar()

    # Render main content based on current view
    if st.session_state.view == "setup":
        render_setup_view()

    elif st.session_state.view == "pets":
        render_pets_view()

    elif st.session_state.view == "tasks":
        render_tasks_view()

    elif st.session_state.view == "schedule":
        render_schedule_view()

    # Footer
    st.divider()
    st.caption("🐾 PawPal+ | Pet Care Scheduling Assistant | Built with Streamlit")


if __name__ == "__main__":
    main()
