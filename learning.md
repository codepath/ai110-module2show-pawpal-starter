# Requirements Learning Journal

## Entry #1

**Functional reqs were okay but vague:**

- "basic info" — what fields exactly?
- "add and edit tasks" — actually 3 requirements bundled into one
- "display clearly" — not testable

**Non-functional reqs were thin:**

- Only 3, none had measurable targets
- "must consider constraints" isn't a requirement, it's a design intention

**Format fixes:**

- Add bold short titles to each req so you can scan without reading everything
- Add IDs (FR-01, NFR-01) — tests and code can reference them

**Structure fixes:**

- Add acceptance criteria — yes/no statements, not descriptions
- Add an Out of Scope section so readers don't assume things

**Content fixes:**

- Split compound reqs (anything with "and" is suspect)
- Replace vague words: "clearly" → describe the actual format, "important" → name the specific cases
- NFR categories to check: Performance, Maintainability, Reliability, Security, Portability

## Entry #2

I asked claude how it would go about implrmenting features or class methods for the pawpal_system.py. It suggested an approach that assures I include the contract, the contrstaints, and the acceptance criteria

Provided example:

"Implement **Class.method()** in **Folder/FileName**  It should:

- Sort tasks by Priority (HIGH first)
- Greedily assign each task to the first AvailabilityWindow that has enough remaining minutes
- Return only tasks that were successfully scheduled (skip if no window fits)
- Do NOT modify the original task list

Assure you implrment classes that are depdencies to other classes

Insert inline assertions directly into the source code. Rather than acting as formal tests, assertions serve as internal safety checks to guarantee that critical properties of the program are behaving exactly as the developer intended at a specific moment in time.

## Entry #3

---

### 1. Build Order (dependency-first)

| #  | Class / Method                            | Why this order                                       |
| -- | ----------------------------------------- | ---------------------------------------------------- |
| 1  | AvailabilityWindow.duration_minutes()     | No deps; everything else measures time against this  |
| 2  | Task.edit()                               | Only depends on Priority enum (already done)         |
| 3  | Owner.add_pet()                           | Only depends on Pet (pure dataclass, no impl needed) |
| 4  | Owner.set_availability()                  | Depends on AvailabilityWindow (step 1 done)          |
| 5  | Scheduler.order_by_priority()             | Only depends on Task + Priority                      |
| 6  | Scheduler.check_constraints()             | Depends on Task + AvailabilityWindow                 |
| 7  | Scheduler.fit_tasks_into_slots()          | Depends on steps 5 & 6 being correct                 |
| 8  | WeeklyMonthlyPlan.generate() + .display() | Depends on Task, RecurrenceScope                     |
| 9  | Scheduler.generate_rationale()            | Depends on DailySchedule shape being clear           |
| 10 | DailySchedule.generate()                  | Depends on Scheduler being fully built               |
| 11 | DailySchedule.display()                   | Last — purely presentational, all data ready        |

---

### 2. Prompt Templates

**Prompt A — simple method, no sub-dependencies:**

Implement **AvailabilityWindow.duration_minutes()** in **pawpal/pawpal_system.py**

It should:

- Compute the number of whole minutes between `start_time` and `end_time`
- Return an `int` >= 0
- Assume `end_time` is always after `start_time` (same calendar day)

Constraints:

- Do NOT import any new libraries — use only `datetime` already imported
- Do NOT modify the dataclass fields or signature

Acceptance criteria:

- `AvailabilityWindow("Mon", time(9,0), time(10,30)).duration_minutes()` returns `90`
- `AvailabilityWindow("Mon", time(8,0), time(8,0)).duration_minutes()` returns `0`

Insert inline `assert` statements directly inside the method body after the
return-value is computed, to verify the result is a non-negative int before
returning it.

---

**Prompt B — method with dependencies:**

Implement **Scheduler.fit_tasks_into_slots()** in **pawpal/pawpal_system.py**

It should:

- Call `self.order_by_priority(tasks)` to sort tasks HIGH → MEDIUM → LOW first
- Greedily assign each task to the first `AvailabilityWindow` whose remaining minutes are >= `task.duration_minutes`
- Mutate each assigned task: set `task.assigned_day` to `window.day` and `task.scheduled_time` to the window's current start cursor
- Track a per-window "used minutes" counter so back-to-back tasks don't overlap
- Return only the successfully scheduled tasks as a new list
- Skip any task that fits in no window — do NOT raise an exception

Constraints:

- Do NOT modify the original `tasks` list passed in
- Do NOT call `self.order_by_priority` more than once
- `windows` list order defines scheduling preference (first window tried first)

Acceptance criteria:

- A 60-min HIGH task and a 30-min LOW task both fit in a 90-min window → both returned, assigned to that window, times non-overlapping
- A 120-min task against a single 60-min window → task is skipped, empty list
- Tasks are returned in scheduled order, not original input order

Insert inline `assert` statements at the point each task is assigned:

- assert `task.assigned_day` is not None
- assert `task.scheduled_time` is not None
- assert the scheduled task's duration <= remaining window time at assignment

---

### The pattern to replicate:

