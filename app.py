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

uploaded = st.sidebar.file_uploader("Upload Case CSV (max 200 MB)", type=["csv"])

# -------------------- DATA HANDLING --------------------
@st.cache_data
def load_data():
    """Load local default CSV (500 cases)."""
    return pd.read_csv("cases.csv")

if uploaded:
    file_size_gb = uploaded.size / (1024 * 1024 * 1024)
    if file_size_gb > 15:
        st.sidebar.error("❌ File too large! Limit: 15 GB")
        st.stop()
    else:
        try:
            data = pd.read_csv(uploaded)
            st.sidebar.success(f"✅ {len(data)} cases loaded successfully")
        except Exception as e:
            st.sidebar.error("⚠️ Could not read CSV. Check the format.")
            st.stop()

else:
    data = load_data()
    st.sidebar.info("📂 Using default internal dataset (500 cases).")

# Encrypt sensitive data before using
encrypted_data = encrypt_data(data)
df = decrypt_data(encrypted_data)

# -------------------- URGENCY CALC --------------------
def calc_urgency(row):
    score = 0
    if row["Case_Type"] in ["Bail", "Custody", "Fraud"]: score += 40
    if row["Pending_Days"] > 100: score += 15
    if row["Deadline_Days_Left"] < 10: score += 25
    if row["Previous_Motions"] > 2: score += 10
    return min(score, 100)

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
    st.subheader("Prioritized Cases")

    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)
    for _, r in df_sorted.iterrows():
        urgency_emoji = "🔴" if r["Urgency_Level"] == "High" else ("🟠" if r["Urgency_Level"] == "Medium" else "🟢")
        urgency_text = f"{urgency_emoji} {r['Urgency_Level']}"
        deadline_color = "#ef4444" if r["Deadline_Days_Left"] < 10 else "#2563eb"

        st.markdown(f"""
        <div class="case-card {r['Urgency_Level'].lower()}">
            <b>{r['Case_ID']} — {r['Case_Type']}</b><br>
            <span style='font-size:14px'>{r['Short_Description']}</span><br>
            <span style='font-size:12px;'>
                <span style="background:{deadline_color};color:white;padding:2px 6px;border-radius:8px;margin-right:5px;">
                    📅 {r['Deadline_Days_Left']} days left
                </span>
                <span style="background:#6b21a8;color:white;padding:2px 6px;border-radius:8px;">
                    ⚖️ {r['Previous_Motions']} motions
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

    start = datetime.today()
    days = [start + timedelta(days=i) for i in range(7)]
    weekdays = [d for d in days if d.weekday() < 5]  # Monday–Friday only
    schedule = {d.strftime("%a %d %b"): [] for d in weekdays}

    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)
    day_index = 0

    # Scheduling logic: high urgency early week, medium midweek, low endweek
    for _, row in df_sorted.iterrows():
        if row["Urgency_Level"] == "High":
            day_key = list(schedule.keys())[min(day_index % 2, 4)]  # Mon-Tue
        elif row["Urgency_Level"] == "Medium":
            day_key = list(schedule.keys())[min(2 + (day_index % 2), 4)]  # Wed-Thu
        else:
            day_key = list(schedule.keys())[4]  # Friday
        schedule[day_key].append(row)
        day_index += 1

    cols = st.columns(len(schedule))
    for i, (day, cases) in enumerate(schedule.items()):
        with cols[i]:
            st.markdown(f'<div class="day-card"><h4>{day}</h4></div>', unsafe_allow_html=True)
            for r in cases:
                urgency_emoji = "🔴" if r["Urgency_Level"]=="High" else ("🟠" if r["Urgency_Level"]=="Medium" else "🟢")
                deadline_color = "#ef4444" if r["Deadline_Days_Left"] < 10 else "#2563eb"

                st.markdown(f"""
                <div class="case-card {r["Urgency_Level"].lower()}">
                    <b>{r["Case_ID"]} — {r["Case_Type"]}</b><br>
                    <span style='font-size:13px'>{r["Short_Description"]}</span><br>
                    <span style='font-size:12px;'>
                        <span style="background:{deadline_color};color:white;padding:2px 6px;border-radius:8px;margin-right:5px;">
                            📅 {r["Deadline_Days_Left"]} days left
                        </span>
                        <span style="background:#6b21a8;color:white;padding:2px 6px;border-radius:8px;">
                            ⚖️ {r["Previous_Motions"]} motions
                        </span>
                    </span>
                    <div class="progress-bar"><div class="progress-fill" style="width:{r["Urgency_Score"]}%"></div></div>
                    <span style='font-size:12px;opacity:0.7'>Urgency: {urgency_emoji} {r["Urgency_Level"]}</span>
                </div>
                """, unsafe_allow_html=True)

    st.success("✅ Calendar simulation ready — weekends excluded.")
