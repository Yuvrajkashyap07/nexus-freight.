from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px

from ..analytics import calculate_risk
from ..constants import DEMO_AS_OF
from ..ui.common import hero, page_header, plotly_dark, map_figure, usd, safe_dataframe, currency_breakdown


def render(data: dict[str, pd.DataFrame]) -> None:
    s = data["shipments"].copy()
    ex = data["exceptions"].copy()
    q = data["quotes"].copy()
    inv = data["invoices"].copy()
    hero("Move freight. Not spreadsheets.", "A unified command centre for quotations, shipment execution, document intelligence and financial control.")

    if s.empty:
        st.warning("No shipment data is available. Initialise the demo dataset from Admin & System.")
        return

    active = s[~s.status.isin(["Delivered", "Cancelled"])]
    delivered = s[s.status == "Delivered"]
    on_time = 0
    for _, row in delivered.iterrows():
        if pd.notna(row.actual_delivery) and pd.notna(row.eta) and row.actual_delivery.date() <= row.eta.date():
            on_time += 1
    on_time_pct = (on_time / len(delivered) * 100) if len(delivered) else 0
    open_ex = ex[ex.status.isin(["Open", "In progress", "Escalated"])] if not ex.empty else ex
    open_ar = inv[(inv.invoice_type == "Receivable") & (inv.status == "Outstanding")] if not inv.empty else inv
    receivables = currency_breakdown(open_ar, "amount")
    pipeline_gp = currency_breakdown(active, "gross_profit")

    cols = st.columns(5)
    cols[0].metric("Active shipments", f"{len(active):,}", f"{len(s)} total records")
    cols[1].metric("On-time delivery", f"{on_time_pct:.1f}%", f"{len(delivered)} delivered")
    cols[2].metric("Open exceptions", f"{len(open_ex):,}", "Needs operational attention", delta_color="inverse")
    cols[3].metric("Open receivables", receivables, "By currency · no FX consolidation")
    cols[4].metric("Gross profit pipeline", pipeline_gp, "By currency · active shipments")

    st.write("")
    left, right = st.columns([1.55, 1])
    with left:
        st.subheader("Global shipment network")
        st.plotly_chart(map_figure(s, 26), use_container_width=True, config={"displayModeBar": False})
    with right:
        st.subheader("Shipment mix")
        mix = s.groupby("mode", as_index=False).size().rename(columns={"size": "Shipments"}).sort_values("Shipments", ascending=True)
        fig = px.bar(mix, x="Shipments", y="mode", orientation="h", color="mode", text="Shipments")
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(plotly_dark(fig, 250), use_container_width=True, config={"displayModeBar": False})
        status_mix = s.groupby("status", as_index=False).size().rename(columns={"size": "Count"})
        fig2 = px.pie(status_mix, names="status", values="Count", hole=.68)
        st.plotly_chart(plotly_dark(fig2, 190), use_container_width=True, config={"displayModeBar": False})

    st.write("")
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Operational risk radar")
        risks = []
        for _, row in s.iterrows():
            score, band, reasons = calculate_risk(row.to_dict(), DEMO_AS_OF)
            if score >= 35:
                risks.append({"Reference": row.reference, "Lane": f"{row.origin} → {row.destination}", "Status": row.status, "ETA": row.eta.date() if pd.notna(row.eta) else None, "Risk": band, "Score": score, "Signal": "; ".join(reasons)})
        risk_df = pd.DataFrame(risks).sort_values("Score", ascending=False).head(7) if risks else pd.DataFrame()
        if risk_df.empty:
            st.success("No high-risk shipments found by the demo rules.")
        else:
            safe_dataframe(risk_df, height=275)
    with right:
        st.subheader("AI operations brief")
        st.markdown("""
        <div class='nexus-card'>
          <div class='nexus-card-label'>Decision support · explainable demo rules</div>
          <div style='font:600 1.08rem Space Grotesk;margin:9px 0'>Prioritise exceptions before the next hand-off.</div>
          <ul style='color:#A9B8CA;padding-left:18px;line-height:1.75'>
            <li>Resolve customs holds before destination arrival to reduce storage exposure.</li>
            <li>Escalate shipments whose ETA has passed without a delivery milestone.</li>
            <li>Review quote margins below the commercial target before release.</li>
            <li>Reconcile payable and receivable invoices against the shipment record.</li>
          </ul>
          <div class='small-muted'>This is a transparent rules-based demo assistant, not a live carrier feed or trained prediction model.</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.subheader("Recent operational activity")
    from ..db import get_session_factory, Milestone, Shipment
    from sqlalchemy import select, desc
    Session = get_session_factory()
    with Session() as db:
        rows = db.execute(select(Milestone, Shipment.reference).join(Shipment, Milestone.shipment_id == Shipment.id).order_by(desc(Milestone.occurred_at)).limit(8)).all()
    activity = [{"Time": m.occurred_at.strftime("%d %b %H:%M"), "Shipment": ref, "Event": m.event_name, "Location": m.location, "Source": m.source} for m, ref in rows]
    safe_dataframe(pd.DataFrame(activity), height=260)

    with st.expander("KPI definitions & assumptions"):
        st.markdown("""
        - **Active shipments:** excludes Delivered and Cancelled.
        - **On-time delivery:** delivered shipments with actual delivery timestamp at or before planned ETA; only delivered records are in the denominator.
        - **Open exceptions:** Open, In progress or Escalated exception records.
        - **Open receivables:** invoice records of type Receivable with status Outstanding.
        - **Gross profit pipeline:** gross profit across non-cancelled active shipments; not the same as recognised accounting revenue.
        - Financial totals are displayed by currency. The demo does not consolidate currencies or apply FX rates.
        - All demo transactions are synthetic. Dates are anchored to the classroom scenario date of 9 November 2026.
        """)
