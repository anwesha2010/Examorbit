"""
modules/student.py
--------------------------------------------------
Student profile, subjects and chapters CRUD.
--------------------------------------------------
"""
from database.db import query, execute, CHAPTER_STAGES


def get_student(student_id=None):
    if student_id:
        return query("SELECT * FROM students WHERE id=?", (student_id,), one=True)
    return query("SELECT * FROM students ORDER BY id LIMIT 1", one=True)


def update_student(student_id, name, class_level, academic_year,
                   target_pct, daily_hours, exam_date):
    execute(
        """UPDATE students SET name=?, class_level=?, academic_year=?,
        target_percentage=?, daily_study_hours=?, exam_start_date=? WHERE id=?""",
        (name, class_level, academic_year, target_pct,
         daily_hours, exam_date, student_id),
    )


def get_subjects(student_id):
    return query(
        "SELECT * FROM subjects WHERE student_id=? ORDER BY id", (student_id,)
    )


def add_subject(student_id, name, color="#1e3a8a"):
    if not name.strip():
        raise ValueError("Subject name cannot be empty.")
    return execute(
        "INSERT INTO subjects (student_id, name, color) VALUES (?,?,?)",
        (student_id, name.strip(), color),
    )


def delete_subject(subject_id):
    execute("DELETE FROM subjects WHERE id=?", (subject_id,))


def get_chapters(subject_id=None, student_id=None):
    base = """
        SELECT c.*, s.name AS subject_name, s.color AS subject_color
        FROM chapters c JOIN subjects s ON c.subject_id = s.id
    """
    if subject_id:
        return query(base + " WHERE c.subject_id=? ORDER BY c.id", (subject_id,))
    if student_id:
        return query(base + " WHERE s.student_id=? ORDER BY s.id, c.id", (student_id,))
    return query(base + " ORDER BY c.id")


def add_chapter(subject_id, name, priority="Medium", difficulty="Medium",
                expected_date=None, notes=None):
    if not name.strip():
        raise ValueError("Chapter name cannot be empty.")
    return execute(
        """INSERT INTO chapters
        (subject_id, name, priority, difficulty, expected_completion_date, notes)
        VALUES (?,?,?,?,?,?)""",
        (subject_id, name.strip(), priority, difficulty, expected_date, notes),
    )


def update_chapter(chapter_id, **kwargs):
    """Update any allowed chapter field."""
    allowed = {"name", "priority", "difficulty", "status", "completion_pct",
               "start_date", "expected_completion_date", "actual_completion_date",
               "revisions_count", "test_marks", "confidence", "is_weak", "notes"}
    fields, values = [], []
    for k, v in kwargs.items():
        if k in allowed:
            fields.append(f"{k}=?")
            values.append(v)
    if not fields:
        return
    values.append(chapter_id)
    execute(f"UPDATE chapters SET {', '.join(fields)} WHERE id=?", tuple(values))


def delete_chapter(chapter_id):
    execute("DELETE FROM chapters WHERE id=?", (chapter_id,))
