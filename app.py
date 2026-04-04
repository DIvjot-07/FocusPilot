"""
app.py  ─  FocusPilot AI  |  The F1 Strategy Engine for Students
Run:  streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from data.data_manager import load_profile, save_profile, load_logs, log_session
from ai_engine.recommender import FocusPilotEngine
from utils.focus_tracker import format_minutes, focus_color, random_quote

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FocusPilot AI",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

:root {
    --bg-dark:    #0d0d1a;
    --bg-card:    #13132b;
    --accent:     #ff2d6b;
    --accent2:    #b44cff;
    --neon-green: #00e676;
    --neon-yellow:#ffeb3b;
    --text-dim:   #8888aa;
    --border:     rgba(180,76,255,0.25);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-dark) !important;
    color: #e8e8ff;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0a0a18 !important;
    border-right: 1px solid var(--border);
}

/* Cards */
.fp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.fp-card::before {
    content:'';
    position: absolute;
    top:0; left:0; right:0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}

/* Big metric */
.fp-metric-val {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--accent);
    line-height:1;
}
.fp-metric-label {
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-top: 4px;
}

/* Subject pill */
.subj-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-right: 6px;
}

/* Recommendation box */
.reco-box {
    background: linear-gradient(135deg, #1a0a2e 0%, #0d0d1a 100%);
    border: 1px solid var(--accent2);
    border-radius: 16px;
    padding: 28px 32px;
    text-align: center;
}
.reco-subject {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #fff;
}
.reco-time {
    font-size: 1.1rem;
    color: var(--accent);
    font-weight: 600;
}

/* Alert banners */
.alert-red    { background:#2d0a0a; border:1px solid #ff5252; border-radius:10px; padding:12px 18px; color:#ff8a80; }
.alert-yellow { background:#2d2800; border:1px solid #ffeb3b; border-radius:10px; padding:12px 18px; color:#fff59d; }
.alert-green  { background:#0a2d12; border:1px solid #00e676; border-radius:10px; padding:12px 18px; color:#b9f6ca; }

/* Progress bar */
.fp-progress-wrap { background:#1a1a30; border-radius:8px; height:10px; width:100%; overflow:hidden; }
.fp-progress-bar  { height:100%; border-radius:8px;
                    background: linear-gradient(90deg, var(--accent), var(--accent2)); }

/* Divider */
.fp-divider { border:none; border-top:1px solid var(--border); margin:20px 0; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "engine" not in st.session_state:
    st.session_state.engine = FocusPilotEngine()

if "profile" not in st.session_state:
    st.session_state.profile = load_profile()

if "logs" not in st.session_state:
    st.session_state.logs = load_logs()
    st.session_state.engine.train(st.session_state.logs)

if "active_session" not in st.session_state:
    st.session_state.active_session = None

if "distraction_count" not in st.session_state:
    st.session_state.distraction_count = 0

engine  = st.session_state.engine
profile = st.session_state.profile
logs    = st.session_state.logs


# ── Top Navigation ────────────────────────────────────────────────────────────
st.markdown("""
<div style='display:flex;align-items:center;justify-content:space-between;
            background:#0a0a18;border-bottom:1px solid rgba(180,76,255,0.25);
            padding:14px 28px;margin:-1rem -1rem 2rem -1rem;'>
    <div>
        <span style='font-family:Rajdhani;font-size:1.6rem;font-weight:700;
                     color:#ff2d6b;letter-spacing:0.05em;'>🏎️ FOCUSPILOT AI</span>
        <span style='font-size:0.7rem;letter-spacing:0.12em;color:#8888aa;
                     text-transform:uppercase;margin-left:12px;'>Strategy Engine</span>
    </div>
