"""
modules/tests.py
--------------------------------------------------
Test/exam recording + analysis.
--------------------------------------------------
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database.db import query, execute
from modules.student import get_subjects, get_chapters


def add_test(student_id, subject_id, chapter_id, test_date, max_marks,
             marks, time_taken, mistakes, improve):
    if max_marks <= 0:
        raise ValueError("Max marks must be > 0.")
    if marks < 0 or marks > max_marks:
        raise ValueError("Marks obtained must be between 0 and max marks.")
    return execute(
        """INSERT INTO test_records
        (student_id, subject_id, chapter_id, test_date, max_marks, marks_obtained,
         time_taken_minutes, mistakes, improvement_topics)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (student_id, subject_id, chapter_id, test_date, max_marks, marks,
         time_taken, mistakes, improve),
    )


def get_tests(student_id):
    return query(
        """SELECT t.*, s.name AS subject_name, c.name AS chapter_name
        FROM test_records t
        JOIN subjects s ON t.subject_id = s.id
        LEFT JOIN chapters c ON t.chapter_id = c.id
        WHERE t.student_id=?
        ORDER BY t.test_date DESC""",
        (student_id,),
    )


def render_test_manager(student_id):
    st.subheader("🧪 Test & Examination Manager")
    subjects = get_subjects(student_id)
    if not subjects:
        st.info("Add subjects first.")
        return
    chapters = get_chapters(student_id=student_id)

    with st.expander("➕ Record a Test", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            subj = st.selectbox("Subject", [s["name"] for s in subjects])
            subj_id = next(s["id"] for s in subjects if s["name"] == subj)
            chap_opts = ["(General)"] + [c["name"] for c in chapters if c["subject_id"] == subj_id]
            chap = st.selectbox("Chapter (optional)", chap_opts)
            chap_id = None if chap == "(General)" else next(
                c["id"] for c in chapters if c["subject_id"] == subj_id and c["name"] == chap
            )
            td = st.date_input("Test date", value=date.today())
        with c2:
            max_m = st.number_input("Max marks", 1.0, 500.0, 100.0, step=1.0)
            obt = st.number_input("Marks obtained", 0.0, 500.0, 75.0, step=1.0)
            time_taken = st.number_input("Time taken (min)", 0, 600, 90)
        mistakes = st.text_input("Mistakes made")
        improve = st.text_input("Topics to improve")
        if st.button("Save Test", type="primary"):
            try:
                add_test(student_id, subj_id, chap_id, td.isoformat(),
                         max_m, obt, time_taken, mistakes, improve)
                st.success("Test saved.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    tests = get_tests(student_id)
    if not tests:
        st.info("No tests recorded yet.")
        return

    df = pd.DataFrame(tests)
    df["percentage"] = (df["marks_obtained"] / df["max_marks"] * 100).round(1)
    st.dataframe(
        df[["test_date", "subject_name", "chapter_name", "marks_obtained",
            "max_marks", "percentage", "mistakes", "improvement_topics"]],
        use_container_width=True, hide_index=True,
    )

    fig = px.line(df.sort_values("test_date"), x="test_date", y="percentage",
                  color="subject_name", markers=True,
                  title="Test Score Trend (%)")
    st.plotly_chart(fig, use_container_width=True)
