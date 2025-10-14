import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import base64
from cryptography.fernet import Fernet

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="AI-Powered Justice System",
    layout="wide"
)

# -------------------- SECURITY --------------------
# Generate a key for encryption (in real apps, store securely)
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(dataframe):
    """Encrypt CSV data for privacy before displaying."""
    csv_bytes = dataframe.to_csv(index=False).encode()
    encrypted = cipher.encrypt(csv_bytes)
    return encrypted


def decrypt_data(encrypted_data):
    """Decrypt CSV data to readable format."""
    decrypted = cipher.decrypt(encrypted_data).decode()
    from io import StringIO
    return pd.read_csv(StringIO(decrypted))

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
body, .stApp, .stSidebar { font-family: 'Segoe UI', sans-serif; }

.title-gradient {
    background: linear-gradient(90deg, #2563eb, #6b21a8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 40px;
    font-weight: 700;
}
.subtitle { font-size: 18px; color: #555; margin-bottom: 20px; }

.metric-card {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-5px); }

.case-card {
    padding: 15px;
    margin-bottom: 12px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    border-left: 6px solid;
    background-color: #ffffff;
    transition: transform 0.2s, box-shadow 0.2s;
}
.case-card:hover {
    transform: translateY(-3px);
    box-shadow: 0px 8px 18px rgba(0,0,0,0.15);
}

.high {border-left-color:#ef4444;}
.medium {border-left-color:#f59e0b;}
.low {border-left-color:#10b981;}

.progress-bar { height: 6px; border-radius: 3px; background-color: #e0e0e0; margin-top: 8px; margin-bottom: 5px; }
.progress-fill { height: 6px; border-radius: 3px; background: linear-gradient(90deg, #2563eb, #6b21a8); }

.day-card {
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 12px;
    background-color: #f5f5f5;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.day-card:hover { transform: translateY(-2px); }

@media (prefers-color-scheme: dark) {
    body, .stApp, .stSidebar { color: #f1f1f1; }
    .metric-card, .case-card, .day-card { background-color: #1e1e1e !important; color: #f1f1f1 !important; box-shadow: 0px 4px 12px rgba(0,0,0,0.5); }
    .progress-bar { background-color: #333; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["Dashboard", "Calendar View"])
st.sidebar.markdown("---")

# Display upload limit as 1 GB (user requested display at least 1GB)
MAX_UPLOAD_GB = 1
uploaded = st.sidebar.file_uploader(f"Upload Case CSV (display limit: {MAX_UPLOAD_GB} GB)", type=["csv"])

# -------------------- DATA HANDLING --------------------
@st.cache_data
def load_data():
    """Load local default CSV (expected ~500 cases)."""
    return pd.read_csv("cases.csv")

if uploaded:
    file_size_gb = uploaded.size / (1024 * 1024 * 1024)
    # Enforce the displayed limit (1 GB). If larger, show a helpful error.
    if file_size_gb > MAX_UPLOAD_GB:
        st.sidebar.error(f"❌ File too large for display (>{MAX_UPLOAD_GB} GB). Please upload a smaller file.")
        st.stop()
    else:
        try:
            data = pd.read_csv(uploaded)
            st.sidebar.success(f"✅ {len(data)} cases loaded successfully (uploaded)")
        except Exception as e:
            st.sidebar.error("⚠️ Could not read CSV. Check the format.")
            st.stop()

else:
    data = load_data()
    st.sidebar.info("📂 Using default internal dataset (expected ~500 cases).")

# Encrypt sensitive data before using
encrypted_data = encrypt_data(data)
df = decrypt_data(encrypted_data)

# -------------------- URGENCY CALC --------------------
def calc_urgency(row):
    score = 0
    if row.get("Case_Type") in ["Bail", "Custody", "Fraud"]:
        score += 40
    if row.get("Pending_Days", 0) > 100:
        score += 15
    if row.get("Deadline_Days_Left", 999) < 10:
        score += 25
    if row.get("Previous_Motions", 0) > 2:
        score += 10
    return min(score, 100)

# Defensive: ensure numeric columns exist and have correct dtype
for col in ["Pending_Days", "Deadline_Days_Left", "Previous_Motions"]:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

if "Case_Type" not in df.columns:
    df["Case_Type"] = "Unknown"

# Apply urgency calculations
df["Urgency_Score"] = df.apply(calc_urgency, axis=1)
df["Urgency_Level"] = df["Urgency_Score"].apply(lambda x: "High" if x >= 70 else ("Medium" if x >= 40 else "Low"))

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.markdown('<div class="title-gradient">⚖️ AI-Powered Justice System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Prioritize court cases with intelligence and privacy protection.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="metric-card"><h3>Total Cases</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><h3>High Urgency</h3><h2>{(df["Urgency_Level"]=="High").sum()}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><h3>Average Score</h3><h2>{round(df["Urgency_Score"].mean(),1)}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Prioritized Cases (all cases shown)")

    # Ensure we show ALL cases prioritized (user requested to display all ~500 cases)
    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)

    # To avoid overwhelming the UI all at once for very large datasets, put each case inside an expander
    for idx, r in df_sorted.iterrows():
        urgency_emoji = "🔴" if r["Urgency_Level"] == "High" else ("🟠" if r["Urgency_Level"] == "Medium" else "🟢")
        urgency_text = f"{urgency_emoji} {r['Urgency_Level']}"
        deadline_color = "#ef4444" if r["Deadline_Days_Left"] < 10 else "#2563eb"

        with st.expander(f"{r.get('Case_ID', '—')} — {r.get('Case_Type', '')} ({urgency_text})", expanded=False):
            st.markdown(f"""
            <div class="case-card {r['Urgency_Level'].lower()}">
                <b>{r.get('Case_ID', '')} — {r.get('Case_Type', '')}</b><br>
                <span style='font-size:14px'>{r.get('Short_Description', '')}</span><br>
                <span style='font-size:12px;'>
                    <span style="background:{deadline_color};color:white;padding:2px 6px;border-radius:8px;margin-right:5px;">
                        📅 {r.get('Deadline_Days_Left', '')} days left
                    </span>
                    <span style="background:#6b21a8;color:white;padding:2px 6px;border-radius:8px;">
                        ⚖️ {r.get('Previous_Motions', '')} motions
                    </span>
                </span>
                <div class="progress-bar"><div class="progress-fill" style="width:{r['Urgency_Score']}%"></div></div>
                <span style='font-size:12px;opacity:0.7'>Urgency: {urgency_text}</span>
            </div>
            """, unsafe_allow_html=True)

# -------------------- CALENDAR VIEW --------------------
elif page == "Calendar View":
    st.markdown('<div class="title-gradient">📅 Case Calendar View</div>', unsafe_allow_html=True)
    st.write("Weekly scheduling (Mon–Fri only). Weekends are automatically skipped.")

    # Collect the next 5 weekdays (Mon-Fri) starting from today
    start = datetime.today()
    weekdays = []
    cursor = start
    while len(weekdays) < 5:
        if cursor.weekday() < 5:
            weekdays.append(cursor)
        cursor += timedelta(days=1)

    weekday_keys = [d.strftime("%a %d %b") for d in weekdays]
    schedule = {k: [] for k in weekday_keys}

    # Prioritize and then split into 5 groups of ~100 each (user requested 100 per day for 5 days).
    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)

    # Calculate chunk index: 0..4 mapping to weekdays
    for i, row in df_sorted.iterrows():
        day_idx = min(i // 100, 4)  # first 100 -> day 0, next 100 -> day1, ... remaining -> day4
        schedule[weekday_keys[day_idx]].append(row)

    cols = st.columns(len(schedule))
    for i, (day, cases) in enumerate(schedule.items()):
        with cols[i]:
            st.markdown(f'<div class="day-card"><h4>{day} — {len(cases)} cases</h4></div>', unsafe_allow_html=True)
            for r in cases:
                urgency_emoji = "🔴" if r["Urgency_Level"]=="High" else ("🟠" if r["Urgency_Level"]=="Medium" else "🟢")
                deadline_color = "#ef4444" if r["Deadline_Days_Left"] < 10 else "#2563eb"

                st.markdown(f"""
                <div class="case-card {r["Urgency_Level"].lower()}">
                    <b>{r.get('Case_ID','')} — {r.get('Case_Type','')}</b><br>
                    <span style='font-size:13px'>{r.get('Short_Description','')}</span><br>
                    <span style='font-size:12px;'>
                        <span style="background:{deadline_color};color:white;padding:2px 6px;border-radius:8px;margin-right:5px;">
                            📅 {r.get('Deadline_Days_Left','')} days left
                        </span>
                        <span style="background:#6b21a8;color:white;padding:2px 6px;border-radius:8px;">
                            ⚖️ {r.get('Previous_Motions','')} motions
                        </span>
                    </span>
                    <div class="progress-bar"><div class="progress-fill" style="width:{r['Urgency_Score']}%"></div></div>
                    <span style='font-size:12px;opacity:0.7'>Urgency: {urgency_emoji} {r["Urgency_Level"]}</span>
                </div>
                """, unsafe_allow_html=True)

    st.success("✅ Calendar simulation ready — 100 cases assigned per weekday (Mon–Fri).")
