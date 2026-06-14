"""AI Sales CRM — Streamlit frontend entry point."""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="AI Sales CRM",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* sidebar */
  [data-testid="stSidebar"] { background: #0f172a; }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label { color: #94a3b8 !important; }

  /* metric cards */
  [data-testid="stMetric"] {
    background: #1e293b;
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid #334155;
  }
  [data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 1.8rem !important; }

  /* buttons */
  .stButton > button {
    border-radius: 8px;
    background: #2563eb;
    color: white;
    border: none;
    padding: 0.45rem 1.2rem;
    font-weight: 500;
    transition: background .2s;
  }
  .stButton > button:hover { background: #1d4ed8; }

  /* success/error pills */
  .pill-green { background:#065f46; color:#6ee7b7; padding:2px 10px; border-radius:20px; font-size:12px; }
  .pill-red   { background:#7f1d1d; color:#fca5a5; padding:2px 10px; border-radius:20px; font-size:12px; }
  .pill-blue  { background:#1e3a5f; color:#93c5fd; padding:2px 10px; border-radius:20px; font-size:12px; }
  .pill-amber { background:#78350f; color:#fcd34d; padding:2px 10px; border-radius:20px; font-size:12px; }

  /* dataframe */
  .stDataFrame { border-radius: 10px; overflow: hidden; }

  /* dividers */
  hr { border-color: #1e293b; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar nav ───────────────────────────────────────────────────────────────
from utils import api_client

with st.sidebar:
    st.markdown("## 🤖 AI Sales CRM")
    st.caption("Groq · Bland AI · Google · WhatsApp")
    st.divider()

    # Backend health indicator
    h = api_client.health()
    if h.get("status") == "ok":
        st.success("✅ Backend online")
    else:
        st.error("❌ Backend offline")
        st.caption("Start the backend: `uvicorn main:app`")

    st.divider()
    st.caption("Navigate using the pages in the sidebar above")

# ── Home page content ─────────────────────────────────────────────────────────
st.title("🤖 AI Sales CRM Dashboard")
st.caption("Powered by Groq Llama-3 · Bland AI · Google Calendar · Gmail · WhatsApp · Instagram")
st.divider()

# Quick stats
try:
    cs = api_client.company_stats()
    cl = api_client.call_stats()
    ms = api_client.meeting_stats()
    es = api_client.email_stats()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("🏢 Companies",   cs.get("total", 0))
    c2.metric("🔥 Hot Leads",   cs.get("hot_leads", 0))
    c3.metric("📞 Calls Made",  cl.get("total", 0))
    c4.metric("📅 Meetings",    ms.get("total", 0))
    c5.metric("📧 Emails Sent", es.get("sent", 0))
    c6.metric("⏳ Upcoming",    ms.get("scheduled", 0))

except Exception as e:
    st.warning(f"Could not load stats — is the backend running? ({e})")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Quick Actions")
    if st.button("➕ Add Company"):
        st.switch_page("pages/2_🏢_Companies.py")
    if st.button("📞 Make AI Call"):
        st.switch_page("pages/3_📞_AI_Calls.py")
    if st.button("📅 Schedule Meeting"):
        st.switch_page("pages/4_📅_Meetings.py")
    if st.button("📧 Generate Email"):
        st.switch_page("pages/5_📧_Emails.py")

with col2:
    st.subheader("🔔 Notification Triggers")
    events = [
        ("🏢", "Company Added",       "New company created"),
        ("🔥", "Hot Lead Alert",      "Lead score ≥ 80"),
        ("📧", "Email Generated",     "Groq draft ready"),
        ("✅", "Email Sent",          "Gmail delivery confirmed"),
        ("📅", "Meeting Scheduled",   "Google Calendar event created"),
        ("✅", "Meeting Completed",   "Meeting time passed"),
        ("📞", "Call Initiated",      "Bland AI call started"),
        ("📤", "Import Completed",    "CSV uploaded"),
        ("📊", "Daily Report",        "Every day at 6 PM UTC"),
        ("🔔", "Meeting Reminder",    "24h / 1h / 10min before"),
    ]
    for emoji, title, desc in events:
        st.markdown(f"{emoji} **{title}** — {desc}")
