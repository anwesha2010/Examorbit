"""
modules/chapters.py
--------------------------------------------------
CRM-style chapter pipeline UI.
--------------------------------------------------
"""
import streamlit as st
import pandas as pd
from datetime import date
from database.db import CHAPTER_STAGES
from modules.student import get_chapters, update_chapter, delete_chapter


def render_chapter_tracker(student_id):
    st.subheader("📚 Subject & Chapter Tracker")
    chapters = get_chapters(student_id=student_id)
    if not chapters:
        st.info("No chapters yet. Add some in the Profile tab.")
        return

    # CRM pipeline visual
    st.markdown("### CRM Pipeline")
    counts = {s: 0 for s in CHAPTER_STAGES}
    for c in chapters:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    cols = st.columns(len(CHAPTER_STAGES))
    for col, stage in zip(cols, CHAPTER_STAGES):
        with col:
            st.markdown(
                f"<div style='background:#f1f5f9;border-radius:10px;"
                f"padding:8px;text-align:center;min-height:80px;'>"
                f"<div style='font-size:20px;font-weight:700;"
                f"color:#1e3a8a;'>{counts[stage]}</div>"
                f"<div style='font-size:11px;color:#475569;'>{stage}</div></div>",
                unsafe_allow_html=True,
            )
    st.markdown("---")

    subs = sorted({c["subject_name"] for c in chapters})
    f = st.selectbox("Filter by subject", ["All"] + subs)
    filtered = chapters if f == "All" else [c for c in chapters if c["subject_name"] == f]

    if filtered:
        df = pd.DataFrame(filtered)[
            ["id", "subject_name", "name", "status", "completion_pct",
             "priority", "difficulty", "revisions_count", "test_marks", "confidence"]
        ]
        df.columns = ["ID", "Subject", "Chapter", "Status", "Progress %",
                      "Priority", "Difficulty", "Revisions", "Test Marks", "Confidence"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Update a Chapter")
    if not filtered:
        return

    opts = {f"{c['id']} • {c['subject_name']} • {c['name']}": c for c in filtered}
    chosen = st.selectbox("Select chapter", list(opts.keys()))
    ch = opts[chosen]

    c1, c2 = st.columns(2)
    with c1:
        new_status = st.selectbox(
            "Pipeline Stage", CHAPTER_STAGES,
            index=CHAPTER_STAGES.index(ch["status"]) if ch["status"] in CHAPTER_STAGES else 0,
        )
        priority = st.selectbox("Priority", ["Low", "Medium", "High"],
                                index=["Low", "Medium", "High"].index(ch["priority"]))
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"],
                                  index=["Easy", "Medium", "Hard"].index(ch["difficulty"]))
    with c2:
        confidence = st.slider("Confidence (1-5)", 1, 5, int(ch["confidence"] or 3))
        tm = st.number_input("Test marks % (0-100)", 0.0, 100.0,
                             float(ch["test_marks"] or 0.0), step=1.0)
        weak = st.checkbox("Mark as weak topic", value=bool(ch["is_weak"]))
    notes = st.text_area("Notes", value=ch["notes"] or "")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("💾 Save Chapter Updates", type="primary"):
            pct = int(CHAPTER_STAGES.index(new_status) / (len(CHAPTER_STAGES) - 1) * 100)
            update_chapter(
                ch["id"], status=new_status, priority=priority,
                difficulty=difficulty, completion_pct=pct, confidence=confidence,
                test_marks=tm if tm > 0 else None,
                is_weak=1 if weak else 0, notes=notes,
                actual_completion_date=(date.today().isoformat()
                                        if new_status == "Exam Ready"
                                        else ch["actual_completion_date"]),
            )
            st.success("Chapter updated.")
            st.rerun()
    with b2:
        if st.button("🗑️ Delete Chapter"):
            delete_chapter(ch["id"])
            st.warning("Chapter deleted.")
            st.rerun()
