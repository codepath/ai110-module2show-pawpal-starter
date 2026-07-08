# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My initial UML design incorporates the four main components as an individual class for my pet care app that checks each requirement on what it's supposed to accomplish, which is to be a smart pet care management system that helps owners keep their furry friends happy and healthy. 

- What classes did you include, and what responsibilities did you assign to each?
As stated earlier, I included four classes that individually represent each main component for the app. For instance, the responsibilities in the Pet class is updating its profile and getting what it needs on a daily schedule. Then, the Owner class has responsibilites for removing tasks, updating their pet's preferences, and receiving a summary of tasks in the form of a schedule. Next, the Task class contains responsibilities to set priorities and time durations of the tasks needed to be complete for their pet on a daily basis to keep them happy and healthy. Finally, the Scheduler class contains responsibilities for sorting tasks, checking conflicts, and providing explanation to the owner so that the pet's schedule accomodates with the owner's lifestyle for the schedule to work.


**b. Design changes**

- Did your design change during implementation?
Yes, my design did change during implementation. 

- If yes, describe at least one change and why you made it.
One change I made is adding the relationships between Scheduler and Task, and Scheduler and Pet. This change was very necessary because the Scheduler class can build a plan accordingly with adding tasks while following constraints based on a pet's information provided by the owner.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler considered the following constraints: priority, time, frequency, and preferences

- How did you decide which constraints mattered most?
I decided which constraints mattered most by priortizing on the app being open to all kinds of pet owners where they find the most helpful accomodations to make the best possible schedule for pet owners to follow by completing tasks to keeping their pets happy and healthy.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
My scheduler made a tradeoff of only noticing overlapping times instead of trying to automatically reschedule conflicts as well.

- Why is that tradeoff reasonable for this scenario?
The tradeoff is reasonable for this scenario because my Scheduler is transparent, fast, and predictable in ensuring the pet owner can complete the tasks assigned in the schedule for their pet, such as having the highest priority and enough time to complete a certain task for their pet. Thus, the tradeoff is reasonable for producing a sensible daily plan from the required constraints. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used the AI tools primarily for testing and design brainstorming when designing my version of PawPal+.

- What kinds of prompts or questions were most helpful?
The most helpful prompts were the ones with the most depth. For example, implementing an important feature for my pet care app and 
the feature's behavior works as intended by adding instructions and examples to ensure there aren't any errors and/or bugs with the 
feature whenever PawPal+ is running.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
The one moment where I didn't want to use an AI suggestion whenever I was building my app was refining my sorting algorithmic method
for my Task objects and their time attributes, but I decided to keep the pre-existing version of the method because it was easier to
read the code for the method.

- How did you evaluate or verify what the AI suggested?
I verified what the AI suggest by making and evaluating tests on if the refined method worked exactly like the pre-existing version 
with the task of sorting my Task objects by their time attributes. The verification was successful, but I was mainly priortizing having
the code for the method be easily readable and understandable rather than look confusing. Thus, I made the decision to keep the pre-existing version of my sorting algorithmic method.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested 3 core behaviors for my pet care app: the tasks are being marked complete or incomplete, the owner's options work as intended on the pet care app, and the daily plan is being created by following certain constraints and including the necessary tasks for the pet.

- Why were these tests important?
These tests were important because these 3 core behaviors set the foundation on bringing my version of PawPal+ to life as the main goal 
is for pet owners to keep their furry friends of any kind happy and healthy, and this goal can be accomplished by ensuring I'm meeting the 
necessary accomodations from pet owners and their pets to create a daily schedule, which follow constraints and include important tasks, for them to easily follow and adjust at any time as part of using a smart pet care management system. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
I'm confident that my scheduler works correctly because I did create and run many tests, specifically 20, on several features to ensure
all test cases passed telling me that my PawPal+ app should work if the main features' expected behavior equates to its actual behavior. For instance, I repeatedly tested the important feature of all the options opened to the pet owner when using PawPal+, such as adding a pet, adding tasks for their pets, filtering their tasks, and building their ideal schedule that works for them and their pets.   


- What edge cases would you test next if you had more time?
If I had more time, I would test the following edge cases:
1. Overlapping tasks with the same priority or time window to see how the scheduler handles conflicts.
2. Pets with incomplete or unusual preferences, such as missing feeding times or special care instructions.
3. Very large task lists to make sure the scheduler stays efficient and still produces a sensible plan.
4. Changes to the owner’s availability after a schedule is created, to verify the system responds appropriately.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm most satisfied with getting a functional app to work. For instance, the app runs to showcase PawPal+'s look and the options that any pet owner has to strengthen the love for their pets.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would redesign PawPal+'s UI to be very pet-themed by adding more color, background, sound effects, and pictures to get the attention of both pet owners and their pets. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
One important thing about working with AI on this project is to always provide instructions and examples as to guide them on what you
specifically need during any moment in building a project. For example, this can range from how a feature should work, understanding test code to not get confused over the project's functionality, and brainstorming ideas to either accept or reject to ensure you can achieve building the ideal version of your project.