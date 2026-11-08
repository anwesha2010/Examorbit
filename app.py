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

st.set_page_config(page_title="ExamOrbit", page_icon="📘", layout="wide", initial_sidebar_state="expanded")

# --- STRONG SIDEBAR CSS (Matching the new design) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
    
    /* Hide Streamlit Header/Menu */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

    /* Sidebar Background & Width */
    [data-testid="stSidebar"] { background-color: #0e0e0e; border-right: 1px solid #1f1f1f; width: 280px !important; padding-top: 2rem; }
    
    /* Hide Default Radio Circles */
    [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child { display: none !important; }
    [data-testid="stSidebar"] [data-baseweb="radio"] > div:last-child { padding-left: 0 !important; }
    
    /* Style Nav Items */
    [data-testid="stSidebar"] label {
        display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-radius: 12px;
        color: #888 !important; font-weight: 500; font-size: 15px; cursor: pointer; transition: 0.2s; margin-bottom: 2px;
    }
    [data-testid="stSidebar"] label:hover { background: #1a1a1a; color: #fff !important; }
    
    /* Active Nav Item (Lime Pill) */
    [data-testid="stSidebar"] label[data-checked="true"] {
        background: #d4ff40 !important; color: #000 !important; font-weight: 700;
    }
    [data-testid="stSidebar"] label[data-checked="true"] p { color: #000 !important; }
    [data-testid="stSidebar"] label[data-checked="true"] .material-symbols-rounded { color: #000 !important; }
    
    /* Notification Dot */
    .notif-dot {
        background: #f472b6; color: #000; border-radius: 50%; width: 20px; height: 20px;
        display: inline-flex; justify-content: center; align-items: center; font-size: 11px; font-weight: 800;
        margin-left: auto;
    }
    </style>
""", unsafe_allow_html=True)

init_db()

# Custom Sidebar Header
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 30px;">
        <div style="background: #d4ff40; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #000; font-size: 20px;">EO</div>
        <div>
            <div style="color: #fff; font-weight: 700; font-size: 20px; line-height: 1;">ExamOrbit</div>
            <div style="color: #888; font-size: 11px; line-height: 1; margin-top: 4px;">Plan Smart. Track daily.</div>
        </div>
    </div>
    """, unsafe_allow_html=True
)

# We use emojis to simulate the icons in the radio buttons since Streamlit doesn't support custom HTML inside radios
page = st.sidebar.radio("Navigation", [
    "▦  Dashboard", 
    "🗓️  My Timetable", 
    "📖  Subjects & Chapters",
    "🔁  Revision",
    "📝  Tests", 
    "📈  Analytics", 
    "👤  My Profile"
])

# Custom Sidebar Footer (Focus Mode)
st.sidebar.markdown(
    """
    <div style="margin-top: 40px; background: #1a1a1a; border-radius: 16px; padding: 20px; border: 1px solid #2a2a2a;">
        <h4 style="color: #fff; margin: 0 0 5px 0; font-size: 14px;">Focus mode</h4>
        <p style="color: #888; font-size: 12px; margin: 0 0 15px 0; line-height: 1.4;">Mute the noise and run a timed study sprint.</p>
        <button style="background: transparent; border: 1px solid #555; color: #fff; width: 100%; padding: 10px; border-radius: 10px; font-size: 12px; font-weight: 600; cursor: pointer;">Start a 25-min sprint</button>
    </div>
    """, unsafe_allow_html=True
)

student = get_student()
if not student:
    st.error("No student found. Delete data/examorbit.db and reload.")
    st.stop()

mark_missed_for_past_days(student["id"])

# Route to pages
if page == "▦  Dashboard":
    render_dashboard(student["id"], student)

elif page == "🗓️  My Timetable":
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

elif page == "📖  Subjects & Chapters":
    render_chapter_tracker(student["id"])

elif page == "🔁  Revision":
    render_revision_manager(student["id"])

elif page == "📝  Tests":
    render_test_manager(student["id"])

elif page == "📈  Analytics":
    render_analytics(student["id"])

elif page == "👤  My Profile":
    st.subheader("👤 My Profile")
    with st.form("profile"):
        name = st.text_input("Name", student["name"])
        cls = st.selectbox("Class", ["9", "10", "11", "12"],
                           index=["9", "10", "11", "12"].index(student["class_level"]) if student["class_level"] in ["9", "10", "11", "12"] else 3)
        yr = st.text_input("Academic Year", student["academic_year"])
        target = st.number_input("Target %", 0.0, 100.0, float(student["target_percentage"]))
        hrs = st.number_input("Daily study hours", 0.0, 16.0, float(student["daily_study_hours"]))
        exam = st.date_input("Exam start date", value=date.fromisoformat(student["exam_start_date"]) if student.get("exam_start_date") else date.today())
        if st.form_submit_button("Save Profile", type="primary"):
            update_student(student["id"], name, cls, yr, target, hrs, exam.isoformat())
            st.success("Profile updated.")
            st.rerun()
