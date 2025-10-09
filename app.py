import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Justice Assistant", layout="wide")

st.title("⚖️ AI-Powered Justice System")
st.write("Smart assistant that prioritizes court cases by urgency.")

uploaded_file = st.file_uploader("📂 Upload Case Data (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Using sample data for demo")
    df = pd.DataFrame({
        "Case_ID": ["C101","C102","C103","C104"],
        "Case_Type": ["Bail","Custody","Fraud","Land Dispute"],
        "Pending_Days": [30,120,240,90],
        "Deadline_Days_Left": [3,10,60,20],
        "Previous_Motions": [1,2,3,1]
    })

def calc_urgency(row):
    score = 0
    if row["Case_Type"] in ["Bail","Custody","Fraud"]:
        score += 40
    if row["Pending_Days"] > 100:
        score += 20
    if row["Deadline_Days_Left"] < 10:
        score += 25
    if row["Previous_Motions"] > 2:
        score += 15
    return min(score, 100)

df["Urgency_Score"] = df.apply(calc_urgency, axis=1)
df["Urgency_Level"] = df["Urgency_Score"].apply(lambda x: "High" if x>=70 else "Low")

st.subheader("📋 Prioritized Case List")
st.dataframe(df.sort_values("Urgency_Score", ascending=False), use_container_width=True)

st.subheader("📊 Urgency Summary")
st.bar_chart(df["Urgency_Level"].value_counts())

st.caption("Prototype by Team Justice League — HackElite 2025")
