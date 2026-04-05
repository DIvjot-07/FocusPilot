"""
ai_engine/recommender.py
FocusPilot AI — Decision Tree + Rule-Based Strategy Engine.

Mirrors an F1 pit-wall: reads real-time inputs, predicts optimal
next action, and fires alerts when the 'driver' loses focus.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

# ── Priority scoring weights ──────────────────────────────────────────────────
W_DIFFICULTY   = 0.30
W_EXAM_URGENCY = 0.40
W_HOURS_NEEDED = 0.20
W_FOCUS_DEBT   = 0.10

FOCUS_THRESHOLD    = 0.55   # below this → distraction alert
SESSION_MIN        = 20     # minimum session to count
DISTRACTION_LIMIT  = 4      # per session before alert fires


class FocusPilotEngine:
    """Core AI engine: combines rule-based priority scoring with a
    decision-tree focus predictor trained on historical logs."""

    def __init__(self):
        self._model: DecisionTreeClassifier | None = None
        self._label_enc = LabelEncoder()
        self._trained = False

    # ── Training ──────────────────────────────────────────────────────────────
    def train(self, logs: list[dict]):
        """Fit a lightweight decision tree on historical study logs."""
        if len(logs) < 5:
            return  # not enough data yet

        df = pd.DataFrame(logs)
        df["focus_label"] = (df["focus_score"] >= FOCUS_THRESHOLD).astype(int)

        features = ["hour_of_day", "planned_minutes", "distraction_count"]
        # encode day_of_week
        df["day_enc"] = self._label_enc.fit_transform(df["day_of_week"])
        features.append("day_enc")

        X = df[features].fillna(0)
        y = df["focus_label"]

        self._model = DecisionTreeClassifier(max_depth=4, random_state=42)
        self._model.fit(X, y)
        self._trained = True

    # ── Focus prediction ──────────────────────────────────────────────────────
    def predict_focus(self, hour: int, planned_minutes: int,
                      distraction_count: int) -> float:
        """Returns predicted focus probability for the given slot."""
        if not self._trained or self._model is None:
            # Heuristic fallback: peak focus mid-morning & early evening
            peak_hours = {9, 10, 11, 16, 17, 18, 19}
            base = 0.75 if hour in peak_hours else 0.55
            penalty = min(distraction_count * 0.05, 0.30)
            return max(0.0, base - penalty)

        try:
            day_name = datetime.now().strftime("%A")
            day_enc = self._label_enc.transform([day_name])[0]
        except ValueError:
            day_enc = 0

        X = np.array([[hour, planned_minutes, distraction_count, day_enc]])
        prob = self._model.predict_proba(X)[0]
        return float(prob[1]) if len(prob) > 1 else 0.5

    # ── Subject prioritisation ────────────────────────────────────────────────
    def rank_subjects(self, subjects: list[dict],
                      logs: list[dict]) -> list[dict]:
        """Score and rank subjects using weighted multi-factor formula."""
        df_logs = pd.DataFrame(logs) if logs else pd.DataFrame()

        ranked = []
        for subj in subjects:
            name        = subj["name"]
            difficulty  = subj.get("difficulty", 3)          # 1-5
            exam_days   = max(subj.get("exam_days", 30), 1)
            hours_pending = subj.get("hours_pending", 4)

            # Normalised scores (0→1)
            diff_score    = difficulty / 5.0
            urgency_score = 1.0 / np.log1p(exam_days)        # steeper near exam
            hours_score   = min(hours_pending / 10.0, 1.0)

            # Focus debt: low historical focus → needs more attention
            if not df_logs.empty and "subject" in df_logs.columns:
                subj_logs = df_logs[df_logs["subject"] == name]
                avg_focus = subj_logs["focus_score"].mean() if len(subj_logs) else 0.5
            else:
                avg_focus = 0.5
            focus_debt = 1.0 - avg_focus

            priority = (W_DIFFICULTY   * diff_score  +
                        W_EXAM_URGENCY * urgency_score +
                        W_HOURS_NEEDED * hours_score  +
                        W_FOCUS_DEBT   * focus_debt)

            # Suggested session length (Pomodoro-aware)
            session_minutes = 45 if difficulty >= 4 else 30

            ranked.append({
                **subj,
                "priority_score": round(priority, 3),
                "session_minutes": session_minutes,
                "urgency_label": _urgency_label(exam_days),
                "avg_focus": round(avg_focus, 2),
            })

        ranked.sort(key=lambda x: x["priority_score"], reverse=True)
        return ranked

    # ── Real-time recommendation ──────────────────────────────────────────────
    def what_should_i_do(self, subjects: list[dict],
                         logs: list[dict]) -> dict:
        """Single-call 'What Should I Do Now?' recommendation."""
        now   = datetime.now()
        hour  = now.hour
        ranked = self.rank_subjects(subjects, logs)

        top = ranked[0] if ranked else None
        focus_prob = self.predict_focus(hour, top["session_minutes"] if top else 45, 0)

        if top is None:
            return {"action": "rest", "message": "No subjects configured."}

        # Time-of-day strategy
        time_label, advice = _time_strategy(hour, focus_prob)

        return {
            "action": "study",
            "subject": top["name"],
            "session_minutes": top["session_minutes"],
            "focus_probability": round(focus_prob, 2),
            "priority_score": top["priority_score"],
            "urgency_label": top["urgency_label"],
            "time_label": time_label,
            "advice": advice,
            "ranked": ranked,
        }

    # ── Distraction detection ─────────────────────────────────────────────────
    def check_distraction(self, elapsed_minutes: int,
                          keystrokes: int,
                          mouse_moves: int) -> dict:
        """Rule-based alert engine — fires when focus degrades."""
        activity_rate = (keystrokes + mouse_moves) / max(elapsed_minutes, 1)
        focus_score   = min(activity_rate / 20.0, 1.0)   # normalise

        alert = False
        message = "Focus is strong — keep going! 🏎️"
        level   = "green"

        if focus_score < 0.25 and elapsed_minutes > 5:
            alert   = True
            message = "⚠️  Distraction detected! Time to re-engage."
            level   = "red"
        elif focus_score < 0.50:
            alert   = True
            message = "⚡ Focus slipping — quick reset recommended."
            level   = "yellow"

        return {
            "alert": alert,
            "focus_score": round(focus_score, 2),
            "message": message,
            "level": level,
        }

    # ── Pattern analysis ──────────────────────────────────────────────────────
    def analyse_patterns(self, logs: list[dict]) -> dict:
        if not logs:
            return {}
        df = pd.DataFrame(logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        best_hour = (df.groupby("hour_of_day")["focus_score"]
                       .mean().idxmax())
        best_day  = (df.groupby("day_of_week")["focus_score"]
                       .mean().idxmax())
        best_subject = (df.groupby("subject")["focus_score"]
                          .mean().idxmax())

        weekly_focus = df.set_index("timestamp")["focus_score"].resample("D").mean()

        return {
            "best_hour": int(best_hour),
            "best_day": best_day,
            "best_subject": best_subject,
            "avg_focus": round(df["focus_score"].mean(), 2),
            "total_hours": round(df["actual_minutes"].sum() / 60, 1),
            "avg_distraction": round(df["distraction_count"].mean(), 1),
            "weekly_focus": weekly_focus.dropna().to_dict(),
        }


# ── Helpers ───────────────────────────────────────────────────────────────────
def _urgency_label(exam_days: int) -> str:
    if exam_days <= 3:   return "🔴 CRITICAL"
    if exam_days <= 7:   return "🟠 HIGH"
    if exam_days <= 14:  return "🟡 MEDIUM"
    return "🟢 LOW"


def _time_strategy(hour: int, focus_prob: float) -> tuple[str, str]:
    if 5 <= hour < 9:
        return "Early Morning", "Great for revision & light reading — mind is fresh."
    if 9 <= hour < 13:
        return "Peak Morning", "Best time for hard problems & new concepts."
    if 13 <= hour < 15:
        return "Post-Lunch Dip", "Take a 10-min walk before studying."
    if 15 <= hour < 20:
        return "Afternoon Power", "Ideal for practice papers & problem sets."
    if 20 <= hour < 23:
        return "Evening Wind-Down", "Review notes & plan tomorrow's sessions."
    return "Late Night", "Sleep is more valuable than cramming. Consider resting."
