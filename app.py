import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Case Dashboard", layout="wide")

MAX_UPLOAD_GB = 1

# -------------------- LOAD DATA --------------------
def load_cases():
    try:
        df = pd.read_csv("cases.csv")
        df.dropna(how='all', inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading cases.csv: {e}")
        return pd.DataFrame()

cases_df = load_cases()

# -------------------- SIDEBAR --------------------
page = st.sidebar.radio("Navigation", ["Dashboard", "Calendar View"])

# -------------------- TITLE --------------------
st.markdown('<h1 style="text-align:center; color:black;">⚖️ Case Management Dashboard</h1>', unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.markdown('<div class="title-gradient">📋 All Case Records</div>', unsafe_allow_html=True)

    if not cases_df.empty:
        total_cases = len(cases_df)
        st.success(f"Total Cases Loaded: {total_cases}")

        for i, row in cases_df.iterrows():
            urgency = str(row.get("Urgency", "")).strip().lower()
            color = {
                "high": "#ffcccc",
                "medium": "#fff4cc",
                "low": "#ccffcc"
            }.get(urgency, "#e6e6fa")

            header = f"{row.get('Case_ID', 'N/A')} | {row.get('Case_Type', 'Unknown')}"

            with st.expander(header):
                st.markdown(f'<div style="background-color:{color}; padding:5px; border-radius:5px;">Urgency: {row.get('Urgency', 'N/A')} </div>', unsafe_allow_html=True)
                st.write({
                    'Case Name': row.get('Case_Name', 'N/A'),
                    'Court': row.get('Court', 'N/A'),
                    'Judge': row.get('Judge', 'N/A'),
                    'Status': row.get('Status', 'N/A'),
                    'Urgency': row.get('Urgency', 'N/A'),
                    'Date Filed': row.get('Date_Filed', 'N/A'),
                    'Petitioner': row.get('Petitioner', 'N/A'),
                    'Respondent': row.get('Respondent', 'N/A'),
                    'Lawyer': row.get('Lawyer', 'N/A'),
                    'Hearing Date': row.get('Hearing_Date', 'N/A'),
                    'Verdict Date': row.get('Verdict_Date', 'N/A'),
                    'Description': row.get('Description', 'N/A')
                })
    else:
        st.warning("No cases found in cases.csv.")

# -------------------- CALENDAR VIEW --------------------
elif page == "Calendar View":
    st.markdown('<div class="title-gradient">📅 Weekly Case Calendar</div>', unsafe_allow_html=True)

    if not cases_df.empty:
        total_cases = len(cases_df)
        st.success(f"Total Cases Loaded: {total_cases}")

        # Get next 5 weekdays (Mon–Fri)
        start_date = datetime.today()
        weekdays = []
        while len(weekdays) < 5:
            if start_date.weekday() < 5:  # 0 = Monday, 4 = Friday
                weekdays.append(start_date)
            start_date += timedelta(days=1)

        # Split cases evenly (100 per day)
        cases_per_day = total_cases // 5
        day_splits = [cases_df.iloc[i*cases_per_day:(i+1)*cases_per_day] for i in range(5)]

        pastel_colors = ["#e3f2fd", "#e8f5e9", "#fff3e0", "#f3e5f5", "#e0f7fa"]

        for idx, day in enumerate(weekdays):
            day_label = day.strftime("%A, %d %B %Y")
            st.markdown(f'<h3 style="background-color:{pastel_colors[idx]}; padding:10px; border-radius:10px; color:black;">{day_label}</h3>', unsafe_allow_html=True)

            daily_cases = day_splits[idx]
            if daily_cases.empty:
                st.write("No cases assigned for this day.")
            else:
                for i, row in daily_cases.iterrows():
                    urgency = str(row.get("Urgency", "")).strip().lower()
                    color = {
                        "high": "#ffcccc",
                        "medium": "#fff4cc",
                        "low": "#ccffcc"
                    }.get(urgency, "#e6e6fa")

                    header = f"{row.get('Case_ID', 'N/A')} | {row.get('Case_Type', 'Unknown')}"

                    with st.expander(header):
                        st.markdown(f'<div style="background-color:{color}; padding:5px; border-radius:5px;">Urgency: {row.get('Urgency', 'N/A')} </div>', unsafe_allow_html=True)
                        st.write({
                            'Case Name': row.get('Case_Name', 'N/A'),
                            'Court': row.get('Court', 'N/A'),
                            'Judge': row.get('Judge', 'N/A'),
                            'Status': row.get('Status', 'N/A'),
                            'Urgency': row.get('Urgency', 'N/A'),
                            'Date Filed': row.get('Date_Filed', 'N/A'),
                            'Petitioner': row.get('Petitioner', 'N/A'),
                            'Respondent': row.get('Respondent', 'N/A'),
                            'Lawyer': row.get('Lawyer', 'N/A'),
                            'Hearing Date': row.get('Hearing_Date', 'N/A'),
                            'Verdict Date': row.get('Verdict_Date', 'N/A'),
                            'Description': row.get('Description', 'N/A')
                        })
    else:
        st.warning("No data to display in Calendar View.")

# -------------------- FOOTER --------------------
st.markdown('<hr><p style="text-align:center; color:grey;">© 2025 Case Dashboard | Built with Streamlit</p>', unsafe_allow_html=True)
