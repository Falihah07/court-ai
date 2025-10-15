import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="AI-Powered Justice System",
    layout="wide"
)

# -------------------- SECURITY --------------------
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(dataframe):
    csv_bytes = dataframe.to_csv(index=False).encode()
    return cipher.encrypt(csv_bytes)

def decrypt_data(encrypted_data):
    decrypted = cipher.decrypt(encrypted_data).decode()
    from io import StringIO
    return pd.read_csv(StringIO(decrypted))

# -------------------- MODERN CSS (Full Visual Upgrade) --------------------
st.markdown("""
<style>
/* ===== BACKGROUND ===== */
body, .stApp, .stSidebar {
    font-family: 'Poppins', 'Segoe UI', sans-serif;
    color: #f3f4f6;
    background: radial-gradient(circle at 25% 25%, #0f172a 0%, #111827 60%, #0a0f1f 100%);
    animation: bgShift 14s ease-in-out infinite alternate;
}
@keyframes bgShift {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}

/* ===== TITLE ===== */
.title-gradient {
    background: linear-gradient(270deg, #60a5fa, #c084fc, #ec4899, #8b5cf6);
    background-size: 600% 600%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 44px;
    font-weight: 900;
    animation: gradientShift 6s ease infinite;
    text-shadow: 0 3px 8px rgba(147,51,234,0.4);
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ===== SUBTITLE ===== */
.subtitle {
    font-size: 18px;
    color: #a1a1aa;
    margin-bottom: 25px;
    letter-spacing: 0.4px;
}

/* ===== METRIC CARDS ===== */
.metric-card {
    background: rgba(17,24,39,0.75);
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.1);
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-6px) scale(1.03);
    box-shadow: 0 0 20px rgba(168,85,247,0.4);
}
.metric-card h3 { color: #a5b4fc; font-weight: 600; margin-bottom: 6px; }
.metric-card h2 { color: #fff; font-size: 38px; margin: 0; }

/* ===== CASE CARDS ===== */
.case-card {
    background: rgba(17,24,39,0.7);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 18px;
    border-left: 6px solid;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
}
.case-card:hover {
    transform: translateY(-3px) scale(1.01);
    box-shadow: 0 0 25px rgba(147,51,234,0.4);
}
.case-card::after {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    opacity: 0;
    background: linear-gradient(120deg, rgba(147,51,234,0.1), rgba(236,72,153,0.1));
    transition: opacity 0.3s ease;
}
.case-card:hover::after { opacity: 1; }

.high { border-left-color: #f87171; }
.medium { border-left-color: #fbbf24; }
.low { border-left-color: #34d399; }

/* ===== PROGRESS BAR ===== */
.progress-bar {
    height: 8px;
    border-radius: 5px;
    background: rgba(255,255,255,0.08);
    margin-top: 10px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 5px;
    background: linear-gradient(90deg, #60a5fa, #a855f7, #ec4899);
    background-size: 200% 200%;
    animation: barFlow 3s linear infinite;
}
@keyframes barFlow {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}

/* ===== SIDEBAR ===== */
.stSidebar {
    backdrop-filter: blur(18px);
    background: linear-gradient(180deg, rgba(15,23,42,0.9), rgba(30,41,59,0.95));
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ===== BUTTONS ===== */
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#6b21a8);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
    transition: all 0.25s ease;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 14px rgba(147,51,234,0.45);
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["Dashboard", "Calendar View"])
st.sidebar.markdown("---")

MAX_UPLOAD_GB = 1
uploaded = st.sidebar.file_uploader(f"Upload Case CSV (limit: {MAX_UPLOAD_GB} GB)", type=["csv"])

# -------------------- DATA LOADING --------------------
@st.cache_data
def load_local_csv(path="cases.csv"):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

if uploaded:
    df = pd.read_csv(uploaded)
    st.sidebar.success(f"✅ {len(df)} cases loaded successfully.")
else:
    df = load_local_csv("cases.csv")
    if df.empty:
        st.sidebar.warning("No local cases.csv found or empty.")
    else:
        st.sidebar.info("📂 Using default dataset.")

if not df.empty:
    encrypted_data = encrypt_data(df)
    df = decrypt_data(encrypted_data)

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
    df['Urgency_Score'] = df.apply(calc_urgency_score, axis=1)
    df['Urgency_Level'] = df['Urgency_Score'].apply(lambda x: "High" if x >= 70 else ("Medium" if x >= 40 else "Low"))

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.markdown('<div class="title-gradient">⚖️ AI-Powered Justice System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Prioritize court cases with intelligence and privacy protection.</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No data.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.markdown(f'<div class="metric-card"><h3>Total Cases</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-card"><h3>High Urgency</h3><h2>{(df["Urgency_Level"]=="High").sum()}</h2></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-card"><h3>Average Score</h3><h2>{round(df["Urgency_Score"].mean(),1)}</h2></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Prioritized Case List")
        df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)
        for _, r in df_sorted.iterrows():
            urgency = r["Urgency_Level"].lower()
            urgency_emoji = "🔴" if urgency == "high" else ("🟠" if urgency == "medium" else "🟢")
            with st.expander(f"{r['Case_ID']} — {r['Case_Type']} ({urgency_emoji} {r['Urgency_Level']})"):
                st.markdown(f"""
                <div class="case-card {urgency}">
                    <b>{r['Case_ID']} — {r['Case_Type']}</b><br>
                    <div style="margin-top:8px;">{r.get('Short_Description','')}</div>
                    <div class="progress-bar"><div class="progress-fill" style="width:{r['Urgency_Score']}%"></div></div>
                    <div style="font-size:12px;opacity:0.8;">Urgency: {r['Urgency_Level']}</div>
                </div>
                """, unsafe_allow_html=True)

# -------------------- CALENDAR VIEW --------------------
elif page == "Calendar View":
    st.markdown('<div class="title-gradient">📅 Smart Case Calendar</div>', unsafe_allow_html=True)
    st.write("AI-optimized weekly scheduling (weekdays only, 10 AM–4 PM).")

    if df.empty:
        st.warning("No cases to schedule.")
    else:
        duration_map = {"Low": 10, "Medium": 25, "High": 60}
        def next_weekday(date):
            date += timedelta(days=1)
            while date.weekday() >= 5:
                date += timedelta(days=1)
            return date

        start_date = datetime.today()
        while start_date.weekday() >= 5:
            start_date += timedelta(days=1)
        current_time = start_date.replace(hour=10, minute=0)
        end_time = current_time.replace(hour=16, minute=0)
        lunch_start = current_time.replace(hour=12, minute=30)
        lunch_end = current_time.replace(hour=13, minute=0)

        schedule = []
        df_sorted = df.sort_values("Urgency_Score", ascending=False)
        for _, row in df_sorted.iterrows():
            duration = duration_map[row["Urgency_Level"]]
            case_start = current_time
            case_end = case_start + timedelta(minutes=duration)
            if case_start < lunch_end and case_end > lunch_start:
                current_time = lunch_end
                case_start = current_time
                case_end = case_start + timedelta(minutes=duration)
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
        for day in schedule_df["Date"].unique():
            day_cases = schedule_df[schedule_df["Date"] == day]
            st.markdown(f"### {day} — {len(day_cases)} cases")
            for _, entry in day_cases.iterrows():
                r = entry["Row"]
                urgency = r["Urgency_Level"]
                with st.expander(f"{r['Case_ID']} — {r['Case_Type']} ({urgency})"):
                    st.markdown(f"""
                    <div class="case-card {urgency.lower()}">
                        <b>{r['Case_ID']} — {r['Case_Type']}</b><br>
                        <div>⏰ {entry['Start']} – {entry['End']}</div>
                        <div>{r.get('Short_Description','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
