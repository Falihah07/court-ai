import streamlit as st
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="HackElite 2025 Dashboard", page_icon="⚡", layout="wide")

# --- CUSTOM STYLES ---
st.markdown("""
    <style>
        /* General page styling */
        body {
            color: black;
            background-color: white;
            font-family: 'Poppins', sans-serif;
        }
        .main {
            padding: 2rem;
        }
        h1, h2, h3, h4 {
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        /* Fancy title animation */
        .title {
            font-size: 2.8rem;
            text-align: center;
            font-weight: 700;
            background: linear-gradient(90deg, #00C9A7, #92FE9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 3s infinite alternate;
        }

        @keyframes glow {
            from { text-shadow: 0 0 5px #00C9A7; }
            to { text-shadow: 0 0 15px #92FE9D; }
        }

        /* Case card styling */
        .case-card {
            border-radius: 20px;
            padding: 20px;
            margin: 10px 0;
            color: black;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease-in-out;
        }

        .case-card:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 18px rgba(0,0,0,0.15);
        }

        /* Case colors */
        .case-green { background: #E8F8F5; border-left: 6px solid #1ABC9C; }
        .case-yellow { background: #FEF9E7; border-left: 6px solid #F1C40F; }
        .case-red { background: #FDEDEC; border-left: 6px solid #E74C3C; }

        /* Status badge */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
            color: white;
        }
        .badge-green { background: #1ABC9C; }
        .badge-yellow { background: #F1C40F; color: black; }
        .badge-red { background: #E74C3C; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 class='title'>⚡ HackElite 2025 - Case Dashboard</h1>", unsafe_allow_html=True)
st.markdown("### Showcasing your sleek UI design and professional dashboard skills ✨")
st.markdown("---")

# --- SAMPLE CASES ---
cases = [
    {"id": "C101", "title": "AI-Powered Waste Sorting", "desc": "Automated waste segregation using AI vision.", "status": "Completed", "color": "green"},
    {"id": "C102", "title": "Smart Water Management", "desc": "IoT system for water conservation and monitoring.", "status": "In Progress", "color": "yellow"},
    {"id": "C103", "title": "AR Campus Navigation", "desc": "Augmented Reality navigation for college events.", "status": "In Progress", "color": "yellow"},
    {"id": "C104", "title": "Cyber Threat Detection", "desc": "AI-driven system for anomaly detection in networks.", "status": "Pending", "color": "red"},
]

# --- DISPLAY CASES ---
cols = st.columns(2)
for i, case in enumerate(cases):
    with cols[i % 2]:
        st.markdown(f"""
            <div class="case-card case-{case['color']}">
                <h3>{case['id']} — {case['title']}</h3>
                <p>{case['desc']}</p>
                <span class="badge badge-{case['color']}">{case['status']}</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("💡 **Tip:** You can make this dashboard fully interactive — filter by status, add animations, or even integrate live hackathon data!")

