"""Meetings page — Google Calendar scheduling + reminders."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date, time
from utils import api_client

st.set_page_config(page_title="Meetings", page_icon="📅", layout="wide")
st.title("📅 Meetings")
st.caption("Schedule meetings directly to Google Calendar · Reminders via WhatsApp & Instagram")
st.divider()

# ── Google Calendar auth status ───────────────────────────────────────────────
try:
    cal_status = api_client.calendar_status()
    cal_ok = cal_status.get("authorized", False)
except Exception:
    cal_ok = False

if cal_ok:
    st.success("✅ Google Calendar connected")
else:
    st.warning("⚠️ Google Calendar not connected")
    try:
        auth_info = api_client.calendar_auth_url()
        auth_url  = auth_info.get("auth_url", "")
        if auth_url:
            st.markdown(f"👉 [**Click here to connect Google Calendar**]({auth_url})")
            st.caption("After authorizing, come back and refresh this page.")
    except Exception as e:
        st.error(f"Cannot get auth URL: {e}")

st.divider()

# ── Stats ─────────────────────────────────────────────────────────────────────
try:
    stats = api_client.meeting_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("📅 Total Meetings",    stats.get("total", 0))
    c2.metric("⏳ Scheduled",         stats.get("scheduled", 0))
    c3.metric("✅ Completed",         stats.get("completed", 0))
except Exception:
    pass

st.divider()

# ── Schedule a new meeting ────────────────────────────────────────────────────
st.subheader("📅 Schedule New Meeting")

try:
    companies = api_client.list_companies(limit=500)
    company_map = {f"{c['name']} (#{c['id']})": c for c in companies}
except Exception:
    companies = []
    company_map = {}

if not companies:
    st.warning("Add a company first before scheduling a meeting.")
else:
    with st.form("new_meeting_form"):
        col1, col2 = st.columns(2)

        with col1:
            company_label    = st.selectbox("Company *", list(company_map.keys()))
            selected_company = company_map.get(company_label, {})
            title            = st.text_input("Meeting Title *", placeholder="Discovery Call / Product Demo / Follow-up")
            description      = st.text_area("Description", height=80, placeholder="Agenda, talking points…")

        with col2:
            meet_date  = st.date_input("Date *", value=date.today() + timedelta(days=1))
            start_time = st.time_input("Start Time (UTC) *", value=time(10, 0))
            duration   = st.selectbox("Duration", ["30 minutes","45 minutes","1 hour","1.5 hours","2 hours"])
            add_meet   = st.checkbox("Add Google Meet link", value=True)

        attendee_text = st.text_input(
            "Attendee Emails",
            value=selected_company.get("email", "") or "",
            placeholder="email1@example.com, email2@example.com",
        )

        submitted = st.form_submit_button("📅 Schedule Meeting", use_container_width=True, type="primary")

        if submitted:
            if not title.strip():
                st.error("Meeting title is required.")
            else:
                dur_map = {"30 minutes": 30, "45 minutes": 45, "1 hour": 60, "1.5 hours": 90, "2 hours": 120}
                dur_min = dur_map.get(duration, 60)

                start_dt = datetime.combine(meet_date, start_time)
                end_dt   = start_dt + timedelta(minutes=dur_min)

                attendees = [e.strip() for e in attendee_text.split(",") if e.strip()]

                with st.spinner("Creating calendar event…"):
                    try:
                        result = api_client.create_meeting({
                            "company_id":    selected_company["id"],
                            "title":         title.strip(),
                            "description":   description.strip(),
                            "start_time":    start_dt.isoformat(),
                            "end_time":      end_dt.isoformat(),
                            "attendees":     attendees,
                            "add_meet_link": add_meet,
                        })
                        st.success(f"✅ Meeting scheduled! ID #{result['id']}")
                        if result.get("meet_link"):
                            st.markdown(f"🔗 **Meet Link:** {result['meet_link']}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Failed: {e}")

st.divider()

# ── Upcoming meetings from Google Calendar ────────────────────────────────────
if cal_ok:
    st.subheader("🗓️ Upcoming from Google Calendar")
    try:
        events_data = api_client.upcoming_events()
        events = events_data.get("events", [])
        if events:
            for ev in events[:10]:
                start = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", ""))
                summary = ev.get("summary", "Untitled")
                link = ev.get("htmlLink", "#")
                st.markdown(f"📌 [{summary}]({link}) — `{start}`")
        else:
            st.info("No upcoming events in Google Calendar.")
    except Exception as e:
        st.warning(f"Could not load calendar events: {e}")
    st.divider()

# ── Meeting List ──────────────────────────────────────────────────────────────
st.subheader("📋 All Meetings")

col_f1, col_f2 = st.columns([2, 1])
with col_f2:
    mstatus = st.selectbox("Filter", ["All", "scheduled", "completed", "cancelled"], key="meet_filter")

try:
    status_param = None if mstatus == "All" else mstatus
    meetings = api_client.list_meetings(status=status_param)
except Exception as e:
    st.error(f"Cannot load meetings: {e}")
    st.stop()

if not meetings:
    st.info("No meetings scheduled yet.")
    st.stop()

cid_to_name = {c["id"]: c["name"] for c in companies}
df = pd.DataFrame(meetings)
if "company_id" in df.columns:
    df["company"] = df["company_id"].apply(lambda x: cid_to_name.get(x, f"#{x}"))

display_cols = ["id", "company", "title", "start_time", "end_time", "status", "meet_link"]
available = [c for c in display_cols if c in df.columns]
st.dataframe(df[available], use_container_width=True, hide_index=True)

st.divider()

# ── Manage Meeting ────────────────────────────────────────────────────────────
st.subheader("⚙️ Manage Meeting")
meet_options = {
    f"#{m['id']} — {cid_to_name.get(m['company_id'],'?')} · {m['title']} ({m['status']})": m["id"]
    for m in meetings
}
selected_meet_label = st.selectbox("Select meeting", list(meet_options.keys()))
selected_meet_id    = meet_options[selected_meet_label]
selected_meet       = next((m for m in meetings if m["id"] == selected_meet_id), {})

col_x, col_y = st.columns(2)
with col_x:
    st.write(f"**Title:** {selected_meet.get('title','')}")
    st.write(f"**Start:** {selected_meet.get('start_time','')}")
    st.write(f"**End:**   {selected_meet.get('end_time','')}")
    if selected_meet.get("meet_link"):
        st.markdown(f"🔗 [Join Meeting]({selected_meet['meet_link']})")

with col_y:
    st.write(f"**Status:** `{selected_meet.get('status','')}`")
    rems = selected_meet.get("reminders_sent") or []
    st.write(f"**Reminders sent:** {', '.join(rems) if rems else 'None yet'}")
    attendees = selected_meet.get("attendees") or []
    st.write(f"**Attendees:** {', '.join(attendees) if attendees else '—'}")

action = st.radio("Action", ["Mark Completed", "Mark Cancelled", "Delete"], horizontal=True, key="meet_action")

if action == "Mark Completed":
    if st.button("✅ Mark as Completed"):
        try:
            api_client.update_meeting(selected_meet_id, {"status": "completed"})
            st.success("Marked as completed.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

elif action == "Mark Cancelled":
    if st.button("🚫 Mark as Cancelled"):
        try:
            api_client.update_meeting(selected_meet_id, {"status": "cancelled"})
            st.success("Marked as cancelled.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

elif action == "Delete":
    st.warning("⚠️ This will delete the meeting from the database AND Google Calendar.")
    if st.button("🗑️ Confirm Delete", type="primary"):
        try:
            api_client.delete_meeting(selected_meet_id)
            st.success("Deleted.")
            st.rerun()
        except Exception as e:
            st.error(str(e))
