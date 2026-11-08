"""
modules/dashboard.py
--------------------------------------------------
Main KPI dashboard — Ultra Premium UI Edition.
--------------------------------------------------
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date, datetime
from database.db import query
from modules.student import get_chapters


def render_dashboard(student_id, student):
    # --- 1. Premium Custom CSS ---
    st.markdown("""
        <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Gradient Glassmorphism Header */
        .header-container {
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.95) 0%, rgba(22, 163, 74, 0.9) 100%);
            backdrop-filter: blur(10px);
            padding: 35px 40px;
            border-radius: 20px;
            color: white;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.3);
            position: relative;
            overflow: hidden;
        }
        /* Decorative circle in header */
        .header-container::before {
            content: '';
            position: absolute;
            top: -50px;
            right: -50px;
            width: 200px;
            height: 200px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
        }
        .header-title {
            font-size: 34px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .header-subtitle {
            font-size: 16px;
            font-weight: 400;
            opacity: 0.9;
            margin-top: 8px;
        }
        
        /* Premium Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #f1f5f9;
            padding: 20px 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px -8px rgba(30, 58, 138, 0.15);
            border-color: #e2e8f0;
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            color: #64748b;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        div[data-testid="stMetricValue"] {
            color: #0f172a;
            font-weight: 800;
            font-size: 36px;
            margin-top: 5px;
        }
        
        /* Custom Task Cards */
        .task-card {
            background: #ffffff;
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 12px;
            border-left: 6px solid #cbd5e1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s;
        }
        .task-card:hover {
            transform: translateX(4px);
        }
        .task-card.completed { border-left-color: #10b981; background: #f0fdf4; }
        .task-card.missed { border-left-color: #ef4444; background: #fef2f2; }
        .task-card.pending { border-left-color: #f59e0b; background: #fffbeb; }
        
        .task-title { font-weight: 600; color: #1e293b; font-size: 16px; }
        .task-time { color: #64748b; font-size: 14px; font-weight: 500;}
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

    tasks = query("""SELECT t.*, s.name as subject_name FROM timetable_tasks t LEFT JOIN subjects s ON t.subject_id = s.id WHERE t.student_id=? AND t.task_date=?""", (student_id, today))
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
            <div class="header-title">Welcome back, {student['name']} 👋</div>
            <div class="header-subtitle">You have <b>{days_left} days</b> left to conquer your exams. Let's make today count.</div>
        </div>
    """, unsafe_allow_html=True)

    # --- KPI Row 1 ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Days Left", days_left, delta="-1 day" if days_left != "—" else None, delta_color="inverse")
    c2.metric("📚 Syllabus", f"{avg_pct}%")
    c3.metric("⏱️ Hours Studied", f"{hours:.1f} h")
    c4.metric("🎯 Test Avg", f"{avg_score}%")

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # --- KPI Row 2 ---
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("📖 Exam-Ready Chapters", f"{exam_ready}/{total_ch}")
    c6.metric("🔁 Revision Done", f"{rev_pct}%")
    c7.metric("✅ Tasks Today", f"{done}/{len(tasks)}")
    c8.metric("🧪 Total Tests", len(tests))

    st.markdown("<hr style='border:1px solid #e2e8f0; margin: 30px 0;'>", unsafe_allow_html=True)

    # --- Middle Section: Charts & Tasks ---
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("<h3 style='color: #1e293b; font-weight: 700; margin-bottom: 20px;'>📈 Subject Mastery</h3>", unsafe_allow_html=True)
        if chapters:
            df = pd.DataFrame(chapters)
            subj_avg = df.groupby("subject_name")["completion_pct"].mean().reset_index()
            # Sort for better visual flow
            subj_avg = subj_avg.sort_values(by="completion_pct", ascending=True)
            
            fig = px.bar(subj_avg, x="completion_pct", y="subject_name", orientation='h',
                         text_auto='.0f', color="subject_name",
                         color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'])
            fig.update_layout(
                xaxis_title="", yaxis_title="",
                showlegend=False, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                font=dict(family="Inter, sans-serif")
            )
            fig.update_xaxes(range=[0, 100], showgrid=True, gridcolor='#f1f5f9')
            fig.update_traces(textposition='inside', insidetextanchor='middle', textfont_size=12, textfont_color="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No chapter data yet.")

    with col_right:
        st.markdown("<h3 style='color: #1e293b; font-weight: 700; margin-bottom: 20px;'>🗓️ Today's Focus</h3>", unsafe_allow_html=True)
        if tasks:
            for t in tasks:
                status_class = "completed" if t["status"] == "Completed" else ("missed" if t["status"] == "Missed" else "pending")
                icon = "✅" if t["status"] == "Completed" else ("❌" if t["status"] == "Missed" else "⏳")
                
                st.markdown(f"""
                    <div class="task-card {status_class}">
                        <div>
                            <div class="task-title">{icon} {t['subject_name'] or 'General Study'}</div>
                            <div class="task-time">{t['priority']} Priority</div>
                        </div>
                        <div style="font-weight: 700; color: #475569;">
                            {t['start_time']} - {t['end_time']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background: #f8fafc; padding: 30px; border-radius: 12px; text-align: center; border: 1px dashed #cbd5e1;">
                    <div style="font-size: 30px; margin-bottom: 10px;">🎉</div>
                    <div style="font-weight: 600; color: #475569;">No tasks scheduled!</div>
                    <div style="color: #94a3b8; font-size: 14px; margin-top: 5px;">Enjoy your free time or add a new task in the Timetable tab.</div>
                </div>
            """, unsafe_allow_html=True)
