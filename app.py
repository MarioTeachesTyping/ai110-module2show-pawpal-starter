import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown("A pet care planning assistant that helps you stay on top of daily tasks.")

# ── Session-state: keep Owner alive across reruns ─────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner

# ── Sidebar: Owner info ──────────────────────────────────────
with st.sidebar:
    st.header("Owner")
    new_name = st.text_input("Owner name", value=owner.name)
    if new_name != owner.name:
        owner.name = new_name

    st.divider()
    st.subheader("Your Pets")
    if owner.get_pets():
        for pet in owner.get_pets():
            st.write(f"**{pet.name}** ({pet.species}) — {pet.task_count()} tasks")
    else:
        st.info("No pets yet. Add one below.")

# ── Add a Pet ─────────────────────────────────────────────────
st.subheader("Add a Pet")
col_pet1, col_pet2 = st.columns(2)
with col_pet1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_pet2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if pet_name.strip():
        owner.add_pet(Pet(name=pet_name.strip(), species=species))
        st.success(f"Added {pet_name}!")
        st.rerun()

st.divider()

# ── Add a Task ────────────────────────────────────────────────
st.subheader("Add a Task")

pet_names = [p.name for p in owner.get_pets()]
if pet_names:
    selected_pet = st.selectbox("Assign to pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_desc = st.text_input("Task description", value="Morning walk")
    with col2:
        task_time = st.text_input("Time (HH:MM)", value="07:00")
    with col3:
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])

    if st.button("Add task"):
        pet = next(p for p in owner.get_pets() if p.name == selected_pet)
        pet.add_task(
            Task(
                description=task_desc,
                time=task_time,
                priority=priority,
                frequency=frequency,
            )
        )
        st.success(f"Added '{task_desc}' for {selected_pet}!")
        st.rerun()
else:
    st.info("Add a pet first, then you can assign tasks.")

st.divider()

# ── Daily Schedule ────────────────────────────────────────────
st.subheader("📅 Today's Schedule")

scheduler = Scheduler(owner)

# Conflict warnings at the top so they're immediately visible
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        st.warning(f"⚠️ {c}")

# Sorting & filtering controls
col_sort, col_filter = st.columns(2)
with col_sort:
    sort_mode = st.radio("Sort by", ["Time", "Priority → Time"], horizontal=True)
with col_filter:
    filter_pet = st.selectbox(
        "Filter by pet", ["All pets"] + [p.name for p in owner.get_pets()]
    )

# Apply sorting
if sort_mode == "Priority → Time":
    schedule = scheduler.sort_by_priority_then_time()
else:
    schedule = scheduler.sort_by_time()

# Apply pet filter
if filter_pet != "All pets":
    schedule = [(pn, t) for pn, t in schedule if pn == filter_pet]

# Display schedule
if schedule:
    rows = []
    for pet_name_s, task in schedule:
        priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
            task.priority, ""
        )
        rows.append(
            {
                "Time": task.time or "—",
                "Task": task.description,
                "Pet": pet_name_s,
                "Priority": f"{priority_badge} {task.priority}",
                "Freq": task.frequency,
                "Status": "✅" if task.completed else "⬜",
            }
        )
    st.table(rows)
else:
    st.info("No tasks yet. Add a pet and some tasks above!")

st.divider()

# ── Mark Complete ─────────────────────────────────────────────
incomplete_tasks = scheduler.filter_tasks(completed=False)
if incomplete_tasks:
    st.subheader("✔️ Mark a Task Complete")
    task_options = [f"{pn}: {t.description} ({t.time})" for pn, t in incomplete_tasks]
    chosen = st.selectbox("Select task to complete", task_options)
    if st.button("Mark complete"):
        idx = task_options.index(chosen)
        pn, t = incomplete_tasks[idx]
        new_task = scheduler.mark_task_complete(pn, t.description)
        st.success(f"Completed '{t.description}' for {pn}!")
        if new_task:
            st.info(
                f"🔁 Recurring task auto-scheduled: '{new_task.description}' "
                f"on {new_task.due_date.strftime('%b %d, %Y')}"
            )
        st.rerun()
