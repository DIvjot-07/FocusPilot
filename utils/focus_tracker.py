"""
utils/focus_tracker.py
Lightweight in-session focus tracking utilities.
"""

import time
from datetime import datetime, timedelta


class SessionTimer:
    """Tracks elapsed time and computes session completion %."""

    def __init__(self, planned_minutes: int):
        self.planned   = planned_minutes
        self.started   = datetime.now()
        self._paused   = False
        self._pause_at = None
        self._pause_total = timedelta()

    @property
    def elapsed_minutes(self) -> float:
        delta = datetime.now() - self.started - self._pause_total
        return delta.total_seconds() / 60

    @property
    def remaining_minutes(self) -> float:
        return max(0.0, self.planned - self.elapsed_minutes)

    @property
    def completion_pct(self) -> float:
        return min(100.0, (self.elapsed_minutes / self.planned) * 100)

    def pause(self):
        if not self._paused:
            self._pause_at = datetime.now()
            self._paused   = True

    def resume(self):
        if self._paused and self._pause_at:
            self._pause_total += datetime.now() - self._pause_at
            self._paused = False

    def is_complete(self) -> bool:
        return self.elapsed_minutes >= self.planned


def format_minutes(minutes: float) -> str:
    """Convert decimal minutes to 'Xm Ys' display string."""
    m = int(minutes)
    s = int((minutes - m) * 60)
    return f"{m}m {s:02d}s"


def focus_color(score: float) -> str:
    """Return a Streamlit-friendly color hex for a focus score 0-1."""
    if score >= 0.75: return "#00e676"   # green
    if score >= 0.50: return "#ffeb3b"   # yellow
    return "#ff5252"                      # red


MOTIVATIONAL_QUOTES = [
    "Speed is nothing without control. — Ayrton Senna",
    "The best engine in the world is the human brain.",
    "Consistency builds champions.",
    "Every lap counts. Every session matters.",
    "Focus is the new IQ.",
    "Champions aren't born in comfort zones.",
    "Pit strategy: rest smart, push hard.",
    "Small gains, compounded daily, win races.",
]

import random
def random_quote() -> str:
    return random.choice(MOTIVATIONAL_QUOTES)
