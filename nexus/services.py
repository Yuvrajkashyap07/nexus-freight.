"""Business services: quote math, shipment transitions, exceptions and audit events."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, desc

from .constants import MILESTONE_CATALOG
from .db import (
    AuditLog, Carrier, Customer, ExceptionRecord, Invoice, Milestone, Quote,
    Shipment, get_session_factory, utcnow,
)
from .seed import ORG_ID


ALLOWED_TRANSITIONS = {
    "Draft": {"Quoted", "Cancelled"},
    "Quoted": {"Booked", "Cancelled"},
    "Booked": {"In transit", "Exception", "Cancelled"},
    "In transit": {"Customs hold", "Exception", "Delivered"},
    "Customs hold": {"In transit", "Exception", "Delivered"},
    "Exception": {"In transit", "Customs hold", "Delivered"},
    "Delivered": set(),
    "Cancelled": set(),
}


def calculate_quote(
    freight_cost: float, fuel_surcharge: float, origin_handling: float,
    destination_handling: float, customs_cost: float, insurance_cost: float,
    other_cost: float, target_margin_pct: float,
) -> dict[str, float]:
    components = [freight_cost, fuel_surcharge, origin_handling, destination_handling, customs_cost, insurance_cost, other_cost]
    if any(float(x) < 0 for x in components):
        raise ValueError("Cost components cannot be negative.")
    margin = float(target_margin_pct) / 100
    if not 0 <= margin <= 0.80:
        raise ValueError("Target gross margin must be between 0% and 80%.")
    total_buy = sum(float(x) for x in components)
    sell_price = total_buy / (1 - margin) if total_buy else 0.0
    gross_profit = sell_price - total_buy
    return {
        "total_buy": round(total_buy, 2), "sell_price": round(sell_price, 2),
        "gross_profit": round(gross_profit, 2), "gross_margin_pct": round((gross_profit / sell_price * 100) if sell_price else 0, 2),
        "markup_pct": round((gross_profit / total_buy * 100) if total_buy else 0, 2),
    }


def log_action(db, actor: str, action: str, entity_type: str, entity_id: str, details: str = "") -> None:
    db.add(AuditLog(organization_id=ORG_ID, actor=actor, action=action, entity_type=entity_type, entity_id=str(entity_id), details=details))


def create_quote(payload: dict, actor: str = "Pricing Analyst") -> str:
    math = calculate_quote(
        payload["freight_cost"], payload["fuel_surcharge"], payload["origin_handling"],
        payload["destination_handling"], payload["customs_cost"], payload["insurance_cost"],
        payload["other_cost"], payload["margin_pct"],
    )
    Session = get_session_factory()
    quote_id = str(uuid.uuid4())
    with Session() as db:
        q = Quote(
            id=quote_id, organization_id=ORG_ID,
            quote_number=f"QT-{datetime.utcnow():%y%m%d}-{uuid.uuid4().hex[:4].upper()}",
            customer_id=int(payload["customer_id"]), origin=payload["origin"], destination=payload["destination"],
            mode=payload["mode"], currency=payload.get("currency", "USD"),
            freight_cost=float(payload["freight_cost"]), fuel_surcharge=float(payload["fuel_surcharge"]),
            origin_handling=float(payload["origin_handling"]), destination_handling=float(payload["destination_handling"]),
            customs_cost=float(payload["customs_cost"]), insurance_cost=float(payload["insurance_cost"]),
            other_cost=float(payload["other_cost"]), total_buy=math["total_buy"], margin_pct=float(payload["margin_pct"]),
            sell_price=math["sell_price"], gross_profit=math["gross_profit"], status="Draft",
            valid_until=utcnow() + timedelta(days=int(payload.get("valid_days", 14))),
        )
        db.add(q)
        log_action(db, actor, "QUOTE_CREATED", "quote", quote_id, f"{q.quote_number}; sell={q.sell_price:.2f} {q.currency}")
        db.commit()
    return quote_id


def convert_quote_to_shipment(quote_id: str, carrier_id: int, actor: str = "Operations Manager") -> str:
    Session = get_session_factory()
    with Session() as db:
        q = db.scalar(select(Quote).where(Quote.id == quote_id, Quote.organization_id == ORG_ID))
        if not q:
            raise ValueError("Quote not found.")
        if q.status == "Accepted":
            raise ValueError("This quote has already been converted.")
        customer = db.get(Customer, q.customer_id)
        from .constants import PORTS
        op = PORTS.get(q.origin, {"code": "", "lat": 0, "lon": 0})
        dp = PORTS.get(q.destination, {"code": "", "lat": 0, "lon": 0})
        shipment_id = str(uuid.uuid4())
        shipment = Shipment(
            id=shipment_id, organization_id=ORG_ID,
            reference=f"NXS-{datetime.utcnow():%y%m%d}-{uuid.uuid4().hex[:4].upper()}",
            customer_id=q.customer_id, carrier_id=int(carrier_id), mode=q.mode, status="Booked",
            origin=q.origin, destination=q.destination, origin_code=op["code"], destination_code=dp["code"],
            origin_lat=op["lat"], origin_lon=op["lon"], destination_lat=dp["lat"], destination_lon=dp["lon"],
            cargo_description="Cargo from accepted quotation", container_no="", container_type="N/A",
            weight_kg=0, volume_cbm=0, incoterm="FOB", currency=q.currency,
            etd=utcnow() + timedelta(days=2), eta=utcnow() + timedelta(days=18),
            buy_cost=q.total_buy, sell_price=q.sell_price, gross_profit=q.gross_profit,
        )
        db.add(shipment)
        db.add(Milestone(shipment_id=shipment_id, event_code="BOOKING_CONFIRMED", event_name="Booking confirmed", location=q.origin, source="NEXUS workflow", note=f"Converted from {q.quote_number}."))
        q.status = "Accepted"
        log_action(db, actor, "QUOTE_CONVERTED", "quote", quote_id, f"Created shipment {shipment.reference}; customer={customer.name if customer else q.customer_id}")
        db.commit()
        return shipment_id


def update_shipment_status(shipment_id: str, new_status: str, note: str = "", actor: str = "Operations Manager") -> None:
    Session = get_session_factory()
    with Session() as db:
        shipment = db.scalar(select(Shipment).where(Shipment.id == shipment_id, Shipment.organization_id == ORG_ID))
        if not shipment:
            raise ValueError("Shipment not found.")
        allowed = ALLOWED_TRANSITIONS.get(shipment.status, set())
        if new_status not in allowed:
            raise ValueError(f"Invalid status transition: {shipment.status} → {new_status}.")
        shipment.status = new_status
        event_code = {
            "Booked": "BOOKING_CONFIRMED", "In transit": "VESSEL_DEPARTED",
            "Customs hold": "CUSTOMS_HOLD", "Delivered": "DELIVERED",
        }.get(new_status, "STATUS_UPDATED")
        event_name = MILESTONE_CATALOG.get(event_code, f"Status changed to {new_status}")
        location = shipment.destination if new_status in ["Customs hold", "Delivered"] else shipment.origin
        db.add(Milestone(shipment_id=shipment.id, event_code=event_code, event_name=event_name, location=location, source="NEXUS user action", note=note or f"Status updated by {actor}."))
        if new_status == "Delivered":
            shipment.actual_delivery = utcnow()
        log_action(db, actor, "SHIPMENT_STATUS_CHANGED", "shipment", shipment.id, f"{new_status}; {note}")
        db.commit()


def create_shipment(payload: dict, actor: str = "Operations Manager") -> str:
    from .constants import PORTS
    origin = PORTS[payload["origin"]]
    destination = PORTS[payload["destination"]]
    Session = get_session_factory()
    shipment_id = str(uuid.uuid4())
    with Session() as db:
        ref = f"NXS-{datetime.utcnow():%y%m%d}-{uuid.uuid4().hex[:4].upper()}"
        shipment = Shipment(
            id=shipment_id, organization_id=ORG_ID, reference=ref,
            customer_id=int(payload["customer_id"]), carrier_id=int(payload["carrier_id"]),
            mode=payload["mode"], status="Booked", origin=payload["origin"], destination=payload["destination"],
            origin_code=origin["code"], destination_code=destination["code"],
            origin_lat=origin["lat"], origin_lon=origin["lon"], destination_lat=destination["lat"], destination_lon=destination["lon"],
            cargo_description=payload["cargo_description"], container_no=payload.get("container_no", ""),
            container_type=payload.get("container_type", "N/A"), weight_kg=float(payload["weight_kg"]),
            volume_cbm=float(payload["volume_cbm"]), incoterm=payload.get("incoterm", "FOB"), currency=payload.get("currency", "USD"),
            etd=payload["etd"], eta=payload["eta"], buy_cost=float(payload["buy_cost"]), sell_price=float(payload["sell_price"]),
            gross_profit=float(payload["sell_price"])-float(payload["buy_cost"]),
        )
        db.add(shipment)
        db.add(Milestone(shipment_id=shipment_id, event_code="BOOKING_CONFIRMED", event_name="Booking confirmed", location=payload["origin"], source="NEXUS user action", note="Shipment created from operations workspace."))
        log_action(db, actor, "SHIPMENT_CREATED", "shipment", shipment_id, ref)
        db.commit()
    return shipment_id


def update_exception(exception_id: str, status: str, owner: str, note: str = "", actor: str = "Operations Manager") -> None:
    Session = get_session_factory()
    with Session() as db:
        record = db.scalar(select(ExceptionRecord).where(ExceptionRecord.id == exception_id, ExceptionRecord.organization_id == ORG_ID))
        if not record:
            raise ValueError("Exception not found.")
        record.status = status
        record.owner = owner
        if status == "Resolved":
            record.resolved_at = utcnow()
        log_action(db, actor, "EXCEPTION_UPDATED", "exception", exception_id, f"{status}; owner={owner}; {note}")
        db.commit()


def create_exception(shipment_id: str, category: str, severity: str, description: str, action: str, actor: str = "Operations Manager") -> str:
    Session = get_session_factory()
    exception_id = str(uuid.uuid4())
    with Session() as db:
        db.add(ExceptionRecord(id=exception_id, organization_id=ORG_ID, shipment_id=shipment_id, category=category, severity=severity, description=description, recommended_action=action))
        log_action(db, actor, "EXCEPTION_RAISED", "exception", exception_id, category)
        db.commit()
    return exception_id


def add_document(filename: str, category: str, mime_type: str, text: str, fields_json: str, shipment_id: str | None = None) -> str:
    from .db import DocumentRecord
    Session = get_session_factory()
    document_id = str(uuid.uuid4())
    with Session() as db:
        db.add(DocumentRecord(id=document_id, organization_id=ORG_ID, shipment_id=shipment_id, filename=filename, category=category, mime_type=mime_type, extracted_text=text[:30000], extracted_fields_json=fields_json))
        log_action(db, "Document Desk", "DOCUMENT_PROCESSED", "document", document_id, filename)
        db.commit()
    return document_id


def add_audit(actor: str, action: str, entity_type: str, entity_id: str, details: str = "") -> None:
    Session = get_session_factory()
    with Session() as db:
        log_action(db, actor, action, entity_type, entity_id, details)
        db.commit()


def update_invoice_status(invoice_id: str, status: str, reference: str = "", actor: str = "Finance Controller") -> None:
    from .db import Invoice
    if status not in {"Paid", "Disputed", "On hold"}:
        raise ValueError("Unsupported invoice status.")
    Session = get_session_factory()
    with Session() as db:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.organization_id == ORG_ID).one_or_none()
        if not invoice:
            raise ValueError("Invoice not found.")
        invoice.status = status
        if status == "Paid":
            invoice.paid_date = utcnow()
        log_action(db, actor, "INVOICE_RECONCILED", "invoice", invoice_id, f"{status}; reference={reference}")
        db.commit()
