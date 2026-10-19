from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day.")

# --- App memory: create the Owner once and keep it across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner
scheduler = Scheduler(owner)


def task_rows(tasks):
    """Turn Task objects into rows for st.table."""
    return [
        {"Time": t.time, "Pet": t.pet_name, "Task": t.title,
         "Minutes": t.duration_minutes, "Priority": t.priority,
         "Repeats": t.frequency, "Due": str(t.due_date),
         "Status": "✅ done" if t.completed else "⏳ to do"}
        for t in tasks
    ]


# --- Owner info ---
st.subheader("👤 Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = st.number_input(
    "Minutes available today", min_value=0, max_value=1440,
    value=owner.available_minutes, step=15,
)

st.divider()

# --- Add a pet ---
st.subheader("🐶 Pets")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif owner.get_pet(pet_name.strip()):
            st.error(f"You already have a pet named {pet_name.strip()}.")
        else:
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name.strip()}!")

if owner.pets:
    st.write("Your pets: " + ", ".join(f"**{p.name}** ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a task ---
st.subheader("📝 Tasks")
if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("For which pet?", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            task_time = st.time_input("Time", value=time(8, 0))
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            owner.get_pet(pet_choice).add_task(Task(
                title=task_title,
                time=task_time.strftime("%H:%M"),
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
            ))
            st.success(f"Added '{task_title}' for {pet_choice}.")

    # Message from the last "Mark complete" click (survives the rerun)
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    # Filter controls -> Scheduler.filter_tasks()
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["All", "To do", "Done"])

    shown = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "To do": False, "Done": True}[status_filter],
    )
    if shown:
        st.table(task_rows(scheduler.sort_by_time(shown)))
    else:
        st.info("No tasks match. Add one above or change the filters.")

    # Mark a task complete -> Scheduler.mark_task_complete() (handles recurrence)
    open_tasks = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if open_tasks:
        with st.form("complete_form"):
            labels = [f"{t.time} · {t.pet_name} · {t.title} (due {t.due_date})" for t in open_tasks]
            picked = st.selectbox("Mark a task complete", range(len(open_tasks)),
                                  format_func=lambda i: labels[i])
            if st.form_submit_button("Mark complete"):
                task = open_tasks[picked]
                next_task = scheduler.mark_task_complete(task)
                if next_task:
                    st.session_state.flash = (f"Done! '{task.title}' repeats {task.frequency}, "
                                              f"so the next one is scheduled for {next_task.due_date}.")
                else:
                    st.session_state.flash = f"Done! '{task.title}' is complete."
                st.rerun()
else:
    st.caption("Add a pet first, then you can add tasks.")

st.divider()

# --- Build the schedule ---
st.subheader("📅 Today's Schedule")
if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_daily_plan()

    conflicts = scheduler.detect_conflicts(plan)
    for warning in conflicts:
        st.warning(f"⚠️ {warning}. Consider moving one of these tasks to a different time.")

    if plan:
        used = sum(t.duration_minutes for t in plan)
        st.success(f"{len(plan)} task(s) planned, using {used} of "
                   f"{owner.available_minutes} available minutes.")
        st.table(task_rows(plan))
    else:
        st.info("Nothing scheduled for today yet.")

    for task in scheduler.skipped:
        st.warning(f"Skipped '{task.title}' for {task.pet_name}: needs "
                   f"{task.duration_minutes} min ({task.priority} priority), "
                   f"but there wasn't enough time left.")

    with st.expander("Why this plan?"):
        st.text(scheduler.explain_plan())