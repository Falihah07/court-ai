# app.py — restored styled UI + robust CSV mapping + correct calendar split
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import math

# -------------------- PAGE SETUP -------------------
st.set_page_config(
    page_title="AI-Powered Justice System",
    layout="wide"
)

# -------------------- SECURITY --------------------
# NOTE: In production, store key securely. For demo, generate each run.
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(dataframe):
    csv_bytes = dataframe.to_csv(index=False).encode()
    return cipher.encrypt(csv_bytes)

def decrypt_data(encrypted_data):
    decrypted = cipher.decrypt(encrypted_data).decode()
    from io import StringIO
    return pd.read_csv(StringIO(decrypted))

# -------------------- CUSTOM CSS (restore original look) --------------------
st.markdown("""
st.markdown("""
<style>
/* ---------- Global Font & Background ---------- */
body, .stApp, .stSidebar {
    font-family: 'Segoe UI', sans-serif;
    color: #f3f4f6;
    background: radial-gradient(circle at top left, #0f172a 0%, #111827 100%);
}

/* ---------- Title Gradient ---------- */
.title-gradient {
    background: linear-gradient(90deg, #60a5fa, #c084fc, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 42px;
    font-weight: 800;
    text-shadow: 0 2px 8px rgba(99,102,241,0.5);
}

/* ---------- Subtitle ---------- */
.subtitle {
    font-size: 18px;
    color: #9ca3af;
    margin-bottom: 22px;
    letter-spacing: 0.3px;
}

/* ---------- Metric Cards ---------- */
.metric-card {
    background: linear-gradient(145deg, #1f2937, #0f172a);
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 8px 22px rgba(0,0,0,0.55);
    transition: all 0.25s ease-in-out;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(59,130,246,0.25);
}
.metric-card h3 { color: #a5b4fc; font-weight: 600; margin-bottom: 8px; }
.metric-card h2 { color: #fff; font-size: 36px; margin: 0; text-shadow: 0 2px 8px rgba(255,255,255,0.2); }

/* ---------- Case Cards ---------- */
.case-card {
    padding: 18px;
    margin-bottom: 18px;
    border-radius: 14px;
    background: rgba(17,24,39,0.95);
    box-shadow: 0 4px 14px rgba(0,0,0,0.6);
    border-left: 6px solid;
    transition: all 0.2s ease;
    position: relative;
}
.case-card:hover {
    transform: translateY(-2px);
    box-shadow: 0px 8px 20px rgba(99,102,241,0.3);
}
.case-card::before {
    content: "";
    position: absolute;
    left: -6px;
    top: 0;
    height: 100%;
    width: 6px;
    border-radius: 6px 0 0 6px;
}
.high::before { background: linear-gradient(180deg,#f87171,#ef4444); }
.medium::before { background: linear-gradient(180deg,#fbbf24,#f59e0b); }
.low::before { background: linear-gradient(180deg,#34d399,#10b981); }

.progress-bar {
    height: 8px;
    border-radius: 6px;
    background-color: #1f2937;
    margin-top: 12px;
    margin-bottom: 6px;
    overflow: hidden;
}
.progress-fill {
    height: 8px;
    border-radius: 6px;
    background: linear-gradient(90deg, #3b82f6, #a855f7, #ec4899);
    box-shadow: 0 0 6px rgba(168,85,247,0.4);
}

/* ---------- Day Cards ---------- */
.day-card {
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 18px;
    background: linear-gradient(145deg, rgba(31,41,55,0.9), rgba(17,24,39,0.9));
    box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
    transition: all 0.2s ease;
}
.day-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(99,102,241,0.25);
}

.day-header {
    padding: 10px 12px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 15px;
    color: #0f1724;
    background: linear-gradient(90deg,#bfdbfe,#ddd6fe,#fce7f3);
    text-align: center;
    box-shadow: inset 0 0 8px rgba(255,255,255,0.4);
}

/* ---------- Expanders ---------- */
.expander .streamlit-expanderHeader {
    color: #e5e7eb !important;
    font-weight: 600 !important;
}

/* ---------- Sidebar ---------- */
.stSidebar {
    background: linear-gradient(180deg, #111827, #0f172a);
    color: #d1d5db;
}
.stSidebar .css-1d391kg { color: #d1d5db; }

/* ---------- Buttons ---------- */
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#6b21a8);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 600;
    transition: all 0.25s ease;
}
.stButton>button:hover {
    transform: scale(1.04);
    box-shadow: 0 0 10px rgba(147,51,234,0.4);
}

/* ---------- Light Mode Adjustments ---------- */
@media (prefers-color-scheme: light) {
    body, .stApp, .stSidebar {
        color: #111827;
        background: linear-gradient(180deg,#f9fafb,#f3f4f6);
    }
    .metric-card, .case-card, .day-card {
        background-color: #ffffff !important;
        color: #111827 !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    .day-header {
        color: #111827;
        background: linear-gradient(90deg,#bfdbfe,#ddd6fe,#fce7f3);
    }
    .progress-bar { background-color: #e5e7eb; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["Dashboard", "Calendar View"])
st.sidebar.markdown("---")

# show displayed upload limit (user requested 1 GB display)
MAX_UPLOAD_GB = 1
uploaded = st.sidebar.file_uploader(f"Upload Case CSV (display limit: {MAX_UPLOAD_GB} GB)", type=["csv"])

# -------------------- DATA LOADING (robust) --------------------
@st.cache_data
def load_local_csv(path="cases.csv"):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

# Decide data source
if uploaded:
    # convert uploaded to DataFrame
    try:
        df = pd.read_csv(uploaded)
        st.sidebar.success(f"✅ {len(df)} cases loaded successfully (uploaded)")
    except Exception as e:
        st.sidebar.error("⚠️ Could not read CSV. Check the format.")
        st.stop()
else:
    df = load_local_csv("cases.csv")
    if df.empty:
        st.sidebar.warning("No local cases.csv found or file empty.")
    else:
        st.sidebar.info("📂 Using default internal dataset (expected ~500 cases).")

# encrypt/decrypt roundtrip (keeps original behavior & simulates privacy)
if not df.empty:
    encrypted_data = encrypt_data(df)
    df = decrypt_data(encrypted_data)

# -------------------- NORMALIZE COLUMNS (robust mapping) --------------------
# Your CSVs varied across versions. Normalize common names to canonical keys we use below.
# Possible column names we might encounter and map them to canonical names:
col_map_candidates = {
    'Case_ID': ['Case_ID','CaseId','case_id','caseid','Case Number','Case_Number','CaseNumber'],
    'Case_Name': ['Case_Name','CaseName','Name','case_name'],
    'Case_Type': ['Case_Type','Type','case_type'],
    'Pending_Days': ['Pending_Days','PendingDays','pending_days'],
    'Deadline_Days_Left': ['Deadline_Days_Left','Days_Left','DeadlineDaysLeft','deadline_days_left'],
    'Previous_Motions': ['Previous_Motions','Prev_Motions','PreviousMotions','previous_motions'],
    'Short_Description': ['Short_Description','ShortDescription','Description','ShortDesc','short_description'],
    'Urgency': ['Urgency','Urgency_Level','Urgency_Level','urgency']
}

# Create canonical columns in df if present in any of the candidate names
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

# Ensure required columns exist (create reasonable defaults)
if not df.empty:
    if 'Case_ID' not in df.columns:
        df['Case_ID'] = df.index.to_series().apply(lambda x: f"C{x+1:03d}")
    # ensure numeric columns exist
    for col in ['Pending_Days','Deadline_Days_Left','Previous_Motions']:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# -------------------- URGENCY SCORE (compute if not present) --------------------
def calc_urgency_score(row):
    # If there's a provided Urgency column with text, try to map to score
    if pd.notna(row.get('Urgency')) and isinstance(row.get('Urgency'), str):
        s = row.get('Urgency').strip().lower()
        if s in ('high','h','urgent'): return 90
        if s in ('medium','med','m'): return 55
        if s in ('low','l'): return 15
    # else compute heuristically from case type and numeric fields (fallback)
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
    st.markdown('<div class="title-gradient">⚖️ AI-Powered Justice System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Prioritize court cases with intelligence and privacy protection.</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No case data to display. Upload a CSV or add a local cases.csv.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.markdown(f'<div class="metric-card"><h3>Total Cases</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-card"><h3>High Urgency</h3><h2>{(df["Urgency_Level"]=="High").sum()}</h2></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-card"><h3>Average Score</h3><h2>{round(df["Urgency_Score"].mean(),1)}</h2></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Prioritized Cases (all cases shown)")

        df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)

        # Show all cases — use expanders like your original UI
        for _, r in df_sorted.iterrows():
            urgency_emoji = "🔴" if r["Urgency_Level"] == "High" else ("🟠" if r["Urgency_Level"] == "Medium" else "🟢")
            urgency_text = f"{urgency_emoji} {r['Urgency_Level']}"
            deadline_color = "#ef4444" if int(r.get("Deadline_Days_Left", 999)) < 10 else "#2563eb"
            level_class = r['Urgency_Level'].lower() if isinstance(r['Urgency_Level'], str) else ""

            header = f"{r.get('Case_ID','')} — {r.get('Case_Type','')}"
            with st.expander(f"{header} ({urgency_text})", expanded=False):
                st.markdown(f"""
                <div class="case-card {level_class}">
                    <b style="font-size:16px">{r.get('Case_ID','')} — {r.get('Case_Type','')}</b><br>
                    <div style='font-size:14px;margin-top:6px'>{r.get('Short_Description', r.get('Description',''))}</div>
                    <div style='margin-top:10px'>
                        <span style="background:{deadline_color};color:white;padding:4px 8px;border-radius:8px;margin-right:6px;">
                            📅 {r.get('Deadline_Days_Left','N/A')} days left
                        </span>
                        <span style="background:#6b21a8;color:white;padding:4px 8px;border-radius:8px;">
                            ⚖️ {r.get('Previous_Motions',0)} motions
                        </span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width:{r['Urgency_Score']}%"></div></div>
                    <div style='font-size:12px;opacity:0.8;margin-top:6px'>Urgency: {urgency_text}</div>
                </div>
                """, unsafe_allow_html=True)

# -------------------- CALENDAR VIEW --------------------
elif page == "Calendar View":
    st.markdown('<div class="title-gradient">📅 Case Calendar View</div>', unsafe_allow_html=True)
    st.write("Smart scheduling with real-world time slots (10 AM – 4 PM, 12:30–1:00 PM lunch, weekdays only).")

    if df.empty:
        st.warning("No cases available to schedule.")
    else:
        total_cases = len(df)
        st.info(f"Total cases to schedule: {total_cases}")

        # Define duration by urgency level (in minutes)
        duration_map = {"Low": 10, "Medium": 25, "High": 60}

        # Function to get next weekday (skip Sat/Sun)
        def next_weekday(date):
            date += timedelta(days=1)
            while date.weekday() >= 5:  # 5=Sat, 6=Sun
                date += timedelta(days=1)
            return date

        # Start at 10 AM today (or next weekday if weekend)
        start_date = datetime.today()
        while start_date.weekday() >= 5:
            start_date += timedelta(days=1)

        current_time = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = current_time.replace(hour=16, minute=0)
        lunch_start = current_time.replace(hour=12, minute=30)
        lunch_end = current_time.replace(hour=13, minute=0)

        # Prepare schedule list
        schedule = []
        df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)

        for _, row in df_sorted.iterrows():
            duration = duration_map.get(row["Urgency_Level"], 10)
            case_start = current_time
            case_end = case_start + timedelta(minutes=duration)

            # Skip lunch
            if case_start < lunch_end and case_end > lunch_start:
                current_time = lunch_end
                case_start = current_time
                case_end = case_start + timedelta(minutes=duration)

            # If exceeds work hours, move to next weekday 10 AM
            if case_end > end_time:
                current_time = next_weekday(current_time).replace(hour=10, minute=0)
                end_time = current_time.replace(hour=16, minute=0)
                lunch_start = current_time.replace(hour=12, minute=30)
                lunch_end = current_time.replace(hour=13, minute=0)
                case_start = current_time
                case_end = case_start + timedelta(minutes=duration)

            # Save scheduled entry
            schedule.append({
                "Date": case_start.strftime("%a %d %b"),
                "Start": case_start.strftime("%I:%M %p"),
                "End": case_end.strftime("%I:%M %p"),
                "Row": row
            })
            current_time = case_end

        # Group by date for display
        schedule_df = pd.DataFrame(schedule)
        days = schedule_df["Date"].unique()
        pastel_colors = ["#dbeafe", "#e6f4ea", "#fff7e6", "#f3e5f5", "#e0f7fa"]

        for i, day in enumerate(days):
            day_cases = schedule_df[schedule_df["Date"] == day]
            color = pastel_colors[i % len(pastel_colors)]
            st.markdown(
                f'<div class="day-card" style="padding:8px;"><div class="day-header" style="background-color:{color};">'
                f"{day} — {len(day_cases)} cases</div></div>", unsafe_allow_html=True
            )

            for _, entry in day_cases.iterrows():
                r = entry["Row"]
                urgency_emoji = "🔴" if r["Urgency_Level"] == "High" else ("🟠" if r["Urgency_Level"] == "Medium" else "🟢")
                deadline_color = "#ef4444" if int(r.get("Deadline_Days_Left", 999)) < 10 else "#2563eb"
                level_class = r['Urgency_Level'].lower() if isinstance(r['Urgency_Level'], str) else ""
                header = f"{r.get('Case_ID','')} — {r.get('Case_Type','')} ({entry['Start']}–{entry['End']})"

                with st.expander(f"{header} ({urgency_emoji} {r['Urgency_Level']})", expanded=False):
                    st.markdown(f"""
                    <div class="case-card {level_class}">
                        <b>{r.get('Case_ID','')} — {r.get('Case_Type','')}</b><br>
                        <div style='font-size:13px'>{r.get('Short_Description', r.get('Description',''))}</div>
                        <div style='margin-top:8px;'>
                            <span style="background:{deadline_color};color:white;padding:4px 8px;border-radius:8px;margin-right:6px;">
                                📅 {r.get('Deadline_Days_Left','N/A')} days left
                            </span>
                            <span style="background:#6b21a8;color:white;padding:4px 8px;border-radius:8px;">
                                ⚖️ {r.get('Previous_Motions',0)} motions
                            </span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width:{r['Urgency_Score']}%"></div></div>
                        <div style='font-size:12px;opacity:0.8;margin-top:6px'>
                            Urgency: {r['Urgency_Level']} | Time: {entry['Start']} – {entry['End']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.success("✅ Smart scheduling applied: weekdays only, with lunch break & urgency-based timing.")
