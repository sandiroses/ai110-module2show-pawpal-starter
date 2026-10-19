"""Tests for the PawPal+ system."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def make_owner(available_minutes=120):
    """Build an owner with two pets (Mochi the dog and Luna the cat) and no tasks."""
    owner = Owner(name="Test", available_minutes=available_minutes)
    owner.add_pet(Pet(name="Mochi", species="dog"))
    owner.add_pet(Pet(name="Luna", species="cat"))
    return owner


# --- Basic behavior ---------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should set completed to True."""
    task = Task(title="Walk", time="08:00", duration_minutes=20)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a pet should increase its task count by one."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(title="Feed", time="09:00", duration_minutes=10))
    assert len(pet.get_tasks()) == 1


def test_owner_collects_tasks_from_all_pets():
    """get_all_tasks() should include tasks from every pet."""
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task(title="Walk", time="08:00", duration_minutes=20))
    owner.get_pet("Luna").add_task(Task(title="Feed", time="09:00", duration_minutes=5))
    assert len(owner.get_all_tasks()) == 2


# --- Sorting ----------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order should come back earliest first."""
    owner = make_owner()
    mochi = owner.get_pet("Mochi")
    for t in ["18:00", "07:30", "12:00"]:
        mochi.add_task(Task(title=f"Task {t}", time=t, duration_minutes=5))
    result = Scheduler(owner).sort_by_time(owner.get_all_tasks())
    assert [t.time for t in result] == ["07:30", "12:00", "18:00"]


# --- Filtering --------------------------------------------------------------

def test_filter_by_pet_name():
    """Filtering by pet name should return only that pet's tasks."""
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task(title="Walk", time="08:00", duration_minutes=20))
    owner.get_pet("Luna").add_task(Task(title="Feed", time="09:00", duration_minutes=5))
    result = Scheduler(owner).filter_tasks(pet_name="Luna")
    assert [t.title for t in result] == ["Feed"]


def test_filter_by_completion_status():
    """Filtering by completed=True should return only finished tasks."""
    owner = make_owner()
    mochi = owner.get_pet("Mochi")
    done = Task(title="Walk", time="08:00", duration_minutes=20)
    mochi.add_task(done)
    mochi.add_task(Task(title="Dinner", time="18:00", duration_minutes=10))
    done.mark_complete()
    result = Scheduler(owner).filter_tasks(completed=True)
    assert result == [done]


# --- Recurring tasks --------------------------------------------------------

def test_daily_task_creates_next_day_task():
    """Completing a daily task should add a new, unfinished copy due tomorrow."""
    owner = make_owner()
    mochi = owner.get_pet("Mochi")
    walk = Task(title="Walk", time="08:00", duration_minutes=20, frequency="daily")
    mochi.add_task(walk)

    next_walk = Scheduler(owner).mark_task_complete(walk)

    assert walk.completed is True
    assert next_walk.due_date == walk.due_date + timedelta(days=1)
    assert next_walk.completed is False
    assert next_walk in mochi.get_tasks()


def test_weekly_task_creates_next_week_task():
    """Completing a weekly task should add a copy due 7 days later."""
    owner = make_owner()
    bath = Task(title="Bath", time="10:00", duration_minutes=30, frequency="weekly")
    owner.get_pet("Mochi").add_task(bath)
    next_bath = Scheduler(owner).mark_task_complete(bath)
    assert next_bath.due_date == bath.due_date + timedelta(days=7)


def test_one_time_task_does_not_repeat():
    """Completing a one-time task should not create another task."""
    owner = make_owner()
    vet = Task(title="Vet visit", time="14:00", duration_minutes=60)
    owner.get_pet("Luna").add_task(vet)
    assert Scheduler(owner).mark_task_complete(vet) is None
    assert len(owner.get_all_tasks()) == 1


# --- Conflict detection -----------------------------------------------------

def test_conflict_detected_for_same_time_across_pets():
    """Two tasks at the same time (even for different pets) should produce a warning."""
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task(title="Walk", time="08:00", duration_minutes=20))
    owner.get_pet("Luna").add_task(Task(title="Meds", time="08:00", duration_minutes=5))
    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_no_conflict_when_times_differ():
    """Tasks at different times should not produce warnings."""
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task(title="Walk", time="08:00", duration_minutes=20))
    owner.get_pet("Luna").add_task(Task(title="Meds", time="09:00", duration_minutes=5))
    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


# --- Daily plan / time budget -------------------------------------------------

def test_plan_skips_low_priority_when_time_runs_out():
    """With limited time, high-priority tasks are kept and lower ones skipped."""
    owner = make_owner(available_minutes=30)
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task(title="Groom", time="07:00", duration_minutes=25, priority="low"))
    mochi.add_task(Task(title="Walk", time="08:00", duration_minutes=25, priority="high"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()

    assert [t.title for t in plan] == ["Walk"]
    assert [t.title for t in scheduler.skipped] == ["Groom"]


def test_plan_ignores_completed_and_future_tasks():
    """Today's plan should leave out finished tasks and tasks due another day."""
    owner = make_owner()
    mochi = owner.get_pet("Mochi")
    done = Task(title="Breakfast", time="07:00", duration_minutes=5)
    mochi.add_task(done)
    done.mark_complete()
    mochi.add_task(Task(title="Bath", time="10:00", duration_minutes=30,
                        due_date=date.today() + timedelta(days=1)))
    mochi.add_task(Task(title="Walk", time="08:00", duration_minutes=20))

    plan = Scheduler(owner).generate_daily_plan()
    assert [t.title for t in plan] == ["Walk"]


# --- Edge cases -------------------------------------------------------------

def test_pet_with_no_tasks_gives_empty_plan():
    """An owner whose pets have no tasks should get an empty plan, not an error."""
    owner = make_owner()
    scheduler = Scheduler(owner)
    assert scheduler.generate_daily_plan() == []
    assert scheduler.detect_conflicts(owner.get_all_tasks()) == []