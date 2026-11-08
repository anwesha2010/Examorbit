"""
modules/dashboard.py
--------------------------------------------------
Ultra Premium Responsive Dashboard (Mobile + Desktop)
--------------------------------------------------
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from database.db import query
from modules.student import get_chapters

def render_dashboard(student_id, student):
    # --- 1. Custom CSS (Responsive) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
        
        /* Hide Streamlit default padding and header */
        .block-container { padding: 1rem !important; max-width: 1200px; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        
        /* Grid System */
        .row { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
        .col-main { flex: 2; min-width: 300px; }
        .col-side { flex: 1.2; min-width: 200px; }
        .col-4 { flex: 1; min-width: 140px; }
        .col-2-side { flex: 1; min-width: 140px; }

        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            .row { flex-direction: column; gap: 12px; }
            .col-main, .col-side, .col-4, .col-2-side { min-width: 100%; }
            .huge-number { font-size: 80px !important; }
            .purple-number { font-size: 50px !important; }
            .header-title { font-size: 32px !important; }
            .mobile-hide { display: none !important; }
        }

        /* Base Card Style */
        .card {
            background-color: #1a1a1a; border-radius: 24px; padding: 24px;
            position: relative; overflow: hidden; border: 1px solid #2a2a2a;
            display: flex; flex-direction: column; justify-content: space-between;
            height: 100%;
        }

        /* Specific Cards */
        .card-yellow { background: #d4ff40; color: #000; }
        .card-yellow .badge {
            background: #000; color: #fff; padding: 4px 12px; border-radius: 20px;
            font-size: 11px; font-weight: 700; display: inline-block; margin-bottom: 15px; letter-spacing: 0.5px;
        }
        .huge-number { font-size: 110px; font-weight: 800; line-height: 0.9; letter-spacing: -2px; }
        
        .card-purple { background: #c4b5fd; color: #000; }
        .purple-number { font-size: 65px; font-weight: 800; line-height: 1; margin-top: 10px; }
        .btn-black { background: #000; color: #fff; text-align: center; padding: 12px; border-radius: 12px; font-weight: 600; font-size: 14px; margin-top: auto; }

        /* SVG Progress */
        .circle-wrap { display: flex; justify-content: center; align-items: center; margin: 10px 0; position: relative; }
        .circle-wrap svg { transform: rotate(-90deg); }
        .circle-bg { fill: none; stroke: #2a2a2a; stroke-width: 12; }
        .circle-progress { fill: none; stroke: #d4ff40; stroke-width: 12; stroke-linecap: round; }
        .circle-text { position: absolute; font-size: 24px; font-weight: 700; color: #fff; }

        /* Small Metric Cards */
        .metric-card { background-color: #1a1a1a; border-radius: 20px; padding: 20px; border: 1px solid #2a2a2a; flex: 1; min-width: 140px; }
        .metric-value { font-size: 24px; font-weight: 700; color: #fff; margin: 0; }
        .metric-label { font-size: 13px; color: #888; margin: 0; }
        /* Colored Values for Mobile view */
        .val-orange { color: #fb923c; }
        .val-blue { color: #38bdf8; }
        .val-pink { color: #f472b6; }
        .val-green { color: #d4ff40; }

        /* Lists */
        .progress-bar-bg { background: #2a2a2a; height: 8px; border-radius: 4px; width: 100%; margin-top: 8px; overflow: hidden; }
        .progress-bar-fill { height: 100%; border-radius: 4px; }
        .list-item { margin-bottom: 18px; }
        .list-header { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; color: #fff; }
        
        /* Tasks */
        .task-row { display: flex; justify-content: space-between; align-items: center; background: #222; border-radius: 16px; padding: 16px; margin-bottom: 12px; }
        .task-row-left { display: flex; align-items: center; gap: 15px; }
        .task-checkbox { width: 24px; height: 24px; border-radius: 6px; border: 2px solid #555; flex-shrink: 0; }
        .task-info h4 { margin: 0; font-size: 16px; color: #fff; }
        .task-info p { margin: 0; font-size: 13px; color: #888; }
        .priority { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .priority-med { background: #3f3015; color: #f59e0b; }
        .priority-low { background: #1e293b; color: #60a5fa; }
        
        .start-btn { background: #d4ff40; color: #000; text-align: center; padding: 16px; border-radius: 16px; font-weight: 700; margin-top: 20px; }
        .open-tracker { color: #d4ff40; font-size: 14px; font-weight: 600; cursor: pointer; }
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

    tasks = query("SELECT t.*, s.name as subject_name FROM timetable_tasks t LEFT JOIN subjects s ON t.subject_id = s.id WHERE t.student_id=? AND t.task_date=?", (student_id, today))
    done = sum(1 for t in tasks if t["status"] == "Completed")

    tests = query("SELECT * FROM test_records WHERE student_id=?", (student_id,))
    avg_score = (round(sum(t["marks_obtained"] / t["max_marks"] * 100 for t in tests) / len(tests), 1) if tests else 0)

    revs = query("SELECT r.* FROM revision_records r JOIN chapters c ON r.chapter_id=c.id JOIN subjects s ON c.subject_id=s.id WHERE s.student_id=?", (student_id,))
    rev_done = sum(1 for r in revs if r["status"] == "Completed")
    rev_pct = round(rev_done / len(revs) * 100, 1) if revs else 0

    hours = query("SELECT COALESCE(SUM(duration_minutes),0)/60.0 AS h FROM timetable_tasks WHERE student_id=? AND status='Completed'", (student_id,), one=True)["h"]

    # --- Top Header ---
    day_str = datetime.today().strftime('%a, %d %b')
    header_html = (
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">'
        f'<div>'
        f'<p style="color: #888; margin: 0; font-size: 13px;">{day_str}</p>'
        f'<h1 class="header-title" style="color: #fff; margin: 0; font-size: 42px; font-weight: 800; line-height: 1.1;">hey {student["name"]},<br>let\'s lock in.</h1>'
        f'</div>'
        f'<div class="mobile-hide" style="background: #c4b5fd; color: #000; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px;">{student["name"][0].upper()}</div>'
        f'</div>'
    )

    # --- Main Grid Row 1 ---
    circ = 2 * 3.14159 * 40
    offset = circ - (avg_pct / 100) * circ
    
    row1_html = (
        f'<div class="row">'
        # Yellow Card
        f'<div class="card card-yellow col-main" style="min-height: 220px;">'
        f'<div class="badge">BOARD EXAM COUNTDOWN</div>'
        f'<div style="display: flex; align-items: baseline; gap: 10px;">'
        f'<div class="huge-number">{days_left}</div>'
        f'<div style="font-size: 22px; font-weight: 600;">days left</div>'
        f'</div>'
        f'<p style="margin-top: 15px; font-weight: 500; font-size: 14px;">Make today count.</p>'
        f'<div style="position: absolute; right: -50px; bottom: -50px; opacity: 0.15;"><svg width="250" height="250" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="none" stroke="black" stroke-width="2"/><circle cx="50" cy="50" r="35" fill="none" stroke="black" stroke-width="2"/></svg></div>'
        f'</div>'
        
        # Wrapper for the two small cards on right
        f'<div class="col-side" style="display: flex; gap: 16px;">'
        
        # Syllabus Card
        f'<div class="card" style="flex: 1; align-items: center; justify-content: center; padding: 20px;">'
        f'<p style="color: #888; font-size: 13px; margin: 0 0 10px 0;">Syllabus</p>'
        f'<div class="circle-wrap">'
        f'<svg width="110" height="110"><circle class="circle-bg" cx="55" cy="55" r="40"></circle><circle class="circle-progress" cx="55" cy="55" r="40" stroke-dasharray="{circ}" stroke-dashoffset="{offset}"></circle></svg>'
        f'<div class="circle-text">{avg_pct}%</div>'
        f'</div>'
        f'</div>'
        
        # Test Average Card
        f'<div class="card card-purple" style="flex: 1; padding: 20px;">'
        f'<div>'
        f'<p style="font-size: 13px; font-weight: 600; margin: 0;">Test average</p>'
        f'<div class="purple-number">{avg_score:.0f}%</div>'
        f'<p style="font-size: 12px; margin: 5px 0 0 0;">across {len(tests)} test</p>'
        f'</div>'
        f'</div>'
        
        f'</div>' # End wrapper
        f'</div>'
    )

    # --- Main Grid Row 2 (4 Metrics) ---
    row2_html = (
        f'<div class="row">'
        f'<div class="metric-card"><p class="metric-value val-orange">{hours:.1f} h</p><p class="metric-label">Hours studied</p></div>'
        f'<div class="metric-card"><p class="metric-value val-blue">{exam_ready}/{total_ch}</p><p class="metric-label">Exam-ready</p></div>'
        f'<div class="metric-card"><p class="metric-value val-pink">{rev_pct}%</p><p class="metric-label">Revision done</p></div>'
        f'<div class="metric-card"><p class="metric-value val-green">{done}/{len(tasks)}</p><p class="metric-label">Tasks today</p></div>'
        f'</div>'
    )

    # --- Main Grid Row 3 (Lists) ---
    subj_html = ""
    if chapters:
        df = pd.DataFrame(chapters)
        subj_avg = df.groupby("subject_name")["completion_pct"].mean().reset_index()
        colors = ['#f472b6', '#d4ff40', '#38bdf8', '#fb923c', '#a78bfa']
        for i, row in subj_avg.iterrows():
            color = colors[i % len(colors)]
            subj_html += (
                f'<div class="list-item">'
                f'<div class="list-header"><span>{row["subject_name"]}</span><span>{row["completion_pct"]:.0f}%</span></div>'
                f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {row["completion_pct"]}%; background: {color};"></div></div>'
                f'</div>'
            )
            
    tasks_html = ""
    if tasks:
        for t in tasks:
            prio_class = "priority-med" if t['priority'] == "Medium" else "priority-low"
            tasks_html += (
                f'<div class="task-row">'
                f'<div class="task-row-left"><div class="task-checkbox"></div>'
                f'<div class="task-info"><h4>{t["subject_name"] or "General"}</h4><p>{t["start_time"]} – {t["end_time"]} <span class="priority {prio_class}">{t["priority"]}</span></p></div></div>'
                f'</div>'
            )
    else:
        tasks_html = "<p style='color:#888;'>No tasks scheduled.</p>"

    row3_html = (
        f'<div class="row" style="align-items: stretch;">'
        # Left: Today's Focus (Moved up for mobile layout)
        f'<div class="card col-side" style="flex: 1.2;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">'
        f'<h3 style="margin:0; color: #fff;">Today\'s focus</h3>'
        f'<span style="color: #888; font-size: 12px;">{done} of {len(tasks)} done</span>'
        f'</div>'
        f'{tasks_html}'
        f'<div class="start-btn">▶ Start next session</div>'
        f'</div>'

        # Right: Subject Mastery
        f'<div class="card col-main" style="flex: 1.5;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">'
        f'<h3 style="margin:0; color: #fff;">Subject mastery</h3>'
        f'</div>'
        f'{subj_html}'
        f'</div>'
        f'</div>'
    )

    # --- Combine Everything and Render ---
    # Note: Order matters here. We put row1, row2, then row3.
    full_html = header_html + row1_html + row2_html + row3_html
    
    st.markdown(full_html, unsafe_allow_html=True)
