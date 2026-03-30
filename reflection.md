# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I designed four core classes with distinct responsibilities:

- **Task** (dataclass): Holds a single care activity — its description, scheduled time (HH:MM), duration, priority (low/medium/high), frequency (once/daily/weekly), completion status, and due date.  Python dataclasses were chosen to keep the model concise and readable with automatic `__init__` and `__repr__`.
- **Pet** (dataclass): Stores a pet's name and species, plus a mutable list of Task objects.  Exposes `add_task` and `remove_task` so the caller does not touch the list directly.
- **Owner**: Manages a list of Pet objects and provides `get_all_tasks()`, which flattens the entire pet/task tree into `(Pet, Task)` tuples that the Scheduler can consume without knowing the internal structure.
- **Scheduler**: Receives an Owner and acts as the "brain."  It is the only place where sorting, filtering, conflict detection, recurrence, and slot-finding logic live — keeping those concerns out of the data classes.

Three core user actions identified during design:
1. Add a pet and register care tasks with priority and time.
2. View today's schedule sorted either by time or priority.
3. Mark a task complete and have the next recurrence appear automatically.

**b. Design changes**

Originally I considered placing scheduling methods directly on the Owner class, but I separated them into Scheduler because Owner's responsibility is data management, not algorithmic reasoning.  Mixing them would have violated single-responsibility and made testing harder.

I also added `get_next_available_slot()` to the Scheduler after noticing that the UI would benefit from suggesting free slots rather than requiring the user to remember what is already booked.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:
- **Time**: Tasks are sorted chronologically using Python's built-in `sorted()` with a `lambda` key on the HH:MM string (lexicographic sort is correct for zero-padded 24-hour strings).
- **Priority**: A secondary sort uses a rank dictionary `{"high": 0, "medium": 1, "low": 2}` so high-priority tasks appear first when two tasks share the same time.
- **Recurrence**: Daily and weekly tasks reschedule themselves via `timedelta` when marked complete, so the owner never has to re-enter repeating care.
- **Conflict detection**: Two tasks for the same pet at the same time on the same date produce a warning.

Priority and time were chosen as the primary constraints because they map directly to what a pet owner cares about: urgent things first, then in the order they happen.

**b. Tradeoffs**

The conflict detector only flags *exact* time matches — it does not check whether a 60-minute vet appointment and a 30-minute grooming session physically overlap.  For example, tasks at 10:00 and 10:30 are not flagged even if the first runs until 11:00.

This tradeoff is reasonable for the current scope: exact matches are the most common scheduling mistake (accidentally booking two events at the same hour), and duration-overlap detection would require end-time calculations that add complexity without a clear benefit in a single-owner app.  A future iteration could add `end_time = time + duration` and flag overlaps.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used throughout the project in three main ways:

1. **Architecture brainstorming**: I described the four-class design to the AI and asked it to validate that the Scheduler-as-separate-class pattern was cleaner than embedding logic on Owner.  That conversation confirmed the single-responsibility approach.
2. **Code generation and iteration**: I used the AI to generate the initial class stubs and then refined them — for example, the AI's first version of `mark_task_complete` returned a new Task but did not automatically attach it to the Pet.  I asked it to revise so the method adds the recurrence task directly.
3. **Test planning**: I asked "what edge cases should a pet scheduler test?" and got back a list that included the pet-with-no-tasks scenario, which I would not have thought of immediately.

Prompts that were most helpful were specific and gave context: `"Based on these four classes, suggest the simplest conflict detection strategy that returns a warning string rather than raising an exception."` Vague prompts like "make it better" produced unhelpful results.

**b. Judgment and verification**

The AI initially suggested using Python's `datetime.strptime` to parse the HH:MM strings before sorting, converting them to `datetime.time` objects for comparison.  I evaluated this suggestion and decided against it: since the times are stored as zero-padded 24-hour strings, lexicographic sorting already produces the correct chronological order (`"07:30" < "12:00" < "18:00"`).  Adding `strptime` would work, but it adds an import and parse call that buys nothing.  I kept the simpler lambda and added a comment explaining why string comparison is safe.

---

## 4. Testing and Verification

**a. What you tested**

The automated test suite (14 tests) covers:

- **Task completion**: `mark_complete()` flips `completed` from False to True.
- **Pet task count**: Adding a Task to a Pet increases `len(pet.tasks)`.
- **Sorting correctness**: `sort_by_time()` returns tasks in ascending HH:MM order; `sort_by_priority()` places high-priority items first.
- **Recurrence logic**: Completing a daily task creates a new task dated `today + 1`; weekly creates `today + 7`; a one-time task creates nothing.
- **Conflict detection**: Same pet, same time → warning; different times or different pets → no warning.
- **Filtering**: `filter_by_pet` returns only the named pet's tasks; `filter_by_status` excludes completed tasks.
- **Edge cases**: Pet with no tasks returns an empty list; `get_next_available_slot` skips occupied slots correctly.

These tests were important because they verify the three behaviors most likely to break quietly — recurrence, conflict detection, and sorting — where a wrong result looks plausible but misleads the user.

**b. Confidence**

⭐⭐⭐⭐ (4/5).  The happy paths and the main edge cases are covered.  Given more time, I would test:

- Duration-overlap conflicts (e.g., a 60-minute task at 10:00 blocking a 30-minute task at 10:30).
- Behaviour when `sort_by_time()` is called with tasks spanning midnight (e.g., "23:30" to "00:15").
- `get_next_available_slot()` when every slot from 07:00 to 21:30 is blocked.

---

## 5. Reflection

**a. What went well**

The CLI-first workflow worked extremely well.  Running `python main.py` after each new method gave instant, readable feedback without needing to restart Streamlit.  The conflict detection feature was particularly satisfying: a simple dictionary keyed on `(pet_name, date, time)` caught all the cases we cared about in under ten lines.

**b. What you would improve**

If I had another iteration, I would add duration-overlap detection to the conflict checker and store tasks in a sorted structure (e.g., a sorted list or a `SortedList` from `sortedcontainers`) so that sort operations are O(log n) inserts rather than O(n log n) on every retrieval.  I would also add JSON persistence so the schedule survives a Streamlit restart.

**c. Key takeaway**

The most important lesson was that AI is most useful when it operates within clear constraints you have already defined.  When I gave the AI a UML diagram and asked it to generate matching code, the output was immediately useful.  When I asked open-ended questions without context, I spent more time evaluating irrelevant suggestions than I would have spent writing the code myself.  Design-first, AI-second is a productive workflow.
