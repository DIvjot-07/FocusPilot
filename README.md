# 🏎️ FocusPilot AI — The F1 Strategy Engine for Students

> **Team:** must_be_the_water | **Members:** Yashita Gaur & Divjot Bedi  
> **Hackathon:** CODE 1

---

## What is FocusPilot AI?

FocusPilot AI is an intelligent study strategy system inspired by Formula 1 pit-wall decision-making. Just like an F1 race strategist tells the driver **when to push, when to pit, and when to conserve**, FocusPilot tells students **what to study, when to study it, and fires alerts when focus drops.**

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| UI    | Streamlit  |
| AI Engine | scikit-learn (Decision Tree) + Rule-based logic |
| Data  | Python (pandas, numpy, JSON) |
| Visualisation | Plotly |
| Language | Python 3.10+ |

---

## Project Structure

```
focuspilot/
├── app.py                  ← Main Streamlit dashboard (entry point)
├── requirements.txt        ← Python dependencies
├── README.md
│
├── data/
│   ├── __init__.py
│   ├── data_manager.py     ← Load/save profiles & study logs
│   ├── study_logs.json     ← Auto-generated on first run
│   └── user_profile.json   ← Auto-generated on first run
│
├── ai_engine/
│   ├── __init__.py
│   └── recommender.py      ← Decision tree + rule-based AI engine
│
├── utils/
│   ├── __init__.py
│   └── focus_tracker.py    ← Session timer & focus utilities
│
└── assets/                 ← Static assets (icons, images)
```

---

## Quick Start

### 1. Clone / download the project
```bash
cd focuspilot
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**

---

## Features

### 🎯 Dashboard
- **"What Should I Do Now?"** — One-click AI recommendation based on current time, subject load, and focus history
- **Subject Priority Queue** — Ranked list with urgency labels, difficulty stars, and progress bars
- **Distraction Alert Simulator** — Interactive sliders to test the real-time alert engine

### 📊 Analytics
- Focus score by hour of day
- Focus score by subject
- Daily focus trend line chart
- Distraction heatmap (day × hour)

### ⚙️ Setup
- Configure subjects, difficulty, exam dates, and pending hours
- Set daily study goals and preferred session length

### 📝 Log Session
- Record completed sessions (subject, planned vs actual, self-rated focus, distractions)
- AI model retrains on every new log entry
- View recent session history

---

## AI Engine Overview

```
Input signals
  ├── Hour of day
  ├── Subject difficulty (1-5)
  ├── Exam urgency (days until exam)
  ├── Hours of study pending
  └── Historical focus score per subject

         ↓ Decision Tree (scikit-learn)
         ↓ Weighted priority formula

Output
  ├── Recommended subject + session length
  ├── Focus probability for current time slot
  ├── Urgency label (CRITICAL / HIGH / MEDIUM / LOW)
  └── Real-time distraction alerts
```

---

## Scalability Roadmap

- [ ] Mobile app (React Native)
- [ ] Browser extension for passive focus tracking
- [ ] Full AI productivity assistant
- [ ] Institutional licensing model

---

*Built with ❤️ and ☕ for CODE 1 Hackathon*
