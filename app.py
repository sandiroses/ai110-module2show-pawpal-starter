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

# --- Owner info ---
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = st.number_input(
    "Minutes available today", min_value=0, max_value=1440,
    value=owner.available_minutes, step=15,
)

st.divider()

# --- Add a pet ---
st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name.strip()}!")
        else:
            st.error("Please enter a pet name.")

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a task ---
st.subheader("Tasks")
if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("For which pet?", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            task_time = st.time_input("Time", value=time(8, 0))
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        if st.form_submit_button("Add task"):
            pet = next(p for p in owner.pets if p.name == pet_choice)
            pet.add_task(Task(
                title=task_title,
                time=task_time.strftime("%H:%M"),
                duration_minutes=int(duration),
                priority=priority,
            ))
            st.success(f"Added '{task_title}' for {pet_choice}.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        st.table([
            {"Pet": t.pet_name, "Time": t.time, "Task": t.title,
             "Minutes": t.duration_minutes, "Priority": t.priority}
            for t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.caption("Add a pet first, then you can add tasks.")

st.divider()

# --- Build the schedule ---
st.subheader("Today's Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()
    if plan:
        st.table([
            {"Time": t.time, "Pet": t.pet_name, "Task": t.title,
             "Minutes": t.duration_minutes, "Priority": t.priority}
            for t in plan
        ])
    else:
        st.info("Nothing scheduled for today yet.")