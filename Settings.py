"""Settings page — API status, notifications, integration config."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from utils import api_client

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
st.title("⚙️ Settings & Integrations")
st.caption("API status · OAuth connections · Notification testing")
st.divider()

# ── Backend Health ────────────────────────────────────────────────────────────
st.subheader("🩺 System Health")
try:
    health = api_client.health()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Backend",          "✅ Online" if health.get("status") == "ok" else "❌ Offline")
    c2.metric("Google Calendar",  "✅ Connected" if health.get("google_calendar") else "❌ Not connected")
    c3.metric("Gmail",            "✅ Connected" if health.get("gmail") else "❌ Not connected")
    c4.metric("Scheduler",        "✅ Running"   if health.get("scheduler")        else "❌ Stopped")
except Exception as e:
    st.error(f"Backend offline: {e}")

st.divider()

# ── API Keys Reference ────────────────────────────────────────────────────────
st.subheader("🔑 Configured API Keys")
st.info("Keys are loaded from the `.env` file. Edit `.env` to change them — no restart needed for most changes.")

key_table = {
    "Service":     ["Groq AI",       "Bland AI",        "Google Calendar",    "Gmail API",       "WhatsApp (Meta)",    "Instagram (Meta)"],
    "Key/ID":      [
        "gsk_sxhrwa9c…mY7",
        "org_b7587d91…",
        "AIzaSyASHQ… (API key)",
        "AIzaSyAz0T… (API key)",
        "Configure in .env",
        "Configure in .env",
    ],
    "Status": ["✅ Set","✅ Set","✅ Set","✅ Set","⚙️ Needs token","⚙️ Needs token"],
}
import pandas as pd
st.dataframe(pd.DataFrame(key_table), use_container_width=True, hide_index=True)

st.divider()

# ── Google OAuth ──────────────────────────────────────────────────────────────
st.subheader("🔗 Google OAuth Connections")
st.caption("Client secrets must be added to `.env` before connecting. Get them from Google Cloud Console.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📅 Google Calendar**")
    try:
        cal_status = api_client.calendar_status()
        if cal_status.get("authorized"):
            st.success("✅ Connected")
        else:
            auth_data = api_client.calendar_auth_url()
            url = auth_data.get("auth_url", "")
            if url:
                st.markdown(f"[🔐 Connect Google Calendar]({url})")
            else:
                st.warning("Add `GOOGLE_CALENDAR_CLIENT_SECRET` to .env first")
    except Exception as e:
        st.error(str(e))

with col2:
    st.markdown("**📧 Gmail**")
    try:
        gmail_status = api_client.gmail_status()
        if gmail_status.get("authorized"):
            st.success("✅ Connected")
        else:
            auth_data = api_client.gmail_auth_url()
            url = auth_data.get("auth_url", "")
            if url:
                st.markdown(f"[🔐 Connect Gmail]({url})")
            else:
                st.warning("Add `GMAIL_CLIENT_SECRET` to .env first")
    except Exception as e:
        st.error(str(e))

st.divider()

# ── WhatsApp / Instagram Setup Guide ─────────────────────────────────────────
st.subheader("📲 WhatsApp & Instagram Setup")

with st.expander("How to get WhatsApp Business API credentials", expanded=False):
    st.markdown("""
