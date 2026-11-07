"""
modules/dashboard.py
--------------------------------------------------
Main KPI dashboard.
--------------------------------------------------
"""
import streamlit as st
from datetime import date, datetime
from database.db import query
from modules.student import get_chapters


def render_dashboard(student_id, student):
    st.subheader(f"👋 Welcome, {student['name']}")
    today = date.today().isoformat()

    chapters = get_chapters(student_id=student_id)
    total_ch = len(chapters)
    exam_ready = sum(1 for c in chapters if c["status"] == "Exam Ready")
    avg_pct = (round(sum(c["completion_pct"] for c in chapters) / total_ch, 1)
               if total_ch else 0)

    days_left = "—"
    if student.get("exam_start_date"):
        try:
            days_left = (datetime.strptime(student["exam_start_date"],
                                           "%Y-%m-%d").date() - date.today()).days
        except Exception:
            pass

    tasks = query(
        "SELECT * FROM timetable_tasks WHERE student_id=? AND task_date=?",
        (student_id, today),
    )
    done = sum(1 for t in tasks if t["status"] == "Completed")

    tests = query("SELECT * FROM test_records WHERE student_id=?", (student_id,))
    avg_score = (round(sum(t["marks_obtained"] / t["max_marks"] * 100
                           for t in tests) / len(tests), 1) if tests else 0)

    revs = query(
        """SELECT r.* FROM revision_records r
        JOIN chapters c ON r.chapter_id=c.id
        JOIN subjects s ON c.subject_id=s.id WHERE s.student_id=?""",
        (student_id,),
    )
    rev_done = sum(1 for r in revs if r["status"] == "Completed")
    rev_pct = round(rev_done / len(revs) * 100, 1) if revs else 0

    hours = query(
        """SELECT COALESCE(SUM(duration_minutes),0)/60.0 AS h
        FROM timetable_tasks WHERE student_id=? AND status='Completed'""",
        (student_id,), one=True,
    )["h"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Days to Exam", days_left)
    c2.metric("📚 Syllabus Progress", f"{avg_pct}%")
    c3.metric("⏱️ Study Hours", f"{hours:.1f}")
    c4.metric("🎯 Avg Test Score", f"{avg_score}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("📖 Exam-Ready", f"{exam_ready}/{total_ch}")
    c6.metric("🔁 Revision", f"{rev_pct}%")
    c7.metric("✅ Today's Tasks", f"{done}/{len(tasks)}")
    c8.metric("🧪 Tests Taken", len(tests))

    st.markdown("---")
    st.markdown("### 🗓️ Today's Tasks")
    if tasks:
        for t in tasks:
            icon = ("✅" if t["status"] == "Completed"
                    else ("❌" if t["status"] == "Missed" else "⏳"))
            st.write(f"{icon} **{t['start_time']}–{t['end_time']}** — "
                     f"{t['priority']} priority")
    else:
        st.caption("No tasks scheduled for today.")
