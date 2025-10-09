import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="AI-Powered Justice System",
    layout="wide"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
/* ----------------- Global Styles ----------------- */
body, .stApp, .stSidebar {
    font-family: 'Segoe UI', sans-serif;
}

/* Gradient Title */
.title-gradient {
    background: linear-gradient(90deg, #2563eb, #6b21a8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 40px;
    font-weight: 700;
}

/* Subtitle */
.subtitle {
    font-size: 18px;
    color: #555;
    margin-bottom: 20px;
}

/* Metric Cards */
.metric-card {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.metric-card:hover {
    transform: translateY(-5px);
}

/* Prioritized Case Cards */
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

/* Urgency colors */
.high {border-left-color:#ef4444;}
.medium {border-left-color:#f59e0b;}
.low {border-left-color:#10b981;}

/* Deadline Progress Bar */
.progress-bar {
    height: 6px;
    border-radius: 3px;
    background-color: #e0e0e0;
    margin-top: 8px;
    margin-bottom: 5px;
}
.progress-fill {
    height: 6px;
    border-radius: 3px;
    background: linear-gradient(90deg, #2563eb, #6b21a8);
}

/* Calendar Day Cards */
.day-card {
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 12px;
    background-color: #f5f5f5;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.day-card:hover {
    transform: translateY(-2px);
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
    body, .stApp, .stSidebar {
        color: #f1f1f1;
    }
    .metric-card, .case-card, .day-card {
        background-color: #1e1e1e !important;
        color: #f1f1f1 !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
    }
    .progress-bar {background-color: #333;}
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["Dashboard", "Calendar View"])
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload Case CSV", type=["csv"])

# -------------------- DATA --------------------
def load_data():
    return pd.DataFrame({
        "Case_ID": ["C101","C102","C103","C104","C105","C106"],
        "Case_Type": ["Bail","Custody","Fraud","Contract","Land Dispute","Bail"],
        "Pending_Days": [30,150,240,90,110,10],
        "Deadline_Days_Left": [3,20,5,40,2,60],
        "Previous_Motions": [1,2,3,1,0,0],
        "Short_Description": [
            "Bail petition urgent",
            "Custody appeal pending",
            "Fraud investigation",
            "Contract dispute",
            "Title correction needed",
            "Bail - new application"
        ]
    })

df = pd.read_csv(uploaded) if uploaded else load_data()

# -------------------- URGENCY --------------------
def calc_urgency(row):
    score = 0
    if row["Case_Type"] in ["Bail","Custody","Fraud"]:
        score += 40
    if row["Pending_Days"] > 100: score += 15
    if row["Deadline_Days_Left"] < 10: score += 25
    if row["Previous_Motions"] > 2: score += 10
    return min(score, 100)

df["Urgency_Score"] = df.apply(calc_urgency, axis=1)
df["Urgency_Level"] = df["Urgency_Score"].apply(
    lambda x: "High" if x >= 70 else ("Medium" if x >= 40 else "Low")
)

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.markdown('<div class="title-gradient">⚖️ AI-Powered Justice System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Prioritize court cases with intelligence and style.</div>', unsafe_allow_html=True)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="metric-card"><h3>Total Cases</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><h3>High Urgency</h3><h2>{int((df["Urgency_Level"]=="High").sum())}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><h3>Average Score</h3><h2>{round(df["Urgency_Score"].mean(),1)}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Prioritized Cases")
    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)
    for i, r in df_sorted.iterrows():
        st.markdown(f"""
        <div class="case-card {r['Urgency_Level'].lower()}">
            <b>{r['Case_ID']} — {r['Case_Type']}</b><br>
            <span style='font-size:14px'>{r['Short_Description']}</span>
            <div class="progress-bar">
                <div class="progress-fill" style="width:{r['Urgency_Score']}%"></div>
            </div>
            <span style='font-size:12px;opacity:0.7'>Deadline: {r['Deadline_Days_Left']} days | Previous Motions: {r['Previous_Motions']}</span>
        </div>
        """, unsafe_allow_html=True)

# -------------------- CALENDAR VIEW --------------------
elif page == "Calendar View":
    st.markdown('<div class="title-gradient">📅 Case Calendar View</div>', unsafe_allow_html=True)
    st.write("Visualized scheduled cases with color-coded urgency bars.")

    start = datetime.today()
    days = [start + timedelta(days=i) for i in range(7)]
    schedule = {d.strftime("%a %d %b"): [] for d in days}
    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)

    day_index = 0
    for _, row in df_sorted.iterrows():
        day_key = list(schedule.keys())[day_index % len(days)]
        schedule[day_key].append(row)
        day_index += 1

    cols = st.columns(len(schedule))
    for i, (day, cases) in enumerate(schedule.items()):
        with cols[i]:
            st.markdown(f'<div class="day-card"><h4>{day}</h4></div>', unsafe_allow_html=True)
            for r in cases:
                level_class = r["Urgency_Level"].lower()
                st.markdown(f"""
                <div class="case-card {level_class}">
                    <b>{r['Case_ID']}</b> — {r['Case_Type']}<br>
                    <span style='font-size:13px'>{r['Short_Description']}</span>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:{r['Urgency_Score']}%"></div>
                    </div>
                    <span style='font-size:11px;opacity:0.7'>Score: {r['Urgency_Score']} | Deadline: {r['Deadline_Days_Left']} days</span>
                </div>
                """, unsafe_allow_html=True)

    st.success("Calendar simulation ready — each card represents a scheduled case.")
