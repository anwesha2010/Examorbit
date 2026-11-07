"""
modules/timetable.py
--------------------------------------------------
Timetable CRUD + missed-task recovery.
--------------------------------------------------
"""
from datetime import date, timedelta
from database.db import query, execute


def add_task(student_id, subject_id, chapter_id, task_date, start_time,
             end_time, duration, priority, notes=""):
    dup = query(
        """SELECT id FROM timetable_tasks
        WHERE student_id=? AND task_date=? AND subject_id IS ?
        AND chapter_id IS ? AND start_time=?""",
        (student_id, task_date, subject_id, chapter_id, start_time), one=True,
    )
    if dup:
        raise ValueError("An identical task already exists for that slot.")
    return execute(
        """INSERT INTO timetable_tasks
        (student_id, subject_id, chapter_id, task_date, start_time, end_time,
         duration_minutes, priority, notes)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (student_id, subject_id, chapter_id, task_date, start_time, end_time,
         duration, priority, notes),
    )


def get_tasks(student_id, task_date=None, status=None):
    sql = """
        SELECT t.*, s.name AS subject_name, c.name AS chapter_name
        FROM timetable_tasks t
        LEFT JOIN subjects s ON t.subject_id = s.id
        LEFT JOIN chapters c ON t.chapter_id = c.id
        WHERE t.student_id=?
    """
    params = [student_id]
    if task_date:
        sql += " AND t.task_date=?"
        params.append(task_date)
    if status:
        sql += " AND t.status=?"
        params.append(status)
    sql += " ORDER BY t.task_date, t.start_time"
    return query(sql, tuple(params))


def mark_task(task_id, status):
    if status not in ("Pending", "Completed", "Missed"):
        raise ValueError("Invalid task status.")
    execute("UPDATE timetable_tasks SET status=? WHERE id=?", (status, task_id))


def delete_task(task_id):
    execute("DELETE FROM timetable_tasks WHERE id=?", (task_id,))


def mark_missed_for_past_days(student_id):
    """Auto-mark yesterday-and-earlier pending tasks as Missed."""
    today = date.today().isoformat()
    count = query(
        """SELECT COUNT(*) AS c FROM timetable_tasks
        WHERE student_id=? AND status='Pending' AND task_date < ?""",
        (student_id, today), one=True,
    )["c"]
    if count:
        execute(
            """UPDATE timetable_tasks SET status='Missed'
            WHERE student_id=? AND status='Pending' AND task_date < ?""",
            (student_id, today),
        )
    return count


def get_missed_tasks(student_id):
    return query(
        """SELECT t.*, s.name AS subject_name
        FROM timetable_tasks t LEFT JOIN subjects s ON t.subject_id=s.id
        WHERE t.student_id=? AND t.status='Missed'
        ORDER BY t.task_date DESC""",
        (student_id,),
    )


def suggest_slots(student_id, days_ahead=7, daily_hours=6):
    today = date.today()
    out = []
    for d in range(1, days_ahead + 1):
        target = (today + timedelta(days=d)).isoformat()
        used = query(
            """SELECT COALESCE(SUM(duration_minutes),0) AS mins
            FROM timetable_tasks WHERE student_id=? AND task_date=?""",
            (student_id, target), one=True,
        )["mins"]
        free = max(0, daily_hours - used / 60)
        if free > 0:
            out.append({"date": target, "free_hours": round(free, 1)})
    return out
