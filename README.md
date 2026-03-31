# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ includes several algorithmic features that make daily pet care planning more intelligent:

- **Sort by time** — Tasks can be sorted chronologically by their `HH:MM` time string using `Scheduler.sort_by_time()`, making it easy to view the day in order even when tasks are added randomly.
- **Sort by priority then time** — `Scheduler.sort_by_priority_then_time()` groups tasks by priority level (high → medium → low) and then sorts within each group by time.
- **Filter by pet or status** — `Scheduler.filter_tasks()` accepts optional `pet_name` and `completed` parameters to narrow down the task list.
- **Recurring task automation** — When a daily or weekly task is marked complete via `Scheduler.mark_task_complete()`, a new task instance is automatically created for the next occurrence (using `timedelta` for date math), so the owner never has to re-enter routine tasks.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans all scheduled tasks and returns warning messages for any tasks that share the exact same time slot, without crashing the program.
