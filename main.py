"""Demo script: builds a sample owner, pets, and tasks, then prints today's schedule."""

from pawpal_system import Owner, Pet, Task, Scheduler

# Create the owner and two pets
owner = Owner(name="Rosandi", available_minutes=90)
mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")
owner.add_pet(mochi)
owner.add_pet(luna)

# Add tasks with different times
mochi.add_task(Task(title="Morning walk", time="08:00", duration_minutes=30, priority="high"))
mochi.add_task(Task(title="Dinner", time="18:00", duration_minutes=10, priority="high"))
luna.add_task(Task(title="Breakfast", time="07:30", duration_minutes=5, priority="high"))
luna.add_task(Task(title="Brush fur", time="12:00", duration_minutes=15, priority="low"))

# Build and print today's schedule
scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan()

print(f"Today's Schedule for {owner.name}")
print("=" * 40)
for task in plan:
    print(f"  {task.time}  {task.pet_name:<6} {task.title:<14} "
          f"({task.duration_minutes} min) [{task.priority}]")
print("=" * 40)
print(f"{len(plan)} tasks planned")