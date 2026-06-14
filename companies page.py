"""Companies page — full CRUD, CSV import, Groq lead scoring."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from utils import api_client

st.set_page_config(page_title="Companies", page_icon="🏢", layout="wide")
st.title("🏢 Companies")
st.caption("Manage your leads and accounts · Lead scoring powered by Groq Llama-3")
st.divider()

# ── Top action bar ────────────────────────────────────────────────────────────
col_add, col_csv, col_search, col_filter = st.columns([1,1,2,1])

with col_add:
    add_mode = st.button("➕ Add Company", use_container_width=True)

with col_csv:
    csv_mode = st.button("📤 Import CSV", use_container_width=True)

with col_search:
    search = st.text_input("🔍 Search", placeholder="Name, email, contact…", label_visibility="collapsed")

with col_filter:
    status_filter = st.selectbox("Status", ["All","new","contacted","qualified","proposal","closed"], label_visibility="collapsed")

# ── Add Company form ──────────────────────────────────────────────────────────
if add_mode:
    st.session_state["show_add"] = not st.session_state.get("show_add", False)

if st.session_state.get("show_add"):
    with st.expander("➕ New Company", expanded=True):
        with st.form("add_company_form"):
            c1, c2, c3 = st.columns(3)
            name    = c1.text_input("Company Name *")
            industry = c2.text_input("Industry")
            contact = c3.text_input("Contact Name")

            c4, c5, c6 = st.columns(3)
            email   = c4.text_input("Email")
            phone   = c5.text_input("Phone")
            website = c6.text_input("Website")

            address = st.text_input("Address")
            notes   = st.text_area("Notes", height=80)

            submitted = st.form_submit_button("💾 Save & Score Lead", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("Company name is required.")
                else:
                    try:
                        result = api_client.create_company({
                            "name": name, "industry": industry,
                            "contact_name": contact, "email": email,
                            "phone": phone, "website": website,
                            "address": address, "notes": notes,
                        })
                        st.success(f"✅ {result['name']} added! Lead score: {result['lead_score']:.0f}/100")
                        st.session_state["show_add"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

# ── CSV Import ────────────────────────────────────────────────────────────────
if csv_mode:
    st.session_state["show_csv"] = not st.session_state.get("show_csv", False)

if st.session_state.get("show_csv"):
    with st.expander("📤 Import from CSV", expanded=True):
        st.markdown("""
**Required column:** `name`  
**Optional columns:** `industry`, `contact_name`, `email`, `phone`, `website`, `address`, `notes`
        """)
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded:
            if st.button("📤 Start Import"):
                try:
                    result = api_client.import_csv(uploaded.read(), uploaded.name)
                    st.success(f"✅ {result['created']} companies imported, {result['skipped']} skipped.")
                    st.session_state["show_csv"] = False
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

st.divider()

# ── Company list ──────────────────────────────────────────────────────────────
try:
    status_param = "" if status_filter == "All" else status_filter
    companies = api_client.list_companies(search=search, status=status_param, limit=500)
except Exception as e:
    st.error(f"Cannot load companies: {e}")
    st.stop()

if not companies:
    st.info("No companies found. Add one above or import a CSV.")
    st.stop()

# Stats bar
total     = len(companies)
hot       = sum(1 for c in companies if c.get("lead_score", 0) >= 80)
qualified = sum(1 for c in companies if c.get("status") == "qualified")
st.markdown(f"**{total}** companies · **{hot}** hot leads · **{qualified}** qualified")

# ── Table ─────────────────────────────────────────────────────────────────────
df = pd.DataFrame(companies)
display_cols = ["id","name","industry","contact_name","email","phone","lead_score","status"]
available = [c for c in display_cols if c in df.columns]
df_display = df[available].copy()
df_display["lead_score"] = df_display["lead_score"].apply(lambda x: f"{float(x):.0f}")

st.dataframe(df_display, use_container_width=True, hide_index=True)

st.divider()

# ── Detail / Edit / Delete ───────────────────────────────────────────────────
st.subheader("Manage Company")
if companies:
    options = {f"{c['name']} (#{c['id']})": c['id'] for c in companies}
    selected_label = st.selectbox("Select company", list(options.keys()))
    selected_id    = options[selected_label]

    try:
        c = api_client.get_company(selected_id)
    except Exception as e:
        st.error(str(e))
        st.stop()

    score = c.get("lead_score", 0)
    score_color = "🔥" if score >= 80 else "🟡" if score >= 50 else "🔵"
    st.markdown(f"**Lead Score:** {score_color} {score:.0f}/100 &nbsp; **Status:** `{c.get('status','new')}`")

    action = st.radio("Action", ["View", "Edit", "Delete", "Re-score with AI"], horizontal=True)

    if action == "View":
        col_a, col_b = st.columns(2)
        col_a.write(f"**Name:** {c.get('name','')}")
        col_a.write(f"**Industry:** {c.get('industry','')}")
        col_a.write(f"**Contact:** {c.get('contact_name','')}")
        col_a.write(f"**Email:** {c.get('email','')}")
        col_b.write(f"**Phone:** {c.get('phone','')}")
        col_b.write(f"**Website:** {c.get('website','')}")
        col_b.write(f"**Address:** {c.get('address','')}")
        st.write(f"**Notes:** {c.get('notes','')}")

    elif action == "Edit":
        with st.form("edit_form"):
            c1, c2, c3 = st.columns(3)
            name     = c1.text_input("Name",         value=c.get("name",""))
            industry = c2.text_input("Industry",     value=c.get("industry","") or "")
            contact  = c3.text_input("Contact Name", value=c.get("contact_name","") or "")
            c4, c5, c6 = st.columns(3)
            email   = c4.text_input("Email",   value=c.get("email","") or "")
            phone   = c5.text_input("Phone",   value=c.get("phone","") or "")
            website = c6.text_input("Website", value=c.get("website","") or "")
            status  = st.selectbox("Status",
                ["new","contacted","qualified","proposal","closed"],
                index=["new","contacted","qualified","proposal","closed"].index(c.get("status","new")))
            notes = st.text_area("Notes", value=c.get("notes","") or "")
            if st.form_submit_button("💾 Save Changes"):
                try:
                    api_client.update_company(selected_id, {
                        "name":name,"industry":industry,"contact_name":contact,
                        "email":email,"phone":phone,"website":website,
                        "status":status,"notes":notes,
                    })
                    st.success("✅ Updated!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    elif action == "Delete":
        st.warning(f"⚠️ This will permanently delete **{c.get('name')}** and all related calls, meetings, and emails.")
        if st.button("🗑️ Confirm Delete", type="primary"):
            try:
                api_client.delete_company(selected_id)
                st.success("Deleted.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

    elif action == "Re-score with AI":
        st.info("This will re-run Groq Llama-3 lead scoring for this company.")
        if st.button("🤖 Re-score Now"):
            with st.spinner("Scoring with Groq…"):
                try:
                    result = api_client.rescore_company(selected_id)
                    st.success(f"New lead score: **{result['lead_score']:.0f}/100**")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
