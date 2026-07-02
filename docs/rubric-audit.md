# PawPal+ Rubric Audit

This document audits every required and stretch rubric item against the codebase, linking directly to the code, tests, and documentation that serve as evidence.

## Required Items (20/20 pts)

### 1. UML Design (4/4 pts)

- **UML Class Diagram**: [diagrams/uml.mmd](../diagrams/uml.mmd) and its final version [diagrams/uml_final.mmd](../diagrams/uml_final.mmd) detail all 4 core classes: `Task`, `Pet`, `Owner`, and `Scheduler`.
- **Attributes & Methods**: Each class includes clear typed attributes and methods matching the UML exactly (delivered in PR 7, finalized in PR 22).
- **Relationships**: Properly models `Owner` "1" -- "_" `Pet` -- "_" `Task` and `Scheduler` --> `Owner`.
- **Match with Final Code**: The final Mermaid diagram exactly aligns with the classes, fields, and signatures in [pawpal_system.py](../pawpal_system.py).

### 2. Classes and Data Model (4/4 pts)

- **Task Class**: Implemented as a dataclass in [pawpal_system.py:L21-L82](../pawpal_system.py#L21-L82). Includes `mark_complete()` and `next_occurrence()`.
- **Pet Class**: Implemented in [pawpal_system.py:L85-L109](../pawpal_system.py#L85-L109). Manages `add_task()`, `list_tasks()`, and `pending_tasks()`.
- **Owner Class**: Implemented in [pawpal_system.py:L112-L129](../pawpal_system.py#L112-L129). Manages `add_pet()` and `get_pet()`.
- **Scheduler Class (Cross-Pet)**: Implemented in [pawpal_system.py:L132-L200](../pawpal_system.py#L132-L200). Uses `all_tasks()` to operate across all pets in the household.

### 3. Scheduling Algorithms (3/3 pts)

- **>=2 Algorithmic Features**:
  1. Chronological sorting: `Scheduler.sort_by_time()` ([pawpal_system.py:L142-L146](../pawpal_system.py#L142-L146)).
  2. Status & Pet Filtering: `Scheduler.filter_by_status()` and `Scheduler.filter_by_pet()` ([pawpal_system.py:L155-L163](../pawpal_system.py#L155-L163)).
  3. Collision warnings: `Scheduler.detect_conflicts()` ([pawpal_system.py:L165-L181](../pawpal_system.py#L165-L181)).
  4. Task Recurrence: `Scheduler.complete_task()` ([pawpal_system.py:L214-L228](../pawpal_system.py#L214-L228)).
- **Correct & Reproducible**: Fully covered by tests in [tests/test_pawpal.py](../tests/test_pawpal.py).
- **Operate Across Multiple Pets**: Sorting, filtering, and conflict detection work seamlessly across the whole household.

### 4. CLI Demo & main.py (3/3 pts)

- **Demo Scenario**: [main.py](../main.py) constructs 1 owner, 2 pets, and 4 today-tasks.
- **Uses Scheduler**: Executes and prints the scheduler sorting, filtering, conflict, and recurrence flows.
- **Readable Sample Output**: pasted verbatim into [README.md:L70-L131](../README.md#L70-L131) showing `tabulate` aligned columns, status markers, and activity emojis.

### 5. Test Suite (3/3 pts)

- **Test File Exists**: [tests/test_pawpal.py](../tests/test_pawpal.py) contains logic tests.
- **Passes Correctly**: Pytest suite of 37 tests is completely green.
- **E2E/UI Testing**: [tests/test_app_ui.py](../tests/test_app_ui.py) uses Streamlit `AppTest` to verify front-end behavior and hooks (including save/load, priority sorting, slot finding, and conflict rendering) without mocks.

### 6. Documentation & Reflection (3/3 pts)

- **README Documentation**: Comprehensive sections describing system architecture, features list, smart scheduling table, persistence, formatting details, and test instructions.
- **Test coverage summary**: Coverage table copied to [README.md:L166-L191](../README.md#L166-L191).
- **Reflection File**: [reflection.md](../reflection.md) fully answered with design tradeoffs, AI influence, judgment examples, testing coverage details, and future improvements.

---

## Stretch Items (10/10 pts)

### SF17: Advanced Scheduling (Priority) (+2 pts)

- **Task.priority**: [pawpal_system.py:L26](../pawpal_system.py#L26).
- **sort_by_priority()**: [pawpal_system.py:L148-L153](../pawpal_system.py#L148-L153).
- **Test coverage**: `test_sort_by_priority_puts_high_priority_first_despite_later_time` and `test_sort_by_priority_breaks_ties_by_time` in [tests/test_pawpal.py](../tests/test_pawpal.py).
- **PR**: PR 17 (`feat-priority-scheduling`).

### SF18: 3rd Algorithm (Next Available Slot) (+2 pts)

- **find_next_available_slot()**: [pawpal_system.py:L183-L200](../pawpal_system.py#L183-L200).
- **Test coverage**: `test_next_available_slot_on_empty_day_is_day_start`, `test_next_available_slot_skips_busy_blocks_across_pets`, `test_next_available_slot_returns_none_when_nothing_fits`, and `test_next_available_slot_respects_day_end_boundary_with_late_task` in [tests/test_pawpal.py](../tests/test_pawpal.py).
- **Agent Workflow section**: Filled in [ai_interactions.md:L7-L28](../ai_interactions.md#L7-L28).
- **PR**: PR 18 (`feat-next-available-slot`).

### SF19: JSON Persistence (+2 pts)

- **save_to_json / load_from_json**: [pawpal_system.py:L231-L263](../pawpal_system.py#L231-L263).
- **Test coverage**: `test_persistence_round_trip` in [tests/test_pawpal.py](../tests/test_pawpal.py) and `test_app_save_and_load_persistence` in [tests/test_app_ui.py](../tests/test_app_ui.py).
- **Sidebar Integration**: [app.py:L21-L52](../app.py#L21-L52).
- **PR**: PR 19 (`feat-persistence`).

### SF20: Output Formatting (+2 pts)

- **Library used**: `tabulate` (in [main.py](../main.py)).
- **Emojis & Statuses**: [main.py:L54-L81](../main.py#L54-L81).
- **PR**: PR 20 (`feat-output-formatting`).

### SF21: Prompt Comparison (+2 pts)

- **Prompt Comparison table**: Filled in [ai_interactions.md:L31-L49](../ai_interactions.md#L31-L49).
- **PR**: PR 21 (`docs-model-comparison`).

---

## Submission Checklist

- [x] Repository is public / accessible.
- [x] All required files present and populated.
- [x] Stack successfully managed and branches pushed using Graphite.
- [x] Pytest and trunk.io formatting/lint check clean on every PR in the stack.
- [x] No placeholders, stubs, or `NotImplementedError` present.
- [x] Reflection answered specifically and in the user's voice.
