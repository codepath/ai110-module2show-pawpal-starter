# PawPal+ Project Reflection

## 1. System Design

- adding a pet and their info
- getting the today's task for the pet
- receiving explanations as to why those tasks were 

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
  - Pet was chosen so we can focus on the amimal being care for.
  - Owner was chosen so we can know owns the pet and what constrains that they have (scheduling limits)
  - Responsibility was chosen so we can track all of the requirements needed to care for the pet.
  - Constraints was chosen because it list all of the factors that will limit the recommended daily plan of the pet.
  - Plan was chosen because it holds the plan that was chosen for the pet.
  - Explanation was chosen because contains the information as to why the specific plan was chosen.
  
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
Our constraints focus on available time. You only have so much time, so we focused on how much time that we had. The total time budget and the start/end window you have.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is that in detect_conflicts() function, is we use a nested loop to go through items in each section, so it is O(n^2) instead of O(n). So I traded a slower space complexity in order for simpler and easier-to-understand code. It was reasonable because it was figured that would be never be a large enough of tasks to where it would cause issue to user.

---

## 3. AI Collaboration

**a. How you used AI**

- I used it for design brainstorming and optimizing code. I told it to focus on a specific function when debugging or just help implement a specific feature. I did not want to overload it with prompt, so I prompted with an simple focused prompt.

**b. Judgment and verification**


  When it gave me the initial classes for the uml_draft, I thought it overly complicated and created a bunch of unnecessary classes, so I asked it to combine certain classes where I felt that they were too closely related.
---

## 4. Testing and Verification

**a. What you tested**


These tests focus on the happy path and ensuring that edge cases are handled. It is focusing that sorting, filtering, and recurring tasks are handled correctly. For example, it tests for a daily task to be added for the next day if it is marked completed. Furthermore, it tests to ensure the user is notified if a duplicate tasks is found. 


**b. Confidence**

Based on the tests, my confidence level is a 5. The tests thoroughly cover edge cases that will cause the site to crash, and ensures graceful handling for duplicates. I think testing for a large number of pets would be interesting to see how it handles it.


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - I am satisfied with how easy it is to input the information about your pet. I think I have made my website incredibly user-friendly and easy to use.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - I would really love to have this to be able to survive a page refresh. I think something like local storage would be great.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  - The main thing that I learned was the importance of using AI as a co-developer instead of letting it control the entire app. You need to work together with AI, or AI can go over complicated with your app.