"""
modules/priority.py
--------------------------------------------------
Rule-based priority engine for ExamOrbit.
Explainable scoring — NOT a mark predictor.
--------------------------------------------------
"""
from datetime import date, datetime


def compute_chapter_priority(chapter, today=None):
    """Return (score, reasons) for one chapter dict."""
    today = today or date.today()
    score, reasons = 0, []

    if chapter.get("status") == "Not Started":
        score += 30
        reasons.append("Not started")

    diff = chapter.get("difficulty", "Medium")
    if diff == "Hard":
        score += 20
        reasons.append("Hard difficulty")
    elif diff == "Medium":
        score += 10

    conf = chapter.get("confidence") or 3
    if conf <= 2:
        score += 15
        reasons.append("Low confidence")

    marks = chapter.get("test_marks")
    if marks is not None:
        if marks < 50:
            score += 25
            reasons.append("Low test marks")
        elif marks < 70:
            score += 10

    if chapter.get("overdue_revisions", 0) > 0:
        score += 30
        reasons.append("Overdue revision")

    prio = chapter.get("priority", "Medium")
    if prio == "High":
        score += 20
        reasons.append("High priority")
    elif prio == "Medium":
        score += 10

    exp = chapter.get("expected_completion_date")
    if exp:
        try:
            days = (datetime.strptime(exp, "%Y-%m-%d").date() - today).days
            if 0 <= days <= 7:
                score += 15
                reasons.append("Deadline near")
        except ValueError:
            pass

    return score, reasons


def rank_chapters(chapters, today=None):
    """Return chapters sorted by priority score (descending)."""
    ranked = []
    for ch in chapters:
        s, r = compute_chapter_priority(ch, today)
        c = dict(ch)
        c["score"] = s
        c["reasons"] = r
        ranked.append(c)
    return sorted(ranked, key=lambda x: x["score"], reverse=True)
