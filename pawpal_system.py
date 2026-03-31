"""PawPal+ Logic Layer — class skeletons derived from UML design."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, grooming, etc.)."""

    description: str
    time: str = ""
    frequency: str = "daily"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    priority: str = "medium"  # "low", "medium", "high"

    def mark_complete(self) -> Task | None:
        """Mark this task as completed and return it, or None if already done."""
        ...


@dataclass
class Pet:
    """A pet belonging to an owner."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        ...

    def task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        ...


class Owner:
    """The pet owner who manages pets."""

    def __init__(self, name: str, pets: list[Pet] | None = None) -> None:
        self.name = name
        self.pets: list[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        ...

    def get_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        ...

    def save_to_json(self, filepath: str) -> None:
        """Persist owner, pets, and tasks to a JSON file."""
        ...

    @staticmethod
    def load_from_json(filepath: str) -> Owner:
        """Load an Owner (with pets and tasks) from a JSON file."""
        ...


class Scheduler:
    """Generates and manages a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Return all tasks across pets as (pet_name, task) tuples."""
        ...

    def sort_by_time(self) -> list[tuple[str, Task]]:
        """Return all tasks sorted by their scheduled time."""
        ...

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[str, Task]]:
        """Filter tasks by pet name and/or completion status."""
        ...

    def detect_conflicts(self) -> list[str]:
        """Return descriptions of any scheduling conflicts (overlapping times)."""
        ...

    def mark_task_complete(self, pet_name: str, description: str) -> None:
        """Mark a specific task as complete by pet name and task description."""
        ...

    def get_today_schedule(self) -> list[tuple[str, Task]]:
        """Return tasks due today, sorted by time."""
        ...

    def find_next_available_slot(self, pet_name: str, duration_minutes: int) -> str:
        """Find the next open time slot of the given duration for a pet."""
        ...

    def sort_by_priority_then_time(self) -> list[tuple[str, Task]]:
        """Return all tasks sorted first by priority, then by time."""
        ...
