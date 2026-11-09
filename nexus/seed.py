"""Seed a realistic, entirely synthetic demo network for classroom presentation."""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, func

from .constants import CARRIERS, CUSTOMER_NAMES, DEMO_AS_OF, PORTS, MILESTONE_CATALOG
from .db import (
    AuditLog, Carrier, Customer, ExceptionRecord, Invoice, Milestone,
    Organization, Quote, Shipment, get_session_factory, init_db,
)

ORG_ID = "nexus-demo-org"


def seed_demo_data(force: bool = False) -> None:
    init_db()
    Session = get_session_factory()
    rng = random.Random(42)
    with Session() as db:
        count = db.scalar(select(func.count()).select_from(Shipment)) or 0
        if count and not force:
            return
        if force:
            for model in [AuditLog, ExceptionRecord, Invoice, Milestone, DocumentRecordSafe, Shipment, Quote, Carrier, Customer, Organization]:
                db.query(model).delete()
            db.commit()

        db.add(Organization(id=ORG_ID, name="NEXUS Global Demo Forwarder", plan="Growth"))
        customers = []
        for i, name in enumerate(CUSTOMER_NAMES):
            customer = Customer(
                organization_id=ORG_ID, name=name,
                country=["Germany", "United States", "Singapore", "UAE", "India", "United Kingdom", "Netherlands"][i % 7],
                segment=["Enterprise", "Mid-market", "SME"][i % 3],
                contact_email=f"logistics.{i+1}@example.com", payment_terms=["Net 30", "Net 45", "Prepaid"][i % 3],
                credit_limit=round(rng.uniform(15000, 180000), 2),
            )
            db.add(customer)
            customers.append(customer)
        carriers = []
        for i, name in enumerate(CARRIERS):
            carrier = Carrier(organization_id=ORG_ID, name=name, modes=["Ocean FCL, Ocean LCL", "Air", "Road, Rail", "Multimodal"][i % 4], on_time_target=94 + (i % 5))
            db.add(carrier)
            carriers.append(carrier)
        db.flush()

        locations = list(PORTS.keys())
        statuses = ["In transit"] * 25 + ["Booked"] * 9 + ["Delivered"] * 19 + ["Customs hold"] * 4 + ["Exception"] * 5 + ["Quoted"] * 4 + ["Draft"] * 2
        modes = ["Ocean FCL"] * 36 + ["Ocean LCL"] * 8 + ["Air"] * 12 + ["Road"] * 5 + ["Rail"] * 3 + ["Multimodal"] * 4
        rng.shuffle(statuses)
        rng.shuffle(modes)
        base = datetime.combine(DEMO_AS_OF, datetime.min.time())
        for i in range(68):
            origin = locations[rng.randrange(len(locations))]
            destination = locations[rng.randrange(len(locations))]
            while destination == origin:
                destination = locations[rng.randrange(len(locations))]
            o, d = PORTS[origin], PORTS[destination]
            mode = modes[i % len(modes)]
            status = statuses[i % len(statuses)]
            etd = base + timedelta(days=rng.randint(-35, 16))
            transit_days = {"Ocean FCL": rng.randint(18, 35), "Ocean LCL": rng.randint(22, 39), "Air": rng.randint(2, 7), "Road": rng.randint(2, 8), "Rail": rng.randint(12, 22), "Multimodal": rng.randint(15, 32)}[mode]
            eta = etd + timedelta(days=transit_days)
            if status == "Delivered":
                eta = base - timedelta(days=rng.randint(1, 25))
                etd = eta - timedelta(days=transit_days)
                actual_delivery = eta + timedelta(days=rng.randint(-2, 4))
            elif status in ["In transit", "Customs hold", "Exception"]:
                etd = base - timedelta(days=rng.randint(2, max(4, transit_days - 2)))
                eta = base + timedelta(days=rng.randint(-4, 20))
                actual_delivery = None
            else:
                etd = base + timedelta(days=rng.randint(2, 20))
                eta = etd + timedelta(days=transit_days)
                actual_delivery = None
            buy = round(rng.uniform(900, 18500) * (1.0 if mode.startswith("Ocean") else (1.35 if mode == "Air" else 0.8)), 2)
            margin_pct = rng.uniform(0.12, 0.28)
            sell = round(buy / (1 - margin_pct), 2)
            shipment = Shipment(
                id=str(uuid.uuid4()), organization_id=ORG_ID, reference=f"NXS-{2026}{i+1:05d}",
                customer_id=customers[rng.randrange(len(customers))].id,
                carrier_id=carriers[rng.randrange(len(carriers))].id,
                mode=mode, status=status, origin=origin, destination=destination,
                origin_code=o["code"], destination_code=d["code"],
                origin_lat=o["lat"], origin_lon=o["lon"], destination_lat=d["lat"], destination_lon=d["lon"],
                cargo_description=rng.choice(["Consumer electronics", "Automotive components", "Medical equipment", "Textile products", "Industrial machinery", "Food-grade packaging", "Retail fixtures", "Solar components"]),
                container_no=(f"NEXU{rng.randint(1000000,9999999)}" if mode.startswith("Ocean") else ""),
                container_type=rng.choice(["20GP", "40GP", "40HC", "45HC"]) if mode.startswith("Ocean") else "N/A",
                weight_kg=round(rng.uniform(450, 23500), 1), volume_cbm=round(rng.uniform(2.5, 68), 1),
                incoterm=rng.choice(["EXW", "FCA", "FOB", "CFR", "CIF", "DAP", "DDP"]), currency="USD",
                etd=etd, eta=eta, actual_delivery=actual_delivery, buy_cost=buy, sell_price=sell, gross_profit=round(sell-buy, 2),
            )
            db.add(shipment)
            db.flush()
            # Every shipment starts with a booking event; a subset has operational milestones.
            events = [("BOOKING_CONFIRMED", "Booking confirmed", origin, etd - timedelta(days=3))]
            if status in ["In transit", "Customs hold", "Exception", "Delivered"]:
                events.extend([
                    ("GATE_IN", "Gate-in at origin terminal", origin, etd - timedelta(days=1)),
                    ("VESSEL_DEPARTED", "Vessel departed", origin, etd),
                ])
            if status == "Delivered":
                events.extend([
                    ("VESSEL_ARRIVED", "Vessel arrived", destination, eta - timedelta(days=2)),
                    ("CUSTOMS_RELEASED", "Customs released", destination, eta - timedelta(days=1)),
                    ("DELIVERED", "Delivered to consignee", destination, actual_delivery or eta),
                ])
            for code, label, place, at in events:
                db.add(Milestone(shipment_id=shipment.id, event_code=code, event_name=label, location=place, occurred_at=at, source="Synthetic carrier feed", note="Illustrative demo event"))

        db.flush()
        shipments = list(db.scalars(select(Shipment)).all())
        for i, s in enumerate(shipments):
            if s.status in ["Exception", "Customs hold"] or (s.status == "In transit" and s.eta.date() < DEMO_AS_OF):
                severity = "Critical" if s.status == "Customs hold" else ("High" if s.eta.date() < DEMO_AS_OF else "Medium")
                category = "Customs documentation" if s.status == "Customs hold" else ("ETA at risk" if s.eta.date() < DEMO_AS_OF else "Milestone gap")
                description = {
                    "Customs documentation": "Clearance is pending; supporting commercial or customs document requires review.",
                    "ETA at risk": "Planned arrival is in the past and no delivery event has been recorded.",
                    "Milestone gap": "Expected tracking milestone has not been received within the control window.",
                }[category]
                db.add(ExceptionRecord(
                    id=str(uuid.uuid4()), organization_id=ORG_ID, shipment_id=s.id,
                    category=category, severity=severity, description=description,
                    recommended_action="Validate latest carrier event, contact the operating partner and update the consignee with an approved ETA.",
                    owner=["Ocean Operations", "Air Desk", "Customs Team"][i % 3], status="Open" if i % 4 else "In progress",
                ))

        for i, s in enumerate(shipments[:36]):
            # Receivable invoices mirror sell price; payables mirror buy cost.
            status = "Paid" if s.status == "Delivered" and i % 3 != 0 else "Outstanding"
            db.add(Invoice(
                id=str(uuid.uuid4()), organization_id=ORG_ID, shipment_id=s.id,
                invoice_number=f"AR-{2026}{i+1:05d}", invoice_type="Receivable", amount=s.sell_price,
                currency=s.currency, status=status, issue_date=s.etd - timedelta(days=2),
                due_date=s.etd + timedelta(days=30), paid_date=(s.actual_delivery + timedelta(days=8) if status == "Paid" and s.actual_delivery else None),
            ))
            db.add(Invoice(
                id=str(uuid.uuid4()), organization_id=ORG_ID, shipment_id=s.id,
                invoice_number=f"AP-{2026}{i+1:05d}", invoice_type="Payable", amount=s.buy_cost,
                currency=s.currency, status="Paid" if i % 4 == 0 else "Outstanding",
                issue_date=s.etd, due_date=s.etd + timedelta(days=15),
            ))

        for i, customer in enumerate(customers[:8]):
            cost = round(rng.uniform(2500, 12000), 2)
            margin = rng.uniform(0.14, 0.25)
            total = cost / (1 - margin)
            db.add(Quote(
                id=str(uuid.uuid4()), organization_id=ORG_ID, quote_number=f"QT-2026{i+1:04d}",
                customer_id=customer.id, origin=locations[i], destination=locations[(i+4) % len(locations)],
                mode=rng.choice(["Ocean FCL", "Air", "Ocean LCL"]), currency="USD",
                freight_cost=cost * 0.78, fuel_surcharge=cost * 0.07, origin_handling=cost * 0.05,
                destination_handling=cost * 0.05, customs_cost=cost * 0.03, insurance_cost=cost * 0.02,
                other_cost=0, total_buy=cost, margin_pct=margin * 100, sell_price=round(total, 2),
                gross_profit=round(total-cost, 2), status=["Sent", "Accepted", "Draft", "Expired"][i % 4],
                valid_until=base + timedelta(days=14),
            ))
        db.add(AuditLog(organization_id=ORG_ID, actor="NEXUS Seeder", action="DEMO_DATA_SEEDED", entity_type="system", entity_id=ORG_ID, details="Synthetic demonstration network initialized."))
        db.commit()


# Only used to make reset order resilient when optional documents table is empty.
from .db import DocumentRecord as DocumentRecordSafe
