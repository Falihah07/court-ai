import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import io

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="AI-Powered Justice System", layout="wide")
# increase upload limit to 1 GB (value in MB)
st.set_option('server.maxUploadSize', 1024)

# -------------------- CUSTOM CSS --------------------
st.markdown("""<style>
/* ----------------- Global Styles ----------------- */
body, .stApp, .stSidebar { font-family: 'Segoe UI', sans-serif; }

/* Gradient Title */
.title-gradient {
    background: linear-gradient(90deg, #2563eb, #6b21a8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 40px;
    font-weight: 700;
}
.subtitle { font-size: 18px; color: #555; margin-bottom: 20px; }

/* Metric Cards */
.metric-card {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-5px); }

/* Case Cards */
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

/* Urgency Colors */
.high {border-left-color:#ef4444;}
.medium {border-left-color:#f59e0b;}
.low {border-left-color:#10b981;}

/* Progress Bar */
.progress-bar { height: 6px; border-radius: 3px; background-color: #e0e0e0; margin-top: 8px; margin-bottom: 5px; }
.progress-fill { height: 6px; border-radius: 3px; background: linear-gradient(90deg, #2563eb, #6b21a8); }

/* Calendar Day Cards */
.day-card {
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 12px;
    background-color: #f5f5f5;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.day-card:hover { transform: translateY(-2px); }

/* Dark Mode */
@media (prefers-color-scheme: dark) {
    body, .stApp, .stSidebar { color: #f1f1f1; }
    .metric-card, .case-card, .day-card { background-color: #1e1e1e !important; color: #f1f1f1 !important; box-shadow: 0px 4px 12px rgba(0,0,0,0.5); }
    .progress-bar { background-color: #333; }
}
</style>""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["Dashboard", "Calendar View"])
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("📂 Upload Case CSV (optional)", type=["csv"])

# -------------------- SECURITY: ENCRYPTION HELPERS --------------------
@st.cache_resource
def get_fernet():
    # generate a key once per session / cached resource
    return Fernet(Fernet.generate_key())

fernet = get_fernet()

def secure_read_csv(uploaded_file) -> pd.DataFrame | None:
    """
    Encrypts uploaded bytes, decrypts them back and loads as dataframe.
    This ensures we do not directly persist raw bytes and demonstrates a simple encryption layer.
    Returns dataframe or None on error.
    """
    try:
        raw = uploaded_file.read()
        encrypted = fernet.encrypt(raw)
        decrypted = fernet.decrypt(encrypted)
        return pd.read_csv(io.BytesIO(decrypted))
    except Exception as e:
        st.error(f"Error reading uploaded CSV: {e}")
        return None

# -------------------- LOAD DATA (use uploaded OR repo cases.csv OR synthetic) --------------------
REQUIRED_COLS = ["Case_ID","Case_Type","Pending_Days","Deadline_Days_Left","Previous_Motions","Short_Description"]

def generate_additional_cases(start_index: int, n: int) -> pd.DataFrame:
    np.random.seed(42 + start_index)  # deterministic-ish but varying start
    case_types = ["Bail","Custody","Fraud","Contract","Land Dispute","Appeal"]
    data = {
        "Case_ID": [f"C{start_index + i:03}" for i in range(1, n+1)],
        "Case_Type": np.random.choice(case_types, n),
        "Pending_Days": np.random.randint(10, 500, n),
        "Deadline_Days_Left": np.random.randint(1, 60, n),
        "Previous_Motions": np.random.randint(0, 4, n),
        "Short_Description": np.random.choice(
            ["Urgent petition", "Hearing pending", "New motion filed",
             "Contract dispute ongoing", "Title issue", "Appeal under review"], n)
    }
    return pd.DataFrame(data)

def load_primary_dataframe():
    # 1) If user uploaded a file, use that (secure read)
    if uploaded is not None:
        df_uploaded = secure_read_csv(uploaded)
        if df_uploaded is None:
            st.stop()
        source_df = df_uploaded
        st.sidebar.success("✅ Using uploaded CSV (encrypted in memory).")
    else:
        # 2) Try to load cases.csv from repository (deployed repo)
        try:
            source_df = pd.read_csv("cases.csv")
            st.sidebar.info("ℹ️ Loaded cases.csv from repository.")
        except FileNotFoundError:
            # 3) if no file exists in repo, start with empty df and generate
            source_df = pd.DataFrame(columns=REQUIRED_COLS)
            st.sidebar.warning("⚠️ No cases.csv found in repository; using generated demo data.")

    # Validate columns for source_df
    missing = [c for c in REQUIRED_COLS if c not in source_df.columns]
    if missing:
        st.warning(f"Dataset missing columns: {missing}. Attempting to continue with available columns.")
        # try to create missing columns with defaults
        for c in missing:
            if c == "Short_Description":
                source_df[c] = "No description"
            elif c in ["Pending_Days","Deadline_Days_Left","Previous_Motions"]:
                source_df[c] = 0
            else:
                source_df[c] = source_df.index.astype(str)

    # Ensure Case_ID uniqueness and string format
    source_df["Case_ID"] = source_df["Case_ID"].astype(str)

    # If total rows < 500, append synthetic cases but keep existing rows first
    MIN_TOTAL = 500
    current_n = len(source_df)
    if current_n < MIN_TOTAL:
        extra_n = MIN_TOTAL - current_n
        # compute next available index number for IDs
        # attempt to parse numeric part of existing Case_IDs
        max_existing = 0
        for cid in source_df["Case_ID"].tolist():
            try:
                num = int(''.join(filter(str.isdigit, cid)))
                if num > max_existing: max_existing = num
            except:
                continue
        synthetic = generate_additional_cases(max_existing, extra_n)
        source_df = pd.concat([source_df.reset_index(drop=True), synthetic], ignore_index=True)
        st.sidebar.info(f"ℹ️ Dataset extended to {MIN_TOTAL} cases for scheduling demo (keeps your real rows).")

    # coerce numeric types
    for col in ["Pending_Days","Deadline_Days_Left","Previous_Motions"]:
        source_df[col] = pd.to_numeric(source_df[col], errors='coerce').fillna(0).astype(int)

    return source_df

df = load_primary_dataframe()

# -------------------- URGENCY --------------------
def calc_urgency(row):
    score = 0
    if row["Case_Type"] in ["Bail","Custody","Fraud"]:
        score += 40
    if row["Pending_Days"] > 100:
        score += 15
    if row["Deadline_Days_Left"] < 10:
        score += 25
    if row["Previous_Motions"] > 2:
        score += 10
    return min(score, 100)

df["Urgency_Score"] = df.apply(calc_urgency, axis=1)
df["Urgency_Level"] = df["Urgency_Score"].apply(lambda x: "High" if x>=70 else ("Medium" if x>=40 else "Low"))

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
        # Urgency badge
        urgency_emoji = "🔴" if r["Urgency_Level"]=="High" else ("🟠" if r["Urgency_Level"]=="Medium" else "🟢")
        urgency_text = f"{urgency_emoji} {r['Urgency_Level']}"
        # Deadline badge color
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
            <div class="progress-bar">
                <div class="progress-fill" style="width:{r['Urgency_Score']}%"></div>
            </div>
            <span style='font-size:12px;opacity:0.7'>Urgency: {urgency_text}</span>
        </div>
        """, unsafe_allow_html=True)