</div>
""", unsafe_allow_html=True)

nav_cols = st.columns(4)
pages = ["🎯  Dashboard", "📊  Analytics", "⚙️  Setup", "📝  Log Session"]
if "page" not in st.session_state:
    st.session_state.page = "🎯  Dashboard"

for i, p in enumerate(pages):
    with nav_cols[i]:
        is_active = st.session_state.page == p
        btn_style = "primary" if is_active else "secondary"
        if st.button(p, use_container_width=True, type=btn_style, key=f"nav_{i}"):
            st.session_state.page = p
            st.rerun()

page = st.session_state.page
st.markdown(f"<div style='font-size:0.8rem;color:#8888aa;font-style:italic;text-align:right;margin-top:-8px;'>\"{random_quote()}\"</div>",
            unsafe_allow_html=True)
st.markdown("<hr style='border-color:#2a2a40;margin:12px 0 20px;'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if "Dashboard" in page:

    # Header
    st.markdown("""
    <div style='display:flex;align-items:center;gap:16px;margin-bottom:8px;'>
        <div>
            <h1 style='font-family:Rajdhani;font-size:2.4rem;font-weight:700;
                       margin:0;color:#fff;'>Race Dashboard</h1>
            <p style='color:#8888aa;margin:0;font-size:0.9rem;'>
                Your real-time study strategy — live from the pit wall.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── What Should I Do Now? ─────────────────────────────────────────────────
    st.markdown("<div class='fp-card'>", unsafe_allow_html=True)
    col_btn, col_res = st.columns([1, 2])

    with col_btn:
        st.markdown("### 🎯 What Should I Do Now?")
        st.markdown("<p style='color:#8888aa;font-size:0.85rem;'>AI recommendation based on your current time, subject load & focus history.</p>",
                    unsafe_allow_html=True)
        go_btn = st.button("⚡  GET RECOMMENDATION", use_container_width=True,
                           type="primary")

    with col_res:
        if go_btn or "last_reco" in st.session_state:
            if go_btn:
                reco = engine.what_should_i_do(profile["subjects"], logs)
                st.session_state.last_reco = reco
            else:
                reco = st.session_state.last_reco

            st.markdown(f"""
            <div class='reco-box'>
                <div style='color:#8888aa;font-size:0.75rem;letter-spacing:0.1em;
                            text-transform:uppercase;margin-bottom:8px;'>
                    📍 {reco['time_label']}
                </div>
                <div class='reco-subject'>📖 {reco['subject']}</div>
                <div class='reco-time'>⏱ {reco['session_minutes']} minutes &nbsp;|&nbsp;
                    {reco['urgency_label']}</div>
                <div style='margin-top:12px;font-size:0.85rem;color:#c8c8e8;'>
                    {reco['advice']}
                </div>
                <div style='margin-top:10px;font-size:0.78rem;color:#6666aa;'>
                    Focus probability: <b style='color:#b44cff;'>
                    {int(reco['focus_probability']*100)}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#8888aa;padding:40px;text-align:center;'>Hit the button to get your F1 pit strategy →</div>",
                        unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Key Metrics Row ───────────────────────────────────────────────────────
    patterns = engine.analyse_patterns(logs)
    c1, c2, c3, c4 = st.columns(4)

    def metric_card(col, value, label, color="#ff2d6b"):
        col.markdown(f"""
        <div class='fp-card' style='text-align:center;padding:18px;'>
            <div class='fp-metric-val' style='color:{color};'>{value}</div>
            <div class='fp-metric-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

    metric_card(c1, f"{patterns.get('total_hours', 0)}h", "Total Study Hours", "#ff2d6b")
    metric_card(c2, f"{int(patterns.get('avg_focus', 0)*100)}%", "Avg Focus Score", "#b44cff")
    metric_card(c3, f"{patterns.get('best_hour', '?')}:00", "Peak Focus Hour", "#00e676")
    metric_card(c4, f"{patterns.get('avg_distraction', 0)}", "Avg Distractions/Session", "#ffeb3b")

    # ── Subject Priority List ─────────────────────────────────────────────────
    st.markdown("### 🏁 Subject Priority Queue")
    ranked = engine.rank_subjects(profile["subjects"], logs)

    for i, subj in enumerate(ranked):
        pct = subj["priority_score"] * 100
        bar_color = ["#ff2d6b","#ff7043","#ffb300","#66bb6a","#42a5f5"][min(i, 4)]
        st.markdown(f"""
        <div class='fp-card' style='padding:14px 20px;'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div>
                    <span style='font-family:Rajdhani;font-size:1.1rem;font-weight:700;
                                 color:#fff;'>#{i+1} {subj['name']}</span>
                    &nbsp; <span class='subj-pill' style='background:{bar_color}22;
                                  color:{bar_color};border:1px solid {bar_color}55;'>
                        {subj['urgency_label']}
                    </span>
                </div>
                <div style='font-size:0.8rem;color:#8888aa;'>
                    {subj['session_minutes']} min session &nbsp;|&nbsp;
                    avg focus {int(subj['avg_focus']*100)}%
                </div>
            </div>
            <div class='fp-progress-wrap' style='margin-top:8px;'>
                <div class='fp-progress-bar' style='width:{pct:.1f}%;background:{bar_color};'></div>
            </div>
            <div style='font-size:0.72rem;color:#8888aa;margin-top:4px;'>
                Priority score: {subj['priority_score']}  &nbsp;·&nbsp;
                Difficulty: {'★'*subj['difficulty'] + '☆'*(5-subj['difficulty'])}  &nbsp;·&nbsp;
                Exam in {subj['exam_days']} days  &nbsp;·&nbsp;
                {subj['hours_pending']}h pending
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Distraction Alert Simulator ───────────────────────────────────────────
    st.markdown("### ⚠️ Distraction Alert System")
    st.markdown("<p style='color:#8888aa;font-size:0.85rem;margin-top:-10px;'>Simulate real-time focus monitoring — adjust sliders to test the alert engine.</p>",
                unsafe_allow_html=True)

    da_col1, da_col2 = st.columns([2, 1])
    with da_col1:
        elapsed  = st.slider("Elapsed session time (minutes)", 0, 60, 15)
        keys     = st.slider("Keystrokes recorded", 0, 500, 80)
        mouse    = st.slider("Mouse movements", 0, 300, 40)

    with da_col2:
        alert_data = engine.check_distraction(elapsed, keys, mouse)
        css_cls    = f"alert-{alert_data['level']}"
        focus_pct  = int(alert_data['focus_score'] * 100)

        st.markdown(f"""
        <div class='{css_cls}' style='margin-top:10px;'>
            <div style='font-size:1.6rem;font-weight:700;'>{focus_pct}%</div>
            <div style='font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;'>
                Focus Score
            </div>
            <div>{alert_data['message']}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif "Analytics" in page:
    st.markdown("<h1 style='font-family:Rajdhani;font-size:2.2rem;'>📊 Pattern Analysis</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#8888aa;'>Learn when you peak, where you drift, and how to improve.</p>",
                unsafe_allow_html=True)

    df = pd.DataFrame(logs)
    if df.empty:
        st.warning("No study logs yet. Complete a session to see analytics.")
        st.stop()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    PLOT_THEME = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c8c8e8", family="Inter"),
        xaxis=dict(gridcolor="#1e1e3a", linecolor="#2a2a40"),
        yaxis=dict(gridcolor="#1e1e3a", linecolor="#2a2a40"),
    )

    col1, col2 = st.columns(2)

    # Focus by hour
    with col1:
        hourly = df.groupby("hour_of_day")["focus_score"].mean().reset_index()
        fig = go.Figure(go.Bar(
            x=hourly["hour_of_day"], y=hourly["focus_score"],
            marker_color="#b44cff", opacity=0.85,
            hovertemplate="Hour %{x}:00<br>Focus: %{y:.0%}<extra></extra>"
        ))
        fig.update_layout(**PLOT_THEME, title="Focus Score by Hour of Day",
                          yaxis_tickformat=".0%", height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Focus by subject
    with col2:
        subj_focus = df.groupby("subject")["focus_score"].mean().sort_values()
        colors = ["#ff2d6b","#ff7043","#ffb300","#66bb6a","#42a5f5"]
        fig2 = go.Figure(go.Bar(
            x=subj_focus.values, y=subj_focus.index, orientation="h",
            marker_color=colors[:len(subj_focus)],
            hovertemplate="%{y}: %{x:.0%}<extra></extra>"
        ))
        fig2.update_layout(**PLOT_THEME, title="Focus Score by Subject",
                           xaxis_tickformat=".0%", height=300)
        st.plotly_chart(fig2, use_container_width=True)

    # Focus trend over time
    df_daily = df.set_index("timestamp").resample("D")["focus_score"].mean().dropna().reset_index()
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_daily["timestamp"], y=df_daily["focus_score"],
        mode="lines+markers",
        line=dict(color="#ff2d6b", width=2),
        marker=dict(size=6, color="#b44cff"),
        fill="tozeroy", fillcolor="rgba(180,76,255,0.08)",
        hovertemplate="%{x|%b %d}: %{y:.0%}<extra></extra>"
    ))
    fig3.update_layout(**PLOT_THEME, title="Daily Focus Trend",
                       yaxis_tickformat=".0%", height=280)
    st.plotly_chart(fig3, use_container_width=True)

    # Distraction heatmap by day + hour
    pivot = df.pivot_table(values="distraction_count",
                           index="day_of_week", columns="hour_of_day",
                           aggfunc="mean").fillna(0)
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])

    fig4 = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns, y=pivot.index,
        colorscale=[[0,"#0d0d1a"],[0.5,"#b44cff"],[1,"#ff2d6b"]],
        hovertemplate="Hour %{x}:00<br>%{y}<br>Avg distractions: %{z:.1f}<extra></extra>"
    ))
    fig4.update_layout(**PLOT_THEME, title="Distraction Heatmap (Day × Hour)", height=300)
    st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — SETUP
