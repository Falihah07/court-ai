import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="AI-Powered Justice System",
    layout="wide"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
:root {
  --primary: #2563eb;
  --bg-light: #f7faff;
  --bg-dark: #0d1117;
  --text-light: #111;
  --text-dark: #f7faff;
}

/* App container */
[data-testid="stAppViewContainer"] {
  background: var(--bg-light);
  color: var(--text-light);
  font-family: 'Segoe UI', sans-serif;
  transition: all 0.3s ease;
}
@media (prefers-color-scheme: dark) {
  [data-testid="stAppViewContainer"] {
    background: var(--bg-dark);
    color: var(--text-dark);
  }
}

/* Sidebar */
[data-testid="stSidebar"] {
  background-color: #eef4ff;
  border-right: 2px solid #c3dafc;
}
@media (prefers-color-scheme: dark) {
  [data-testid="stSidebar"] {
    background-color: #161b22;
    border-color: #30363d;
  }
}

/* Gradient glowing title */
.glow-title {
  font-size: 2.8rem;
  font-weight: 800;
  text-align: center;
  background: linear-gradient(90deg, #2563eb, #9333ea, #14b8a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: glow 5s ease-in-out infinite;
}
@keyframes glow {
  0%,100% { text-shadow: 0 0 10px #2563eb; }
  50% { text-shadow: 0 0 20px #9333ea; }
}

/* Case cards */
.case-card {
  background-color: #ffffff;
  border-left: 5px solid var(--primary);
  padding: 15px;
  margin-bottom: 12px;
  border-radius: 14px;
  box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.case-card:hover {
  transform: translateY(-4px);
  box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
}

/* Urgency colors */
.high {border-left-color:#ef4444;}
.medium {border-left-color:#f59e0b;}
.low {border-left-color:#10b981;}
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
        "Case_ID": ["C101","C102","C103","C104"],
        "Case_Type": ["Fraud","Custody","Contract","Bail"],
        "Pending_Days": [240,150,90,30],
        "Deadline_Days_Left": [5,20,40,15],
        "Previous_Motions": [3,2,1,0],
        "Short_Description": [
            "Fraud case – immediate attention",
            "Custody appeal pending",
            "Contract dispute under review",
            "Bail petition new application"
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
df["Urgency_Level"] = df["Urgency_Score"].apply(
    lambda x: "High" if x >= 70 else ("Medium" if x >= 40 else "Low")
)

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.markdown("<h1 class='glow-title'>AI-Powered Justice System ⚖️</h1>", unsafe_allow_html=True)
    st.write("A smart assistant that prioritizes court cases based on urgency and deadlines.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", len(df))
    col2.metric("High Urgency", int((df["Urgency_Level"]=="High").sum()))
    col3.metric("Average Score", round(df["Urgency_Score"].mean(), 1))

    st.markdown("---")
    st.subheader("Prioritized Case List")

    # 🔥 Case cards visual (your beautiful UI restored)
    for _, r in df.sort_values("Urgency_Score", ascending=False).iterrows():
        level_class = "high" if r["Urgency_Level"]=="High" else (
                      "medium" if r["Urgency_Level"]=="Medium" else "low")
        st.markdown(f"""
        <div class="case-card {level_class}">
            <b>{r["Case_ID"]}</b> — {r["Case_Type"]}<br>
            <span style='font-size:13px'>{r["Short_Description"]}</span><br>
            <span style='font-size:12px;opacity:0.75'>
                Score: {r["Urgency_Score"]} | Deadline: {r["Deadline_Days_Left"]} days | Motions: {r["Previous_Motions"]}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Urgency Summary")
    st.bar_chart(df["Urgency_Level"].value_counts())

    st.caption("Switch to the 'Calendar View' from the sidebar to visualize scheduled cases.")

# -------------------- CALENDAR VIEW --------------------
elif page == "Calendar View":
    st.markdown("<h1 class='glow-title'>Case Calendar View 📅</h1>", unsafe_allow_html=True)
    st.write("Color-coded display of prioritized cases across upcoming days.")

    start = datetime.today()
    days = [start + timedelta(days=i) for i in range(7)]
    schedule = {d.strftime("%a %d %b"): [] for d in days}
    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)

    # Distribute cases
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
                    <span style='font-size:11px;opacity:0.7'>
                        Score: {r["Urgency_Score"]} | Deadline: {r["Deadline_Days_Left"]} days
                    </span>
                </div>
                """, unsafe_allow_html=True)

    st.success("Calendar simulation ready — each card represents a scheduled case.")
    st.caption("Return to Dashboard using sidebar navigation.")