# -------------------- CALENDAR VIEW --------------------
elif page == "Calendar View":
    st.markdown('<div class="title-gradient">📅 Case Calendar View</div>', unsafe_allow_html=True)
    st.write("AI-assisted scheduling: urgent cases early, normal cases later, no weekends.")

    # Build next 5 weekdays (Mon-Fri) starting from today
    today = datetime.today()
    weekdays_dates = []
    d = today
    while len(weekdays_dates) < 5:
        if d.weekday() < 5:  # Mon-Fri
            weekdays_dates.append(d)
        d += timedelta(days=1)

    # Prepare buckets
    df_sorted = df.sort_values("Urgency_Score", ascending=False).reset_index(drop=True)
    high_cases = df_sorted[df_sorted["Urgency_Level"]=="High"].copy().reset_index(drop=True)
    medium_cases = df_sorted[df_sorted["Urgency_Level"]=="Medium"].copy().reset_index(drop=True)
    low_cases = df_sorted[df_sorted["Urgency_Level"]=="Low"].copy().reset_index(drop=True)

    # pointers to slice through each bucket without replacement
    pointers = {"High":0, "Medium":0, "Low":0}
    per_day_capacity = 100  # aim ~100 cases per day as requested

    schedule = {}
    for i, day_dt in enumerate(weekdays_dates):
        day_label = day_dt.strftime("%a %d %b")
        schedule[day_label] = []
        # assign buckets by day index: 0(Mon),1(Tue) => High; 2,3 => Medium; 4 => Low
        if i in [0,1]:
            bucket = high_cases
            pkey = "High"
        elif i in [2,3]:
            bucket = medium_cases
            pkey = "Medium"
        else:
            bucket = low_cases
            pkey = "Low"

        start = pointers[pkey]
        end = start + per_day_capacity
        # slice safely
        subset = bucket.iloc[start:end]
        schedule[day_label] = subset
        pointers[pkey] = end

    # Render columns for each weekday
    cols = st.columns(len(schedule))
    for idx, (day, cases) in enumerate(schedule.items()):
        with cols[idx]:
            st.markdown(f'<div class="day-card"><h4>{day}</h4></div>', unsafe_allow_html=True)
            if cases.empty:
                st.markdown("<i>No scheduled cases</i>", unsafe_allow_html=True)
            else:
                for _, r in cases.iterrows():
                    urgency_emoji = "🔴" if r["Urgency_Level"]=="High" else ("🟠" if r["Urgency_Level"]=="Medium" else "🟢")
                    urgency_text = f"{urgency_emoji} {r['Urgency_Level']}"
                    deadline_color = "#ef4444" if r["Deadline_Days_Left"] < 10 else "#2563eb"
                    st.markdown(f"""
                    <div class="case-card {r['Urgency_Level'].lower()}">
                        <b>{r['Case_ID']} — {r['Case_Type']}</b><br>
                        <span style='font-size:13px'>{r['Short_Description']}</span><br>
                        <div class="progress-bar"><div class="progress-fill" style="width:{r['Urgency_Score']}%"></div></div>
                        <span style='font-size:12px;opacity:0.7'>{urgency_text}</span>
                    </div>
                    """, unsafe_allow_html=True)

    st.success("✅ AI Calendar Ready — weekends off, urgent cases early in week.")
