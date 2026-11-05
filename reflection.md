# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial design was an app that helps a busy owner keep up with pet care. I started with adding pets, managing care tasks, and generating a daily plan based on available time and task priorities. I kept four classes because each one answers a different question about the same problem.

Their responsibilities are:

- **Owner:** Stores the owner's name, time budget, short-task preference, and pets. It collects tasks across pets.
- **Pet:** Stores pet information and manages its task list, including completion and adding the next recurring occurrence.
- **Task:** Stores and validates the details of one care activity, including duration, priority, recurrence, scheduled time, due date, and completion date.
- **Scheduler:** Builds the daily plan, sorts and filters task lists, reports same-time conflicts, and finds the next available interval across pets.

Owner manages pets, Pet contains tasks, and Scheduler uses their information. None of these classes needs to inherit from another. Keeping the Streamlit interface in app.py also lets me test the care logic without opening the app.

**b. Design changes**

The four-class structure stayed, but the details grew during implementation. Task gained scheduled_time and due_date, and Pet.complete_task() now keeps the completed task and adds a new daily or weekly occurrence. I updated the final UML to reflect these additions instead of leaving it at the original skeleton.

Input validation, pet-task associations, and a consistent plan format are now implemented. Owner.get_all_tasks() returns pairs so a task stays connected to the right pet. The plan dictionary contains selected and skipped tasks, explanations, and time totals. Separate sorting, filtering, and conflict methods let me add features without changing that format.

I kept the scope manageable for a short assignment. The Streamlit app now exposes the scheduling features without extra domain classes. It supports adding, viewing, editing pending tasks, and completing tasks. Editing uses the existing Task.update_details() method and keeps the same task object; removal remains a backend operation.

The bonus follow-up adds storage functions in `persistence.py`, without a fifth domain class. Explicit JSON Save/Load retains pets, tasks, recurrence history and owner settings between runs. A validated load creates a new object graph, so the UI clears old editor references, drafts and plans before displaying it. Storage is a single local file, not a multi-user database.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

I put priority and the owner's available minutes first because the main goal is a useful daily care plan. The scheduler considers high-priority tasks first and adds whole tasks that fit. Completed and future-dated tasks are skipped. If a task is too long, it records a reason and continues looking for tasks that fit. The short-task preference only breaks ties within a priority.

This is a straightforward choice-by-choice approach, not a search through every possible combination. It is easy to explain, but it does not guarantee the fullest possible use of the budget. Chronological sorting is a separate view: it orders HH:MM times and puts untimed tasks last. Pet and completion filters help browse the list without changing the plan across all pets.

For recurrence, completing a daily task creates one pending occurrence due the next day; a weekly task creates one due seven days later. The dates are based on completion, so finishing late shifts the next occurrence instead of maintaining a fixed calendar schedule. Keeping the original completed task makes the history clear, and repeating completion does not add another copy.

**b. Tradeoffs**

I chose to keep conflict detection simple. The scheduler groups pending tasks by their date and exact starting time, including tasks for different pets, and returns a warning when a group has more than one task. It uses each task's due date when available, otherwise the planning date, which defaults to today. It ignores completed tasks and tasks without a scheduled time. It only reports conflicts; it does not change tasks or the generated plan.

The tradeoff is that it detects identical starting times on the same date but does not detect overlapping intervals with different starting times. For example, tasks scheduled for 09:00–09:30 and 09:15–09:45 would not trigger a warning. I chose this approach for a short assignment because the dictionary grouping is easy to understand and test, while full overlap detection would need more logic and edge cases. I kept the explicit dictionary version because a shorter version would not improve what it detects.

The bonus follow-up uses duration intervals in a separate next-available-slot search. It sorts reservations and advances a candidate start past overlaps until a sufficiently long gap appears. Tests cover nested and partial overlaps, previous-day spillover, and touching endpoints. This improves the search for free space while leaving the original same-start warning and priority-plan behavior unchanged. A future improvement would use interval logic to report every existing overlap, not only avoid reservations when suggesting a new slot.

---

## 3. AI Collaboration

**a. How you used AI**

I used Codex to brainstorm the four classes, draft the UML and Python skeleton, and implement features in small phases. My prompts named the files to read, the behavior to add, the files to leave alone, and the checks to run. This made each change easier to review. For testing, I asked for a coverage plan before adding tests so we could build on the existing suite instead of starting over.

