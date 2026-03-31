export const diagram = `
classDiagram

  class Task {
    +String title
    +String description
    +String time
    +String frequency
    +String priority
    +int duration_minutes
    +String category
    +bool completed
    +String last_completed_date
    +String due_date
    +bool spawned_next_occurrence
    +mark_complete(completed_on) void
    +create_next_occurrence(reference_date) Task
    +is_due_today(reference_date) bool
    +get_task_info() dict
    +getTask() String
    +edit_task(title, description, time, frequency, priority, duration_minutes, category, due_date) void
    +editTask(name, description, due_time, priority, duration_minutes, category, due_date) void
  }

  class Pet {
    +String pet_name
    +String pet_desc
    +float pet_height
    +float pet_weight
    +List~Task~ tasks
    +add_task(task) void
    +remove_task(title) void
    +get_tasks() List~Task~
    +getPetDesc() String
    +getPetHeight() float
    +getPetWeight() float
  }

  class Owner {
    +String owner_name
    +List~String~ constraints
    +List~String~ priorities
    +List~Pet~ pets
    +add_pet(pet) void
    +remove_pet(pet_name) void
    +get_pets() List~Pet~
    +getOwnerName() String
    +getConstraints() List~String~
    +getPriorities() List~String~
    +get_all_tasks() List~Tuple~
  }

  class Plan {
    +String date
    +List~Task~ tasks
    +List~String~ constraints
    +List~String~ priorities
    +List~String~ conflicts
    +get_plan() List~Task~
    +getPlan() List~Task~
    +edit_plan(tasks, constraints, priorities, conflicts) void
    +editPlan(tasks, constraints, priorities, conflicts) void
  }

  class Scheduler {
    +Dict PRIORITY_ORDER
    +Set HEALTH_CATEGORIES
    +get_tasks_for_pet(pet) List~Task~
    +get_all_tasks(owner) List~Tuple~
    +get_pending_tasks(owner) List~Tuple~
    +mark_task_complete(owner, pet_name, task_title) bool
    +is_health_related(task) bool
    +task_sort_key(task) Tuple
    +detect_conflicts(scheduled_items, owner) List~String~
    +get_conflict_warnings(owner) List~String~
    +organize_by_time(owner) List~Tuple~
    +generatePlan(owner, pet, tasks) Plan
  }

  Owner "1" *-- "*" Pet : owns
  Pet "1" *-- "*" Task : has
  Plan "1" o-- "*" Task : contains
  Scheduler ..> Owner : uses
  Scheduler ..> Pet : uses
  Scheduler ..> Task : evaluates
  Scheduler ..> Plan : creates
`;
