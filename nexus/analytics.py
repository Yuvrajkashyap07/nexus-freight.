"""Analytics and explainable operational decision support."""
from __future__ import annotations

from datetime import date
from collections import defaultdict

import pandas as pd
from sqlalchemy import select

from .db import Shipment, ExceptionRecord, Invoice, Carrier, Customer, Quote, get_session_factory
from .seed import ORG_ID


def load_frames() -> dict[str, pd.DataFrame]:
    Session = get_session_factory()
    with Session() as db:
        shipments = db.scalars(select(Shipment).where(Shipment.organization_id == ORG_ID)).all()
        customers = db.scalars(select(Customer).where(Customer.organization_id == ORG_ID)).all()
        carriers = db.scalars(select(Carrier).where(Carrier.organization_id == ORG_ID)).all()
        exceptions = db.scalars(select(ExceptionRecord).where(ExceptionRecord.organization_id == ORG_ID)).all()
        invoices = db.scalars(select(Invoice).where(Invoice.organization_id == ORG_ID)).all()
        quotes = db.scalars(select(Quote).where(Quote.organization_id == ORG_ID)).all()
        shipment_rows = []
        for s in shipments:
            shipment_rows.append({
                "id": s.id, "reference": s.reference, "customer_id": s.customer_id,
                "customer": s.customer.name if s.customer else "Unknown", "carrier_id": s.carrier_id,
                "carrier": s.carrier.name if s.carrier else "Unassigned", "mode": s.mode,
                "status": s.status, "origin": s.origin, "destination": s.destination,
                "origin_code": s.origin_code, "destination_code": s.destination_code,
                "origin_lat": s.origin_lat, "origin_lon": s.origin_lon,
                "destination_lat": s.destination_lat, "destination_lon": s.destination_lon,
                "cargo_description": s.cargo_description, "container_no": s.container_no,
                "container_type": s.container_type, "weight_kg": s.weight_kg, "volume_cbm": s.volume_cbm,
                "incoterm": s.incoterm, "currency": s.currency, "etd": s.etd, "eta": s.eta,
                "actual_delivery": s.actual_delivery, "buy_cost": s.buy_cost,
                "sell_price": s.sell_price, "gross_profit": s.gross_profit,
            })
        ex_rows = [{"id": x.id, "shipment_id": x.shipment_id, "category": x.category, "severity": x.severity,
                    "description": x.description, "recommended_action": x.recommended_action, "owner": x.owner,
                    "status": x.status, "created_at": x.created_at} for x in exceptions]
        inv_rows = [{"id": x.id, "shipment_id": x.shipment_id, "invoice_number": x.invoice_number,
                     "invoice_type": x.invoice_type, "amount": x.amount, "currency": x.currency,
                     "status": x.status, "issue_date": x.issue_date, "due_date": x.due_date, "paid_date": x.paid_date} for x in invoices]
        carrier_rows = [{"id": c.id, "name": c.name, "modes": c.modes, "on_time_target": c.on_time_target, "active": c.active} for c in carriers]
        customer_rows = [{"id": c.id, "name": c.name, "country": c.country, "segment": c.segment,
                          "contact_email": c.contact_email, "payment_terms": c.payment_terms, "credit_limit": c.credit_limit} for c in customers]
        quote_rows = [{"id": q.id, "quote_number": q.quote_number, "customer_id": q.customer_id,
                       "customer": q.customer.name if q.customer else "Unknown", "origin": q.origin,
                       "destination": q.destination, "mode": q.mode, "currency": q.currency,
                       "total_buy": q.total_buy, "margin_pct": q.margin_pct, "sell_price": q.sell_price,
                       "gross_profit": q.gross_profit, "status": q.status, "created_at": q.created_at,
                       "valid_until": q.valid_until} for q in quotes]
    return {
        "shipments": pd.DataFrame(shipment_rows), "exceptions": pd.DataFrame(ex_rows),
        "invoices": pd.DataFrame(inv_rows), "carriers": pd.DataFrame(carrier_rows),
        "customers": pd.DataFrame(customer_rows), "quotes": pd.DataFrame(quote_rows),
    }


def calculate_risk(row: dict, as_of: date | None = None) -> tuple[int, str, list[str]]:
    """Transparent rule-based risk score; not a trained ETA prediction model."""
    as_of = as_of or date.today()
    score = 0
    reasons: list[str] = []
    status = str(row.get("status", ""))
    eta = row.get("eta")
    if status == "Customs hold":
        score += 50; reasons.append("Customs hold is active")
    if status == "Exception":
        score += 35; reasons.append("Shipment has an active exception status")
    if eta is not None and hasattr(eta, "date") and eta.date() < as_of and status not in ["Delivered", "Cancelled"]:
        score += 35; reasons.append("Planned ETA has passed")
    if status in ["Booked", "In transit"] and eta is not None and hasattr(eta, "date"):
        days = (eta.date() - as_of).days
        if 0 <= days <= 2:
            score += 15; reasons.append("Arrival is within 48 hours")
    score = min(score, 100)
    band = "Critical" if score >= 70 else ("High" if score >= 45 else ("Medium" if score >= 20 else "Low"))
    return score, band, reasons


def calculate_carrier_scorecard(shipments: pd.DataFrame) -> pd.DataFrame:
    if shipments.empty:
        return pd.DataFrame(columns=["Carrier", "Shipments", "Delivered", "On-time %", "Gross profit", "Target %"])
    rows = []
    for (carrier, currency), grp in shipments.groupby(["carrier", "currency"]):
        delivered = grp[grp.status == "Delivered"]
        on_time = 0
        for _, r in delivered.iterrows():
            if pd.notna(r.actual_delivery) and pd.notna(r.eta) and r.actual_delivery.date() <= r.eta.date():
                on_time += 1
        rate = (on_time / len(delivered) * 100) if len(delivered) else 0
        rows.append({"Carrier": carrier, "Currency": currency, "Shipments": len(grp), "Delivered": len(delivered),
                     "On-time %": round(rate, 1), "Gross profit": grp.gross_profit.sum(), "Target %": 95.0})
    return pd.DataFrame(rows).sort_values("Shipments", ascending=False)
