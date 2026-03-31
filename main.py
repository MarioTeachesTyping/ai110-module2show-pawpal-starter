"""PawPal+ Demo Script — verifies backend logic from the terminal."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

# ── Create Owner ──────────────────────────────────────────────
owner = Owner(name="Jordan")

# ── Create Pets ───────────────────────────────────────────────
mochi = Pet(name="Mochi", species="dog")
whiskers = Pet(name="Whiskers", species="cat")

owner.add_pet(mochi)
owner.add_pet(whiskers)

# ── Add Tasks (intentionally out of order to demo sorting) ────
mochi.add_task(Task(description="Evening play", time="17:00", priority="medium"))
mochi.add_task(Task(description="Morning walk", time="07:00", priority="high", frequency="daily"))
mochi.add_task(Task(description="Breakfast", time="08:00", priority="high", frequency="daily"))

whiskers.add_task(Task(description="Brush fur", time="17:00", priority="low", frequency="weekly"))
whiskers.add_task(Task(description="Feed wet food", time="07:00", priority="high", frequency="daily"))
whiskers.add_task(Task(description="Litter box clean", time="09:00", priority="medium"))

# ── Build Scheduler ───────────────────────────────────────────
scheduler = Scheduler(owner)

# ── 1. Sorting by time ───────────────────────────────────────
print(f"{'='*50}")
print(f"  PawPal+ Daily Schedule for {owner.name}")
print(f"  Date: {date.today().strftime('%A, %B %d, %Y')}")
print(f"{'='*50}\n")

print("── Sorted by time ──")
for pet_name, task in scheduler.sort_by_time():
    status = "✓" if task.completed else "○"
    print(f"  {task.time}  [{status}]  {task.description:<20}  ({pet_name})  priority: {task.priority}")

# ── 2. Conflict Detection ────────────────────────────────────
# Mochi's "Morning walk" and Whiskers' "Feed wet food" are both at 07:00;
# Mochi's "Evening play" and Whiskers' "Brush fur" are both at 17:00.
conflicts = scheduler.detect_conflicts()
if conflicts:
    print(f"\n⚠  Scheduling Conflicts:")
    for c in conflicts:
        print(f"   • {c}")

# ── 3. Filtering by pet and status ───────────────────────────
print(f"\n── Whiskers' tasks only ──")
for pet_name, task in scheduler.filter_tasks(pet_name="Whiskers"):
    print(f"  {task.time}  {task.description:<20}  priority: {task.priority}")

# ── 4. Recurring task automation ─────────────────────────────
print(f"\n── Completing Mochi's daily 'Morning walk' ──")
new_task = scheduler.mark_task_complete("Mochi", "Morning walk")
if new_task:
    print(f"  ✓ Completed! Next occurrence auto-scheduled for {new_task.due_date}")

# Show updated state: incomplete tasks only
print(f"\n── Remaining incomplete tasks ──")
incomplete = scheduler.filter_tasks(completed=False)
for pet_name, task in scheduler.sort_by_time():
    if not task.completed:
        freq_tag = f" [{task.frequency}]" if task.frequency != "daily" else ""
        print(f"  {task.time}  {task.description:<20}  ({pet_name})  due: {task.due_date}{freq_tag}")

# ── 5. Sort by priority then time ────────────────────────────
print(f"\n── All tasks by priority → time ──")
for pet_name, task in scheduler.sort_by_priority_then_time():
    status = "✓" if task.completed else "○"
    print(f"  [{task.priority:<6}] {task.time}  [{status}]  {task.description:<20}  ({pet_name})")

print(f"\n{'='*50}")
print("  Demo complete!")
print(f"{'='*50}")
