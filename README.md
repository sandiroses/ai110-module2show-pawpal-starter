# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

All backend logic lives in `pawpal_system.py`, built from four classes:

- **Task** (dataclass): one care activity with a title, time ("HH:MM"), duration, priority, frequency, due date, and completion status. `mark_complete()` marks it done.
- **Pet** (dataclass): holds a pet's name, species, and list of tasks. `add_task()` also tags each task with the pet's name so tasks can be traced back to their pet.
- **Owner** (dataclass): holds the owner's name, available minutes, and pets. `get_all_tasks()` gathers every pet's tasks into one list.
- **Scheduler**: the "brain." It pulls tasks from `Owner.get_all_tasks()` (so it works across all pets) and handles sorting, filtering, conflicts, recurrence, and building the daily plan.

`main.py` is a demo script that creates an owner with two pets and six tasks, then shows every scheduler feature in the terminal.

## 🖥️ Sample Output

Output from running `python main.py`:

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

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Uses `sorted()` with a lambda key on the "HH:MM" string. Zero-padded times sort correctly as text, so "07:30" comes before "18:00". |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Returns tasks for one pet, by completion status, or both. Either filter can be left out. |
| Time budget | `Scheduler.generate_daily_plan()`, `Scheduler.explain_plan()` | Picks today's unfinished tasks by priority (high → low, earlier first on ties) until the owner's available minutes run out, then orders the plan by time. `explain_plan()` says which tasks were skipped and why. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups tasks by start time and returns a warning message for any time slot with 2+ tasks, across all pets. It warns instead of crashing. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | When a daily or weekly task is completed, a new copy is created for the next day (+1) or week (+7) using `timedelta` and added to the same pet. One-time tasks don't repeat. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->