1. **It should** — behavior bullets (the contract / what it does)
2. **Constraints** — what it must NOT do (bounds on implementation)
3. **Acceptance criteria** — concrete input/output examples (your test oracle)
4. **Inline assert rule** — tells Claude exactly where/what to assert, so assertions are meaningful safety checks, not noise

## Entry #4

Acceptance critiera and line assertions, create the object and with the method you are building out add assertions for which to be true and you can observe whether the values being outputted are as intended and make sense

The nice part is that claude has context of the acceptance criteria, and will not stop resolving or creating somehting if its not functioning properly. This is the beifits of having acceptance creitiera wit hthe methods you are writting. Kind of analgous to passive testing IMO

## Entry #5:

  How to write these yourself — the pattern:

1. Read the skeleton — look at the method signature, its parameters, return type, and the fields on the class. This tells you the inputs/outputs.
2. Decide the category — does the method call other methods on self or other classes? If no, it's a Prompt A (simple). If yes, it's a Prompt B (has dependencies).
3. Fill in the template:
   - "It should" — describe the core behavior in 2-4 bullet points. Think: what does it do step by step?
   - "Constraints" — what must the implementation not touch? (no new imports, no signature changes, don't mutate inputs, etc.)
   - "Acceptance criteria" — write 2-3 concrete examples with specific inputs and expected outputs. Cover the happy path, an edge case, and a boundary condition.
   - "Assert statements" — pick 1-2 postconditions that should hold after the method runs (type checks, length checks, value bounds).

## Entry #6: 

Implement Owner.add_pet() in pawpal/pawpal_system 

The method should append the given Pet to the owner's _pets list 

Contraints: 

    No new imports

    No changes to the mthod signatures

    Do not mutate the pet input

Acceptance Criteria (assert statment to include in the method body)

    After appending, assert that pet is contained in self._pets (pet in self._pets)

Context: 

    Owner is a @dataclass (line 69) with _pets: List[Pet] = feild(... )

    Pet is a @dataclass with feilds: name.species, age, care

    The existing Task.edit() method demonstrates the projects pattern of using inline asset statement for post-condtion validation)

## Entry #7


Implement Owner.set_availability() in pawpal/pawpal_system.py (line 81).

  The method should replace the owner's availability windows for a given day. It must:

1. Remove all existing AvailabilityWindow entries in self.weekly_availability whose .day matches the day parameter
2. Extend self.weekly_availability with the new windows list

  Constraints:

- No new imports
- No changes to the method signature (self, day: str, windows: list[AvailabilityWindow]) -> None
- Do not mutate the windows input list

  Acceptance criteria (assert statements to include in the method body):

1. Assert that every window in windows is now contained in self.weekly_availability
2. Assert that no window remaining in self.weekly_availability with a matching .day exists outside the provided windows list (i.e., old entries for that day were fully replaced)

  Context:

- Owner is a @dataclass (line 68) with weekly_availability: list[AvailabilityWindow] = field(default_factory=list) (line 71)
- AvailabilityWindow is a @dataclass with fields: day, start_time, end_time (lines 38–42)
- The day parameter is a string like "Monday" — it matches AvailabilityWindow.day (line 40)
- Owner.add_pet() (line 75) demonstrates the project's pattern of capturing pre-state, performing the mutation, then asserting post-conditions with inline asserts
- Task.edit() (line 99) shows the same inline assert pattern

## Entry #8:


  The Senior's Advice

  "Before you ask Claude to write tests, read the code yourself and notice what's missing."

  Look at your current Task class — there's no mark_complete() method and no status field. And Pet has no task list. The tests the assignment asks for test features that don't exist yet.

  A senior would tell you: don't ask Claude to write tests AND invent the implementation in one shot. That's how you get code you don't understand. Instead, break it into two clean steps:

  Step 1: Add the missing pieces yourself (or with Claude's help, one at a time)

  Ask Claude something like:

  ▎ "I need to add a status field and mark_complete() method to my Task class, and a task list with an add_task() method to Pet. Can you show me what to add to pawpal_system.py?"

  Review what it suggests. Make sure you understand it before accepting. A status field is probably just a boolean or an enum. add_task() is just appending to a list — same pattern as Owner.add_pet() that already
  exists in your code.

  Step 2: Then ask for the tests

  Once the features exist, ask Claude:

  ▎ "Write two pytest tests in tests/test_pawpal.py: one that verifies mark_complete() changes a task's status, and one that verifies add_task() on a Pet increases the task count."

  The tests will be simple — create an object, call a method, assert the result. You should be able to read them and immediately understand what they do.

  The key principle1

  Tests verify behavior. The behavior has to exist first. If you ask Claude to "write tests for mark_complete" when there's no mark_complete, it'll either hallucinate an implementation or write tests that fail for the
  wrong reason. Either way, you'll spend more time debugging Claude's guess than you saved.

  Running it

  pip install pytest
  python3 -m pytest

  If tests fail, read the error message top to bottom. 90% of the time the answer is right there. Only ask Claude for help after you've read the traceback yourself.

---

  TL;DR from the senior: Don't use AI to skip understanding. Use it to move faster through steps you do understand. Add the missing methods first, then write the tests. Two small prompts beats one big confused one.
