"""Emails page — Groq AI email generation + Gmail sending."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from utils import api_client

st.set_page_config(page_title="Emails", page_icon="📧", layout="wide")
st.title("📧 Email Manager")
st.caption("Generate personalised emails with Groq Llama-3 · Send via Gmail API")
st.divider()

# ── Gmail auth status ─────────────────────────────────────────────────────────
try:
    gmail_ok = api_client.gmail_status().get("authorized", False)
except Exception:
    gmail_ok = False

if gmail_ok:
    st.success("✅ Gmail connected and ready to send")
else:
    st.warning("⚠️ Gmail not connected — you can generate but not send emails")
    try:
        auth_info = api_client.gmail_auth_url()
        auth_url  = auth_info.get("auth_url", "")
        if auth_url:
            st.markdown(f"👉 [**Click here to connect Gmail**]({auth_url})")
    except Exception as e:
        st.error(f"Cannot get Gmail auth URL: {e}")

st.divider()

# ── Stats ─────────────────────────────────────────────────────────────────────
try:
    stats = api_client.email_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📧 Total",     stats.get("total", 0))
    c2.metric("✍️ Generated", stats.get("generated", 0))
    c3.metric("✅ Sent",      stats.get("sent", 0))
    c4.metric("❌ Failed",    stats.get("failed", 0))
except Exception:
    pass

st.divider()

# ── Generate Email ────────────────────────────────────────────────────────────
st.subheader("✨ Generate AI Sales Email")

try:
    companies = api_client.list_companies(limit=500)
    company_map = {f"{c['name']} (#{c['id']})": c for c in companies}
except Exception:
    companies = []
    company_map = {}

if not companies:
    st.warning("Add a company first in the Companies page.")
else:
    with st.form("generate_email_form"):
        col1, col2 = st.columns(2)
        with col1:
            company_label    = st.selectbox("Company *", list(company_map.keys()))
            selected_company = company_map.get(company_label, {})
            sender_name      = st.text_input("Sender Name", value="Sales Team")
        with col2:
            st.markdown("**Company Info (auto-filled)**")
            st.caption(f"Contact: {selected_company.get('contact_name','N/A')}")
            st.caption(f"Email:   {selected_company.get('email','N/A')}")
            st.caption(f"Industry:{selected_company.get('industry','N/A')}")

        extra_context = st.text_area(
            "Extra context for this email",
            height=80,
            placeholder="e.g. They attended our webinar, interested in enterprise plan, follow-up after trade show…",
        )

        submitted = st.form_submit_button("🤖 Generate Email with Groq", use_container_width=True, type="primary")

        if submitted:
            with st.spinner("Writing email with Groq Llama-3…"):
                try:
                    result = api_client.generate_email({
                        "company_id":    selected_company["id"],
                        "sender_name":   sender_name,
                        "extra_context": extra_context,
                    })
                    st.success(f"✅ Email generated! ID #{result['id']}")
                    st.session_state["last_generated_email"] = result
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Generation failed: {e}")

# Show last generated email preview
if "last_generated_email" in st.session_state:
    email = st.session_state["last_generated_email"]
    st.subheader("📬 Generated Email Preview")
    st.markdown(f"**Subject:** {email.get('subject','')}")
    st.text_area("Body", email.get("body", ""), height=250, disabled=True)

    col_send, col_del = st.columns([1, 3])
    with col_send:
        if gmail_ok:
            if st.button("📤 Send This Email Now", type="primary"):
                with st.spinner("Sending via Gmail…"):
                    try:
                        api_client.send_email(email["id"])
                        st.success("✅ Email sent successfully!")
                        del st.session_state["last_generated_email"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Send failed: {e}")
        else:
            st.warning("Connect Gmail to send.")

st.divider()

# ── Email History ─────────────────────────────────────────────────────────────
st.subheader("📋 Email History")

col_f1, col_f2 = st.columns([2, 1])
with col_f2:
    email_filter = st.selectbox("Filter by status", ["All", "generated", "sent", "failed"])

try:
    status_param = None if email_filter == "All" else email_filter
    emails = api_client.list_emails(status=status_param)
except Exception as e:
    st.error(f"Cannot load emails: {e}")
    st.stop()

if not emails:
    st.info("No emails yet. Generate one above.")
    st.stop()

cid_to_name = {c["id"]: c["name"] for c in companies}
df = pd.DataFrame(emails)
if "company_id" in df.columns:
    df["company"] = df["company_id"].apply(lambda x: cid_to_name.get(x, f"#{x}"))

display_cols = ["id", "company", "recipient_email", "subject", "status", "created_at", "sent_at"]
available    = [c for c in display_cols if c in df.columns]
st.dataframe(df[available], use_container_width=True, hide_index=True)

st.divider()

# ── Manage Email ──────────────────────────────────────────────────────────────
st.subheader("⚙️ Manage Email")
email_options = {
    f"#{e['id']} — {cid_to_name.get(e['company_id'],'?')} ({e['status']}) — {(e.get('subject') or '')[:40]}": e["id"]
    for e in emails
}
if email_options:
    selected_email_label = st.selectbox("Select email", list(email_options.keys()))
    selected_email_id    = email_options[selected_email_label]
    selected_email       = next((e for e in emails if e["id"] == selected_email_id), {})

    st.markdown(f"**To:** {selected_email.get('recipient_email','')}")
    st.markdown(f"**Subject:** {selected_email.get('subject','')}")
    st.markdown(f"**Status:** `{selected_email.get('status','')}`")

    if selected_email.get("body"):
        with st.expander("📄 Email Body"):
            st.text_area("Body", selected_email["body"], height=250, disabled=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if selected_email.get("status") == "generated" and gmail_ok:
            if st.button("📤 Send Now"):
                with st.spinner("Sending…"):
                    try:
                        api_client.send_email(selected_email_id)
                        st.success("✅ Sent!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    with col_b:
        if st.button("🗑️ Delete Email"):
            try:
                api_client.delete_email(selected_email_id)
                st.success("Deleted.")
                st.rerun()
            except Exception as e:
                st.error(str(e))
