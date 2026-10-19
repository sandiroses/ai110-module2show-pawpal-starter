"""PawPal+ logic layer: classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


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
        """Return the next copy of a recurring task (implemented in Phase 4)."""
        pass


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

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered from earliest to latest time."""
        return sorted(tasks, key=lambda task: task.time)

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[Task]:
        """Filter tasks by pet or completion status (implemented in Phase 4)."""
        pass

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Find tasks scheduled at the same time (implemented in Phase 4)."""
        pass

    def generate_daily_plan(self) -> List[Task]:
        """Return today's unfinished tasks for all pets, sorted by time."""
        today = date.today()
        todays_tasks = [
            task for task in self.owner.get_all_tasks()
            if task.due_date == today and not task.completed
        ]
        return self.sort_by_time(todays_tasks)

    def explain_plan(self) -> str:
        """Explain why tasks were chosen (implemented in Phase 4)."""
        pass