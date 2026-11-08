"""
modules/dashboard.py
--------------------------------------------------
Ultra Premium Dashboard (Study Streak & Study Buddy update)
--------------------------------------------------
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database.db import query
from modules.student import get_chapters

def render_dashboard(student_id, student):
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
        
        /* Widen layout */
        .block-container { padding: 2rem 3rem !important; max-width: 1400px !important; padding-bottom: 100px !important; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        
        /* Grids */
        .row { display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
        .col-main { flex: 2; min-width: 300px; }
        .col-side { flex: 1.2; min-width: 250px; }
        .col-5 { flex: 1; min-width: 130px; }
        .row-split { display: flex; gap: 20px; width: 100%; }
        .row-split > div { flex: 1; }
        
        /* Cards */
        .card { background-color: #1a1a1a; border-radius: 24px; padding: 24px; position: relative; overflow: hidden; border: 1px solid #2a2a2a; display: flex; flex-direction: column; height: 100%; }
        .card-yellow { background: #d4ff40; color: #000; border: none; }
        .card-yellow .badge { background: #000; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; display: inline-block; margin-bottom: 15px; }
        .huge-number { font-size: 110px; font-weight: 800; line-height: 0.9; letter-spacing: -2px; }
        
        .card-purple { background: #c4b5fd; color: #000; border: none; }
        .purple-number { font-size: 65px; font-weight: 800; line-height: 1; margin-top: 10px; }
        .btn-black { background: #000; color: #fff; text-align: center; padding: 12px; border-radius: 12px; font-weight: 600; font-size: 14px; margin-top: 15px; cursor: pointer; }

        /* SVG Progress */
        .circle-wrap { display: flex; justify-content: center; align-items: center; margin: 10px 0; position: relative; }
        .circle-wrap svg { transform: rotate(-90deg); }
        .circle-bg { fill: none; stroke: #2a2a2a; stroke-width: 12; }
        .circle-progress { fill: none; stroke: #d4ff40; stroke-width: 12; stroke-linecap: round; }
        .circle-text { position: absolute; font-size: 24px; font-weight: 700; color: #fff; }

        /* Metric Cards */
        .metric-card { background-color: #1a1a1a; border-radius: 20px; padding: 20px; border: 1px solid #2a2a2a; flex: 1; display: flex; flex-direction: column; }
        .metric-value { font-size: 28px; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
        .metric-label { font-size: 13px; color: #888; margin: 0; font-weight: 500; }
        .val-orange { color: #fb923c; } .val-blue { color: #38bdf8; } .val-pink { color: #f472b6; } .val-green { color: #d4ff40; } .val-purple { color: #c4b5fd; }

        /* Lists & Tasks */
        .progress-bar-bg { background: #2a2a2a; height: 8px; border-radius: 4px; width: 100%; margin-top: 8px; overflow: hidden; }
        .progress-bar-fill { height: 100%; border-radius: 4px; }
        .list-item { margin-bottom: 18px; }
        .list-header { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; color: #fff; }
        .task-row { display: flex; justify-content: space-between; align-items: center; background: #222; border-radius: 16px; padding: 16px; margin-bottom: 12px; }
        .task-row-left { display: flex; align-items: center; gap: 15px; }
        .task-checkbox { width: 24px; height: 24px; border-radius: 8px; border: 2px solid #555; flex-shrink: 0; }
        .task-info h4 { margin: 0; font-size: 16px; color: #fff; }
        .task-info p { margin: 0; font-size: 13px; color: #888; }
        .priority { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-left: 5px; }
        .priority-med { background: #3f3015; color: #f59e0b; }
        .priority-low { background: #1e293b; color: #60a5fa; }
        
        .start-btn { background: #d4ff40; color: #000; text-align: center; padding: 16px; border-radius: 16px; font-weight: 700; margin-top: 20px; cursor: pointer; }
        .open-tracker { color: #d4ff40; font-size: 14px; font-weight: 600; cursor: pointer; }
        
        /* Heatmap Grid */
        .heatmap-container { display: grid; grid-template-columns: repeat(12, 1fr); gap: 4px; margin-top: 15px; }
        .heatmap-cell { aspect-ratio: 1; background: #2a2a2a; border-radius: 4px; }
        .heatmap-cell.active { background: #d4ff40; }
        
        /* Badges */
        .badge-row { display: flex; gap: 15px; margin-top: 15px; }
        .badge-item { display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center; font-size: 11px; color: #888; flex: 1; }
        .badge-icon { width: 50px; height: 50px; border-radius: 50%; border: 1px dashed #444; display: flex; justify-content: center; align-items: center; color: #444; }
        .badge-icon.unlocked { border: 1px solid #d4ff40; color: #d4ff40; background: rgba(212, 255, 64, 0.1); }
        </style>
    """, unsafe_allow_html=True)

    # Data
    today = date.today().isoformat()
    chapters = get_chapters(student_id=student_id)
    total_ch = len(chapters)
    exam_ready = sum(1 for c in chapters if c["status"] == "Exam Ready")
    avg_pct = (round(sum(c["completion_pct"] for c in chapters) / total_ch, 1) if total_ch else 0)
    days_left = (datetime.strptime(student["exam_start_date"], "%Y-%m-%d").date() - date.today()).days if student.get("exam_start_date") else "—"
    tasks = query("SELECT t.*, s.name as subject_name FROM timetable_tasks t LEFT JOIN subjects s ON t.subject_id = s.id WHERE t.student_id=? AND t.task_date=?", (student_id, today))
    done = sum(1 for t in tasks if t["status"] == "Completed")
    tests = query("SELECT * FROM test_records WHERE student_id=?", (student_id,))
    avg_score = (round(sum(t["marks_obtained"] / t["max_marks"] * 100 for t in tests) / len(tests), 1) if tests else 0)
    rev_pct = 0 # Simplified for this view
    hours = query("SELECT COALESCE(SUM(duration_minutes),0)/60.0 AS h FROM timetable_tasks WHERE student_id=? AND status='Completed'", (student_id,), one=True)["h"]

    circ = 2 * 3.14159 * 40
    offset = circ - (avg_pct / 100) * circ

    # Build HTML
    header_html = f'''
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px;">
        <div><p style="color: #888; margin: 0; font-size: 14px;">{datetime.today().strftime("%A, %d %B")}</p>
        <h1 class="header-title" style="color: #fff; margin: 0; font-size: 42px; font-weight: 800; line-height: 1.1;">hey {student["name"]}, let&#39;s lock in.</h1></div>
        <div style="display: flex; gap: 15px; align-items: center;">
            <div style="background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 20px; padding: 10px 20px; display: flex; align-items: center; gap: 10px; width: 200px; color: #888;">
                <span class="material-symbols-rounded" style="font-size: 20px;">search</span><input type="text" placeholder="Search chapters" style="background: transparent; border: none; outline: none; color: #fff; width: 100%;">
            </div>
            <div style="background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 20px; padding: 10px 20px; color: #fff; font-weight: 600; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                <span class="material-symbols-rounded" style="font-size: 18px;">ios_share</span> Share progress
            </div>
            <div style="background: #1a1a1a; border: 1px solid #2a2a2a; width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff;"><span class="material-symbols-rounded">notifications</span></div>
            <div style="background: #c4b5fd; color: #000; width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px;">{student["name"][0].upper()}</div>
        </div>
    </div>
    '''

    row1_html = f'''
    <div class="row">
        <div class="card card-yellow col-main">
            <div class="badge">BOARD EXAM COUNTDOWN</div>
            <div style="display: flex; align-items: baseline; gap: 10px;"><div class="huge-number">{days_left}</div><div style="font-size: 24px; font-weight: 600;">days left</div></div>
            <p style="margin-top: 15px; font-weight: 500; font-size: 15px; margin-bottom: 0;">Make today count — two sessions on the plan.</p>
        </div>
        <div class="col-side"><div class="row-split">
            <div class="card" style="align-items: center; justify-content: center; padding: 20px;">
                <p style="color: #888; font-size: 14px; margin: 0 0 10px 0; width: 100%; text-align: left;">Syllabus done</p>
                <div class="circle-wrap"><svg width="120" height="120"><circle class="circle-bg" cx="60" cy="60" r="40"></circle><circle class="circle-progress" cx="60" cy="60" r="40" stroke-dasharray="{circ}" stroke-dashoffset="{offset}"></circle></svg><div class="circle-text">{avg_pct}%</div></div>
            </div>
            <div class="card card-purple" style="justify-content: space-between; padding: 20px;">
                <div><p style="font-size: 14px; font-weight: 600; margin: 0;">Test average</p><div class="purple-number">{avg_score:.0f}%</div><p style="font-size: 14px; margin: 5px 0 0 0; font-weight: 500;">across {len(tests)} test taken</p></div>
                <div class="btn-black">Take a mock test</div>
            </div>
        </div></div>
    </div>
    '''

    row2_html = f'''
    <div class="row">
        <div class="metric-card col-5"><span class="material-symbols-rounded" style="color: #fb923c; background: #2a1a0c; padding: 8px; border-radius: 10px; margin-bottom: 15px;">timer</span><p class="metric-value val-orange">{hours:.1f} h</p><p class="metric-label">Hours studied</p></div>
        <div class="metric-card col-5"><span class="material-symbols-rounded" style="color: #38bdf8; background: #0c1a2a; padding: 8px; border-radius: 10px; margin-bottom: 15px;">menu_book</span><p class="metric-value val-blue">{exam_ready}/{total_ch}</p><p class="metric-label">Exam-ready chapters</p></div>
        <div class="metric-card col-5"><span class="material-symbols-rounded" style="color: #f472b6; background: #2a0c1a; padding: 8px; border-radius: 10px; margin-bottom: 15px;">autorenew</span><p class="metric-value val-pink">{rev_pct}%</p><p class="metric-label">Revision done</p></div>
        <div class="metric-card col-5"><span class="material-symbols-rounded" style="color: #d4ff40; background: #1a2a0c; padding: 8px; border-radius: 10px; margin-bottom: 15px;">check_box</span><p class="metric-value val-green">{done}/{len(tasks)}</p><p class="metric-label">Tasks today</p></div>
        <div class="metric-card col-5"><span class="material-symbols-rounded" style="color: #c4b5fd; background: #1a0c2a; padding: 8px; border-radius: 10px; margin-bottom: 15px;">science</span><p class="metric-value val-purple">{len(tests)}</p><p class="metric-label">Tests taken</p></div>
    </div>
    '''

    # HEATMAP & BADGES ROW
    heatmap_cells = "".join(['<div class="heatmap-cell active"></div>' if i > 80 else '<div class="heatmap-cell"></div>' for i in range(84)])
    
    row3_html = f'''
    <div class="row">
        <div class="card col-main">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin:0; color: #fff;">Study streak</h3>
                <span style="background: #2a2a2a; color: #d4ff40; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">🔥 1 day current streak</span>
            </div>
            <p style="color: #888; font-size: 13px; margin: 5px 0 0 0;">Every square is a day you logged study time.</p>
            <div class="heatmap-container">{heatmap_cells}</div>
            <div style="display: flex; justify-content: space-between; color: #666; font-size: 11px; margin-top: 10px;">
                <span>Last 12 weeks</span><span>Less 🟩 More</span>
            </div>
        </div>
        <div class="col-side">
            <div class="card" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between;"><h3 style="margin:0; color: #fff;">Badges</h3><span style="color: #888; font-size: 12px;">1 of 4 unlocked</span></div>
                <div class="badge-row">
                    <div class="badge-item"><div class="badge-icon unlocked"><span class="material-symbols-rounded">science</span></div>First mock test</div>
                    <div class="badge-item"><div class="badge-icon"><span class="material-symbols-rounded">local_fire_department</span></div>7-day streak</div>
                    <div class="badge-item"><div class="badge-icon"><span class="material-symbols-rounded">book</span></div>First exam-ready</div>
                    <div class="badge-item"><div class="badge-icon"><span class="material-symbols-rounded">autorenew</span></div>First revision</div>
                </div>
            </div>
            <div class="card" style="background: #222;">
                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 15px;"><span class="material-symbols-rounded" style="color: #d4ff40;">auto_awesome</span><h3 style="margin:0; color: #fff; font-size: 16px;">Study buddy</h3></div>
                <div style="background: #111; border-radius: 12px; padding: 4px 12px; display: flex; align-items: center; border: 1px solid #333;">
                    <input type="text" placeholder="Quiz me on Electrochemistry..." style="background: transparent; border: none; color: #fff; padding: 10px 0; width: 100%; outline: none;">
                    <div style="background: #c4b5fd; color: #000; border-radius: 8px; padding: 4px 8px; cursor: pointer;">➔</div>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <span style="border: 1px solid #444; color: #888; padding: 6px 12px; border-radius: 20px; font-size: 12px;">Explain a chapter</span>
                    <span style="border: 1px solid #444; color: #888; padding: 6px 12px; border-radius: 20px; font-size: 12px;">Quiz me</span>
                </div>
            </div>
        </div>
    </div>
    '''

    # SUBJECT MASTERY & TODAY'S FOCUS (Re-ordered)
    subj_html = ""
    if chapters:
        df = pd.DataFrame(chapters)
        subj_avg = df.groupby("subject_name")["completion_pct"].mean().reset_index()
        colors = ['#f472b6', '#d4ff40', '#38bdf8', '#fb923c', '#a78bfa']
        for i, row in subj_avg.iterrows():
            subj_html += f'<div class="list-item"><div class="list-header"><span>{row["subject_name"]}</span><span>{row["completion_pct"]:.0f}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {row["completion_pct"]}%; background: {colors[i % len(colors)]};"></div></div></div>'

    tasks_html = ""
    if tasks:
        for t in tasks:
            prio_class = "priority-med" if t['priority'] == "Medium" else "priority-low"
            tasks_html += f'<div class="task-row"><div class="task-row-left"><div class="task-checkbox"></div><div class="task-info"><h4>{t["subject_name"] or "General"}</h4><p>{t["start_time"]} – {t["end_time"]} <span class="priority {prio_class}">{t["priority"]}</span></p></div></div></div>'
    
    row4_html = f'''
    <div class="row">
        <div class="card col-main">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;"><h3 style="margin:0; color: #fff;">Subject mastery</h3><span class="open-tracker">Open tracker</span></div>
            {subj_html}
            <div style="background: rgba(212, 255, 64, 0.1); border-left: 4px solid #d4ff40; padding: 16px; border-radius: 12px; margin-top: 15px; color: #d4ff40; font-weight: 500; font-size: 14px;">
                English is trailing the pack — a 30-minute session today would close the gap.
            </div>
        </div>
        <div class="card col-side">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;"><h3 style="margin:0; color: #fff;">Today&#39;s focus</h3><span style="color: #888; font-size: 13px; background: #2a2a2a; padding: 4px 10px; border-radius: 10px;">{done} of {len(tasks)} done</span></div>
            {tasks_html}
            <div style="border: 1px dashed #444; border-radius: 12px; padding: 15px; text-align: center; color: #888; font-size: 14px; margin-top: 15px;">+ Add a study block</div>
            <div class="start-btn">▶ Start next session</div>
        </div>
    </div>
    '''

    st.markdown(header_html + row1_html + row2_html + row3_html + row4_html, unsafe_allow_html=True)
