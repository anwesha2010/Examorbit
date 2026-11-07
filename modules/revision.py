"""
modules/revision.py
--------------------------------------------------
Revision manager with upcoming / overdue tracking.
--------------------------------------------------
"""
import streamlit as st
from datetime import date, timedelta
from database.db import query, execute
from modules.student import get_chapters
from modules.priority import rank_chapters


def schedule_revision(chapter_id, rev_no, scheduled_date, notes=""):
    if rev_no not in (1, 2, 3):
        raise ValueError("Revision number must be 1, 2 or 3.")
    return execute(
        """INSERT INTO revision_records
        (chapter_id, revision_number, scheduled_date, notes)
        VALUES (?,?,?,?)""",
        (chapter_id, rev_no, scheduled_date, notes),
    )


def get_revisions(student_id):
    return query(
        """SELECT r.*, c.name AS chapter_name, s.name AS subject_name
        FROM revision_records r
        JOIN chapters c ON r.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE s.student_id=? ORDER BY r.scheduled_date""",
        (student_id,),
    )


def complete_revision(rev_id):
    execute(
        "UPDATE revision_records SET status='Completed', completed_date=? WHERE id=?",
        (date.today().isoformat(), rev_id),
    )


def mark_overdue_revisions(student_id):
    today = date.today().isoformat()
    execute(
        """UPDATE revision_records SET status='Overdue'
        WHERE status='Pending' AND scheduled_date < ? AND chapter_id IN (
            SELECT c.id FROM chapters c
            JOIN subjects s ON c.subject_id=s.id WHERE s.student_id=?)""",
        (today, student_id),
    )


def render_revision_manager(student_id):
    st.subheader("🔁 Revision Manager")
    mark_overdue_revisions(student_id)

    chapters = get_chapters(student_id=student_id)
    if not chapters:
        st.info("Add chapters first.")
        return

    with st.expander("➕ Schedule a Revision", expanded=False):
        opts = {f"{c['id']} • {c['subject_name']} • {c['name']}": c["id"]
                for c in chapters}
        chosen = st.selectbox("Chapter", list(opts.keys()), key="rev_ch")
        rev_no = st.selectbox("Revision #", [1, 2, 3])
        sched = st.date_input("Scheduled date",
                              value=date.today() + timedelta(days=3))
        note = st.text_input("Notes (optional)")
        if st.button("Schedule Revision"):
            schedule_revision(opts[chosen], rev_no, sched.isoformat(), note)
            st.success("Revision scheduled.")
            st.rerun()

    revs = get_revisions(student_id)
    if not revs:
        st.info("No revisions scheduled yet.")
        return

    today = date.today().isoformat()
    upcoming = [r for r in revs if r["status"] == "Pending"
                and r["scheduled_date"] >= today]
    overdue = [r for r in revs if r["status"] == "Overdue"]
    completed = [r for r in revs if r["status"] == "Completed"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Upcoming", len(upcoming))
    c2.metric("Overdue", len(overdue))
    c3.metric("Completed", len(completed))

    st.markdown("#### ⏰ Upcoming")
    if upcoming:
        for r in upcoming:
            cols = st.columns([3, 2, 1, 1])
            cols[0].write(f"**{r['subject_name']}** — {r['chapter_name']} "
                          f"(Rev {r['revision_number']})")
            cols[1].write(f"Due: {r['scheduled_date']}")
            if cols[2].button("✅", key=f"c_{r['id']}"):
                complete_revision(r["id"]); st.rerun()
            if cols[3].button("🗑️", key=f"d_{r['id']}"):
                execute("DELETE FROM revision_records WHERE id=?", (r["id"],))
                st.rerun()
    else:
        st.caption("Nothing upcoming.")

    st.markdown("#### ⚠️ Overdue")
    if overdue:
        for r in overdue:
            cols = st.columns([3, 2, 1])
            cols[0].write(f"**{r['subject_name']}** — {r['chapter_name']} "
                          f"(Rev {r['revision_number']})")
            cols[1].write(f"Was due: {r['scheduled_date']}")
            if cols[2].button("Mark complete", key=f"oc_{r['id']}"):
                complete_revision(r["id"]); st.rerun()
    else:
        st.caption("No overdue revisions. 🎉")

    st.markdown("#### 🎯 Suggested Revision Priority")
    ranked = rank_chapters(chapters)[:5]
    for ch in ranked:
        reasons = ", ".join(ch["reasons"]) or "baseline priority"
        st.write(f"**{ch['subject_name']} • {ch['name']}** "
                 f"— score {ch['score']} ({reasons})")
