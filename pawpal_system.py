"""PawPal+ Logic Layer — class skeletons derived from UML design."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta


# ---------------------------------------------------------------------------
# Priority ordering helper
# ---------------------------------------------------------------------------
_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


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
        if self.completed:
            return None
        self.completed = True
        return self


@dataclass
class Pet:
    """A pet belonging to an owner."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        return len(self.tasks)


class Owner:
    """The pet owner who manages pets."""

    def __init__(self, name: str, pets: list[Pet] | None = None) -> None:
        self.name = name
        self.pets: list[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def save_to_json(self, filepath: str) -> None:
        """Persist owner, pets, and tasks to a JSON file."""
        data = {
            "name": self.name,
            "pets": [
                {
                    "name": pet.name,
                    "species": pet.species,
                    "tasks": [
                        {**asdict(task), "due_date": task.due_date.isoformat()}
                        for task in pet.tasks
                    ],
                }
                for pet in self.pets
            ],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_from_json(filepath: str) -> Owner:
        """Load an Owner (with pets and tasks) from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        pets: list[Pet] = []
        for pet_data in data.get("pets", []):
            tasks = [
                Task(
                    description=t["description"],
                    time=t.get("time", ""),
                    frequency=t.get("frequency", "daily"),
                    completed=t.get("completed", False),
                    due_date=date.fromisoformat(t["due_date"]) if t.get("due_date") else date.today(),
                    priority=t.get("priority", "medium"),
                )
                for t in pet_data.get("tasks", [])
            ]
            pets.append(Pet(name=pet_data["name"], species=pet_data["species"], tasks=tasks))
        return Owner(name=data["name"], pets=pets)


class Scheduler:
    """Generates and manages a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Return all tasks across pets as (pet_name, task) tuples."""
        return [
            (pet.name, task)
            for pet in self.owner.get_pets()
            for task in pet.tasks
        ]

    def sort_by_time(self) -> list[tuple[str, Task]]:
        """Return all tasks sorted by their scheduled time.

        Uses a lambda key to compare time strings in "HH:MM" format.
        Tasks without a time are sorted to the beginning.
        """
        return sorted(self.get_all_tasks(), key=lambda t: t[1].time)

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[str, Task]]:
        """Filter tasks by pet name and/or completion status.

        Args:
            pet_name: If provided, only return tasks for this pet.
            completed: If provided, only return tasks matching this completion state.

        Returns:
            A filtered list of (pet_name, Task) tuples.
        """
        results = self.get_all_tasks()
        if pet_name is not None:
            results = [(pn, t) for pn, t in results if pn == pet_name]
        if completed is not None:
            results = [(pn, t) for pn, t in results if t.completed == completed]
        return results

    def detect_conflicts(self) -> list[str]:
        """Detect scheduling conflicts where two tasks share the exact same time.

        Uses a lightweight approach: sorts all timed tasks and checks adjacent
        pairs for matching times. Returns warning messages rather than raising
        exceptions, so the program continues running.

        Returns:
            A list of human-readable conflict warning strings.
        """
        timed = [(pn, t) for pn, t in self.get_all_tasks() if t.time]
        timed.sort(key=lambda x: x[1].time)
        conflicts: list[str] = []
        for i in range(len(timed) - 1):
            if timed[i][1].time == timed[i + 1][1].time:
                conflicts.append(
                    f"Conflict at {timed[i][1].time}: "
                    f"'{timed[i][1].description}' ({timed[i][0]}) and "
                    f"'{timed[i + 1][1].description}' ({timed[i + 1][0]})"
                )
        return conflicts

    def mark_task_complete(self, pet_name: str, description: str) -> Task | None:
        """Mark a task as complete and auto-schedule recurring tasks.

        When a task with frequency "daily" or "weekly" is completed, a new
        Task instance is automatically created for the next occurrence using
        Python's timedelta (1 day for daily, 7 days for weekly).

        Args:
            pet_name: Name of the pet that owns the task.
            description: Description string of the task to complete.

        Returns:
            The newly created recurring Task if one was generated, or None.
        """
        for pet in self.owner.get_pets():
            if pet.name == pet_name:
                for task in pet.tasks:
                    if task.description == description and not task.completed:
                        task.mark_complete()
                        # Auto-schedule recurring tasks
                        if task.frequency == "daily":
                            next_task = Task(
                                description=task.description,
                                time=task.time,
                                frequency=task.frequency,
                                due_date=task.due_date + timedelta(days=1),
                                priority=task.priority,
                            )
                            pet.add_task(next_task)
                            return next_task
                        elif task.frequency == "weekly":
                            next_task = Task(
                                description=task.description,
                                time=task.time,
                                frequency=task.frequency,
                                due_date=task.due_date + timedelta(days=7),
                                priority=task.priority,
                            )
                            pet.add_task(next_task)
                            return next_task
                        return None
        return None

    def get_today_schedule(self) -> list[tuple[str, Task]]:
        """Return tasks due today, sorted by time."""
        today = date.today()
        return sorted(
            [(pn, t) for pn, t in self.get_all_tasks() if t.due_date == today],
            key=lambda x: x[1].time,
        )

    def find_next_available_slot(self, pet_name: str, duration_minutes: int) -> str:
        """Find the next open time slot of the given duration for a pet."""
        pet_tasks = [t for pn, t in self.get_all_tasks() if pn == pet_name and t.time]
        occupied = sorted(t.time for t in pet_tasks)

        candidate = datetime.strptime("08:00", "%H:%M")
        end_of_day = datetime.strptime("20:00", "%H:%M")

        for occ_time_str in occupied:
            occ = datetime.strptime(occ_time_str, "%H:%M")
            if candidate + timedelta(minutes=duration_minutes) <= occ:
                return candidate.strftime("%H:%M")
            candidate = occ + timedelta(minutes=30)  # assume 30-min default slots

        if candidate + timedelta(minutes=duration_minutes) <= end_of_day:
            return candidate.strftime("%H:%M")
        return ""

    def sort_by_priority_then_time(self) -> list[tuple[str, Task]]:
        """Return all tasks sorted first by priority (high → low), then by time.

        Uses a composite sort key: priority rank from _PRIORITY_ORDER dict,
        then the time string for secondary ordering.
        """
        return sorted(
            self.get_all_tasks(),
            key=lambda x: (_PRIORITY_ORDER.get(x[1].priority, 1), x[1].time),
        )
