"""
modules/dashboard.py
--------------------------------------------------
Ultra Premium Dashboard (Claude Design Clone)
--------------------------------------------------
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from database.db import query
from modules.student import get_chapters

def render_dashboard(student_id, student):
    # --- 1. Custom CSS ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
        
        /* Hide Streamlit default padding and header */
        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1400px; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        header {visibility: hidden;}

        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        
        /* Custom Grid Layout */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 2fr 1.5fr 1.5fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .sub-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .small-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        
        /* Base Card Style */
        .card {
            background-color: #1a1a1a;
            border-radius: 24px;
            padding: 24px;
            position: relative;
            overflow: hidden;
            border: 1px solid #2a2a2a;
        }

        /* Neon Yellow Card */
        .card-yellow {
            background: #d4ff40;
            color: #000;
        }
        .card-yellow .badge {
            background: #000; color: #fff; padding: 4px 12px; border-radius: 20px;
            font-size: 11px; font-weight: 700; display: inline-block; margin-bottom: 15px;
            letter-spacing: 0.5px;
        }
        .huge-number { font-size: 110px; font-weight: 800; line-height: 0.9; letter-spacing: -2px; }
        
        /* Purple Card */
        .card-purple {
            background: #c4b5fd; color: #000;
            display: flex; flex-direction: column; justify-content: space-between;
        }
        .purple-number { font-size: 65px; font-weight: 800; line-height: 1; margin-top: 10px; }
        .btn-black {
            background: #000; color: #fff; text-align: center; padding: 12px; 
            border-radius: 12px; font-weight: 600; font-size: 14px; margin-top: 20px;
        }

        /* SVG Circular Progress */
        .circle-wrap { display: flex; justify-content: center; align-items: center; margin: 20px 0; position: relative;}
        .circle-wrap svg { transform: rotate(-90deg); }
        .circle-bg { fill: none; stroke: #2a2a2a; stroke-width: 12; }
        .circle-progress { fill: none; stroke: #d4ff40; stroke-width: 12; stroke-linecap: round; }
        .circle-text { position: absolute; font-size: 24px; font-weight: 700; color: #fff; }

        /* Small Metric Cards */
        .metric-card {
            background-color: #1a1a1a; border-radius: 20px; padding: 20px;
            display: flex; flex-direction: column; justify-content: center; border: 1px solid #2a2a2a;
        }
        .metric-icon { 
            background: #252525; width: 40px; height: 40px; border-radius: 12px; 
            display: flex; align-items: center; justify-content: center; margin-bottom: 15px;
            font-size: 18px;
        }
        .metric-value { font-size: 24px; font-weight: 700; color: #fff; margin: 0; }
        .metric-label { font-size: 13px; color: #888; margin: 0; }

        /* Lists (Subject Mastery, Today's Focus) */
        .progress-bar-bg { background: #2a2a2a; height: 8px; border-radius: 4px; width: 100%; margin-top: 8px; overflow: hidden; }
        .progress-bar-fill { height: 100%; border-radius: 4px; }
        
        .list-item { margin-bottom: 18px; }
        .list-header { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; color: #fff; }
        
        .task-row {
            display: flex; justify-content: space-between; align-items: center;
            background: #222; border-radius: 16px; padding: 16px; margin-bottom: 12px;
        }
        .task-row-left { display: flex; align-items: center; gap: 15px; }
        .task-checkbox { width: 24px; height: 24px; border-radius: 6px; border: 2px solid #555; }
        .task-info h4 { margin: 0; font-size: 16px; color: #fff; }
        .task-info p { margin: 0; font-size: 13px; color: #888; }
        .priority { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .priority-med { background: #3f3015; color: #f59e0b; }
        .priority-low { background: #1e293b; color: #60a5fa; }
        
        .start-btn { background: #d4ff40; color: #000; text-align: center; padding: 16px; border-radius: 16px; font-weight: 700; margin-top: 20px; }
        .open-tracker { color: #d4ff40; font-size: 14px; font-weight: 600; cursor: pointer;}
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

    # --- Top Header ---
    day_str = datetime.today().strftime('%A, %d %B')
    st.markdown(f"""
        <div style='margin-bottom: 30px;'>
            <p style='color: #888; margin: 0; font-size: 14px;'>{day_str}</p>
            <h1 style='color: #fff; margin: 0; font-size: 42px; font-weight: 700;'>hey {student['name']}, let's lock in.</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- Main Grid ---
    # We use columns in Streamlit to create the exact layout, but style them via CSS
    col1, col2, col3 = st.columns([2, 1.2, 1.2])
    
    with col1:
        st.markdown(f"""
            <div class="card card-yellow" style="min-height: 260px;">
                <div class="badge">BOARD EXAM COUNTDOWN</div>
                <div style="display: flex; align-items: baseline; gap: 10px;">
                    <div class="huge-number">{days_left}</div>
                    <div style="font-size: 24px; font-weight: 600;">days left</div>
                </div>
                <p style="margin-top: 20px; font-weight: 500;">Make today count — two sessions on the plan.</p>
                <div style="position: absolute; right: -50px; bottom: -50px; opacity: 0.2;">
                    <svg width="250" height="250" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="none" stroke="black" stroke-width="2"/><circle cx="50" cy="50" r="35" fill="none" stroke="black" stroke-width="2"/></svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # SVG Circular Progress logic
        circumference = 2 * 3.14159 * 40
        offset = circumference - (avg_pct / 100) * circumference
        st.markdown(f"""
            <div class="card" style="min-height: 260px; text-align: center;">
                <p style="color: #888; font-size: 14px; font-weight: 500; text-align: left; margin: 0;">Syllabus done</p>
                <div class="circle-wrap">
                    <svg width="140" height="140">
                        <circle class="circle-bg" cx="70" cy="70" r="40"></circle>
                        <circle class="circle-progress" cx="70" cy="70" r="40" stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"></circle>
                    </svg>
                    <div class="circle-text">{avg_pct}%</div>
                </div>
                <p style="color: #888; font-size: 13px; margin: 0;">Keep stacking chapters</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="card card-purple" style="min-height: 260px;">
                <div>
                    <p style="font-size: 14px; font-weight: 600; margin: 0;">Test average</p>
                    <div class="purple-number">{avg_score:.0f}%</div>
                    <p style="font-size: 14px; margin: 5px 0 0 0;">across {len(tests)} test taken</p>
                </div>
                <div class="btn-black">Take a mock test</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # --- Small Metrics Row ---
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""<div class="metric-card"><div class="metric-icon">⏱</div><p class="metric-value">{hours:.1f} h</p><p class="metric-label">Hours studied</p></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="metric-card"><div class="metric-icon">📖</div><p class="metric-value">{exam_ready}/{total_ch}</p><p class="metric-label">Exam-ready chapters</p></div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""<div class="metric-card"><div class="metric-icon">🔁</div><p class="metric-value">{rev_pct}%</p><p class="metric-label">Revision done</p></div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class="metric-card"><div class="metric-icon">🧪</div><p class="metric-value">{done}/{len(tasks)}</p><p class="metric-label">Tasks today</p></div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # --- Bottom Grid (Subject Mastery + Today's Focus) ---
    b1, b2 = st.columns([1.5, 1])
    
    with b1:
        st.markdown("""<div class="card" style="min-height: 400px;">""", unsafe_allow_html=True)
        st.markdown("""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;"><h3 style="margin:0; color: #fff;">Subject mastery</h3><span class="open-tracker">Open tracker</span></div>""", unsafe_allow_html=True)
        
        if chapters:
            df = pd.DataFrame(chapters)
            subj_avg = df.groupby("subject_name")["completion_pct"].mean().reset_index()
            colors = ['#f472b6', '#d4ff40', '#38bdf8', '#fb923c', '#a78bfa']
            
            for i, row in subj_avg.iterrows():
                color = colors[i % len(colors)]
                st.markdown(f"""
                    <div class="list-item">
                        <div class="list-header"><span>{row['subject_name']}</span><span>{row['completion_pct']:.0f}%</span></div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {row['completion_pct']}%; background: {color};"></div></div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("""</div>""", unsafe_allow_html=True)

    with b2:
        st.markdown("""<div class="card" style="min-height: 400px;">""", unsafe_allow_html=True)
        st.markdown(f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;"><h3 style="margin:0; color: #fff;">Today's focus</h3><span style="background: #2a2a2a; color: #aaa; padding: 4px 12px; border-radius: 20px; font-size: 12px;">{done} of {len(tasks)} done</span></div>""", unsafe_allow_html=True)
        
        if tasks:
            for t in tasks:
                prio_class = "priority-med" if t['priority'] == "Medium" else "priority-low"
                st.markdown(f"""
                    <div class="task-row">
                        <div class="task-row-left">
                            <div class="task-checkbox"></div>
                            <div class="task-info">
                                <h4>{t['subject_name'] or 'General'}</h4>
                                <p>{t['start_time']} – {t['end_time']}</p>
                            </div>
                        </div>
                        <div class="priority {prio_class}">{t['priority']} priority</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#888;'>No tasks scheduled.</p>", unsafe_allow_html=True)
            
        st.markdown("""<div style="border: 1px dashed #444; border-radius: 12px; padding: 15px; text-align: center; color: #888; font-size: 14px; margin-top: 10px;">+ Add a study block</div>""", unsafe_allow_html=True)
        st.markdown("""<div class="start-btn">▶ Start next session</div>""", unsafe_allow_html=True)
        st.markdown("""</div>""", unsafe_allow_html=True)
