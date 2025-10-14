# app.py — AI-Powered Justice System (Futuristic Neon Glass UI + Smart Scheduling)
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import math

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="AI-Powered Justice System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- SECURITY --------------------
# NOTE: demo-only: generate key each run. Store securely in production.
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(dataframe):
    csv_bytes = dataframe.to_csv(index=False).encode()
    return cipher.encrypt(csv_bytes)

def decrypt_data(encrypted_data):
    decrypted = cipher.decrypt(encrypted_data).decode()
    from io import StringIO
    return pd.read_csv(StringIO(decrypted))

# -------------------- GLOBAL STYLES (Neon Glass) --------------------
st.markdown("""
<style>
:root{
  --glass-bg: rgba(11,14,22,0.55);
  --glass-border: rgba(255,255,255,0.06);
  --accent1: #60a5fa;
  --accent2: #a855f7;
  --accent3: #ec4899;
  --muted: #9ca3af;
  --card-radius: 16px;
}

/* page background */
body, .stApp {
  background: radial-gradient(circle at 10% 10%, #071129 0%, #05060a 50%, #040407 100%);
  color: #e6eef8;
  font-family: "Segoe UI", system-ui, -apple-system, Roboto, "Helvetica Neue", Arial;
}

/* title gradient */
.title-gradient {
  background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
  font-size: 42px;
  letter-spacing: -0.6px;
  text-shadow: 0 8px 28px rgba(168,85,247,0.08);
}

/* subtitle */
.subtitle {
  color: var(--muted);
  margin-bottom: 18px;
  font-size: 15px;
}

/* neon glass container (used for dashboard & calendar sections) */
.glass {
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
  border: 1px solid rgba(255,255,255,0.04);
  box-shadow: 0 6px 30px rgba(99,102,241,0.06);
  backdrop-filter: blur(10px) saturate(140%);
  -webkit-backdrop-filter: blur(10px) saturate(140%);
  border-radius: var(--card-radius);
  padding: 18px;
}

/* header row */
.header-row{
  display:flex; align-items:center; gap:14px;
}

/* small svg icon circle */
.icon-circle {
  width:56px; height:56px; border-radius:12px;
  display:flex; align-items:center; justify-content:center;
  background: linear-gradient(135deg, rgba(96,165,250,0.08), rgba(168,85,247,0.06));
  border: 1px solid rgba(255,255,255,0.04);
  box-shadow: 0 6px 18px rgba(99,102,241,0.08), inset 0 -6px 14px rgba(0,0,0,0.2);
}

/* metric cards */
.metric-row { display:flex; gap:16px; }
.metric-card {
  flex:1;
  border-radius:14px;
  padding:18px;
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border: 1px solid rgba(255,255,255,0.03);
  box-shadow: 0 8px 30px rgba(99,102,241,0.06);
  transition: transform .22s ease, box-shadow .22s ease;
}
.metric-card:hover { transform: translateY(-6px); box-shadow: 0 18px 50px rgba(99,102,241,0.12); }
.metric-card h3 { margin:0; color: #cfe3ff; font-weight:700; font-size:13px; letter-spacing:0.2px; }
.metric-card h2 { margin:8px 0 0 0; font-size:28px; font-weight:800; color:white; }

/* neon stat icon */
.stat-icon {
  float:right;
  opacity:0.95;
}

/* case card (dashboard & calendar) */
.case-card {
  border-radius:12px;
  padding:14px;
  margin-top:12px;
  position:relative;
  overflow:hidden;
  border:1px solid rgba(255,255,255,0.03);
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  transition: transform .18s ease, box-shadow .18s ease;
}
.case-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(99,102,241,0.08); }

/* left urgency stripe + glow */
.case-card .left-stripe {
  position:absolute; left:0; top:0; bottom:0; width:8px; border-radius:8px 0 0 8px;
  box-shadow: 0 6px 20px rgba(168,85,247,0.06), inset 0 6px 18px rgba(0,0,0,0.2);
}
.high-stripe { background: linear-gradient(180deg,#ff7b7b,#ef4444); box-shadow: 0 0 18px rgba(239,68,68,0.14); }
.medium-stripe { background: linear-gradient(180deg,#ffd36b,#f59e0b); box-shadow: 0 0 18px rgba(245,158,11,0.12); }
.low-stripe { background: linear-gradient(180deg,#73f3b6,#10b981); box-shadow: 0 0 18px rgba(16,185,129,0.12); }

/* progress bar (animated) */
.progress-bar {
  height:10px; border-radius:10px; overflow:hidden; background: rgba(255,255,255,0.03); margin-top:10px;
  border: 1px solid rgba(255,255,255,0.02);
}
.progress-fill {
  height:100%; width:0%;
  background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
  box-shadow: 0 6px 28px rgba(168,85,247,0.12);
  border-radius:10px;
  animation: fillAnim 1.1s ease forwards;
}
@keyframes fillAnim { from { width: 0%; } to { width: var(--fill-width); } }

/* small meta badges */
.meta-badge {
  display:inline-block; font-size:12px; padding:6px 8px; border-radius:10px; margin-right:8px;
  background: rgba(255,255,255,0.03); color:#e6eef8; border:1px solid rgba(255,255,255,0.02);
}

/* urgency tags */
.urgency-tag {
  padding:6px 10px; border-radius:12px; font-weight:700; letter-spacing:0.3px; font-size:12px;
  display:inline-block; margin-left:8px; color: #08101a;
}
.urgency-high { background: linear-gradient(90deg,#ff9b9b,#ff6b6b); color:#11060a; box-shadow: 0 6px 24px rgba(239,68,68,0.14); }
.urgency-medium { background: linear-gradient(90deg,#ffe08a,#ffb347); color:#11060a; box-shadow: 0 6px 22px rgba(245,158,11,0.12); }
.urgency-low { background: linear-gradient(90deg,#9fffdc,#5df0a4); color:#02271a; box-shadow: 0 6px 22px rgba(16,185,129,0.12); }

/* day column header for calendar */
.day-column {
  border-radius:12px; padding:12px; margin-bottom:12px;
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border:1px solid rgba(255,255,255,0.03);
  text-align:center;
}
.day-column .day-title {
  font-weight:800; font-size:16px; background: linear-gradient(90deg,var(--accent1),var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}

/* sidebar tweaks */
.stSidebar .css-1d391kg { color: #cbd7ee; }
.stSidebar .stFileUploader { color: #cbd7ee; }
.stButton>button { border-radius:10px; padding:8px 12px; font-weight:700; background: linear-gradient(90deg,var(--accent1),var(--accent2)); color:white; border:none; box-shadow: 0 8px 30px rgba(99,102,241,0.06); }

/* responsive small screens */
@media (max-width:900px) {
  .metric-row { flex-direction: column; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.markdown("<div style='display:flex;align-items:center;gap:10px'><div style='font-size:20px'>⚖️</div><div><b>AI-Powered Justice</b><div style='font-size:12px;color:#9ca3af'>Neon Glass UI</div></div></div>", unsafe_allow_html=True)
page = st.sidebar.radio("Select View:", ["Dashboard", "Calendar View"])
st.sidebar.markdown("---")
MAX_UPLOAD_GB = 1
uploaded = st.sidebar.file_uploader(f"Upload Case CSV (display limit: {MAX_UPLOAD_GB} GB)", type=["csv"])

# -------------------- DATA LOADING --------------------
@st.cache_data
def load_local_csv(path="cases.csv"):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

if uploaded:
    try:
        df = pd.read_csv(uploaded)
        st.sidebar.success(f"✅ {len(df)} cases loaded successfully (uploaded)")
    except Exception:
        st.sidebar.error("⚠️ Could not read CSV. Check the format.")
        st.stop()
else:
    df = load_local_csv("cases.csv")
    if df.empty:
        st.sidebar.warning("No local cases.csv found or file empty.")
    else:
        st.sidebar.info("📂 Using default internal dataset (expected ~500 cases).")

if not df.empty:
    encrypted_data = encrypt_data(df)
    df = decrypt_data(encrypted_data)

# -------------------- NORMALIZE COLUMNS --------------------
col_map_candidates = {
    'Case_ID': ['Case_ID','CaseId','case_id','caseid','Case Number','Case_Number','CaseNumber'],
    'Case_Name': ['Case_Name','CaseName','Name','case_name'],
    'Case_Type': ['Case_Type','Type','case_type'],
    'Pending_Days': ['Pending_Days','PendingDays','pending_days'],
    'Deadline_Days_Left': ['Deadline_Days_Left','Days_Left','DeadlineDaysLeft','deadline_days_left'],
    'Previous_Motions': ['Previous_Motions','Prev_Motions','PreviousMotions','previous_motions'],
    'Short_Description': ['Short_Description','ShortDescription','Description','ShortDesc','short_description'],
    'Urgency': ['Urgency','Urgency_Level','urgency']
}
if not df.empty:
    df_cols_lower = {c.lower(): c for c in df.columns}
    def find_existing(possible_names):
        for n in possible_names:
            if n in df.columns:
                return n
            if n.lower() in df_cols_lower:
                return df_cols_lower[n.lower()]
        return None
    for canonical, cand_list in col_map_candidates.items():
        found = find_existing(cand_list)
        if found:
            df.rename(columns={found: canonical}, inplace=True)
if not df.empty:
    if 'Case_ID' not in df.columns:
        df['Case_ID'] = df.index.to_series().apply(lambda x: f"C{x+1:03d}")
    for col in ['Pending_Days','Deadline_Days_Left','Previous_Motions']:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# -------------------- URGENCY SCORE --------------------
def calc_urgency_score(row):
    if pd.notna(row.get('Urgency')) and isinstance(row.get('Urgency'), str):
        s = row.get('Urgency').strip().lower()
        if s in ('high','h','urgent'): return 90
        if s in ('medium','med','m'): return 55
        if s in ('low','l'): return 15
    score = 0
    ct = str(row.get('Case_Type','')).lower()
    if ct in ['bail','custody','fraud']: score += 40
    if row.get('Pending_Days',0) > 100: score += 15
    if row.get('Deadline_Days_Left',999) < 10: score += 25
    if row.get('Previous_Motions',0) > 2: score += 10
    return min(100, score)

if not df.empty:
    if 'Urgency_Score' not in df.columns:
        df['Urgency_Score'] = df.apply(calc_urgency_score, axis=1)
    else:
        df['Urgency_Score'] = pd.to_numeric(df['Urgency_Score'], errors='coerce').fillna(0).astype(int)
    df['Urgency_Level'] = df['Urgency_Score'].apply(lambda x: "High" if x >= 70 else ("Medium" if x >= 40 else "Low"))

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.markdown('<div class="header-row"><div class="icon-circle"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L15 8H9L12 2Z" fill="white" opacity="0.9"/></svg></div><div><div class="title-gradient">⚖️ AI-Powered Justice System</div><div class="subtitle">Prioritize court cases with intelligence & neon-grade privacy.</div></div></div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No case data to display. Upload a CSV or add a local cases.csv.")
    else:
        # metrics top row with icons
        total_cases = len(df)
        high_count = (df["Urgency_Level"]=="High").sum()
        avg_score = round(df["Urgency_Score"].mean(),1)

        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="display:flex; gap:16px;" class="metric-row">
                <div class="metric-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div>
                            <h3>📈 Total Cases</h3>
                            <h2>{total_cases}</h2>
                        </div>
                        <div class="stat-icon" title="Total Cases" style="font-size:28px;">🗂️</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div>
                            <h3>🔥 High Urgency</h3>
                            <h2>{high_count}</h2>
                        </div>
                        <div class="stat-icon" title="High Urgency" style="font-size:28px;">🚨</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div>
                            <h3>✨ Average Score</h3>
                            <h2>{avg_score}</h2>
                        </div>
                        <div class="stat-icon" title="Average Urgency Score" style="font-size:28px;">🧠</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>")

        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;align-items:center;justify-content:space-between;"><h3 style="margin:0">📊 Prioritized Cases</h3><div style="color:#9ca3af;font-size:13px">Sorted by urgency score (desc)</div></div><hr style="opacity:0.04;margin-top:12px">', unsafe_allow_html=True)

        df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)
        for _, r in df_sorted.iterrows():
            urgency = r["Urgency_Level"]
            stripe_class = "high-stripe" if urgency=="High" else ("medium-stripe" if urgency=="Medium" else "low-stripe")
            urgency_tag_class = "urgency-high" if urgency=="High" else ("urgency-medium" if urgency=="Medium" else "urgency-low")
            deadline_color = "#ef4444" if int(r.get("Deadline_Days_Left", 999)) < 10 else "#60a5fa"
            fill_pct = int(r['Urgency_Score']) if not pd.isna(r['Urgency_Score']) else 0

            # each case block
            st.markdown(f"""
            <div class="case-card" style="margin-bottom:10px;">
                <div class="left-stripe {stripe_class}"></div>
                <div style="margin-left:14px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div>
                            <b style="font-size:15px">{r.get('Case_ID','')} — {r.get('Case_Type','')}</b>
                            <div style="font-size:13px;color:#bcd8ff;margin-top:6px">{r.get('Short_Description','')}</div>
                        </div>
                        <div style="text-align:right">
                            <div class="{urgency_tag_class} urgency-tag">{urgency} </div>
                            <div style="font-size:12px;color:#9ca3af;margin-top:8px">⏱ {r.get('Pending_Days',0)}d pending</div>
                        </div>
                    </div>

                    <div style="margin-top:10px;">
                        <span class="meta-badge" style="background:{deadline_color};color:white;">📅 {r.get('Deadline_Days_Left','N/A')}d left</span>
                        <span class="meta-badge">⚖️ {r.get('Previous_Motions',0)} motions</span>
                    </div>

                    <div class="progress-bar" style="--fill-width: {fill_pct}%;">
                        <div class="progress-fill" style="--fill-width:{fill_pct}%;"></div>
                    </div>
                    <div style="font-size:12px;color:#9ca3af;margin-top:8px">Urgency Score: {fill_pct} • { 'High priority' if urgency=='High' else ('Needs attention' if urgency=='Medium' else 'Routine') }</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------- CALENDAR VIEW --------------------
elif page == "Calendar View":
    st.markdown('<div style="display:flex;align-items:center;gap:12px"><div class="icon-circle"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="4" width="18" height="18" rx="2" fill="white" opacity="0.92"/></svg></div><div><div class="title-gradient">📅 Smart Case Calendar</div><div class="subtitle">Weekday scheduling • 10:00 AM – 4:00 PM • Lunch 12:30–1:00</div></div></div>', unsafe_allow_html=True)

    # calendar-level glass wrapper & styles integrated already above
    if df.empty:
        st.warning("No cases available to schedule.")
    else:
        total_cases = len(df)
        st.markdown(f'<div class="glass"><div style="display:flex;justify-content:space-between;align-items:center"><div style="font-weight:700">🗓️ Scheduling Overview</div><div style="color:#9ca3af">Total cases: {total_cases}</div></div></div>', unsafe_allow_html=True)
        st.write("")

        # durations by urgency in minutes
        duration_map = {"Low": 10, "Medium": 25, "High": 60}

        def next_weekday(date):
            date += timedelta(days=1)
            while date.weekday() >= 5:
                date += timedelta(days=1)
            return date

        # start scheduling at next available weekday 10:00 AM
        start_date = datetime.today()
        while start_date.weekday() >= 5:
            start_date += timedelta(days=1)

        current_time = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = current_time.replace(hour=16, minute=0)
        lunch_start = current_time.replace(hour=12, minute=30)
        lunch_end = current_time.replace(hour=13, minute=0)

        schedule = []
        df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)

        for _, row in df_sorted.iterrows():
            duration = duration_map.get(row["Urgency_Level"], 10)
            case_start = current_time
            case_end = case_start + timedelta(minutes=duration)

            # handle lunch overlap
            if case_start < lunch_end and case_end > lunch_start:
                current_time = lunch_end
                case_start = current_time
                case_end = case_start + timedelta(minutes=duration)

            # if exceed work hours, move to next weekday 10AM
            if case_end > end_time:
                current_time = next_weekday(current_time).replace(hour=10, minute=0)
                end_time = current_time.replace(hour=16, minute=0)
                lunch_start = current_time.replace(hour=12, minute=30)
                lunch_end = current_time.replace(hour=13, minute=0)
                case_start = current_time
                case_end = case_start + timedelta(minutes=duration)

            schedule.append({
                "Date": case_start.strftime("%a %d %b"),
                "Start": case_start.strftime("%I:%M %p"),
                "End": case_end.strftime("%I:%M %p"),
                "Row": row
            })
            current_time = case_end

        schedule_df = pd.DataFrame(schedule)
        days = schedule_df["Date"].unique().tolist()

        # layout: show days in rows (wrap as needed)
        for day in days:
            day_cases = schedule_df[schedule_df["Date"] == day]
            st.markdown(f'<div class="glass" style="margin-top:14px;"><div style="display:flex;justify-content:space-between;align-items:center"><div class="day-column"><div class="day-title">{day}</div></div><div style="color:#9ca3af">{len(day_cases)} cases</div></div>', unsafe_allow_html=True)

            # print each case as a neon card
            for _, entry in day_cases.iterrows():
                r = entry["Row"]
                urgency = r["Urgency_Level"]
                stripe_class = "high-stripe" if urgency=="High" else ("medium-stripe" if urgency=="Medium" else "low-stripe")
                urgency_tag_class = "urgency-high" if urgency=="High" else ("urgency-medium" if urgency=="Medium" else "urgency-low")
                fill_pct = int(r['Urgency_Score']) if not pd.isna(r['Urgency_Score']) else 0
                header = f"{r.get('Case_ID','')} — {r.get('Case_Type','')}"

                st.markdown(f"""
                <div class="case-card" style="margin-top:12px;">
                  <div class="left-stripe {stripe_class}"></div>
                  <div style="margin-left:14px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                      <div>
                        <b style="font-size:15px">{header}</b>
                        <div style="font-size:13px;color:#bcd8ff;margin-top:6px">{r.get('Short_Description','')}</div>
                      </div>
                      <div style="text-align:right">
                        <div class="{urgency_tag_class} urgency-tag">{urgency}</div>
                        <div style="font-size:12px;color:#9ca3af;margin-top:6px">⏰ {entry['Start']} — {entry['End']}</div>
                      </div>
                    </div>

                    <div style="margin-top:10px;">
                      <span class="meta-badge" style="background:{('#ef4444' if int(r.get('Deadline_Days_Left',999))<10 else '#60a5fa')};color:white">📅 {r.get('Deadline_Days_Left','N/A')}d left</span>
                      <span class="meta-badge">⚖️ {r.get('Previous_Motions',0)} motions</span>
                    </div>

                    <div class="progress-bar" style="--fill-width: {fill_pct}%;">
                      <div class="progress-fill" style="--fill-width:{fill_pct}%;"></div>
                    </div>

                    <div style="font-size:12px;color:#9ca3af;margin-top:8px">Urgency Score: {fill_pct} • Duration: { ( '1 hr' if urgency=='High' else ( '25 min' if urgency=='Medium' else '10 min') ) }</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.success("✅ Smart scheduling applied with Neon Glass UI — weekdays only, lunch respected.")

# -------------------- FOOTER --------------------
st.markdown('<div style="text-align:center;padding:18px;color:#9ca3af;font-size:13px">© 2025 Case Dashboard • Built with Streamlit • Neon Glass Mode</div>', unsafe_allow_html=True)
