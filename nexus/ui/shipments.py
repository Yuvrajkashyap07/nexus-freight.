from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from sqlalchemy import select, desc

from ..constants import DEMO_AS_OF, PORTS, MODES, INCOTERMS, CURRENCIES
from ..db import get_session_factory, Shipment, Milestone, Customer, Carrier
from ..services import create_shipment, update_shipment_status, ALLOWED_TRANSITIONS
from .common import page_header, safe_dataframe, usd


def render(data: dict[str, pd.DataFrame], actor: str, permissions: list[str]) -> None:
    page_header("EXECUTION WORKSPACE", "Shipment operations", "Create, monitor and update every shipment from booking through delivery.")
    s = data["shipments"].copy()
    c1, c2, c3 = st.columns(3)
    search = c1.text_input("Search shipments", placeholder="Reference, customer, container or port")
    mode_filter = c2.multiselect("Transport mode", sorted(s["mode"].unique().tolist()) if not s.empty else MODES, default=[])
    status_filter = c3.multiselect("Status", sorted(s.status.unique().tolist()) if not s.empty else [], default=[])
    filtered = s.copy()
    if search:
        needle = search.lower()
        mask = filtered.apply(lambda r: any(needle in str(r[col]).lower() for col in ["reference", "customer", "container_no", "origin", "destination"]), axis=1)
        filtered = filtered[mask]
    if mode_filter:
        filtered = filtered[filtered["mode"].isin(mode_filter)]
    if status_filter:
        filtered = filtered[filtered.status.isin(status_filter)]
    display_cols = ["reference", "customer", "mode", "origin", "destination", "status", "etd", "eta", "carrier", "sell_price", "gross_profit", "currency"]
    if not filtered.empty:
        table = filtered[display_cols].copy()
        table["etd"] = pd.to_datetime(table.etd).dt.strftime("%d %b %Y")
        table["eta"] = pd.to_datetime(table.eta).dt.strftime("%d %b %Y")
        table["sell_price"] = table.apply(lambda r: f"{r.sell_price:,.0f} {r.currency}", axis=1)
        table["gross_profit"] = table.gross_profit.map(lambda x: f"{x:,.0f}")
        st.dataframe(table.rename(columns={"reference":"Reference", "customer":"Customer", "mode":"Mode", "origin":"Origin", "destination":"Destination", "status":"Status", "etd":"ETD", "eta":"ETA", "carrier":"Carrier", "sell_price":"Sell price", "gross_profit":"Gross profit"}), use_container_width=True, hide_index=True, height=330)
    else:
        st.info("No shipments match the current filters.")

    st.divider()
    st.subheader("Shipment workspace")
    if not filtered.empty:
        options = {f"{r.reference} · {r.customer} · {r.origin} → {r.destination}": r.id for _, r in filtered.iterrows()}
        selected_label = st.selectbox("Select a shipment", list(options.keys()))
        shipment_id = options[selected_label]
        row = filtered[filtered.id == shipment_id].iloc[0]
        left, right = st.columns([1.15, 1])
        with left:
            st.markdown(f"### {row.reference}")
            st.caption(f"{row.customer} · {row["mode"]} · {row.carrier}")
            st.markdown(f"**{row.origin}** → **{row.destination}**")
            metric_cols = st.columns(3)
            metric_cols[0].metric("Status", row.status)
            metric_cols[1].metric("Gross profit", usd(row.gross_profit, row.currency))
            metric_cols[2].metric("Weight", f"{row.weight_kg:,.0f} kg")
            st.write(f"**Cargo:** {row.cargo_description}")
            st.write(f"**Equipment:** {row.container_no or 'Not assigned'} · {row.container_type}")
            st.write(f"**Incoterm:** {row.incoterm} · **Volume:** {row.volume_cbm:,.1f} CBM")
        with right:
            st.markdown("#### Update shipment status")
            allowed = sorted(ALLOWED_TRANSITIONS.get(row.status, set()))
            if not allowed:
                st.info("This shipment is in a terminal state. No further status transitions are allowed.")
            elif "write" in permissions:
                with st.form("shipment_status_form"):
                    next_status = st.selectbox("Next status", allowed)
                    note = st.text_area("Operational note", placeholder="Carrier update, customs reference or delivery note…")
                    if st.form_submit_button("Apply status update", type="primary"):
                        try:
                            update_shipment_status(shipment_id, next_status, note, actor)
                            st.success(f"Shipment updated to {next_status}.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
            else:
                st.info("Your demo role is read-only for shipment updates.")

        Session = get_session_factory()
        with Session() as db:
            events = db.scalars(select(Milestone).where(Milestone.shipment_id == shipment_id).order_by(desc(Milestone.occurred_at))).all()
        st.markdown("#### Shipment event timeline")
        if events:
            timeline = pd.DataFrame([{"Event": e.event_name, "Location": e.location, "Time": e.occurred_at.strftime("%d %b %Y · %H:%M"), "Source": e.source, "Note": e.note} for e in events])
            safe_dataframe(timeline, height=240)
        else:
            st.info("No milestones recorded yet.")

    if "write" in permissions:
        with st.expander("＋ Create a new shipment", expanded=False):
            Session = get_session_factory()
            with Session() as db:
                customers = db.scalars(select(Customer).order_by(Customer.name)).all()
                carriers = db.scalars(select(Carrier).where(Carrier.active.is_(True)).order_by(Carrier.name)).all()
            customer_map = {f"{c.name} · {c.country}": c.id for c in customers}
            carrier_map = {c.name: c.id for c in carriers}
            with st.form("create_shipment_form"):
                a, b, c = st.columns(3)
                customer_label = a.selectbox("Customer", list(customer_map.keys()))
                carrier_label = b.selectbox("Carrier", list(carrier_map.keys()))
                mode = c.selectbox("Transport mode", MODES)
                a, b = st.columns(2)
                origin = a.selectbox("Origin", list(PORTS.keys()), index=0)
                destination = b.selectbox("Destination", list(PORTS.keys()), index=3)
                a, b, c = st.columns(3)
                cargo = a.text_input("Cargo description", "General cargo")
                container = b.text_input("Container / equipment no.", "")
                container_type = c.selectbox("Equipment type", ["40HC", "40GP", "20GP", "45HC", "ULD", "N/A"])
                a, b, c = st.columns(3)
                weight = a.number_input("Gross weight (kg)", min_value=0.0, value=12000.0, step=100.0)
                volume = b.number_input("Volume (CBM)", min_value=0.0, value=28.0, step=1.0)
                incoterm = c.selectbox("Incoterm", INCOTERMS, index=2)
                a, b, c, d = st.columns(4)
                etd = a.date_input("ETD", value=DEMO_AS_OF + timedelta(days=2))
                eta = b.date_input("ETA", value=DEMO_AS_OF + timedelta(days=23))
                buy = c.number_input("Buy cost (USD)", min_value=0.0, value=4200.0, step=100.0)
                sell = d.number_input("Sell price (USD)", min_value=0.0, value=5400.0, step=100.0)
                if st.form_submit_button("Create shipment", type="primary"):
                    if origin == destination:
                        st.error("Origin and destination must be different.")
                    elif eta <= etd:
                        st.error("ETA must be after ETD.")
                    elif sell < buy:
                        st.error("Sell price is below buy cost. Confirm the loss-making shipment before creating.")
                    else:
                        try:
                            create_shipment({
                                "customer_id": customer_map[customer_label], "carrier_id": carrier_map[carrier_label],
                                "mode": mode, "origin": origin, "destination": destination,
                                "cargo_description": cargo, "container_no": container, "container_type": container_type,
                                "weight_kg": weight, "volume_cbm": volume, "incoterm": incoterm,
                                "etd": datetime.combine(etd, datetime.min.time()), "eta": datetime.combine(eta, datetime.min.time()),
                                "buy_cost": buy, "sell_price": sell,
                            }, actor)
                            st.success("Shipment created and booking milestone added.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Unable to create shipment: {exc}")
    else:
        st.caption("Shipment creation is available to Operations Manager demo role.")
