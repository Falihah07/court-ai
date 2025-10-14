# app.py — restored styled UI + robust CSV mapping + correct calendar split
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import math

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="AI-Powered Justice System",
    layout="wide"
)

# -------------------- SECURITY --------------------
# NOTE: In production, store key securely. For demo, generate each run.
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(dataframe):
    csv_bytes = dataframe.to_csv(index=False).encode()
    return cipher.encrypt(csv_bytes)

def decrypt_data(encrypted_data):
    decrypted = cipher.decrypt(encrypted_data).decode()
    from io import StringIO
    return pd.read_csv(StringIO(decrypted))

# -------------------- CUSTOM CSS (restore original look) --------------------
st.markdown("""
<style>
body, .stApp, .stSidebar { font-family: 'Segoe UI', sans-serif; color: #fff; }
.title-gradient {
    background: linear-gradient(90deg, #2563eb, #6b21a8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 40px;
    font-weight: 700;
}
.subtitle { font-size: 18px; color: #9ca3af; margin-bottom: 20px; }

.metric-card {
    background-color: #111827;
    border-radius: 15px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 6px 16px rgba(0,0,0,0.6);
    transition: transform 0.2s;
}
.metric-card h3 { color: #e5e7eb; font-weight: 600; margin-bottom: 8px; }
.metric-card h2 { color: #fff; font-size: 34px; margin: 0; }

.case-card {
    padding: 18px;
    margin-bottom: 18px;
    border-radius: 12px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.6);
    border-left: 6px solid;
    background-color: #0f1724;
    transition: transform 0.15s, box-shadow 0.15s;
}
.case-card:hover {
    transform: translateY(-2px);
    box-shadow: 0px 10px 22px rgba(0,0,0,0.7);
}

.high {border-left-color:#ef4444;}
.medium {border-left-color:#f59e0b;}
.low {border-left-color:#10b981;}

.progress-bar { height: 8px; border-radius: 6px; background-color: #1f2937; margin-top: 12px; margin-bottom: 6px; }
.progress-fill { height: 8px; border-radius: 6px; background: linear-gradient(90deg, #2563eb, #6b21a8); }

.day-card {
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 12px;
    background-color: rgba(255,255,255,0.03);
    box-shadow: 0px 4px 10px rgba(0,0,0,0.6);
    transition: transform 0.12s;
}
.day-header {
    padding: 10px;
    border-radius: 10px;
    color: #0f1724;
    font-weight: 700;
}

.expander .streamlit-expanderHeader { color: #e5e7eb !important; }

.stSidebar .css-1d391kg { color: #d1d5db; }  /* sidebar text */
.stButton>button { background-color: #111827; color: #fff; }

@media (prefers-color-scheme: light) {
    body, .stApp, .stSidebar { color: #111827; }
    .metric-card, .case-card, .day-card { background-color: #ffffff !important; color: #111827 !important; box-shadow: 0px 4px 12px rgba(0,0,0,0.08); }
    .progress-bar { background-color: #e6e7eb; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["Dashboard", "Calendar View"])
st.sidebar.markdown("---")

# show displayed upload limit (user requested 1 GB display)
MAX_UPLOAD_GB = 1
uploaded = st.sidebar.file_uploader(f"Upload Case CSV (display limit: {MAX_UPLOAD_GB} GB)", type=["csv"])

# -------------------- DATA LOADING (robust) --------------------
@st.cache_data
def load_local_csv(path="cases.csv"):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

# Decide data source
if uploaded:
    # convert uploaded to DataFrame
    try:
        df = pd.read_csv(uploaded)
        st.sidebar.success(f"✅ {len(df)} cases loaded successfully (uploaded)")
    except Exception as e:
        st.sidebar.error("⚠️ Could not read CSV. Check the format.")
        st.stop()
else:
    df = load_local_csv("cases.csv")
    if df.empty:
        st.sidebar.warning("No local cases.csv found or file empty.")
    else:
        st.sidebar.info("📂 Using default internal dataset (expected ~500 cases).")

# encrypt/decrypt roundtrip (keeps original behavior & simulates privacy)
if not df.empty:
    encrypted_data = encrypt_data(df)
    df = decrypt_data(encrypted_data)

# -------------------- NORMALIZE COLUMNS (robust mapping) --------------------
# Your CSVs varied across versions. Normalize common names to canonical keys we use below.
# Possible column names we might encounter and map them to canonical names:
col_map_candidates = {
    'Case_ID': ['Case_ID','CaseId','case_id','caseid','Case Number','Case_Number','CaseNumber'],
    'Case_Name': ['Case_Name','CaseName','Name','case_name'],
    'Case_Type': ['Case_Type','Type','case_type'],
    'Pending_Days': ['Pending_Days','PendingDays','pending_days'],
    'Deadline_Days_Left': ['Deadline_Days_Left','Days_Left','DeadlineDaysLeft','deadline_days_left'],
    'Previous_Motions': ['Previous_Motions','Prev_Motions','PreviousMotions','previous_motions'],
    'Short_Description': ['Short_Description','ShortDescription','Description','ShortDesc','short_description'],
    'Urgency': ['Urgency','Urgency_Level','Urgency_Level','urgency']
}

# Create canonical columns in df if present in any of the candidate names
if not df.empty:
    df_cols_lower = {c.lower(): c for c in df.columns}
    def find_existing(possible_names):
        for n in possible_names:
            if n in df.columns:
                return n
            if n.lower() in df_cols_lower:
                return df_cols_lower[n.lower()]
        return None

    for canonical, cand_list in col_map_candidates.items():
        found = find_existing(cand_list)
        if found:
            df.rename(columns={found: canonical}, inplace=True)

# Ensure required columns exist (create reasonable defaults)
if not df.empty:
    if 'Case_ID' not in df.columns:
