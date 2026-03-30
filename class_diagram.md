```mermaid
classDiagram
    class Owner {
        +str name
        +time available_start
        +time available_end
        +get_available_window() tuple
        +get_total_available_time() int
    }

    class Pet {
        +str name
        +str species
        +int age
        +List~Task~ tasks
        +add_task(task Task)
        +remove_task(task_id int)
        +get_tasks() List~Task~
    }

    class Task {
        +int id
        +str title
        +int duration_minutes
        +str priority
        +str frequency
        +Optional~time~ preferred_time
        +bool is_completed
        +Optional~str~ pet_name
        +mark_complete()
        +next_occurrence(new_id int) Task
        +is_high_priority() bool
        +fits_in_window(start time, end time) bool
    }

    class ScheduledTask {
        +Task task
        +time start_time
        +str reason
        +end_time time
        +get_time_range() tuple
        +to_display_string() str
    }

    class Scheduler {
        +Owner owner
        +List~Pet~ pets
        +List~ScheduledTask~ scheduled_tasks
        +List~Task~ skipped_tasks
        -int _next_task_id
        +add_pet(pet Pet)
        +complete_task(task_id int) Task
        +get_all_tasks() List~Task~
        +generate_recurring_tasks() List~Task~
        +build_schedule() List~ScheduledTask~
        +filter_tasks(pet_name, completed) List~Task~
        +filter_by_pet(pet_name str) List~Task~
        +filter_by_priority(priority str) List~Task~
        +sort_by_time(tasks) List~Task~
        +check_conflicts(task, proposed_start) bool
        +get_all_conflicts() List~dict~
        +warn_conflicts() List~str~
        -_sort_by_priority(tasks) List~Task~
        -_assign_time_slots(tasks) tuple
    }

    Owner "1" --o "1" Scheduler : constrains
    Scheduler "1" o-- "*" Pet : manages
    Pet "1" *-- "*" Task : owns
    Scheduler "1" --> "*" ScheduledTask : produces
    ScheduledTask "1" *-- "1" Task : wraps
    Task ..> Task : next_occurrence()
```

<!--
DESIGN NOTES

ScheduledTask replaces DailyPlan:
  The initial design had a single DailyPlan holding the full day's output.
  Replaced by individual ScheduledTask objects — one per placed task — so the
  UI can render per-task reasoning and time slots independently. end_time is a
  computed @property (derived from start_time + duration), not a stored field.

Task.pet_name added:
  Once Scheduler.get_all_tasks() flattens all pets into one list, the pet
  association is lost. pet_name is stamped onto the Task by Pet.add_task() so
  the scheduler and UI can always display ownership without a reverse lookup.

Task.next_occurrence() — self-referential:
  Recurring tasks (daily/weekly) need a fresh copy when marked complete.
  next_occurrence() lives on Task because only Task knows its own frequency.
  Scheduler.complete_task() calls it and re-registers the result with the pet.

Scheduler._next_task_id:
  Private counter starting at 1000 to avoid ID collisions with user-created
  tasks when auto-generating next occurrences for recurring tasks.

skipped_tasks added to Scheduler:
  The greedy algorithm silently dropped tasks that didn't fit. skipped_tasks
  surfaces them so the UI can warn the owner rather than hiding the overflow.

explain_plan() removed:
  The per-task reason field on ScheduledTask already covers this. A separate
  method returning a monolithic string would duplicate that logic and be harder
  to test.

Relationships upgraded to composition where appropriate:
  Pet *-- Task: Pet owns its tasks' lifecycle (remove_task deletes them).
  ScheduledTask *-- Task: ScheduledTask wraps exactly one Task and cannot
  exist without it. Scheduler o-- Pet: Scheduler manages pets but does not
  create or destroy them (aggregation, not composition).
-->
