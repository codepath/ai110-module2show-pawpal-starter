# PawPal+ — Final Class Diagram

```mermaid
classDiagram
    direction TB

    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
        +from_any(value) Priority
    }

    class TimeWindow {
        +time start
        +time end
        +duration_minutes() int
        +contains(t time) bool
    }

    class Task {
        +UUID id
        +str title
        +str description
        +int duration_minutes
        +Priority priority
        +str recurrence
        +bool completed
        +date next_due
        +time earliest_start
        +time latest_end
        +str notes
        +UUID required_pet_id
        +complete(today date)
        +reset()
        +is_recurring() bool
        +validate() bool
        +spawn_next_occurrence() Task
        +to_dict() dict
    }

    class Pet {
        +UUID id
        +str name
        +str species
        +str breed
        +float age_years
        +add_task(task Task)
        +remove_task(task_id UUID) bool
        +get_task(task_id UUID) Task
        +get_tasks() List
        +get_pending_tasks() List
        +get_completed_tasks() List
        +get_tasks_by_priority(p) List
        +get_recurring_tasks() List
        +complete_task(task_id, today) bool
        +reset_all_tasks()
        +to_dict() dict
    }

    class Owner {
        +UUID id
        +str name
        +str contact
        +List availability_windows
        +add_pet(pet Pet)
        +remove_pet(pet_id UUID) bool
        +get_pet(pet_id UUID) Pet
        +get_pets() List
        +all_tasks() List
        +all_pending_tasks() List
        +tasks_by_priority(p) List
        +start_new_day()
        +to_dict() dict
    }

    class TaskInstance {
        +UUID id
        +UUID task_id
        +str title
        +datetime start
        +datetime end
        +str status
        +str reason
        +UUID owner_id
        +UUID pet_id
        +duration() int
        +mark_completed()
        +to_dict() dict
    }

    class Schedule {
        +date date
        +UUID owner_id
        +List slots
        +List skipped_tasks
        +int total_minutes_scheduled
        +str generated_by
        +to_dict() dict
        +persist() str
        +summary() str
    }

    class Scheduler {
        +int max_daily_minutes
        +get_all_tasks(owner) List
        +get_pending_tasks(owner) List
        +sort_by_time(tasks) List
        +filter_tasks(owner, pet_name, completed) List
        +sorted_by_priority(tasks) List
        +group_by_pet(owner) dict
        +group_by_priority(owner) dict
        +generate_daily_plan(owner, date) Schedule
        +complete_task(owner, pet_id, task_id) bool
        +complete_slot(schedule, slot_id, owner) bool
        +detect_conflicts(schedule) List
        +start_new_day(owner)
        +summary(owner) str
    }

    Owner "1" *-- "0..*" Pet       : owns
    Owner "1" *-- "1..*" TimeWindow : availability_windows
    Pet   "1" *-- "0..*" Task       : tasks
    Task        -->       Priority   : uses

    Scheduler   ..>       Owner      : reads from
    Scheduler   ..>       Schedule   : produces

    Schedule "1" *-- "0..*" TaskInstance : slots
    Schedule     o--  "0..*" Task         : skipped_tasks
    TaskInstance ..>         Task         : references by id
```

## Key relationships added vs. initial design

| Relationship | Why it was added |
|---|---|
| `Task.required_pet_id → Pet.id` | Lets each task slot know which pet it belongs to |
| `Task.next_due` | Stores the next recurrence date after completion |
| `Owner.availability_windows: List[TimeWindow]` | Replaces single start/end; supports morning + evening blocks |
| `Schedule` wraps `List[TaskInstance]` | Keeps date, totals, and skipped tasks together with the slots |
| `Scheduler.sort_by_time / filter_tasks / detect_conflicts` | New algorithmic methods added in Phase 3 |
