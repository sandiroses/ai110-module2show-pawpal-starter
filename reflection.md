# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Three core actions a user should be able to perform:**
1. Add a pet and set how much time I have today.
2. Add care tasks (like walks or feeding) with a time, duration, and priority.
3. See today's schedule, sorted by time, with warnings if tasks overlap.

My UML has four classes connected in a chain: an Owner has many Pets, each Pet has many Tasks, and a Scheduler reads from the Owner to plan the day.

- **Task** (dataclass): one care activity. Holds the title, time ("HH:MM"), duration, priority, frequency (once/daily/weekly), due date, and whether it's completed. It can mark itself complete and create its next occurrence for recurring tasks.
- **Pet** (dataclass): stores a pet's name, species, and its list of tasks. It can add, remove, and return its tasks.
- **Owner** (dataclass): stores the owner's name, how many minutes they have available today, and their pets. Its `get_all_tasks()` method collects every pet's tasks into one list.
- **Scheduler**: the "brain." It gets all tasks through `Owner.get_all_tasks()`, then sorts them by time, filters them by pet or completion status, detects conflicts, builds the daily plan, and explains it.

**b. Design changes**

- I added a `pet_name` field to Task. Once the Scheduler combines every pet's tasks into one list, it can no longer tell which task belongs to which pet, so each task needs to carry its pet's name for filtering and display.
- I named the Task fields `title`, `duration_minutes`, and `priority` to match the names the starter `app.py` already uses. This made connecting the UI in Phase 3 much simpler.
- An earlier draft had a separate `sort_by_priority()` method. I removed it to keep the design small and focused on the required features (sorting by time, filtering, conflicts, recurrence).
- During implementation I added `Owner.get_pet()` and `Scheduler.mark_task_complete()`, so that when a recurring task is completed, its next occurrence gets added back to the right pet. The final diagram is in `diagrams/uml_final.mmd`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers four things:
- **Available time**: the owner's `available_minutes` is a hard limit. The plan never goes over it.
- **Priority**: when there isn't enough time for everything, high-priority tasks are picked first, then medium, then low.
- **Time of day**: once tasks are chosen, they're ordered by their "HH:MM" time so the plan reads like a real day.
- **Due date and status**: only tasks due today that aren't completed are included.

I made priority matter most when choosing tasks, because missing a medication or a meal is much worse for a pet than skipping a grooming session. Time of day matters most for *ordering*, because that's how an owner actually follows a plan.

**b. Tradeoffs**

My conflict detection only checks for tasks that start at the **exact same time**. It doesn't check overlapping durations. For example, a 30-minute walk at 08:00 and a task at 08:15 would not be flagged, even though they overlap.

I think this is reasonable for this app because it keeps the logic simple and easy to read (it just groups tasks by start time), and it catches the most common mistake: scheduling two things at once. Also, many pet tasks are quick (feeding, medication), and two pets' tasks can often happen at the same time anyway. Checking real overlaps would be a good improvement for a future version.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude as my main AI assistant. I used it to break the assignment into small steps, set up my environment, brainstorm the four classes and the UML diagram. The most helpful prompts were the specific ones: asking how to set up and breaking everything down into smaller steps so I could understand. Pasting my exact terminal output or error messages back to the AI was the most effective feature, because it could see exactly what went wrong on my computer.

I kept it organized by working through one phase at a time and committing to GitHub after each phase.

**b. Judgment and verification**

- The AI's first setup instructions were Mac/Linux commands (like `source .venv/bin/activate`), which was wrong, so I made sure that I did the Windows versions.
- My computer blocked programs inside the `.venv` folder, so I decided not to use a virtual environment. Instead I used the packages that were already installed and ran tools with `python -m` (for example, `python -m pytest`).
- The README template suggested `pytest --cov`, but that needs an extra package, so I used `python -m pytest` instead.
- To verify the code, I ran `python main.py` with tasks added out of order and checked that the schedule printed in correct time order. I ran `python -m pytest` after each phase (2 tests at first, then all 14 passed). I also tested the Streamlit app by hand, adding pets and tasks and checking the conflict warnings, skipped tasks, and recurring tasks.

Being in the lead meant I had to check that each piece actually worked on my computer and fit the assignment, instead of just accepting what the AI gave me.

---

## 4. Testing and Verification

**a. What you tested**

My 14 tests cover:
- **Basics**: marking a task complete, adding a task to a pet, and the Owner collecting tasks from all pets.
- **Sorting**: tasks added out of order come back in time order.
- **Filtering**: by pet name and by completed/not completed.
- **Recurring tasks**: daily tasks repeat the next day, weekly tasks repeat 7 days later, and one-time tasks don't repeat.
- **Conflicts**: two tasks at the same time get flagged (even for different pets), and different times don't.
- **Daily plan**: low-priority tasks get skipped when time runs out, and completed or future tasks are left out.
- **Edge case**: a pet with no tasks gives an empty plan instead of crashing.

These tests were important because the scheduler makes decisions automatically (what to include, what to skip, when to repeat). If one of those is wrong, a pet could miss a meal or medication, and the owner might not notice.

**b. Confidence**

I'm about 4 out of 5 confident. All 14 tests pass, and the app worked when I tested it by hand. If I had more time, I would test:
- Tasks whose durations overlap but start at different times (my current conflict check misses these).
- Two tasks with exactly the same priority and time.
- Invalid input, like a time typed in the wrong format.
- The Streamlit UI with automated tests, not just by hand.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with getting the app working. It was exciting to see the website actually add pets and tasks, build a schedule, show warnings, and create the next day's task when I marked one complete.

**b. What you would improve**

If I had another iteration, I would work on a nicer design for the app. Right now it works, but it's mostly default Streamlit forms and tables. I'd like it to look more polished and be easier to use.

**c. Key takeaway**

The most important thing I learned is the value of planning everything in an organized way. Designing the classes and the UML first, then building one phase at a time and testing after each step, made a big project feel manageable. It also made it much easier to find and fix problems along the way.