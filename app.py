import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="AI-Powered Justice System",
    layout="wide",
    page_icon="⚖️"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
/* Background */
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #f0f6ff, #ffffff);
  color: #0a0a0a !important;
  font-family: 'Segoe UI', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background-color: #e9f2ff;
  border-right: 2px solid #c3dafc;
}

/* Titles and Headers */
h1, h2, h3 {
  color: #0f172a;
  font-weight: 700;
}

/* Metrics */
div[data-testid="stMetricValue"] {
  color: #1e3a8a !important;
}

/* Buttons */
button[kind="primary"] {
  background-color: #2563eb !important;
  color: white !important;
  border-radius: 10px !important;
}

/* Cards */
.case-card {
  background-color: #e8f0ff;
  border-left: 5px solid #2563eb;
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 10px;
  box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
}

/* High / Medium / Low urgency colors */
.high {
  background-color: #ffebee;
  border-left: 5px solid #ef4444;
}
.medium {
  background-color: #fff7ed;
  border-left: 5px solid #f59e0b;
}
.low {
  background-color: #ecfdf5;
  border-left: 5px solid #10b981;
}

/* Table */
[data-testid="stDataFrame"] {
  background-color: #ffffff !important;
  border-radius: 10px;
}

/* Chart section */
.block-container {
  padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR NAV --------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3595/3595455.png", width=60)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["🏛 Dashboard", "📅 Calendar View"])
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("📂 Upload Case CSV", type=["csv"])

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

# -------------------- URGENCY SCORING --------------------
def calc_urgency(row):
    score = 0
    if row["Case_Type"] in ["Bail","Custody","Fraud"]:
        score += 40
    if row["Pending_Days"] > 100: score += 15
    if row["Deadline_Days_Left"] < 10: score += 25
    if row["Previous_Motions"] > 2: score += 10
    return min(score, 100)

df["Urgency_Score"] = df.apply(calc_urgency, axis=1)
df["Urgency_Level"] = df["Urgency_Score"].apply(lambda x: "High" if x >= 70 else ("Medium" if x >= 40 else "Low"))

# -------------------- DASHBOARD PAGE --------------------
if page == "🏛 Dashboard":
    st.title("⚖️ AI-Powered Justice System")
    st.write("A smart assistant that prioritizes court cases based on urgency and deadlines.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", len(df))
    col2.metric("High Urgency", int((df["Urgency_Level"]=="High").sum()))
    col3.metric("Average Score", round(df["Urgency_Score"].mean(), 1))

    st.markdown("---")
    st.subheader("📋 Prioritized Case List")
    st.dataframe(df.sort_values("Urgency_Score", ascending=False), use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Urgency Summary")
    st.bar_chart(df["Urgency_Level"].value_counts())

    st.info("Switch to **📅 Calendar View** from the sidebar to visualize scheduled cases.")

# -------------------- CALENDAR PAGE --------------------
elif page == "📅 Calendar View":
    st.title("📅 Case Calendar View")
    st.write("Color-coded view of prioritized cases over upcoming days.")

    start = datetime.today()
    days = [start + timedelta(days=i) for i in range(7)]
    schedule = {d.strftime("%a %d %b"): [] for d in days}
    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)

    # distribute cases across days (demo scheduler)
    day_index = 0
    for _, row in df_sorted.iterrows():
        day_key = list(schedule.keys())[day_index % len(days)]
        schedule[day_key].append(row)
        day_index += 1

    cols = st.columns(len(schedule))
    for i, (day, cases) in enumerate(schedule.items()):
        with cols[i]:
            st.markdown(f"### {day}")
            if not cases:
                st.write("_No cases scheduled_")
            for r in cases:
                level_class = "high" if r["Urgency_Level"]=="High" else (
                              "medium" if r["Urgency_Level"]=="Medium" else "low")
                st.markdown(f"""
                <div class="case-card {level_class}">
                    <b>{r["Case_ID"]}</b> — {r["Case_Type"]}<br>
                    <span style='font-size:13px'>{r["Short_Description"]}</span><br>
                    <span style='font-size:11px;opacity:0.7'>Score: {r["Urgency_Score"]} | Deadline: {r["Deadline_Days_Left"]} days</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.success("✅ Calendar simulation ready — each card represents a scheduled case.")
    st.caption("Back to Dashboard → use sidebar navigation.")
