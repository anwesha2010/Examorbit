"""
database/db.py
--------------------------------------------------
SQLite connection, schema initialisation, and
sample data seeding for ExamOrbit.
--------------------------------------------------
"""
import os
import sqlite3
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "examorbit.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

CHAPTER_STAGES = [
    "Not Started",
    "Learning in Progress",
    "Theory Completed",
    "Practice Completed",
    "Revision 1 Completed",
    "Revision 2 Completed",
    "Previous Year Questions Completed",
    "Test Completed",
    "Exam Ready",
]


def get_connection():
    """Return a SQLite connection with dict-like row access."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables from schema.sql if missing, seed demo data on first run."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        seed_sample_data(conn)
    conn.close()


def seed_sample_data(conn):
    """Insert a demo student with subjects, chapters and sample activity."""
    today = date.today()
    exam_start = today + timedelta(days=90)

    cur = conn.execute(
        """INSERT INTO students
        (name, class_level, board, academic_year, target_percentage,
         daily_study_hours, exam_start_date)
        VALUES (?,?,?,?,?,?,?)""",
        ("Demo Student", "12", "CBSE", "2025-2026", 92.0, 6.0, exam_start.isoformat()),
    )
    sid = cur.lastrowid

    subject_map = {
        "Physics":          ["Electric Charges & Fields", "Current Electricity",
                             "Magnetism", "Optics", "Modern Physics"],
        "Chemistry":        ["Solutions", "Electrochemistry", "Chemical Kinetics",
                             "d-Block Elements", "Organic Chemistry"],
        "Mathematics":      ["Relations & Functions", "Inverse Trigonometry",
                             "Matrices", "Calculus", "Probability"],
        "Computer Science": ["Python Revision", "File Handling",
                             "Data Structures", "SQL", "Computer Networks"],
        "English":          ["Reading Comprehension", "Writing Skills",
                             "Literature – Flamingo", "Literature – Vistas"],
    }
    colors = ["#1e3a8a", "#16a34a", "#0ea5e9", "#f59e0b", "#8b5cf6"]
    difficulties = ["Easy", "Medium", "Hard"]
    priorities = ["Low", "Medium", "High"]

    subject_ids = {}
    for (subj, _), color in zip(subject_map.items(), colors):
        c = conn.execute(
            "INSERT INTO subjects (student_id, name, color) VALUES (?,?,?)",
            (sid, subj, color),
        )
        subject_ids[subj] = c.lastrowid

    idx = 0
    for subj, chapters in subject_map.items():
        for i, ch in enumerate(chapters):
            stage = CHAPTER_STAGES[min(i, len(CHAPTER_STAGES) - 1)]
            pct = int(CHAPTER_STAGES.index(stage) / (len(CHAPTER_STAGES) - 1) * 100)
            start = today - timedelta(days=15 - i * 2)
            expected = today + timedelta(days=20 + i * 3)
            conn.execute(
                """INSERT INTO chapters
                (subject_id, name, priority, difficulty, status, completion_pct,
                 start_date, expected_completion_date, revisions_count, confidence)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (subject_ids[subj], ch,
                 priorities[idx % 3], difficulties[idx % 3],
                 stage, pct, start.isoformat(), expected.isoformat(),
                 min(i, 2), 3 + (idx % 2)),
            )
            idx += 1

    for i in range(4):
        td = today + timedelta(days=i % 2)
        conn.execute(
            """INSERT INTO timetable_tasks
            (student_id, subject_id, task_date, start_time, end_time,
             duration_minutes, priority, status)
            VALUES (?,?,?,?,?,?,?,?)""",
            (sid, subject_ids[list(subject_map)[i % 5]], td.isoformat(),
             f"{9 + i * 2:02d}:00", f"{10 + i * 2:02d}:00",
             60, priorities[i % 3], "Completed" if i == 0 else "Pending"),
        )

    conn.execute(
        """INSERT INTO test_records
        (student_id, subject_id, test_date, max_marks, marks_obtained,
         mistakes, improvement_topics)
        VALUES (?,?,?,?,?,?,?)""",
        (sid, subject_ids["Physics"], (today - timedelta(days=5)).isoformat(),
         50, 38, "Sign errors in integration", "Electrostatics formulas"),
    )

    conn.commit()


def query(sql, params=(), one=False):
    """Run a SELECT and return list of dicts (or single dict if one=True)."""
    conn = get_connection()
    try:
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        return (rows[0] if rows else None) if one else rows
    finally:
        conn.close()


def execute(sql, params=()):
    """Run INSERT/UPDATE/DELETE and return lastrowid."""
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
