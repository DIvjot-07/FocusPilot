"""
data/data_manager.py
Handles all data collection, storage, and retrieval for FocusPilot AI.
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent
LOGS_FILE = DATA_DIR / "study_logs.json"
PROFILE_FILE = DATA_DIR / "user_profile.json"


# ── Default user profile ──────────────────────────────────────────────────────
DEFAULT_PROFILE = {
    "name": "Student",
    "subjects": [
        {"name": "Mathematics",   "difficulty": 5, "hours_pending": 8,  "exam_days": 7},
        {"name": "Physics",        "difficulty": 4, "hours_pending": 6,  "exam_days": 10},
        {"name": "Chemistry",      "difficulty": 3, "hours_pending": 5,  "exam_days": 12},
        {"name": "English",        "difficulty": 2, "hours_pending": 3,  "exam_days": 14},
        {"name": "History",        "difficulty": 2, "hours_pending": 4,  "exam_days": 20},
    ],
    "focus_goal_minutes": 120,
    "preferred_session_length": 45,
    "break_length": 10,
}


def load_profile() -> dict:
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE) as f:
            return json.load(f)
    return DEFAULT_PROFILE.copy()


def save_profile(profile: dict):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2)


# ── Study logs ────────────────────────────────────────────────────────────────
def load_logs() -> list[dict]:
    if LOGS_FILE.exists():
        with open(LOGS_FILE) as f:
            return json.load(f)
    return _generate_sample_logs()


def save_log_entry(entry: dict):
    logs = load_logs()
    logs.append(entry)
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2, default=str)


def log_session(subject: str, planned_minutes: int, actual_minutes: int,
                focus_score: float, distraction_count: int):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "subject": subject,
        "planned_minutes": planned_minutes,
        "actual_minutes": actual_minutes,
        "focus_score": round(focus_score, 2),
        "distraction_count": distraction_count,
        "hour_of_day": datetime.now().hour,
        "day_of_week": datetime.now().strftime("%A"),
    }
    save_log_entry(entry)
    return entry


def _generate_sample_logs() -> list[dict]:
    """Seed realistic historical data so the AI has patterns to learn from."""
    subjects = ["Mathematics", "Physics", "Chemistry", "English", "History"]
    logs = []
    now = datetime.now()
    for i in range(60):
        dt = now - timedelta(days=random.randint(1, 30),
                             hours=random.randint(0, 8))
        focus = round(random.uniform(0.4, 1.0), 2)
        logs.append({
            "timestamp": dt.isoformat(),
            "subject": random.choice(subjects),
            "planned_minutes": random.choice([30, 45, 60]),
            "actual_minutes": random.randint(15, 60),
            "focus_score": focus,
            "distraction_count": random.randint(0, 8),
            "hour_of_day": dt.hour,
            "day_of_week": dt.strftime("%A"),
        })
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2, default=str)
    return logs
