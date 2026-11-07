"""
modules/analytics.py
--------------------------------------------------
Plotly analytics dashboard.
--------------------------------------------------
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import query
from modules.student import get_chapters, get_subjects


def render_analytics(student_id):
    st.subheader("📊 Academic Analytics")
    chapters = get_chapters(student_id=student_id)
    if not chapters:
        st.info("Add data first.")
        return

    df = pd.DataFrame(chapters)
    subj_avg = df.groupby("subject_name")["completion_pct"].mean().reset_index()
    fig1 = px.bar(subj_avg, x="subject_name", y="completion_pct",
                  title="Subject-wise Completion (%)",
                  color="subject_name", text_auto=".0f")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df.sort_values("completion_pct"), x="completion_pct",
                  y="name", color="subject_name", orientation="h",
                  title="Chapter-wise Progress")
    st.plotly_chart(fig2, use_container_width=True)

    rows = query(
        """SELECT s.name AS subject, COALESCE(SUM(t.duration_minutes),0)/60.0 AS hours
        FROM timetable_tasks t LEFT JOIN subjects s ON t.subject_id=s.id
        WHERE t.student_id=? AND t.status='Completed'
        GROUP BY s.name""",
        (student_id,),
    )
    if rows:
        dfh = pd.DataFrame(rows)
        fig3 = px.pie(dfh, names="subject", values="hours",
                      title="Study Hours by Subject (Completed Tasks)")
        st.plotly_chart(fig3, use_container_width=True)

    rows2 = query(
        """SELECT task_date,
                  SUM(duration_minutes)/60.0 AS planned,
                  SUM(CASE WHEN status='Completed' THEN duration_minutes ELSE 0 END)/60.0 AS actual
        FROM timetable_tasks WHERE student_id=?
        GROUP BY task_date ORDER BY task_date""",
        (student_id,),
    )
    if rows2:
        dfp = pd.DataFrame(rows2)
        fig4 = px.bar(dfp, x="task_date", y=["planned", "actual"],
                      barmode="group", title="Planned vs Actual Study Hours")
        st.plotly_chart(fig4, use_container_width=True)
