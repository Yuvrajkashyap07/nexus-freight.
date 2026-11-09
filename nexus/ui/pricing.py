from __future__ import annotations

from datetime import timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import select

from ..constants import CURRENCIES, MODES, PORTS
from ..db import get_session_factory, Customer, Carrier, Quote
from ..services import calculate_quote, create_quote, convert_quote_to_shipment
from .common import page_header, usd, plotly_dark, safe_dataframe, currency_breakdown


PLANS = [
    {"name": "Launch", "price": 149, "shipments": 250, "users": 3, "features": "Core operations · quote builder · shipment timeline · email support"},
    {"name": "Growth", "price": 499, "shipments": 1500, "users": 10, "features": "Workflow automation · exceptions · carrier scorecards · document desk"},
    {"name": "Scale", "price": 1499, "shipments": 7500, "users": 30, "features": "Multi-branch · advanced analytics · integrations · priority support"},
    {"name": "Enterprise", "price": None, "shipments": None, "users": None, "features": "Custom volume · SSO · dedicated controls · SLA · private deployment"},
]


def render(data: dict[str, pd.DataFrame], actor: str, permissions: list[str]) -> None:
    page_header("COMMERCIAL CONTROL", "Pricing & unit economics", "Two layers of pricing: the freight quote we sell to customers, and the NEXUS software subscription model.")
    tab_quote, tab_pipeline, tab_platform, tab_economics = st.tabs(["Freight quote calculator", "Quote pipeline", "Platform pricing", "Unit economics"])

    with tab_quote:
        st.subheader("Build a freight quotation")
        st.caption("Sell price is calculated from target gross margin: sell = total buy ÷ (1 − margin). This is not the same as adding a markup.")
        Session = get_session_factory()
        with Session() as db:
            customers = db.scalars(select(Customer).order_by(Customer.name)).all()
        customer_map = {f"{c.name} · {c.segment}": c.id for c in customers}
        if not customer_map:
            st.warning("Add customer records before creating a quote.")
        else:
            with st.form("freight_quote_form"):
                a, b, c = st.columns(3)
                customer_label = a.selectbox("Customer", list(customer_map.keys()))
                mode = b.selectbox("Transport mode", MODES)
                currency = c.selectbox("Currency", CURRENCIES, index=0)
                a, b = st.columns(2)
                origin = a.selectbox("Origin", list(PORTS.keys()), index=0)
                destination = b.selectbox("Destination", list(PORTS.keys()), index=3)
                st.markdown("**Buy-side cost stack**")
                a, b, c, d = st.columns(4)
                freight = a.number_input("Base freight", min_value=0.0, value=3250.0, step=100.0)
                fuel = b.number_input("Fuel / peak surcharge", min_value=0.0, value=380.0, step=25.0)
                origin_handling = c.number_input("Origin handling", min_value=0.0, value=180.0, step=25.0)
                destination_handling = d.number_input("Destination handling", min_value=0.0, value=240.0, step=25.0)
                a, b, c = st.columns(3)
                customs = a.number_input("Customs / brokerage", min_value=0.0, value=120.0, step=25.0)
                insurance = b.number_input("Insurance", min_value=0.0, value=65.0, step=10.0)
                other = c.number_input("Other cost", min_value=0.0, value=0.0, step=25.0)
                a, b = st.columns(2)
                margin = a.slider("Target gross margin", 0, 60, 18, 1, format="%d%%")
                valid_days = b.selectbox("Quote validity", [7, 14, 21, 30], index=1)
                submitted = st.form_submit_button("Calculate and save quote", type="primary", disabled="write_quote" not in permissions)
                if submitted:
                    if origin == destination:
                        st.error("Origin and destination must be different.")
                    else:
                        try:
                            calc = calculate_quote(freight, fuel, origin_handling, destination_handling, customs, insurance, other, margin)
                            quote_id = create_quote({
                                "customer_id": customer_map[customer_label], "origin": origin, "destination": destination,
                                "mode": mode, "currency": currency, "freight_cost": freight, "fuel_surcharge": fuel,
                                "origin_handling": origin_handling, "destination_handling": destination_handling,
                                "customs_cost": customs, "insurance_cost": insurance, "other_cost": other,
                                "margin_pct": margin, "valid_days": valid_days,
                            }, actor)
                            st.success(f"Quote saved. Sell price: {currency} {calc['sell_price']:,.2f} · gross profit: {currency} {calc['gross_profit']:,.2f}")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
        if "write_quote" not in permissions:
            st.info("Your demo persona can view quote pricing but cannot create or release quotes.")

    with tab_pipeline:
        st.subheader("Quote pipeline")
        q = data["quotes"].copy()
        if q.empty:
            st.info("No quotes found.")
        else:
            metrics = st.columns(4)
            metrics[0].metric("Total quotes", len(q))
            open_quotes = q[q.status.isin(["Draft", "Sent"])]
            metrics[1].metric("Open value", currency_breakdown(open_quotes, "sell_price"), help="Separated by currency; no FX conversion is applied.")
            metrics[2].metric("Accepted", int((q.status == "Accepted").sum()))
            metrics[3].metric("Win rate", f"{(q.status.eq('Accepted').mean()*100):.1f}%")
            table = q[["quote_number", "customer", "origin", "destination", "mode", "status", "total_buy", "sell_price", "gross_profit", "currency", "valid_until"]].copy()
            for col in ["total_buy", "sell_price", "gross_profit"]:
                table[col] = table.apply(lambda r: f"{r[col]:,.2f} {r.currency}", axis=1)
            table["valid_until"] = pd.to_datetime(table.valid_until).dt.strftime("%d %b %Y")
            safe_dataframe(table.rename(columns={"quote_number":"Quote", "customer":"Customer", "origin":"Origin", "destination":"Destination", "mode":"Mode", "status":"Status", "total_buy":"Total buy", "sell_price":"Sell price", "gross_profit":"Gross profit", "currency":"Currency", "valid_until":"Valid until"}), height=260)
            st.markdown("#### Convert an accepted quote into a shipment")
            Session = get_session_factory()
            with Session() as db:
                candidates = db.scalars(select(Quote).where(Quote.organization_id == "nexus-demo-org", Quote.status.in_(["Draft", "Sent"])).order_by(Quote.created_at.desc())).all()
                carriers = db.scalars(select(Carrier).where(Carrier.active.is_(True)).order_by(Carrier.name)).all()
            if candidates and carriers and "approve_quote" in permissions:
                q_map = {f"{x.quote_number} · {x.origin} → {x.destination} · {x.sell_price:,.0f} {x.currency}": x.id for x in candidates}
                c_map = {x.name: x.id for x in carriers}
                a, b, c = st.columns([2, 1, 1])
                quote_label = a.selectbox("Quote to convert", list(q_map.keys()))
                carrier_label = b.selectbox("Assign carrier", list(c_map.keys()))
                if c.button("Convert to booked shipment", type="primary", use_container_width=True):
                    try:
                        shipment_id = convert_quote_to_shipment(q_map[quote_label], c_map[carrier_label], actor)
                        st.success("Quote accepted and booked shipment created.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            elif "approve_quote" not in permissions:
                st.caption("Quote conversion is restricted to the Operations Manager demo persona.")
            else:
                st.info("No draft/sent quotes or active carriers available for conversion.")

    with tab_platform:
        st.subheader("NEXUS SaaS pricing architecture")
        st.caption("Illustrative launch pricing hypotheses for a global B2B SaaS product. Validate with customers before commercial release.")
        cols = st.columns(4)
        for i, plan in enumerate(PLANS):
            with cols[i]:
                st.markdown(f"<div class='nexus-card'><div class='nexus-card-label'>{plan['name']}</div><div class='nexus-card-value'>{('$'+format(plan['price'], ',')+'/mo') if plan['price'] else 'Custom'}</div><div class='nexus-card-sub'>{(format(plan['shipments'], ',')+' shipments/mo') if plan['shipments'] else 'Negotiated volume'}</div><p style='color:#A9B8CA;font-size:.82rem;margin-top:14px'>{plan['features']}</p></div>", unsafe_allow_html=True)
        st.markdown("#### Packaging principles")
        st.markdown("""
        - **Land:** Launch plan for a small forwarder testing digital operations.
        - **Expand:** Growth plan priced around active shipment volume, automation and team seats.
        - **Scale:** Multi-branch workflows, integrations, reporting and support commitments.
        - **Enterprise:** SSO, tenant-specific controls, SLAs, private connectivity and negotiated data retention.
        - Avoid unlimited AI/document-processing allowances until per-document and per-shipment costs are measured.
        """)

    with tab_economics:
        st.subheader("SaaS revenue and contribution model")
        st.caption("Scenario model only. Change customer mix and service costs to test pricing before presenting a business case.")
        a, b, c = st.columns(3)
        launch = a.number_input("Launch customers", min_value=0, value=120, step=10)
        growth = b.number_input("Growth customers", min_value=0, value=55, step=5)
        scale = c.number_input("Scale customers", min_value=0, value=12, step=1)
        a, b, c = st.columns(3)
        launch_cost = a.number_input("Launch service cost / mo", min_value=0.0, value=38.0, step=5.0)
        growth_cost = b.number_input("Growth service cost / mo", min_value=0.0, value=125.0, step=10.0)
        scale_cost = c.number_input("Scale service cost / mo", min_value=0.0, value=390.0, step=25.0)
        mrr = launch * 149 + growth * 499 + scale * 1499
        cogs = launch * launch_cost + growth * growth_cost + scale * scale_cost
        gross_profit = mrr - cogs
        gross_margin = gross_profit / mrr * 100 if mrr else 0
        k = st.columns(4)
        k[0].metric("Monthly recurring revenue", usd(mrr))
        k[1].metric("Annual recurring revenue", usd(mrr * 12))
        k[2].metric("Monthly service COGS", usd(cogs))
        k[3].metric("Gross margin", f"{gross_margin:.1f}%")
        scenario = pd.DataFrame({"Plan": ["Launch", "Growth", "Scale"], "Customers": [launch, growth, scale], "MRR": [launch*149, growth*499, scale*1499], "Service COGS": [launch*launch_cost, growth*growth_cost, scale*scale_cost]})
        fig = px.bar(scenario, x="Plan", y=["MRR", "Service COGS"], barmode="group", title="Monthly plan revenue vs service COGS")
        st.plotly_chart(plotly_dark(fig, 300), use_container_width=True)
        st.warning("Excludes sales, marketing, product development, G&A, taxes, payment fees, bad debt and enterprise implementation costs. ARR is a run-rate calculation, not recognised revenue.")
