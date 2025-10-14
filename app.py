# app.py — restored styled UI + robust CSV mapping + correct calendar split
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import math

# -------------------- PAGE SETUP --------------------
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
<style>
body, .stApp, .stSidebar { font-family: 'Segoe UI', sans-serif; color: #fff; }
.title-gradient {
    background: linear-gradient(90deg, #2563eb, #6b21a8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 40px;
    font-weight: 700;
}
.subtitle { font-size: 18px; color: #9ca3af; margin-bottom: 20px; }

.metric-card {
    background-color: #111827;
    border-radius: 15px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 6px 16px rgba(0,0,0,0.6);
    transition: transform 0.2s;
}
.metric-card h3 { color: #e5e7eb; font-weight: 600; margin-bottom: 8px; }
.metric-card h2 { color: #fff; font-size: 34px; margin: 0; }

.case-card {
    padding: 18px;
    margin-bottom: 18px;
    border-radius: 12px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.6);
    border-left: 6px solid;
    background-color: #0f1724;
    transition: transform 0.15s, box-shadow 0.15s;
}
.case-card:hover {
    transform: translateY(-2px);
    box-shadow: 0px 10px 22px rgba(0,0,0,0.7);
}

.high {border-left-color:#ef4444;}
.medium {border-left-color:#f59e0b;}
.low {border-left-color:#10b981;}

.progress-bar { height: 8px; border-radius: 6px; background-color: #1f2937; margin-top: 12px; margin-bottom: 6px; }
.progress-fill { height: 8px; border-radius: 6px; background: linear-gradient(90deg, #2563eb, #6b21a8); }

.day-card {
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 12px;
    background-color: rgba(255,255,255,0.03);
    box-shadow: 0px 4px 10px rgba(0,0,0,0.6);
    transition: transform 0.12s;
}
.day-header {
    padding: 10px;
    border-radius: 10px;
    color: #0f1724;
    font-weight: 700;
}

.expander .streamlit-expanderHeader { color: #e5e7eb !important; }

.stSidebar .css-1d391kg { color: #d1d5db; }  /* sidebar text */
.stButton>button { background-color: #111827; color: #fff; }

@media (prefers-color-scheme: light) {
    body, .stApp, .stSidebar { color: #111827; }
    .metric-card, .case-card, .day-card { background-color: #ffffff !important; color: #111827 !important; box-shadow: 0px 4px 12px rgba(0,0,0,0.08); }
    .progress-bar { background-color: #e6e7eb; }
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
    st.write("Weekly scheduling (Mon–Fri only). Weekends are skipped automatically.")

    if df.empty:
        st.warning("No cases available to schedule.")
    else:
        total_cases = len(df)
        st.info(f"Total cases to schedule: {total_cases}")

        # Determine next 5 weekdays
        start = datetime.today()
        weekdays = []
        cur = start
        while len(weekdays) < 5:
            if cur.weekday() < 5:
                weekdays.append(cur)
            cur += timedelta(days=1)
        weekday_keys = [d.strftime("%a %d %b") for d in weekdays]

        # Evenly split cases into 5 lists (as even as possible)
        # For exactly 500 -> yields five lists of length 100.
        per_day_base = total_cases // 5
        remainder = total_cases % 5
        splits = []
        start_idx = 0
        for i in range(5):
            size = per_day_base + (1 if i < remainder else 0)
            end_idx = start_idx + size
            splits.append(df.sort_values("Urgency_Score", ascending=False).iloc[start_idx:end_idx].reset_index(drop=True))
            start_idx = end_idx

        pastel_colors = ["#dbeafe", "#e6f4ea", "#fff7e6", "#f3e5f5", "#e0f7fa"]

        cols = st.columns(5)
        for i, key in enumerate(weekday_keys):
            with cols[i]:
                # day header with pastel tint and dark text for clear separation
                st.markdown(f'<div class="day-card" style="padding:8px;"><div class="day-header" style="background-color:{pastel_colors[i]};">{key} — {len(splits[i])} cases</div></div>', unsafe_allow_html=True)
                if splits[i].empty:
                    st.write("No cases assigned.")
                else:
                    for _, r in splits[i].iterrows():
                        urgency_emoji = "🔴" if r["Urgency_Level"] == "High" else ("🟠" if r["Urgency_Level"] == "Medium" else "🟢")
                        deadline_color = "#ef4444" if int(r.get("Deadline_Days_Left", 999)) < 10 else "#2563eb"
                        level_class = r['Urgency_Level'].lower() if isinstance(r['Urgency_Level'], str) else ""
                        header = f"{r.get('Case_ID','')} — {r.get('Case_Type','')}"
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
                                <div style='font-size:12px;opacity:0.8;margin-top:6px'>Urgency: {r['Urgency_Level']}</div>
                            </div>
                            """, unsafe_allow_html=True)

        st.success("✅ Calendar simulation: cases evenly distributed across next 5 weekdays (Mon–Fri).")

# -------------------- FOOTER --------------------
st.markdown('<hr><p style="text-align:center; color:grey; font-size:12px;">© 2025 Case Dashboard | Built with Streamlit</p>', unsafe_allow_html=True)
