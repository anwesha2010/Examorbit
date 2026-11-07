"""
modules/dashboard.py
--------------------------------------------------
Main KPI dashboard — Premium UI Edition.
--------------------------------------------------
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date, datetime
from database.db import query
from modules.student import get_chapters


def render_dashboard(student_id, student):
    # --- Premium Custom CSS ---
    st.markdown("""
        <style>
        /* Gradient Background for Header */
        .header-container {
            background: linear-gradient(135deg, #1e3a8a 0%, #16a34a 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .header-title {
            font-size: 32px;
            font-weight: 700;
            margin: 0;
        }
        .header-subtitle {
            font-size: 16px;
            opacity: 0.9;
            margin-top: 5px;
        }
        
        /* KPI Card Styling */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            color: #475569;
        }
        div[data-testid="stMetricValue"] {
            color: #1e3a8a;
            font-weight: 700;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Data Fetching ---
    today = date.today().isoformat()
    chapters = get_chapters(student_id=student_id)
    total_ch = len(chapters)
    exam_ready = sum(1 for c in chapters if c["status"] == "Exam Ready")
    avg_pct = (round(sum(c["completion_pct"] for c in chapters) / total_ch, 1) if total_ch else 0)

    days_left = "—"
    if student.get("exam_start_date"):
        try:
            days_left = (datetime.strptime(student["exam_start_date"], "%Y-%m-%d").date() - date.today()).days
        except Exception:
            pass

    tasks = query("SELECT * FROM timetable_tasks WHERE student_id=? AND task_date=?", (student_id, today))
    done = sum(1 for t in tasks if t["status"] == "Completed")

    tests = query("SELECT * FROM test_records WHERE student_id=?", (student_id,))
    avg_score = (round(sum(t["marks_obtained"] / t["max_marks"] * 100 for t in tests) / len(tests), 1) if tests else 0)

    revs = query("""SELECT r.* FROM revision_records r JOIN chapters c ON r.chapter_id=c.id JOIN subjects s ON c.subject_id=s.id WHERE s.student_id=?""", (student_id,))
    rev_done = sum(1 for r in revs if r["status"] == "Completed")
    rev_pct = round(rev_done / len(revs) * 100, 1) if revs else 0

    hours = query("""SELECT COALESCE(SUM(duration_minutes),0)/60.0 AS h FROM timetable_tasks WHERE student_id=? AND status='Completed'""", (student_id,), one=True)["h"]

    # --- Header ---
    st.markdown(f"""
        <div class="header-container">
            <div class="header-title">👋 Welcome back, {student['name']}</div>
            <div class="header-subtitle">You have {days_left} days left until your board exams. Keep pushing!</div>
        </div>
    """, unsafe_allow_html=True)

    # --- KPI Row 1 ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Days to Exam", days_left, delta="-1 day" if days_left != "—" else None, delta_color="inverse")
    c2.metric("📚 Syllabus Progress", f"{avg_pct}%", delta=f"{avg_pct}% overall" if avg_pct > 0 else None)
    c3.metric("⏱️ Study Hours", f"{hours:.1f}")
    c4.metric("🎯 Avg Test Score", f"{avg_score}%")

    # --- KPI Row 2 ---
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("📖 Exam-Ready", f"{exam_ready}/{total_ch}")
    c6.metric("🔁 Revision", f"{rev_pct}%")
    c7.metric("✅ Today's Tasks", f"{done}/{len(tasks)}")
    c8.metric("🧪 Tests Taken", len(tests))

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Middle Section: Charts & Tasks ---
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📈 Subject Progress")
        if chapters:
            df = pd.DataFrame(chapters)
            subj_avg = df.groupby("subject_name")["completion_pct"].mean().reset_index()
            fig = px.bar(subj_avg, x="completion_pct", y="subject_name", orientation='h',
                         text_auto='.0f', color="subject_name",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(
                xaxis_title="Completion %", yaxis_title="",
                showlegend=False, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=300
            )
            fig.update_xaxes(range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No chapter data yet.")

    with col_right:
        st.markdown("### 🗓️ Today's Schedule")
        if tasks:
            for t in tasks:
                icon = "✅" if t["status"] == "Completed" else ("❌" if t["status"] == "Missed" else "⏳")
                color = "#16a34a" if t["status"] == "Completed" else ("#ef4444" if t["status"] == "Missed" else "#f59e0b")
                st.markdown(f"""
                    <div style="background-color: #f8fafc; padding: 12px; border-left: 4px solid {color}; border-radius: 8px; margin-bottom: 8px;">
                        <strong style="color: #1e293b;">{icon} {t['start_time']} - {t['end_time']}</strong><br>
                        <span style="color: #64748b; font-size: 14px;">{t['priority']} Priority Task</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No tasks scheduled for today. Enjoy your free time!")