# ══════════════════════════════════════════════════════════════════════════════
elif "Setup" in page:
    st.markdown("<h1 style='font-family:Rajdhani;font-size:2.2rem;'>⚙️ Configure Your Race</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#8888aa;'>Set up your subjects, exam timeline, and study goals.</p>",
                unsafe_allow_html=True)

    with st.form("profile_form"):
        st.markdown("#### 👤 Student Profile")
        name = st.text_input("Your name", value=profile.get("name", "Student"))

        c1, c2 = st.columns(2)
        with c1:
            focus_goal = st.number_input("Daily focus goal (minutes)",
                                         min_value=30, max_value=600,
                                         value=profile.get("focus_goal_minutes", 120))
        with c2:
            session_len = st.number_input("Preferred session length (minutes)",
                                          min_value=10, max_value=120,
                                          value=profile.get("preferred_session_length", 45))

        st.markdown("#### 📚 Subjects")
        subjects_out = []
        for i, subj in enumerate(profile["subjects"]):
            st.markdown(f"**{subj['name']}**")
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                sname = st.text_input("Name", value=subj["name"], key=f"sname_{i}")
            with sc2:
                diff  = st.slider("Difficulty", 1, 5, subj["difficulty"], key=f"diff_{i}")
            with sc3:
                hrs   = st.number_input("Hours pending", 1, 50, subj["hours_pending"], key=f"hrs_{i}")
            with sc4:
                days  = st.number_input("Exam in (days)", 1, 365, subj["exam_days"], key=f"days_{i}")
            subjects_out.append({"name": sname, "difficulty": diff,
                                  "hours_pending": hrs, "exam_days": days})

        submitted = st.form_submit_button("💾  Save Profile", type="primary")
        if submitted:
            profile.update({
                "name": name,
                "focus_goal_minutes": focus_goal,
                "preferred_session_length": session_len,
                "subjects": subjects_out,
            })
            save_profile(profile)
            st.session_state.profile = profile
            st.success("✅ Profile saved! Your strategy has been updated.")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — LOG SESSION
