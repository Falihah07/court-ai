import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.markdown("""
<style>
/* Main background */
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg,#f9fcff,#e9f2ff);
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: #f3f7ff;
  border-right: 2px solid #dbe4ff;
}

/* Title and headers */
h1, h2, h3 {
  color: #1e3a8a;
}

/* Case cards */
div[style*="background:#ff6b6b"], 
div[style*="background:#ffa94d"],
div[style*="background:#a3e635"] {
  box-shadow: 0 3px 8px rgba(0,0,0,0.15);
}

/* Buttons */
button[kind="primary"] {
  background-color:#2563eb !important;
  color:white !important;
  border-radius:10px !important;
}
</style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="AI-Powered Justice System", layout="wide")

# ---- Sidebar navigation ----
st.sidebar.title("⚖️ Navigation")
page = st.sidebar.radio("Go to:", ["Dashboard", "Calendar 📅"])

# ---- Load / sample data ----
def load_data():
    return pd.DataFrame({
        "Case_ID": ["C101","C102","C103","C104","C105","C106"],
        "Case_Type": ["Bail","Custody","Fraud","Contract","Land Dispute","Bail"],
        "Pending_Days": [30,150,240,90,110,10],
        "Deadline_Days_Left": [3,20,5,40,2,60],
        "Previous_Motions": [1,2,3,1,0,0],
        "Short_Description": [
            "Bail petition urgent","Custody appeal","Investigation pending",
            "Contract dispute","Title correction","Bail – new"
        ]
    })

uploaded = st.sidebar.file_uploader("📂 Upload Case CSV", type=["csv"])
df = pd.read_csv(uploaded) if uploaded else load_data()

# ---- Urgency scoring ----
def calc_urgency(row):
    score = 0
    if row["Case_Type"] in ["Bail","Custody","Fraud"]:
        score += 40
    if row["Pending_Days"] > 100: score += 15
    if row["Deadline_Days_Left"] < 10: score += 25
    if row["Previous_Motions"] > 2: score += 10
    return min(score,100)

df["Urgency_Score"] = df.apply(calc_urgency, axis=1)
df["Urgency_Level"] = df["Urgency_Score"].apply(
    lambda x: "High" if x>=70 else ("Medium" if x>=40 else "Low")
)

# ===========================
# DASHBOARD PAGE
# ===========================
if page == "Dashboard":
    st.title("⚖️ AI-Powered Justice System – Dashboard")
    st.write("Automatically prioritizes cases based on urgency factors.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", len(df))
    col2.metric("High Urgency", int((df["Urgency_Level"]=="High").sum()))
    col3.metric("Avg Score", round(df["Urgency_Score"].mean(),1))

    st.subheader("📋 Prioritized Case List")
    st.dataframe(df.sort_values("Urgency_Score", ascending=False), use_container_width=True)

    st.subheader("📊 Urgency Summary")
    st.bar_chart(df["Urgency_Level"].value_counts())

    st.info("Use the sidebar to open the Calendar 📅 view.")

# ===========================
# CALENDAR PAGE
# ===========================
else:
    st.title("📅 Case Calendar View")
    st.write("Displays urgent and scheduled cases over upcoming days.")

    # create schedule: highest urgency first over next 7 days
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
    for i,(day, cases) in enumerate(schedule.items()):
        with cols[i]:
            st.markdown(f"**{day}**")
            if not cases:
                st.write("_No cases_")
            for r in cases:
                color = "#ff6b6b" if r["Urgency_Level"]=="High" else (
                        "#ffa94d" if r["Urgency_Level"]=="Medium" else "#a3e635")
                st.markdown(f"""
                <div style='background:{color};padding:6px;border-radius:6px;margin-bottom:5px;color:#000'>
                    <b>{r["Case_ID"]}</b> – {r["Case_Type"]}<br>
                    <span style='font-size:12px'>{r["Short_Description"]}</span><br>
                    <span style='font-size:11px'>Score: {r["Urgency_Score"]}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Back to Dashboard → use sidebar switch.")
