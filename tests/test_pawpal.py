"""Tests for PawPal+ core logic."""

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