The most useful capabilities were codebase inspection, focused changes, test generation, and explanations of algorithm choices. Inspecting the actual methods helped keep the UI aligned with the backend. Generating tests helped cover less obvious cases, such as two different Task objects with identical details and completing a recurring task more than once. The explanations helped me judge whether a shorter implementation was actually better.

I mostly used the same Codex chat throughout the project. Keeping the earlier context helped maintain continuity because we could refer back to the design, decisions, and completed work. I kept things organized by giving focused prompts for each phase, from planning and algorithms to testing and final documentation. That helped make the next task clear without having to explain the whole project again.

**b. Judgment and verification**

One alternative we considered was replacing the explicit dictionary used for conflict grouping with defaultdict(list). That would remove the check for a missing group, but both approaches have expected O(n) time for n tasks. I kept the explicit dictionary because it was easier for me to follow and there was no meaningful improvement in behavior. This was a considered alternative, not a code change that had to be undone.

I made scope decisions throughout the work: keep the four classes, preserve working APIs and tests, limit conflicts to exact starting times, and separate documentation changes from code changes. I asked Codex to inspect existing behavior before adding requirements and to report actual test output. That gave me specific results to review rather than just accepting a claim that a feature worked.

I personally ran terminal commands, including python main.py and pytest, and shared the successful output. The CLI demo stayed within 40 minutes and explained why Grooming was skipped, and the test suite reached 97 passing cases. Running the commands myself gave me a way to check the results alongside Codex's reports.

Codex also ran and reported automated tests, syntax checks, and Streamlit AppTest smoke checks. AppTest checked task entry, sorting and filtering, conflict warnings, recurring completion, and state across reruns. These were automated UI checks, so I would not describe them as a full manual browser review that I completed myself.

For the pending-task editor, I compared a direct prompt with a staged prompt using the same frozen requirements and acceptance tests. Both implementations passed, so the experiment ended in a tie. I chose Strategy A for integration because its form lets users edit several fields and save them together. The context conditions were unequal: A retained preparation history, while B started in a separate session. That limits what I can conclude about the prompting strategies themselves.

---

## 4. Testing and Verification

**a. What you tested**

The automated suite checks priority and time-budget scheduling, chronological sorting, pet and completion filters, daily and weekly recurrence, and same-start-time conflict warnings. It also checks empty inputs, invalid times and settings, duplicate object additions, repeated completion, leap days, and year changes. Tests verify that rejected updates do not partly change an object and that detecting conflicts leaves tasks and the plan unchanged.

Phase 4 ended with 87 passing cases. Phase 5 added focused cases for duplicate prevention, strict owner settings, and recurrence chains, and extended a sorting test to check 09:05 before 09:45. That backend suite reached 97 cases and remains unchanged. The integrated editor adds 19 frozen Streamlit AppTest cases, bringing the suite to 116 passing cases. These tests use real backend objects; a few narrowly scoped wrappers or accessor replacements check that the intended APIs are called.

These checks matter because a plausible-looking schedule can still hide errors, such as assigning a task to the wrong pet or creating duplicate recurring tasks. The saved editor tests check identical task names, unsaved drafts, atomic rejection, object identity, optional-field clearing, cached plans, recurrence, stale submissions, and empty states. Earlier UI smoke checks were separate from the backend suite; the 19 editor cases now run as part of pytest.

**b. Confidence**

My confidence is 4 out of 5. After the bonus follow-up, 150 tests pass: the original 116 plus 34 persistence, interval-search and UI checks. These support the implemented behaviors, but they are not proof that every possible interaction works. The original conflict warning still checks only identical starts; free-slot search handles duration overlaps separately. Automated UI coverage does not replace a recorded visual browser or accessibility review.

With more time, I would extend repeatable UI tests to longer flows, such as completing tasks while changing filters, and review keyboard use and layout in a browser. The new persistence tests include a separate Python process and simulated failed writes, but they do not establish safe concurrent use or durability on every hosting platform.

---

## 5. Reflection

**a. What went well**

The separation between the backend and UI worked well. Sorting, filtering, recurring-task creation, and conflict warnings could be added to the same four-class design and then exposed in Streamlit. Returning pet-task pairs kept the results understandable even with multiple pets. Working in small phases also made it possible to identify specific gaps and grow the suite from 87 to 97 cases without replacing working tests.

**b. What you would improve**

Pending-task editing, JSON storage and next-available-slot search are now implemented. I would next consider full duration-overlap warnings, per-user storage and broader browser testing. Before expanding those features, I would define their behavior and edge cases so the implementation stays understandable instead of growing only because AI can generate more code.

