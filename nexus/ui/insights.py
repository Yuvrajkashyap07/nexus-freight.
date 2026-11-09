from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import select

from ..analytics import calculate_carrier_scorecard
from ..db import get_session_factory, Customer, Invoice
from ..services import add_audit, update_invoice_status
from ..seed import ORG_ID
from .common import page_header, plotly_dark, safe_dataframe, usd, currency_breakdown


def render_network(data: dict[str, pd.DataFrame]) -> None:
    page_header("NETWORK INTELLIGENCE", "Carrier & lane analytics", "Compare partner reliability, transport mode economics and route-level performance.")
    s = data["shipments"].copy()
    if s.empty:
        st.info("No shipment records available.")
        return
    scorecard = calculate_carrier_scorecard(s)
    a, b, c = st.columns(3)
    a.metric("Active carriers", int(data["carriers"].active.sum()) if not data["carriers"].empty else 0)
    b.metric("Gross profit pipeline", currency_breakdown(s, "gross_profit"), help="Separated by currency; no FX conversion is applied.")
    c.metric("Distinct trade lanes", s[["origin", "destination"]].drop_duplicates().shape[0])
    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Carrier scorecard")
        if not scorecard.empty:
            fig = px.bar(scorecard, x="Carrier", y="On-time %", color="On-time %", range_y=[0, 100], text="On-time %", color_continuous_scale=["#F07178", "#F4B860", "#35C98A"])
            fig.add_hline(y=95, line_dash="dash", line_color="#F4B860", annotation_text="95% target")
            st.plotly_chart(plotly_dark(fig, 320), use_container_width=True)
            safe_dataframe(scorecard, height=230)
    with right:
        st.subheader("Mode economics")
        mode = s.groupby(["mode", "currency"], as_index=False).agg(Shipments=("id", "count"), Revenue=("sell_price", "sum"), BuyCost=("buy_cost", "sum"), GrossProfit=("gross_profit", "sum"))
        mode["Margin %"] = (mode.GrossProfit / mode.Revenue * 100).round(1)
        mode["Mode / currency"] = mode["mode"] + " · " + mode["currency"]
        fig = px.scatter(mode, x="Shipments", y="Margin %", size="Revenue", color="Mode / currency", hover_name="Mode / currency", title="Volume vs gross margin · bubble size = sell value")
        st.plotly_chart(plotly_dark(fig, 320), use_container_width=True)
        safe_dataframe(mode.rename(columns={"mode":"Mode", "Shipments":"Shipments", "Revenue":"Revenue", "BuyCost":"Buy cost", "GrossProfit":"Gross profit"}), height=230)

    st.divider()
    st.subheader("Top trade lanes")
    lanes = s.groupby(["origin", "destination", "mode", "currency"], as_index=False).agg(Shipments=("id", "count"), Revenue=("sell_price", "sum"), GrossProfit=("gross_profit", "sum"))
    lanes["Lane"] = lanes.origin + " → " + lanes.destination + " · " + lanes.currency
    lanes = lanes.sort_values(["Shipments", "GrossProfit"], ascending=False).head(15)
    fig = px.bar(lanes.sort_values("GrossProfit"), x="GrossProfit", y="Lane", orientation="h", color="mode", hover_data=["Shipments", "Revenue"])
    st.plotly_chart(plotly_dark(fig, 430), use_container_width=True)


