"""
app.py — ExamOrbit main entry point.
"""
import streamlit as st
from datetime import date
from database.db import init_db
from modules.student import get_student, update_student, get_subjects, add_subject
from modules.dashboard import render_dashboard
from modules.timetable import (
    add_task, get_tasks, mark_task, delete_task, mark_missed_for_past_days,
    get_missed_tasks, suggest_slots,
)
from modules.chapters import render_chapter_tracker
from modules.revision import render_revision_manager
from modules.tests import render_test_manager
from modules.analytics import render_analytics

st.set_page_config(page_title="ExamOrbit", page_icon="📘", layout="wide")
init_db()

# Sidebar
st.sidebar.title("📘 ExamOrbit")
st.sidebar.caption("Plan Smart. Track Daily. Score Better.")

page = st.sidebar.radio("Navigate", [
    "Dashboard", "My Timetable", "Subject & Chapter Tracker",
    "Revision Manager", "Test Manager", "Performance Analytics",
    "My Profile",
])

student = get_student()
if not student:
    st.error("No student found. Delete data/examorbit.db and reload.")
    st.stop()

mark_missed_for_past_days(student["id"])

if page == "Dashboard":
    render_dashboard(student["id"], student)

elif page == "My Timetable":
    st.subheader("🗓️ My Timetable")
    subjects = get_subjects(student["id"])
    with st.expander("➕ Add Task", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            td = st.date_input("Date", value=date.today())
            s = st.selectbox("Subject", [x["name"] for x in subjects]) if subjects else None
            subj_id = next((x["id"] for x in subjects if x["name"] == s), None)
            st_time = st.time_input("Start time")
            en_time = st.time_input("End time")
        with c2:
            dur = st.number_input("Duration (min)", 15, 480, 60, step=15)
            prio = st.selectbox("Priority", ["Low", "Medium", "High"])
            note = st.text_input("Notes")
        if st.button("Add Task", type="primary") and subjects:
            try:
                add_task(student["id"], subj_id, None, td.isoformat(),
                         st_time.strftime("%H:%M"), en_time.strftime("%H:%M"),
                         dur, prio, note)
                st.success("Task added.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    filter_date = st.date_input("View date", value=date.today(), key="view_date")
    tasks = get_tasks(student["id"], task_date=filter_date.isoformat())
    for t in tasks:
        cols = st.columns([3, 2, 1, 1])
        cols[0].write(f"**{t['subject_name'] or '—'}** — {t['start_time']}–{t['end_time']}")
        cols[1].write(t["status"])
        if t["status"] != "Completed" and cols[2].button("✅", key=f"d_{t['id']}"):
            mark_task(t["id"], "Completed"); st.rerun()
        if cols[3].button("🗑️", key=f"x_{t['id']}"):
            delete_task(t["id"]); st.rerun()

    missed = get_missed_tasks(student["id"])
    if missed:
        st.markdown("### ⚠️ Missed Tasks — Recovery")
        for m in missed:
            st.write(f"**{m['task_date']}** — {m['subject_name']}")
        st.markdown("**Suggested free slots:**")
        for s in suggest_slots(student["id"]):
            st.caption(f"{s['date']}: ~{s['free_hours']}h free")

elif page == "Subject & Chapter Tracker":
    render_chapter_tracker(student["id"])

elif page == "Revision Manager":
    render_revision_manager(student["id"])

elif page == "Test Manager":
    render_test_manager(student["id"])

elif page == "Performance Analytics":
    render_analytics(student["id"])

elif page == "My Profile":
    st.subheader("👤 My Profile")
    with st.form("profile"):
        name = st.text_input("Name", student["name"])
        cls = st.selectbox("Class", ["10", "12"],
                           index=0 if student["class_level"] == "10" else 1)
        yr = st.text_input("Academic Year", student["academic_year"])
        target = st.number_input("Target %", 0.0, 100.0,
                                 float(student["target_percentage"]))
        hrs = st.number_input("Daily study hours", 0.0, 16.0,
                              float(student["daily_study_hours"]))
        exam = st.date_input("Exam start date",
                             value=date.fromisoformat(student["exam_start_date"])
                             if student.get("exam_start_date") else date.today())
        if st.form_submit_button("Save Profile", type="primary"):
            update_student(student["id"], name, cls, yr, target, hrs, exam.isoformat())
            st.success("Profile updated.")
            st.rerun()

    st.markdown("---")
    st.markdown("### Subjects")
    for s in get_subjects(student["id"]):
        st.write("•", s["name"])
    with st.form("add_subj"):
        new_s = st.text_input("New subject name")
        if st.form_submit_button("Add Subject") and new_s.strip():
            add_subject(student["id"], new_s)
            st.rerun()
