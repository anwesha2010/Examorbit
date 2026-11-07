-- ============================================================
-- ExamOrbit — SQLite Schema
-- ============================================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class_level TEXT NOT NULL CHECK(class_level IN ('10','12')),
    board TEXT NOT NULL DEFAULT 'CBSE',
    academic_year TEXT NOT NULL,
    target_percentage REAL DEFAULT 90.0,
    daily_study_hours REAL DEFAULT 6.0,
    exam_start_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#1e3a8a',
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    priority TEXT DEFAULT 'Medium' CHECK(priority IN ('Low','Medium','High')),
    difficulty TEXT DEFAULT 'Medium' CHECK(difficulty IN ('Easy','Medium','Hard')),
    status TEXT DEFAULT 'Not Started',
    completion_pct INTEGER DEFAULT 0,
    start_date TEXT,
    expected_completion_date TEXT,
    actual_completion_date TEXT,
    revisions_count INTEGER DEFAULT 0,
    test_marks REAL,
    confidence INTEGER DEFAULT 3,
    is_weak INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS timetable_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER,
    chapter_id INTEGER,
    task_date TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    duration_minutes INTEGER DEFAULT 60,
    priority TEXT DEFAULT 'Medium',
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Completed','Missed')),
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    FOREIGN KEY(chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS revision_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    revision_number INTEGER NOT NULL CHECK(revision_number IN (1,2,3)),
    scheduled_date TEXT NOT NULL,
    completed_date TEXT,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Completed','Overdue')),
    notes TEXT,
    FOREIGN KEY(chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS test_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    chapter_id INTEGER,
    test_date TEXT NOT NULL,
    max_marks REAL NOT NULL,
    marks_obtained REAL NOT NULL,
    time_taken_minutes INTEGER,
    mistakes TEXT,
    improvement_topics TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY(chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER,
    chapter_id INTEGER,
    session_date TEXT NOT NULL,
    minutes_studied INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    FOREIGN KEY(chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS student_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    chapter_id INTEGER,
    note_text TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_chapters_subject ON chapters(subject_id);
CREATE INDEX IF NOT EXISTS idx_tasks_date ON timetable_tasks(task_date);
CREATE INDEX IF NOT EXISTS idx_revision_sched ON revision_records(scheduled_date);
