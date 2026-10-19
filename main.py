"""Demo script: builds a sample owner, pets, and tasks, then shows the scheduler's features."""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_tasks(heading, tasks):
    """Print a heading and a neat table of tasks."""
    print(f"\n{heading}")
    print("-" * 50)
    if not tasks:
        print("  (none)")
    for task in tasks:
        status = "done" if task.completed else "todo"
        print(f"  {task.time}  {task.pet_name:<6} {task.title:<14} "
              f"({task.duration_minutes} min) [{task.priority}] {status}")


# Create the owner and two pets
owner = Owner(name="Rosandi", available_minutes=90)
mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")
owner.add_pet(mochi)
owner.add_pet(luna)

# Add tasks OUT OF ORDER on purpose, including one time conflict (08:00)
mochi.add_task(Task(title="Dinner", time="18:00", duration_minutes=10, priority="high", frequency="daily"))
luna.add_task(Task(title="Brush fur", time="12:00", duration_minutes=40, priority="low"))
mochi.add_task(Task(title="Morning walk", time="08:00", duration_minutes=30, priority="high", frequency="daily"))
luna.add_task(Task(title="Breakfast", time="07:30", duration_minutes=5, priority="high"))
luna.add_task(Task(title="Medication", time="08:00", duration_minutes=5, priority="medium"))
mochi.add_task(Task(title="Fetch", time="16:00", duration_minutes=20, priority="medium"))

scheduler = Scheduler(owner)

# 1. Sorting
print_tasks("All tasks, sorted by time", scheduler.sort_by_time(owner.get_all_tasks()))

# 2. Filtering
print_tasks("Only Luna's tasks", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")))

# 3. Conflict detection
print("\nConflict check")
print("-" * 50)
conflicts = scheduler.detect_conflicts(owner.get_all_tasks())
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts found")

# 4. Today's plan (fits the owner's available time) + explanation
print_tasks(f"Today's Schedule for {owner.name}", scheduler.generate_daily_plan())
print("\nWhy this plan?")
print("-" * 50)
print(scheduler.explain_plan())

# 5. Recurring tasks
walk = next(t for t in mochi.get_tasks() if t.title == "Morning walk")
next_walk = scheduler.mark_task_complete(walk)
print("\nRecurring task")
print("-" * 50)
print(f"  Completed '{walk.title}' (due {walk.due_date})")
print(f"  Next '{next_walk.title}' automatically created for {next_walk.due_date}")
print_tasks("Completed tasks", scheduler.filter_tasks(completed=True))