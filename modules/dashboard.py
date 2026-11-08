"""
modules/dashboard.py
--------------------------------------------------
Ultra Premium Pixel-Perfect Dashboard (Desktop + Mobile)
--------------------------------------------------
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from database.db import query
from modules.student import get_chapters

def render_dashboard(student_id, student):
    # --- 1. Custom CSS (Hides Streamlit Sidebar, Builds Custom Grid) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
        
        /* Hide Streamlit Defaults */
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; background-color: #0e0e0e; }

        /* --- LAYOUT WRAPPERS --- */
        .app-container { display: flex; min-height: 100vh; }
        
        /* --- CUSTOM SIDEBAR --- */
        .custom-sidebar {
            width: 260px; background: #0e0e0e; border-right: 1px solid #1f1f1f;
            padding: 30px 20px; display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 100;
        }
        .logo-box { display: flex; align-items: center; gap: 10px; margin-bottom: 40px; }
        .logo-icon { background: #d4ff40; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #000; font-size: 20px; }
        .logo-text { color: #fff; font-weight: 700; font-size: 20px; line-height: 1; }
        .logo-sub { color: #888; font-size: 11px; line-height: 1; margin-top: 4px; }
        
        .nav-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
        .nav-item { display: flex; align-items: center; gap: 15px; padding: 12px 16px; border-radius: 12px; color: #888; font-weight: 500; font-size: 14px; text-decoration: none; cursor: pointer; transition: 0.2s; }
        .nav-item:hover { background: #1a1a1a; color: #fff; }
        .nav-item.active { background: #d4ff40; color: #000; font-weight: 600; }
        .nav-item.active .material-symbols-rounded { color: #000; }

        /* Focus Mode (Sidebar Bottom) */
        .focus-mode { margin-top: auto; background: #1a1a1a; border-radius: 16px; padding: 20px; border: 1px solid #2a2a2a; }
        .focus-mode h4 { color: #fff; margin: 0 0 5px 0; font-size: 14px; }
        .focus-mode p { color: #888; font-size: 12px; margin: 0 0 15px 0; line-height: 1.4; }
        .focus-btn { background: transparent; border: 1px solid #555; color: #fff; width: 100%; padding: 10px; border-radius: 10px; font-size: 12px; font-weight: 600; cursor: pointer; }

        /* --- MAIN CONTENT AREA --- */
        .main-content { margin-left: 260px; flex: 1; padding: 40px; max-width: 1200px; }

        /* Top Header (Search & Avatar) */
        .top-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; }
        .search-bar { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 20px; padding: 10px 20px; display: flex; align-items: center; gap: 10px; width: 300px; color: #888; }
        .search-bar input { background: transparent; border: none; outline: none; color: #fff; font-family: 'Outfit'; font-size: 14px; width: 100%; }
        .header-right { display: flex; align-items: center; gap: 15px; }
        .icon-btn { background: #1a1a1a; border: 1px solid #2a2a2a; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; cursor: pointer; }
        .avatar { background: #c4b5fd; color: #000; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; }

        /* Titles */
        .date-text { color: #888; margin: 0; font-size: 14px; }
        .page-title { color: #fff; margin: 0; font-size: 42px; font-weight: 800; line-height: 1.1; }

        /* --- GRID SYSTEM (Desktop) --- */
        .row { display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
        .col-main { flex: 2; min-width: 300px; }
        .col-side { flex: 1.2; min-width: 250px; }
        .col-4 { flex: 1; min-width: 150px; }
        .split-2 { display: flex; gap: 20px; width: 100%; }
        .split-2 > div { flex: 1; }

        /* --- CARDS --- */
        .card { background-color: #1a1a1a; border-radius: 24px; padding: 24px; position: relative; overflow: hidden; border: 1px solid #2a2a2a; display: flex; flex-direction: column; justify-content: space-between; height: 100%; }
        
        /* Specific Cards */
        .card-yellow { background: #d4ff40; color: #000; border: none; }
        .card-yellow .badge { background: #000; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; display: inline-block; margin-bottom: 15px; letter-spacing: 0.5px; }
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
        .metric-card { background-color: #1a1a1a; border-radius: 20px; padding: 20px; border: 1px solid #2a2a2a; flex: 1; }
        .metric-value { font-size: 24px; font-weight: 700; margin: 0; }
        .metric-label { font-size: 13px; color: #888; margin: 0; }
        .val-orange { color: #fb923c; } .val-blue { color: #38bdf8; } .val-pink { color: #f472b6; } .val-green { color: #d4ff40; }

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

        /* --- MOBILE BOTTOM NAV --- */
        .bottom-nav { display: none; position: fixed; bottom: 0; left: 0; width: 100%; background: #1a1a1a; justify-content: space-around; padding: 15px 0 25px 0; border-top-left-radius: 30px; border-top-right-radius: 30px; border-top: 1px solid #2a2a2a; z-index: 9999; }
        .nav-icon-mobile { display: flex; flex-direction: column; align-items: center; color: #666; font-size: 11px; gap: 4px; }
        .nav-icon-mobile.active { color: #d4ff40; }
        .nav-icon-mobile.active .material-symbols-rounded { background: #d4ff40; color: #000; border-radius: 12px; padding: 4px 16px; }

        /* --- RESPONSIVE MEDIA QUERIES --- */
        @media (max-width: 900px) {
            /* Hide Sidebar & Adjust Main */
            .custom-sidebar { display: none; }
            .main-content { margin-left: 0; padding: 20px 20px 100px 20px; }
            .top-header .search-bar { display: none; } /* Hide search on mobile */
            
            /* Stack Grids */
            .row { flex-direction: column; gap: 15px; }
            .col-main, .col-side, .col-4 { min-width: 100%; }
            .split-2 { flex-direction: row; gap: 15px; } /* Keep small cards side-by-side */
            
            /* Adjust Text Sizes */
            .page-title { font-size: 32px; }
            .huge-number { font-size: 80px; }
            .purple-number { font-size: 55px; }
            
            /* Show Bottom Nav */
            .bottom-nav { display: flex; }
            
            /* Reorder Desktop Layout for Mobile (Focus before Mastery) */
            .mobile-order-1 { order: 1; }
            .mobile-order-2 { order: 2; }
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Data Fetching ---
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
    revs = query("SELECT r.* FROM revision_records r JOIN chapters c ON r.chapter_id=c.id JOIN subjects s ON c.subject_id=s.id WHERE s.student_id=?", (student_id,))
    rev_pct = round(sum(1 for r in revs if r["status"] == "Completed") / len(revs) * 100, 1) if revs else 0
    hours = query("SELECT COALESCE(SUM(duration_minutes),0)/60.0 AS h FROM timetable_tasks WHERE student_id=? AND status='Completed'", (student_id,), one=True)["h"]

    # --- SVG Circular Logic ---
    circ = 2 * 3.14159 * 40
    offset = circ - (avg_pct / 100) * circ

    # --- Generate HTML Strings ---
    
    # Subjects
    subj_html = ""
    if chapters:
        df = pd.DataFrame(chapters)
        subj_avg = df.groupby("subject_name")["completion_pct"].mean().reset_index()
        colors = ['#f472b6', '#d4ff40', '#38bdf8', '#fb923c', '#a78bfa']
        for i, row in subj_avg.iterrows():
            subj_html += f'<div class="list-item"><div class="list-header"><span>{row["subject_name"]}</span><span>{row["completion_pct"]:.0f}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {row["completion_pct"]}%; background: {colors[i % len(colors)]};"></div></div></div>'

    # Tasks
    tasks_html = ""
    if tasks:
        for t in tasks:
            prio_class = "priority-med" if t['priority'] == "Medium" else "priority-low"
            tasks_html += f'<div class="task-row"><div class="task-row-left"><div class="task-checkbox"></div><div class="task-info"><h4>{t["subject_name"] or "General"}</h4><p>{t["start_time"]} – {t["end_time"]} <span class="priority {prio_class}">{t["priority"]}</span></p></div></div></div>'
    else:
        tasks_html = "<p style='color:#888;'>No tasks scheduled.</p>"

    # --- Assemble Full HTML Layout ---
    
    # 1. Sidebar
    sidebar_html = (
        f'<div class="custom-sidebar">'
        f'<div class="logo-box"><div class="logo-icon">EO</div><div><div class="logo-text">ExamOrbit</div><div class="logo-sub">Plan Smart. Track daily.</div></div></div>'
        f'<ul class="nav-list">'
        f'<li class="nav-item active"><span class="material-symbols-rounded">grid_view</span> Dashboard</li>'
        f'<li class="nav-item"><span class="material-symbols-rounded">calendar_month</span> My Timetable</li>'
        f'<li class="nav-item"><span class="material-symbols-rounded">menu_book</span> Subjects & Chapters</li>'
        f'<li class="nav-item"><span class="material-symbols-rounded">autorenew</span> Revision</li>'
        f'<li class="nav-item"><span class="material-symbols-rounded">edit_document</span> Tests</li>'
        f'<li class="nav-item"><span class="material-symbols-rounded">monitoring</span> Analytics</li>'
        f'<li class="nav-item"><span class="material-symbols-rounded">person</span> My Profile</li>'
        f'</ul>'
        f'<div class="focus-mode"><h4>Focus mode</h4><p>Mute the noise and run a timed study sprint.</p><div class="focus-btn">Start a sprint</div></div>'
        f'</div>'
    )

    # 2. Top Header
    header_html = (
        f'<div class="top-header">'
        f'<div>'
        f'<p class="date-text">{datetime.today().strftime("%A, %d %B")}</p>'
        f'<h1 class="page-title">hey {student["name"]}, let\'s lock in.</h1>'
        f'</div>'
        f'<div class="header-right">'
        f'<div class="search-bar"><span class="material-symbols-rounded">search</span><input type="text" placeholder="Search chapters"></div>'
        f'<div class="icon-btn"><span class="material-symbols-rounded">notifications</span></div>'
        f'<div class="avatar">{student["name"][0].upper()}</div>'
        f'</div>'
        f'</div>'
    )

    # 3. Row 1 (Countdown + Syllabus + Test)
    row1_html = (
        f'<div class="row">'
        # Countdown
        f'<div class="card card-yellow col-main">'
        f'<div class="badge">BOARD EXAM COUNTDOWN</div>'
        f'<div style="display: flex; align-items: baseline; gap: 10px;"><div class="huge-number">{days_left}</div><div style="font-size: 24px; font-weight: 600;">days left</div></div>'
        f'<p style="margin-top: 15px; font-weight: 500; font-size: 15px; margin-bottom: 0;">Make today count — two sessions on the plan.</p>'
        f'<div style="position: absolute; right: -50px; bottom: -50px; opacity: 0.15;"><svg width="250" height="250" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="none" stroke="black" stroke-width="2"/><circle cx="50" cy="50" r="35" fill="none" stroke="black" stroke-width="2"/></svg></div>'
        f'</div>'
        
        # Syllabus
        f'<div class="card col-side" style="align-items: center; justify-content: center;">'
        f'<p style="color: #888; font-size: 14px; margin: 0 0 10px 0; width: 100%; text-align: left;">Syllabus done</p>'
        f'<div class="circle-wrap"><svg width="120" height="120"><circle class="circle-bg" cx="60" cy="60" r="40"></circle><circle class="circle-progress" cx="60" cy="60" r="40" stroke-dasharray="{circ}" stroke-dashoffset="{offset}"></circle></svg><div class="circle-text">{avg_pct}%</div></div>'
        f'<p style="color: #888; font-size: 13px; margin-top: 10px;">Keep stacking chapters</p>'
        f'</div>'
        
        # Test Average
        f'<div class="card card-purple col-side" style="justify-content: space-between;">'
        f'<div><p style="font-size: 14px; font-weight: 600; margin: 0;">Test average</p><div class="purple-number">{avg_score:.0f}%</div><p style="font-size: 14px; margin: 5px 0 0 0; font-weight: 500;">across {len(tests)} test taken</p></div>'
        f'<div class="btn-black">Take a mock test</div>'
        f'</div>'
        f'</div>'
    )

    # 4. Row 2 (4 Metrics)
    row2_html = (
        f'<div class="row">'
        f'<div class="metric-card col-4"><span class="material-symbols-rounded" style="color: #fb923c; background: #2a1a0c; padding: 8px; border-radius: 10px; margin-bottom: 15px;">timer</span><p class="metric-value val-orange">{hours:.1f} h</p><p class="metric-label">Hours studied</p></div>'
        f'<div class="metric-card col-4"><span class="material-symbols-rounded" style="color: #38bdf8; background: #0c1a2a; padding: 8px; border-radius: 10px; margin-bottom: 15px;">menu_book</span><p class="metric-value val-blue">{exam_ready}/{total_ch}</p><p class="metric-label">Exam-ready chapters</p></div>'
        f'<div class="metric-card col-4"><span class="material-symbols-rounded" style="color: #f472b6; background: #2a0c1a; padding: 8px; border-radius: 10px; margin-bottom: 15px;">autorenew</span><p class="metric-value val-pink">{rev_pct}%</p><p class="metric-label">Revision done</p></div>'
        f'<div class="metric-card col-4"><span class="material-symbols-rounded" style="color: #d4ff40; background: #1a2a0c; padding: 8px; border-radius: 10px; margin-bottom: 15px;">check_box</span><p class="metric-value val-green">{done}/{len(tasks)}</p><p class="metric-label">Tasks today</p></div>'
        f'</div>'
    )

    # 5. Row 3 (Mastery + Focus) - Uses flex to swap order on mobile via CSS
    row3_html = (
        f'<div class="row">'
        
        # Subject Mastery
        f'<div class="card col-main mobile-order-2">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;"><h3 style="margin:0; color: #fff;">Subject mastery</h3><span class="open-tracker">Open tracker</span></div>'
        f'{subj_html}'
        f'</div>'
        
        # Today's Focus
        f'<div class="card col-side mobile-order-1">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;"><h3 style="margin:0; color: #fff;">Today\'s focus</h3><span style="color: #888; font-size: 13px; background: #2a2a2a; padding: 4px 10px; border-radius: 10px;">{done} of {len(tasks)} done</span></div>'
        f'{tasks_html}'
        f'<div style="border: 1px dashed #444; border-radius: 12px; padding: 15px; text-align: center; color: #888; font-size: 14px; margin-top: 15px;">+ Add a study block</div>'
        f'<div class="start-btn">▶ Start next session</div>'
        f'</div>'
        
        f'</div>'
    )

    # 6. Mobile Bottom Nav
    bottom_nav_html = (
        f'<div class="bottom-nav">'
        f'<div class="nav-icon-mobile active"><span class="material-symbols-rounded">grid_view</span></div>'
        f'<div class="nav-icon-mobile"><span class="material-symbols-rounded">calendar_month</span></div>'
        f'<div class="nav-icon-mobile"><span class="material-symbols-rounded">menu_book</span></div>'
        f'<div class="nav-icon-mobile"><span class="material-symbols-rounded">check_box</span></div>'
        f'<div class="nav-icon-mobile"><span class="material-symbols-rounded">monitoring</span></div>'
        f'</div>'
    )

    # Combine into final layout
    full_html = (
        f'<div class="app-container">'
        f'{sidebar_html}'
        f'<div class="main-content">'
        f'{header_html}'
        f'{row1_html}'
        f'{row2_html}'
        f'{row3_html}'
        f'</div>'
        f'{bottom_nav_html}'
        f'</div>'
    )

    st.markdown(full_html, unsafe_allow_html=True)
