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
- I named the Task fields `title`, `duration_minutes`, and `priority` to match the names the starter `app.py` already uses. This will make connecting the UI in Phase 3 much simpler.
- An earlier draft had a separate `sort_by_priority()` method. I removed it to keep the design small and focused on the required features (sorting by time, filtering, conflicts, recurrence).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?