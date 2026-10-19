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
        pass

    def next_occurrence(self) -> Optional["Task"]:
        pass


@dataclass
class Pet:
    """A pet and its care tasks."""
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    """A pet owner with one or more pets."""
    name: str
    available_minutes: int = 120
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass


class Scheduler:
    """The 'brain': organizes and plans tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        pass

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[Task]:
        pass

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        pass

    def generate_daily_plan(self) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass