# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The UML design includes four classes:

- **Task** (dataclass) — Represents a single care activity (e.g., "Morning walk"). Holds a description, time, frequency, completion status, due date, and priority. Has a `mark_complete()` method.
- **Pet** (dataclass) — Represents a pet with a name and species. Owns a list of Tasks. Responsibility: manage its own task list and report task count.
- **Owner** — Represents the pet owner with a name and a list of Pets. Responsibility: manage pets and support JSON persistence (save/load).
- **Scheduler** — The orchestrator. Takes an Owner, collects all tasks from all pets, sorts by time or priority, filters, detects conflicts, finds available time slots, and manages today's schedule.

Key relationships: Owner owns Pets (composition, 1-to-many), Pet schedules Tasks (composition, 1-to-many), Scheduler drives Owner (association).

**b. Design changes**

After simplifying from the initial five-class design to four classes, the following changes were made:

1. **Removed `ScheduledTask` class** — The original design had a separate wrapper class. This added unnecessary complexity since the Scheduler can return `(pet_name, Task)` tuples directly, keeping things simpler.
2. **Added JSON persistence to `Owner`** — `save_to_json()` and `load_from_json()` let users persist their data across sessions, which is important for a practical pet care app.
3. **Expanded `Scheduler` with practical methods** — Added `detect_conflicts()`, `filter_tasks()`, `find_next_available_slot()`, and `sort_by_priority_then_time()` to make the scheduler more useful without adding extra classes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler considers **time** (tasks have an `HH:MM` slot), **priority** (high/medium/low), **due date** (tasks are scoped to a specific day), and **frequency** (daily, weekly, or one-time) as its core constraints.
- Time and priority were treated as the most important constraints because a pet owner's day revolves around "what needs to happen and when." Priority breaks ties when multiple tasks compete for attention — high-priority tasks like feeding and medication come before lower-priority grooming. Frequency was added next because routine pet care is inherently recurring, so automating the next occurrence saves the most manual effort.

**b. Tradeoffs**

- The conflict detection algorithm only checks for **exact time matches** — two tasks at "07:00" trigger a warning, but overlapping durations (e.g., a 60-minute walk at 07:00 and a feeding at 07:30) do not. This keeps the algorithm simple (O(n log n) sort + single pass) and avoids requiring a "duration" field on every task. For a pet owner's daily schedule with short, well-separated tasks, exact-match detection catches the most common conflicts without adding complexity.
- Recurring task generation creates only the **next single occurrence** when a task is completed, rather than pre-generating all future instances. This keeps the task list small and avoids stale future tasks if the owner changes their routine.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
