import streamlit as st
import pandas as pd

st.set_page_config(page_title="Court Case Prioritization – AI Assistant", layout="wide")

# --- PAGE HEADER ---
st.title("⚖️ Court Case Prioritization – AI Assistant")
st.write("Analyze and prioritize court cases based on urgency factors like deadlines, motions, and case type.")

st.markdown("---")

# --- LAYOUT: FORM + ANALYSIS ---
col1, col2 = st.columns(2, gap="large")

# ----- LEFT SIDE: INPUT FORM -----
with col1:
    st.subheader("📄 Enter Case Details")

    case_id = st.text_input("Case ID", placeholder="e.g., C101")
    case_type = st.selectbox("Case Type", ["Select", "Bail", "Custody", "Fraud", "Contract", "Land Dispute"])
    filing_date = st.date_input("Filing Date")
    parties = st.number_input("Parties Involved", min_value=1, step=1, value=2)
    previous_motions = st.number_input("Previous Motions", min_value=0, step=1)
    deadline_days = st.number_input("Days Left for Deadline", min_value=0, step=1)
    summary = st.text_area("Brief Case Summary", placeholder="Provide short details...")

    analyze = st.button("🔍 Analyze Case")

# ----- RIGHT SIDE: ANALYSIS RESULT -----
with col2:
    st.subheader("📊 Analysis Results")

    if analyze:
        urgency_score = 0
        reasons = []

        if case_type in ["Bail", "Custody", "Fraud"]:
            urgency_score += 40
            reasons.append("Critical case type (e.g., Bail, Custody, Fraud)")

        if deadline_days < 10:
            urgency_score += 25
            reasons.append("Tight deadline (<10 days remaining)")

        if previous_motions > 2:
            urgency_score += 15
            reasons.append(f"High motion count ({previous_motions})")

        if urgency_score == 0:
            urgency_score += 10
            reasons.append("No specific urgency detected — normal priority")

        urgency_label = "High" if urgency_score >= 70 else ("Medium" if urgency_score >= 40 else "Low")

        # Display results
        st.markdown(f"### Prioritization Score: **{urgency_score}** / 100")
        st.markdown(f"**Predicted Urgency:** :red[{urgency_label}]")

        st.markdown("#### 🔎 Key Factors Considered:")
        for r in reasons:
            st.write(f"- {r}")

        st.markdown("---")
        st.success("✅ Recommendation: Approve prioritization for judge review.")
    else:
        st.info("Fill in the case details and click *Analyze Case* to generate the urgency score.")

st.markdown("---")
st.caption("Developed by Team Justice League — HackElite 2025")
