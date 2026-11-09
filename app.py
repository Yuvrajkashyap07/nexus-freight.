from __future__ import annotations

import streamlit as st

from nexus.analytics import load_frames
from nexus.constants import DEMO_USERS
from nexus.db import init_db, db_health
from nexus.seed import seed_demo_data
from nexus.ui.common import inject_css
from nexus.ui.dashboard import render as render_dashboard
from nexus.ui.shipments import render as render_shipments
from nexus.ui.pricing import render as render_pricing
from nexus.ui.operations import render_exceptions, render_documents
from nexus.ui.insights import render_insights
from nexus.ui.admin import render as render_admin

st.set_page_config(
    page_title="NEXUS Freight | Logistics OS",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# Initialise the demo database and seed it only once. For durable cloud data, configure NEXUS_DATABASE_URL.
try:
    init_db()
    seed_demo_data()
except Exception as exc:
    st.error("Database initialisation failed. Check NEXUS_DATABASE_URL and the deployment setup.")
    st.exception(exc)
    st.stop()

with st.sidebar:
    st.markdown("<div style='font:700 1.38rem Space Grotesk;color:#E8F4FF;letter-spacing:-.06em'>NEXUS<span style='color:#51D5E8'>.</span></div><div style='font-size:.68rem;letter-spacing:.14em;color:#8293A8;margin-top:-3px'>GLOBAL FREIGHT OPERATING SYSTEM</div>", unsafe_allow_html=True)
    st.write("")
    st.caption("DEMO WORKSPACE · SYNTHETIC DATA")
    role = st.selectbox("Demo persona", list(DEMO_USERS.keys()), index=0, help="Role switch is for classroom demonstration only; it is not production authentication.")
    actor = role
    permissions = DEMO_USERS[role]["permissions"]
    st.divider()
    page = st.radio("WORKSPACE", [
        "Command Centre", "Shipments", "Quotes & Pricing", "Exception Control",
        "Document Desk", "Network & Finance", "Admin & Architecture",
    ], label_visibility="collapsed")
    st.divider()
    st.markdown("<div class='small-muted'>Connected modules</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.82rem;line-height:1.9;color:#A9B8CA'>● Shipment operations<br>● Freight rating<br>● Document intelligence<br>● Exception management<br>● Financial control</div>", unsafe_allow_html=True)
    st.divider()
    health = db_health()
    st.caption(f"Database · {'Connected' if health.get('ok') else 'Issue'}")
    st.caption("NEXUS Freight v0.1 · Classroom build")

try:
    data = load_frames()
except Exception as exc:
    st.error("Unable to load application data.")
    st.exception(exc)
    st.stop()

if page == "Command Centre":
    render_dashboard(data)
elif page == "Shipments":
    render_shipments(data, actor, permissions)
elif page == "Quotes & Pricing":
    render_pricing(data, actor, permissions)
elif page == "Exception Control":
    render_exceptions(data, actor, permissions)
elif page == "Document Desk":
    render_documents(data, actor, permissions)
elif page == "Network & Finance":
    render_insights(data, actor, permissions)
elif page == "Admin & Architecture":
    def reset_demo():
        seed_demo_data(force=True)
    render_admin(actor, role, permissions, data, reset_demo)

st.markdown("<div style='margin-top:36px;padding-top:13px;border-top:1px solid rgba(148,163,184,.12);display:flex;justify-content:space-between;color:#71839A;font-size:.72rem'><span>NEXUS Freight · AI-native logistics operating system</span><span>Classroom prototype · synthetic data · no live carrier feeds</span></div>", unsafe_allow_html=True)
