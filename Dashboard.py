"""Dashboard — KPIs, charts, recent activity."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import api_client

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard")
st.caption("Real-time overview of your sales pipeline")
st.divider()

# ── KPI cards ────────────────────────────────────────────────────────────────
try:
    cs = api_client.company_stats()
    cl = api_client.call_stats()
    ms = api_client.meeting_stats()
    es = api_client.email_stats()
    ns = api_client.notification_stats()

    k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
    k1.metric("🏢 Total Companies",  cs.get("total",0))
    k2.metric("🔥 Hot Leads (≥80)",  cs.get("hot_leads",0))
    k3.metric("📞 Total Calls",      cl.get("total",0))
    k4.metric("✅ Calls Completed",  cl.get("completed",0))
    k5.metric("📅 Meetings Sched.",  ms.get("scheduled",0))
    k6.metric("📧 Emails Sent",      es.get("sent",0))
    k7.metric("🔔 Notifications",    ns.get("sent",0))

except Exception as e:
    st.error(f"Backend unavailable: {e}")
    st.stop()

st.divider()

# ── Charts row 1 ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pipeline by Status")
    by_status = cs.get("by_status", {})
    if by_status:
        fig = px.pie(
            names=list(by_status.keys()),
            values=list(by_status.values()),
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.4,
        )
        fig.update_layout(
            margin=dict(t=20,b=20,l=20,r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No pipeline data yet.")

with col2:
    st.subheader("Call Activity")
    call_data = {
        "Status": ["Initiated","Completed","Failed"],
        "Count":  [cl.get("initiated",0), cl.get("completed",0), cl.get("failed",0)],
    }
    fig2 = px.bar(
        call_data, x="Status", y="Count",
        color="Status",
        color_discrete_map={"Initiated":"#3b82f6","Completed":"#22c55e","Failed":"#ef4444"},
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        showlegend=False,
        margin=dict(t=20,b=20),
    )
    fig2.update_yaxes(gridcolor="#1e293b")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Charts row 2 ─────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Email Pipeline")
    email_data = {
        "Stage": ["Generated","Sent","Failed"],
        "Count": [es.get("generated",0), es.get("sent",0), es.get("failed",0)],
    }
    fig3 = go.Figure(go.Funnel(
        y=email_data["Stage"],
        x=email_data["Count"],
        textinfo="value+percent initial",
        marker=dict(color=["#3b82f6","#22c55e","#ef4444"]),
    ))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(t=20,b=20),
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Meetings Overview")
    meet_data = {
        "Status":  ["Scheduled","Completed"],
        "Count":   [ms.get("scheduled",0), ms.get("completed",0)],
    }
    fig4 = px.bar(
        meet_data, x="Status", y="Count",
        color="Status",
        color_discrete_map={"Scheduled":"#f59e0b","Completed":"#22c55e"},
    )
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        showlegend=False,
        margin=dict(t=20,b=20),
    )
    fig4.update_yaxes(gridcolor="#1e293b")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Recent data tables ────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏢 Recent Companies", "📞 Recent Calls", "🔔 Recent Notifications"])

with tab1:
    try:
        companies = api_client.list_companies(limit=10)
        if companies:
            df = pd.DataFrame(companies)[["id","name","industry","contact_name","lead_score","status","created_at"]]
            df["lead_score"] = df["lead_score"].apply(lambda x: f"{x:.0f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No companies yet. Add one in the Companies page.")
    except Exception as e:
        st.error(str(e))

with tab2:
    try:
        calls = api_client.list_calls()
        if calls:
            df = pd.DataFrame(calls)[["id","company_id","phone_number","status","duration","created_at"]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No calls yet.")
    except Exception as e:
        st.error(str(e))

with tab3:
    try:
        notifs = api_client.list_notifications(limit=20)
        if notifs:
            df = pd.DataFrame(notifs)[["id","type","platform","status","created_at"]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No notifications yet.")
    except Exception as e:
        st.error(str(e))
