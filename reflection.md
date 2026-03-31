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

- I used VS Code Copilot throughout every phase of this project — from UML design brainstorming to implementing scheduling logic, writing tests, and polishing the Streamlit UI.
- **Copilot Chat** was the most effective feature for building the scheduler. I could describe a method's purpose in natural language (e.g., "detect scheduling conflicts by comparing time slots") and get a working implementation to evaluate. Inline completions also accelerated routine code like dataclass fields and test boilerplate.
- The most helpful prompts were specific, constrained requests: "Given my current `Task` dataclass, write a method that marks it complete and returns `None` if already done" worked much better than vague prompts like "make the scheduler smarter."

**b. Judgment and verification**

- One AI suggestion I rejected: Copilot initially suggested a `ScheduledTask` wrapper class to pair each task with its pet name. I rejected this because simple `(pet_name, Task)` tuples served the same purpose without adding a fifth class. Keeping the design at four classes reduced complexity and made the codebase easier to test and maintain.
- I verified AI suggestions by running `pytest` after every change to confirm existing tests still passed, and by manually tracing the logic for edge cases (e.g., what happens when a pet has zero tasks, or when a non-existent task is marked complete).
- Using separate chat sessions for different phases (design, implementation, testing, UI) helped keep the context focused. Each session could reference the specific files being worked on without carrying irrelevant history from earlier phases.

---

## 4. Testing and Verification

**a. What you tested**

- The test suite (18 tests) covers the core behaviors of every class: task completion toggling, pet/task management, chronological sorting, priority-based sorting, daily and weekly recurrence, one-time task handling, single and multiple conflict detection, filtering by pet name and completion status, and edge cases like empty pet task lists and nonexistent tasks.
- These tests are important because the scheduler is the "brain" of the app — if sorting is wrong, the owner sees a confusing schedule; if recurrence breaks, routine tasks silently stop appearing; if conflict detection fails, overlapping tasks go unnoticed. Each test targets a specific behavior that a real user would depend on.

**b. Confidence**

- Confidence: ⭐⭐⭐⭐⭐ (5/5). All 18 tests pass, covering happy paths, recurrence logic, conflict detection, and edge cases.
- If I had more time, I would test: tasks with identical descriptions on different pets, JSON round-trip (save then load and verify equality), time-boundary edge cases (e.g., tasks at "00:00" and "23:59"), and the `find_next_available_slot` method with a fully packed schedule.

---

## 5. Reflection

**a. What went well**

- I'm most satisfied with how the four-class architecture stayed clean from UML through final implementation. The `Scheduler` class cleanly separates orchestration logic (sorting, filtering, conflicts, recurrence) from data ownership (`Owner`/`Pet`/`Task`), making each piece independently testable. The 18-test suite gave me confidence to refactor freely without fear of breaking things.

**b. What you would improve**

- I would add task duration so conflict detection could catch overlapping time ranges, not just exact matches. I'd also add a data persistence layer to the Streamlit app (using `save_to_json`/`load_from_json`) so tasks survive between sessions, and build a "weekly overview" view that shows recurring tasks across multiple days.

**c. Key takeaway**

- The most important lesson was that when collaborating with AI, I need to be the architect who makes design decisions — not just accept whatever code is generated. AI is excellent at producing working code fast, but the human engineer must decide *what* to build, evaluate tradeoffs (like dropping the `ScheduledTask` class for simplicity), and verify correctness through tests. The AI amplifies my productivity, but the design judgment is mine.