def render_finance(data: dict[str, pd.DataFrame], actor: str, permissions: list[str]) -> None:
    page_header("FINANCIAL CONTROL", "Freight finance", "Shipment-level gross profit, receivables, payables and ageing exposure.")
    inv = data["invoices"].copy()
    s = data["shipments"].copy()
    if inv.empty:
        st.info("No invoice records available.")
        return
    currency_options = sorted(inv.currency.dropna().unique().tolist()) or ["USD"]
    reporting_currency = st.selectbox("Reporting currency (no FX conversion)", currency_options)
    inv_currency = inv[inv.currency == reporting_currency]
    s_currency = s[s.currency == reporting_currency]
    ar = inv_currency[(inv_currency.invoice_type == "Receivable") & (inv_currency.status == "Outstanding")]
    ap = inv_currency[(inv_currency.invoice_type == "Payable") & (inv_currency.status == "Outstanding")]
    paid_ar = inv_currency[(inv_currency.invoice_type == "Receivable") & (inv_currency.status == "Paid")]
    c = st.columns(4)
    c[0].metric("Open receivables", usd(ar.amount.sum()))
    c[1].metric("Open payables", usd(ap.amount.sum()))
    c[2].metric("Collected receivables", usd(paid_ar.amount.sum()))
    c[3].metric("Shipment gross profit", usd(s_currency.gross_profit.sum(), reporting_currency))
    left, right = st.columns([1.05, 1])
    with left:
        st.subheader("Accounts receivable / payable")
        summary = pd.DataFrame({"Type": ["Receivable", "Payable"], "Outstanding": [ar.amount.sum(), ap.amount.sum()]})
        fig = px.bar(summary, x="Type", y="Outstanding", color="Type", text_auto=".2s")
        st.plotly_chart(plotly_dark(fig, 270), use_container_width=True)
    with right:
        st.subheader("Receivables ageing")
        as_of = pd.Timestamp("2026-11-09")
        if not ar.empty:
            ar = ar.copy()
            ar["days_overdue"] = (as_of - pd.to_datetime(ar.due_date)).dt.days.clip(lower=0)
            ar["bucket"] = pd.cut(ar.days_overdue, bins=[-1, 0, 30, 60, 90, 100000], labels=["Not due", "1–30 days", "31–60 days", "61–90 days", "90+ days"])
            aging = ar.groupby("bucket", observed=False).amount.sum().reset_index()
            fig = px.bar(aging, x="bucket", y="amount", color="bucket")
            st.plotly_chart(plotly_dark(fig, 270), use_container_width=True)
        else:
            st.success("No open receivables.")
    st.markdown("#### Invoice ledger")
    table = inv_currency.merge(s[["id", "reference", "customer", "origin", "destination"]], left_on="shipment_id", right_on="id", how="left")
    view = table[["invoice_number", "invoice_type", "reference", "customer", "amount", "currency", "status", "issue_date", "due_date"]].copy()
    view["issue_date"] = pd.to_datetime(view.issue_date).dt.strftime("%d %b %Y")
    view["due_date"] = pd.to_datetime(view.due_date).dt.strftime("%d %b %Y")
    safe_dataframe(view.rename(columns={"invoice_number":"Invoice", "invoice_type":"Type", "reference":"Shipment", "customer":"Customer", "amount":"Amount", "currency":"Currency", "status":"Status", "issue_date":"Issued", "due_date":"Due date"}), height=340)
    if "finance" in permissions:
        st.markdown("#### Manual settlement reconciliation")
        st.caption("Records a finance-team settlement status in the demo ledger. This does not initiate or verify a bank transfer.")
        outstanding = table[table.status == "Outstanding"]
        if not outstanding.empty:
            invoice_map = {f"{r.invoice_number} · {r.invoice_type} · {r.amount:,.2f} {r.currency}": r.id_x for _, r in outstanding.iterrows()}
            with st.form("invoice_reconcile_form"):
                selected_invoice = st.selectbox("Outstanding invoice", list(invoice_map.keys()))
                next_status = st.selectbox("Reconciliation result", ["Paid", "Disputed", "On hold"])
                reference = st.text_input("Payment / dispute reference", placeholder="Bank reference or case ID")
                if st.form_submit_button("Update finance ledger", type="primary"):
                    try:
                        update_invoice_status(invoice_map[selected_invoice], next_status, reference, actor)
                        st.success("Invoice ledger updated and audit event recorded.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
        else:
            st.success("No outstanding invoices to reconcile.")


def render_customers(data: dict[str, pd.DataFrame], actor: str, permissions: list[str]) -> None:
    page_header("CUSTOMER MANAGEMENT", "Customer directory", "Customer segmentation, commercial terms and account exposure.")
    customers = data["customers"].copy()
    s = data["shipments"].copy()
    inv = data["invoices"].copy()
    if not customers.empty:
        if not inv.empty:
            ar_detail = inv[(inv.invoice_type == "Receivable") & (inv.status == "Outstanding")].merge(s[["id", "customer"]], left_on="shipment_id", right_on="id", how="left")
            outstanding_by_customer = ar_detail.groupby(["customer", "currency"]).amount.sum().reset_index()
            ar_labels = outstanding_by_customer.assign(label=outstanding_by_customer.apply(lambda r: f"{r.currency} {r.amount:,.0f}", axis=1)).groupby("customer").label.apply(" · ".join)
        else:
            ar_labels = pd.Series(dtype=str)
        customer_summary = customers.copy()
        customer_summary["Outstanding AR (by currency)"] = customer_summary.name.map(ar_labels).fillna("—")
        customer_summary["Shipments"] = customer_summary.name.map(s.groupby("customer").size()).fillna(0).astype(int)
        c = st.columns(3)
        c[0].metric("Customer accounts", len(customers))
        c[1].metric("Enterprise accounts", int((customers.segment == "Enterprise").sum()))
        c[2].metric("Total credit limits", usd(customers.credit_limit.sum()))
        safe_dataframe(customer_summary.rename(columns={"name":"Customer", "country":"Country", "segment":"Segment", "contact_email":"Contact", "payment_terms":"Terms", "credit_limit":"Credit limit"})[["Customer", "Country", "Segment", "Contact", "Terms", "Credit limit", "Outstanding AR (by currency)", "Shipments"]], height=330)
    if "write" in permissions:
        with st.expander("＋ Add customer account"):
            with st.form("customer_create_form"):
                a, b, c = st.columns(3)
                name = a.text_input("Legal / trading name")
                country = b.text_input("Country")
                segment = c.selectbox("Segment", ["SME", "Mid-market", "Enterprise"])
                a, b, c = st.columns(3)
                email = a.text_input("Operations email")
                terms = b.selectbox("Payment terms", ["Prepaid", "Net 15", "Net 30", "Net 45", "Net 60"])
                limit = c.number_input("Credit limit (USD)", min_value=0.0, value=25000.0, step=5000.0)
                if st.form_submit_button("Create customer"):
                    if not name.strip():
                        st.error("Customer name is required.")
                    else:
                        Session = get_session_factory()
                        with Session() as db:
                            item = Customer(organization_id=ORG_ID, name=name.strip(), country=country.strip(), segment=segment, contact_email=email.strip(), payment_terms=terms, credit_limit=limit)
                            db.add(item); db.commit(); customer_id = item.id
                        add_audit(actor, "CUSTOMER_CREATED", "customer", customer_id, name)
                        st.success("Customer created.")
                        st.rerun()


def render_insights(data: dict[str, pd.DataFrame], actor: str, permissions: list[str]) -> None:
    tab1, tab2, tab3 = st.tabs(["Carrier & lanes", "Finance", "Customers"])
    with tab1:
        render_network(data)
    with tab2:
        render_finance(data, actor, permissions)
    with tab3:
        render_customers(data, actor, permissions)
