# 📘 ExamOrbit

> **Plan Smart. Track Daily. Score Better.**

A CRM-style 90-day study tracker built for **CBSE Class 10 & 12** students preparing for board exams.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 📊 **KPI Dashboard** — days remaining, syllabus %, avg test score, revision status
- 🗓️ **Smart Timetable** — daily schedules with priority and missed-task recovery
- 📚 **Chapter CRM Pipeline** — 9-stage pipeline per chapter (Not Started → Exam Ready)
- 🔁 **Revision Manager** — schedule 1st/2nd/3rd revisions, overdue alerts
- 🧪 **Test Manager** — record marks, mistakes, trends by subject/chapter
- 📈 **Analytics** — Plotly charts for subject-wise progress, study hours, score trends
- 🎯 **Priority Engine** — transparent rule-based ranking (no black boxes)
- 💾 **SQLite persistence** — data survives restarts

## 🚀 Quick Start

```bash
git clone https://github.com/anwesha2010/Examorbit.git
cd Examorbit
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