**c. Key takeaway**

My main takeaway is that using AI does not remove my role as the lead architect. Codex can generate code quickly, but I am responsible for the requirements, class responsibilities, scope decisions, validation, and understanding the final product. A passing test suite is useful evidence, and I still need to know what it covers and what it leaves out. The best result comes from giving focused instructions, reviewing the changes and evidence, and choosing solutions I can explain.
# AI110 final-project extension (November 2026)

This section supplements the earlier Module 2 reflection below. Repository evidence shows that the AI110 work extended the existing four-class scheduler with local retrieval, Gemini answers, and a review-only planning workflow. The original scheduling and JSON Save/Load behavior stayed in place. The AI tools helped inspect the staged implementation, identify gaps, draft modular changes, and generate tests. The source notes were checked against AVMA and ASPCA pages before being added; source URLs and the live model outputs are recorded in the repository.

The first planner syntax check caught an unclosed JSON-schema dictionary, which was corrected before evaluation. The first full pytest attempt ran into a Windows permission error while pytest tried to clear an existing `.pytest_temp` directory; those were fixture setup errors, not failed AI assertions. A later run with a fresh temporary directory is recorded in the final verification results. The deterministic AI evaluation used mocked model calls so safety and citation rules could be checked without network variability. A separate live comparison showed a direct Gemini answer with uncited, specific advice and a grounded answer citing two AVMA chunks; the direct answer was truncated at 200 tokens. The live planning trace recorded three suggestions passing the scheduler's 30-minute demo budget. These observations support only the tested examples.

The biggest limitation is that a valid source ID does not prove every sentence is supported by its source. Keyword retrieval can also miss a relevant care question or retrieve a broad paragraph. The emergency and medical guards cover common patterns but cannot replace veterinary judgment. The scheduler checks the total daily budget for proposals; it does not create appointment times. I would review the UI in a real browser and ask a veterinarian to review any medical-facing wording before wider use.

## Personal Reflection — PawPal+ AI110 Final Project

For my AI110 final project, I extended my original PawPal+ pet-care scheduling application by integrating Google Gemini, Retrieval-Augmented Generation (RAG), and an AI-powered pet-care planning assistant.

### What I Learned

One of the most important things I learned was how to integrate a large language model into an existing Python application. Originally, PawPal+ used predefined scheduling rules to organize pet-care tasks. By adding Gemini and RAG, I learned how AI can make an application more interactive and useful.

I also learned how RAG works. Instead of relying only on the model's existing knowledge, the application retrieves relevant information from a knowledge base and uses it to generate answers with citations.

### Challenges I Faced

One of my biggest challenges was connecting Gemini to my Streamlit application. I initially encountered API configuration issues, unavailable models, and slow API responses.

I also faced difficulties with Python indentation and understanding the difference between writing Python code in VS Code and executing commands in Git Bash.

By troubleshooting these problems, I improved my understanding of Python, API integration, environment variables, and debugging.

### How I Used AI Tools

I used ChatGPT and Codex throughout the development process to understand AI concepts, generate code, troubleshoot errors, and improve my project.

Codex helped implement additional features, including multi-source RAG, a multi-step planning workflow, automated evaluation, and documentation.

However, I also tested the application myself, checked its responses, ran automated tests, and reviewed the changes before committing them to GitHub.

### Human-in-the-Loop

This project helped me understand the importance of keeping humans involved in AI systems.

AI-generated recommendations are not always correct, especially when dealing with pet health and care. That is why PawPal+ provides supporting sources and allows users to review proposed tasks instead of automatically changing their schedules.

As a future software engineer, I believe AI should assist people in making decisions rather than completely replacing human judgment.

### Testing and Evaluation

I verified the Gemini integration by asking questions about dog exercise and drinking water and checking the generated responses.

The final project also passed 178 automated tests, including 23 deterministic AI evaluation cases.

This helped me understand that building an AI feature is not enough. It is equally important to test its reliability, handle errors, and evaluate its limitations.

### Future Improvements

In the future, I would like to expand the pet-care knowledge base, improve retrieval accuracy, support more types of pets, and make the AI planning assistant more personalized.

### Final Thoughts

Overall, this project helped me move beyond simply using AI tools to understanding how AI systems can be designed, integrated, tested, and improved.

The biggest lesson I learned is that AI can make software more powerful, but reliable applications still require careful engineering, testing, and human oversight.

---


