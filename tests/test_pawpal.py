"""Tests for PawPal+ core logic."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


# ── Task Completion ───────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task(description="Morning walk", time="07:00")
    assert task.completed is False
    result = task.mark_complete()
    assert task.completed is True
    assert result is task


def test_mark_complete_returns_none_if_already_done():
    task = Task(description="Morning walk", time="07:00", completed=True)
    result = task.mark_complete()
    assert result is None


# ── Task Addition ─────────────────────────────────────────────

def test_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog")
    assert pet.task_count() == 0
    pet.add_task(Task(description="Walk"))
    assert pet.task_count() == 1
    pet.add_task(Task(description="Feed"))
    assert pet.task_count() == 2


def test_add_pet_to_owner():
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))
    assert len(owner.get_pets()) == 1


# ── Scheduler ─────────────────────────────────────────────────

def test_get_all_tasks_across_pets():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(Task(description="Walk", time="07:00"))
    whiskers = Pet(name="Whiskers", species="cat")
    whiskers.add_task(Task(description="Feed", time="08:00"))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    scheduler = Scheduler(owner)
    all_tasks = scheduler.get_all_tasks()
    assert len(all_tasks) == 2
    assert all_tasks[0][0] == "Mochi"
    assert all_tasks[1][0] == "Whiskers"


def test_detect_conflicts():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(Task(description="Walk", time="07:00"))
    whiskers = Pet(name="Whiskers", species="cat")
    whiskers.add_task(Task(description="Feed", time="07:00"))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "07:00" in conflicts[0]


# ── Sorting Correctness ──────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order should come back sorted by time."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Groom", time="15:00"))
    pet.add_task(Task(description="Walk", time="07:00"))
    pet.add_task(Task(description="Feed", time="12:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for _, t in sorted_tasks]
    assert times == ["07:00", "12:00", "15:00"]


def test_sort_by_time_tasks_without_time_come_first():
    """Tasks with no time string should sort to the beginning."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk", time="07:00"))
    pet.add_task(Task(description="Brush teeth", time=""))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()
    assert sorted_tasks[0][1].description == "Brush teeth"
    assert sorted_tasks[1][1].description == "Walk"


def test_sort_by_priority_then_time():
    """High-priority tasks come first; within the same priority, sort by time."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk", time="09:00", priority="low"))
    pet.add_task(Task(description="Meds", time="08:00", priority="high"))
    pet.add_task(Task(description="Feed", time="07:00", priority="high"))
    pet.add_task(Task(description="Play", time="10:00", priority="medium"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    result = scheduler.sort_by_priority_then_time()
    descriptions = [t.description for _, t in result]
    assert descriptions == ["Feed", "Meds", "Play", "Walk"]


# ── Recurrence Logic ─────────────────────────────────────────

def test_daily_recurrence_creates_next_day_task():
    """Completing a daily task should auto-create a new task for tomorrow."""
    today = date.today()
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk", time="07:00", frequency="daily", due_date=today))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    new_task = scheduler.mark_task_complete("Mochi", "Walk")

    assert new_task is not None
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False
    assert new_task.description == "Walk"
    # Original task should be marked complete
    assert pet.tasks[0].completed is True
    # Pet should now have 2 tasks (original + new)
    assert pet.task_count() == 2


def test_weekly_recurrence_creates_next_week_task():
    """Completing a weekly task should create a new task 7 days later."""
    today = date.today()
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Grooming", time="10:00", frequency="weekly", due_date=today))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    new_task = scheduler.mark_task_complete("Mochi", "Grooming")

    assert new_task is not None
    assert new_task.due_date == today + timedelta(days=7)
    assert new_task.completed is False


def test_one_time_task_no_recurrence():
    """A task with frequency 'once' should not create a new task."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Vet visit", time="14:00", frequency="once"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    result = scheduler.mark_task_complete("Mochi", "Vet visit")

    assert result is None
    assert pet.task_count() == 1
    assert pet.tasks[0].completed is True


# ── Conflict Detection (additional) ──────────────────────────

def test_no_conflicts_when_times_differ():
    """No conflicts should be reported when all tasks have distinct times."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk", time="07:00"))
    pet.add_task(Task(description="Feed", time="08:00"))
    pet.add_task(Task(description="Play", time="09:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


def test_multiple_conflicts_detected():
    """Multiple overlapping times should each produce a conflict."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk", time="07:00"))
    pet.add_task(Task(description="Feed", time="07:00"))
    pet.add_task(Task(description="Play", time="09:00"))
    pet.add_task(Task(description="Groom", time="09:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 2


# ── Edge Cases ────────────────────────────────────────────────

def test_pet_with_no_tasks():
    """A pet with zero tasks should not break sorting or conflict detection."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))

    scheduler = Scheduler(owner)
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.filter_tasks() == []


def test_filter_tasks_by_pet_name():
    """Filtering by pet name should return only that pet's tasks."""
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(Task(description="Walk", time="07:00"))
    whiskers = Pet(name="Whiskers", species="cat")
    whiskers.add_task(Task(description="Feed", time="08:00"))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    scheduler = Scheduler(owner)
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    assert len(mochi_tasks) == 1
    assert mochi_tasks[0][0] == "Mochi"


def test_filter_tasks_by_completion_status():
    """Filtering by completed=False should exclude completed tasks."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk", time="07:00", completed=True))
    pet.add_task(Task(description="Feed", time="08:00", completed=False))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    incomplete = scheduler.filter_tasks(completed=False)
    assert len(incomplete) == 1
    assert incomplete[0][1].description == "Feed"


def test_mark_complete_nonexistent_task_returns_none():
    """Trying to complete a task that doesn't exist should return None."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))

    scheduler = Scheduler(owner)
    result = scheduler.mark_task_complete("Mochi", "Nonexistent task")
    assert result is None
