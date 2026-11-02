classDiagram
    %% Matches the skeleton in Pawpal_system.py.

    class Owner {
        +str name
        +int available_minutes = 120
        +List~str~ preferences
        +List~Pet~ pets
        +add_pet(pet: Pet) None
        +get_all_tasks() List~tuple~
    }

    class Pet {
        +str name
        +str species
        +int age
        +List~Task~ tasks
        +add_task(task: Task) None
    }

    class Task {
        +str description
        +datetime due_time
        +int duration_mins
        +str priority = "medium"
        +str frequency = "Once"
        +bool is_completed = False
        +mark_complete() None
        +end_time() datetime
        +overlaps(other: Task) bool
    }

    class ScheduledTask {
        +str pet_name
        +Task task
        +datetime start_time
        +str reason
    }

    class Scheduler {
        +Owner owner
        +get_all_tasks() List~tuple~
        +get_upcoming_tasks() List~tuple~
        +check_conflicts(new_task: Task) bool
        +generate_recurring_tasks() List~tuple~
        +generate_plan() List~ScheduledTask~
        +explain_plan(plan: List~ScheduledTask~) str
    }

    Owner "1" o-- "0..*" Pet : owns
    Pet "1" *-- "0..*" Task : has
    Scheduler "1" --> "1" Owner : plans for
    Scheduler ..> ScheduledTask : creates
    ScheduledTask "0..*" --> "1" Task : wraps
