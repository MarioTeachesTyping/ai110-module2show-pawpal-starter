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

# ── Add Tasks ─────────────────────────────────────────────────
mochi.add_task(Task(description="Morning walk", time="07:00", priority="high"))
mochi.add_task(Task(description="Breakfast", time="08:00", priority="high"))
mochi.add_task(Task(description="Evening play", time="17:00", priority="medium"))

whiskers.add_task(Task(description="Feed wet food", time="07:30", priority="high"))
whiskers.add_task(Task(description="Litter box clean", time="09:00", priority="medium"))
whiskers.add_task(Task(description="Brush fur", time="17:00", priority="low"))

# ── Build Scheduler ───────────────────────────────────────────
scheduler = Scheduler(owner)

# ── Print Today's Schedule ────────────────────────────────────
print(f"{'='*50}")
print(f"  PawPal+ Daily Schedule for {owner.name}")
print(f"  Date: {date.today().strftime('%A, %B %d, %Y')}")
print(f"{'='*50}\n")

schedule = scheduler.get_today_schedule()

for pet_name, task in schedule:
    status = "✓" if task.completed else "○"
    print(f"  {task.time}  [{status}]  {task.description:<20}  ({pet_name})  priority: {task.priority}")

# ── Detect Conflicts ──────────────────────────────────────────
conflicts = scheduler.detect_conflicts()
if conflicts:
    print(f"\n⚠  Scheduling Conflicts:")
    for c in conflicts:
        print(f"   • {c}")

# ── Mark a task complete and show filtered view ───────────────
scheduler.mark_task_complete("Mochi", "Morning walk")
print(f"\n── After completing Mochi's morning walk ──")
incomplete = scheduler.filter_tasks(completed=False)
for pet_name, task in incomplete:
    print(f"  {task.time}  {task.description:<20}  ({pet_name})")

# ── Sort by priority then time ────────────────────────────────
print(f"\n── All tasks by priority → time ──")
for pet_name, task in scheduler.sort_by_priority_then_time():
    status = "✓" if task.completed else "○"
    print(f"  [{task.priority:<6}] {task.time}  [{status}]  {task.description:<20}  ({pet_name})")

print(f"\n{'='*50}")
print("  Demo complete!")
print(f"{'='*50}")
