"""PawPal+ logic layer: classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import List, Optional

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet care activity."""
    title: str
    time: str                      # "HH:MM", e.g. "08:00"
    duration_minutes: int
    priority: str = "medium"       # "low", "medium", or "high"
    frequency: str = "once"        # "once", "daily", or "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh copy for the next day/week, or None if the task is one-time."""
        if self.frequency == "daily":
            days = 1
        elif self.frequency == "weekly":
            days = 7
        else:
            return None
        return replace(self, due_date=self.due_date + timedelta(days=days), completed=False)


@dataclass
class Pet:
    """A pet and its care tasks."""
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return this pet's tasks."""
        return self.tasks


@dataclass
class Owner:
    """A pet owner with one or more pets."""
    name: str
    available_minutes: int = 120
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the pet with this name, or None if there isn't one."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return every task from every pet in one list."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """The 'brain': organizes and plans tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Store the owner whose pets' tasks will be scheduled."""
        self.owner = owner
        self.skipped: List[Task] = []

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered from earliest to latest "HH:MM" time."""
        return sorted(tasks, key=lambda task: task.time)

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[Task]:
        """Return the owner's tasks, optionally only for one pet and/or one completion status."""
        result = []
        for task in self.owner.get_all_tasks():
            if pet_name is not None and task.pet_name != pet_name:
                continue
            if completed is not None and task.completed != completed:
                continue
            result.append(task)
        return result

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return a warning for every time slot that has more than one task (exact time match)."""
        by_time = {}
        for task in tasks:
            by_time.setdefault(task.time, []).append(task)

        warnings = []
        for slot, slot_tasks in sorted(by_time.items()):
            if len(slot_tasks) > 1:
                names = ", ".join(f"{t.title} ({t.pet_name})" for t in slot_tasks)
                warnings.append(f"Conflict at {slot}: {names}")
        return warnings

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; if it repeats, add its next occurrence to the same pet and return it."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    def generate_daily_plan(self) -> List[Task]:
        """Pick today's unfinished tasks by priority until time runs out, then sort them by time."""
        today = date.today()
        candidates = [
            task for task in self.owner.get_all_tasks()
            if task.due_date == today and not task.completed
        ]
        # Most important first; ties go to the earlier task.
        candidates.sort(key=lambda t: (PRIORITY_RANK.get(t.priority, 1), t.time))

        chosen, self.skipped = [], []
        minutes_left = self.owner.available_minutes
        for task in candidates:
            if task.duration_minutes <= minutes_left:
                chosen.append(task)
                minutes_left -= task.duration_minutes
            else:
                self.skipped.append(task)
        return self.sort_by_time(chosen)

    def explain_plan(self) -> str:
        """Explain which tasks made it into today's plan and why others were skipped."""
        plan = self.generate_daily_plan()
        used = sum(t.duration_minutes for t in plan)
        lines = [
            f"{len(plan)} task(s) fit into {used} of your "
            f"{self.owner.available_minutes} available minutes.",
            "Tasks were chosen by priority (high first), then ordered by time.",
        ]
        for task in self.skipped:
            lines.append(
                f"Skipped '{task.title}' for {task.pet_name}: needs "
                f"{task.duration_minutes} min ({task.priority} priority) "
                f"and there wasn't enough time left."
            )
        return "\n".join(lines)