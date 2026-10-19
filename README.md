# 🐾 PawPal+

PawPal+ is a Streamlit app that helps a busy pet owner plan daily care for their pets. It tracks tasks like walks, feeding, and medication, then builds a daily plan that fits the owner's available time, puts the most important tasks first, warns about scheduling conflicts, and explains its choices.

## ✨ Features

- **Multiple pets per owner**: the Scheduler reads every pet's tasks through `Owner.get_all_tasks()`.
- **Sorting by time**: tasks are always shown earliest first.
- **Filtering**: view tasks by pet, by status (to do / done), or both.
- **Time budget with priorities**: the daily plan picks high-priority tasks first and skips lower-priority ones when the owner's available minutes run out.
- **Conflict warnings**: tasks scheduled at the same time (for any pets) trigger a warning instead of an error.
- **Daily and weekly recurrence**: completing a repeating task automatically creates the next one (+1 day or +7 days).
- **Plan explanation**: the app says how much time is used and why any task was skipped.

## 🚀 Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run app.py
```

Run the terminal demo:

```bash
python main.py
```

## 🛠️ Implementation Summary

All backend logic lives in `pawpal_system.py`, built from four classes:

- **Task** (dataclass): one care activity with a title, time ("HH:MM"), duration, priority, frequency, due date, completion status, and the name of its pet.
- **Pet** (dataclass): holds a pet's name, species, and list of tasks. `add_task()` also tags each task with the pet's name so tasks can be traced back to their pet.
- **Owner** (dataclass): holds the owner's name, available minutes, and pets. `get_all_tasks()` gathers every pet's tasks into one list.
- **Scheduler**: the "brain." It pulls tasks from `Owner.get_all_tasks()` and handles sorting, filtering, conflicts, recurrence, and building and explaining the daily plan.

`app.py` is the Streamlit UI. It stores the Owner in `st.session_state` so pets and tasks survive Streamlit's reruns. `main.py` is a terminal demo of every scheduler feature.

The class design is documented in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd) (the first draft is in `diagrams/uml.mmd`).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Uses `sorted()` with a lambda key on the "HH:MM" string. Zero-padded times sort correctly as text, so "07:30" comes before "18:00". |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Returns tasks for one pet, by completion status, or both. Either filter can be left out. |
| Time budget | `Scheduler.generate_daily_plan()`, `Scheduler.explain_plan()` | Picks today's unfinished tasks by priority (high → low, earlier first on ties) until the owner's available minutes run out, then orders the plan by time. `explain_plan()` says which tasks were skipped and why. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups tasks by start time and returns a warning message for any time slot with 2+ tasks, across all pets. It warns instead of crashing. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | When a daily or weekly task is completed, a new copy is created for the next day (+1) or week (+7) using `timedelta` and added to the same pet. One-time tasks don't repeat. |

## 📸 Demo Walkthrough

**Main UI features:**
- **Owner**: set your name and how many minutes you have today.
- **Pets**: add pets with a name and species (duplicate names are blocked).
- **Tasks**: add a task for any pet with a time, duration, priority, and whether it repeats (once, daily, weekly). The task table can be filtered by pet and by status, and is always sorted by time.
- **Mark complete**: pick a task and mark it done. Repeating tasks automatically get their next occurrence.
- **Today's Schedule**: generates the plan, with green success messages, yellow warnings, and a "Why this plan?" explanation.

**Example workflow:**
1. Set **Minutes available today** to 30.
2. Add two pets: **Mochi** (dog) and **Luna** (cat).
3. Add for Mochi: "Walk" at 09:00, 20 min, high priority, repeats daily.
4. Add for Luna: "Meds" at 09:00, 5 min, high priority.
5. Add for Luna: "Groom" at 07:00, 25 min, low priority.
6. Click **Generate schedule**. The app plans Walk and Meds (25 of 30 minutes), shows a **conflict warning** because both are at 09:00, and shows a **skipped warning** for Groom because it needs 25 minutes and only 5 are left.
7. Mark **Walk** complete. The app confirms the next Walk was created for tomorrow, and the task table now shows both the done Walk and tomorrow's new one.

**Key Scheduler behaviors shown:** sorting by time, priority-based time budget, conflict warnings, filtering, daily recurrence, and plan explanation.

**Sample CLI output** from `python main.py`:

```
All tasks, sorted by time
--------------------------------------------------
  07:30  Luna   Breakfast      (5 min) [high] todo
  08:00  Mochi  Morning walk   (30 min) [high] todo
  08:00  Luna   Medication     (5 min) [medium] todo
  12:00  Luna   Brush fur      (40 min) [low] todo
  16:00  Mochi  Fetch          (20 min) [medium] todo
  18:00  Mochi  Dinner         (10 min) [high] todo

Only Luna's tasks
--------------------------------------------------
  07:30  Luna   Breakfast      (5 min) [high] todo
  08:00  Luna   Medication     (5 min) [medium] todo
  12:00  Luna   Brush fur      (40 min) [low] todo

Conflict check
--------------------------------------------------
  WARNING: Conflict at 08:00: Morning walk (Mochi), Medication (Luna)

Today's Schedule for Rosandi
--------------------------------------------------
  07:30  Luna   Breakfast      (5 min) [high] todo
  08:00  Mochi  Morning walk   (30 min) [high] todo
  08:00  Luna   Medication     (5 min) [medium] todo
  16:00  Mochi  Fetch          (20 min) [medium] todo
  18:00  Mochi  Dinner         (10 min) [high] todo

Why this plan?
--------------------------------------------------
5 task(s) fit into 70 of your 90 available minutes.
Tasks were chosen by priority (high first), then ordered by time.
Skipped 'Brush fur' for Luna: needs 40 min (low priority) and there wasn't enough time left.

Recurring task
--------------------------------------------------
  Completed 'Morning walk' (due 2026-10-18)
  Next 'Morning walk' automatically created for 2026-10-19

Completed tasks
--------------------------------------------------
  08:00  Mochi  Morning walk   (30 min) [high] done
```

## 🧪 Testing PawPal+

Run the full test suite from the project folder:

```bash
python -m pytest
```

The 14 tests in `tests/test_pawpal.py` cover:

- **Basics**: marking a task complete, adding tasks to a pet, and collecting tasks from all pets through the Owner.
- **Sorting**: tasks added out of order come back in chronological order.
- **Filtering**: by pet name and by completion status.
- **Recurring tasks**: daily tasks repeat the next day, weekly tasks repeat 7 days later, and one-time tasks don't repeat.
- **Conflict detection**: two tasks at the same time are flagged (even for different pets), and different times are not.
- **Daily plan**: low-priority tasks are skipped when time runs out, and completed or future tasks are left out.
- **Edge case**: pets with no tasks produce an empty plan instead of an error.

Sample test output:

```
==================== test session starts ====================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
collected 14 items

tests\test_pawpal.py ..............                    [100%]

==================== 14 passed in 0.07s =====================
```

**Confidence level: (4/5).** Every core feature has passing tests, including edge cases. I'm holding back because conflict detection only catches tasks with the exact same start time, not overlapping durations, and the UI isn't covered by automated tests.