# ══════════════════════════════════════════════════════════════════════════════
elif "Log Session" in page:
    st.markdown("<h1 style='font-family:Rajdhani;font-size:2.2rem;'>📝 Log Study Session</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#8888aa;'>Record a completed session to improve AI recommendations.</p>",
                unsafe_allow_html=True)

    subject_names = [s["name"] for s in profile["subjects"]]

    with st.form("log_form"):
        lc1, lc2 = st.columns(2)
        with lc1:
            sel_subject  = st.selectbox("Subject", subject_names)
            planned_min  = st.number_input("Planned duration (min)", 10, 180, 45)
        with lc2:
            actual_min   = st.number_input("Actual duration (min)", 5, 180, 40)
            distractions = st.number_input("Distraction events", 0, 30, 2)

        focus_self = st.slider("Self-rated focus (1 = poor, 10 = locked in)", 1, 10, 7)
        notes      = st.text_area("Session notes (optional)", height=80)

        if st.form_submit_button("🏁  Log Session", type="primary"):
            focus_score = focus_self / 10.0
            entry = log_session(sel_subject, planned_min, actual_min,
                                focus_score, distractions)
            st.session_state.logs = load_logs()
            st.session_state.engine.train(st.session_state.logs)
            st.success(f"✅ Session logged! AI model retrained on {len(st.session_state.logs)} sessions.")
            st.json(entry)

    # Recent sessions table
    st.markdown("#### 🕓 Recent Sessions")
    if logs:
        df_show = pd.DataFrame(logs[-10:][::-1])
        df_show = df_show[["timestamp","subject","actual_minutes","focus_score","distraction_count"]]
        df_show.columns = ["Time","Subject","Minutes","Focus","Distractions"]
        df_show["Time"] = pd.to_datetime(df_show["Time"]).dt.strftime("%b %d %H:%M")
        df_show["Focus"] = (df_show["Focus"] * 100).round(0).astype(int).astype(str) + "%"
        st.dataframe(df_show, use_container_width=True, hide_index=True)