**Steps to set up WhatsApp:**
1. Go to [Meta for Developers](https://developers.facebook.com)
2. Create a Meta App → Add **WhatsApp** product
3. In WhatsApp → API Setup, copy:
   - **Phone Number ID** → `WHATSAPP_PHONE_NUMBER_ID` in `.env`
   - **Access Token** → `WHATSAPP_ACCESS_TOKEN` in `.env`
4. Add your phone number to receive alerts → `WHATSAPP_RECIPIENT_NUMBER` (with country code, e.g. `+919XXXXXXXXX`)
5. Send a template message first to verify the number
    """)

with st.expander("How to get Instagram DM API credentials", expanded=False):
    st.markdown("""
**Steps to set up Instagram DM:**
1. Go to [Meta for Developers](https://developers.facebook.com)
2. Connect your Instagram Business Account to your Facebook Page
3. Add **Instagram Graph API** product to your Meta App
4. In **Instagram → Setup**, get:
   - **Instagram Business Account ID** → `INSTAGRAM_BUSINESS_ACCOUNT_ID`
   - **Access Token** (with `instagram_manage_messages` scope) → `INSTAGRAM_ACCESS_TOKEN`
5. Get the recipient's Instagram User ID → `INSTAGRAM_RECIPIENT_ID`
    """)

st.divider()

# ── Test Notifications ────────────────────────────────────────────────────────
st.subheader("🔔 Test Notifications")
st.caption("Send a test message to verify your WhatsApp/Instagram integration")

col_plat, col_btn = st.columns([2, 1])
with col_plat:
    test_platform = st.selectbox("Platform to test", ["both", "whatsapp", "instagram"])
with col_btn:
    st.write("")
    st.write("")
    if st.button("🚀 Send Test Notification"):
        with st.spinner("Sending…"):
            try:
                result = api_client.test_notification(test_platform)
                st.success("Test notification sent!")
                st.json(result)
            except Exception as e:
                st.error(f"Failed: {e}")

st.divider()

# ── Manual Notification ───────────────────────────────────────────────────────
st.subheader("✉️ Send Manual Notification")

EVENT_TYPES = [
    "company_added","hot_lead","email_generated","email_sent",
    "meeting_scheduled","meeting_completed","call_initiated",
    "csv_imported","daily_report","reminder_24h","reminder_1h","reminder_10min",
]

with st.form("manual_notify_form"):
    col_a, col_b, col_c = st.columns(3)
    event_type  = col_a.selectbox("Event Type", EVENT_TYPES)
    platform    = col_b.selectbox("Platform", ["both","whatsapp","instagram"])
    col_c.write("")
    detail      = st.text_area("Message Detail", placeholder="Custom detail text…")
    if st.form_submit_button("📤 Send Now"):
        if detail.strip():
            try:
                result = api_client.send_manual_notification(event_type, detail.strip(), platform)
                st.success(f"Sent! Status: {result.get('status','unknown')}")
            except Exception as e:
                st.error(str(e))
        else:
            st.error("Detail cannot be empty.")

st.divider()

# ── Notification History ──────────────────────────────────────────────────────
st.subheader("📋 Recent Notification Log")
try:
    notifs = api_client.list_notifications(limit=30)
    if notifs:
        df = pd.DataFrame(notifs)[["id","type","platform","status","created_at","sent_at"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No notifications sent yet.")
except Exception as e:
    st.error(str(e))

st.divider()

# ── Groq AI Chat Playground ───────────────────────────────────────────────────
st.subheader("🤖 Groq AI Playground")
st.caption("Test Groq Llama-3 directly from here")

with st.form("ai_chat_form"):
    system_msg = st.text_input("System prompt", value="You are a helpful sales assistant.")
    user_msg   = st.text_area("Your message", height=80, placeholder="Ask anything…")
    if st.form_submit_button("⚡ Ask Groq"):
        with st.spinner("Calling Groq Llama-3…"):
            try:
                result = api_client.ai_chat(user_msg, system=system_msg)
                st.markdown("**Response:**")
                st.markdown(result.get("reply", ""))
            except Exception as e:
                st.error(f"Groq error: {e}")

st.divider()

# ── .env Reference ────────────────────────────────────────────────────────────
st.subheader("📄 .env Configuration Reference")
st.code("""
# ─── GROQ AI ─────────────────────────────────────────
GROQ_API_KEY=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
GROQ_MODEL=llama-3.3-70b-versatile

# ─── BLAND AI ────────────────────────────────────────
BLAND_AI_API_KEY=org_b7587d91a5be8468c8fd2bab7a50ede5671e50b2264bad92b1e9f24171f2bf698a7f279164187663202a69

# ─── GOOGLE CALENDAR ─────────────────────────────────
GOOGLE_CALENDAR_API_KEY=AIzaSyASHQpaE_HUBkk3VJfSSAsTlkR0vMDWZgY
GOOGLE_CALENDAR_CLIENT_ID=869844262487-sr7vaeatfj5q32hme113vd4p72iffak2.apps.googleusercontent.com
GOOGLE_CALENDAR_CLIENT_SECRET=<from Google Cloud Console>

# ─── GMAIL ───────────────────────────────────────────
GMAIL_API_KEY=AIzaSyAz0TNvxTCx6TwghDiHHKNcKd6Rv8F-qeA
GMAIL_CLIENT_ID=869844262487-1eecpn7til8ngp3a7ngc46lsdrf1ius2.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=<from Google Cloud Console>
GMAIL_SENDER_EMAIL=your-email@gmail.com

# ─── WHATSAPP (Meta) ─────────────────────────────────
WHATSAPP_ACCESS_TOKEN=<from Meta for Developers>
WHATSAPP_PHONE_NUMBER_ID=<your WhatsApp Phone Number ID>
WHATSAPP_RECIPIENT_NUMBER=+91XXXXXXXXXX

# ─── INSTAGRAM (Meta) ────────────────────────────────
INSTAGRAM_ACCESS_TOKEN=<from Meta Graph API>
INSTAGRAM_BUSINESS_ACCOUNT_ID=<your IG Business Account ID>
INSTAGRAM_RECIPIENT_ID=<Instagram User ID to notify>
""", language="bash")
