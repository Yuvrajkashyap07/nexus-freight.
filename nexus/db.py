"""Persistence layer. SQLite is used for local/demo mode; PostgreSQL is supported via NEXUS_DATABASE_URL."""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text,
    create_engine, select, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import DATA_DIR, database_url


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    plan: Mapped[str] = mapped_column(String(40), default="Growth")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="")
    segment: Mapped[str] = mapped_column(String(50), default="SME")
    contact_email: Mapped[str] = mapped_column(String(180), default="")
    payment_terms: Mapped[str] = mapped_column(String(50), default="Net 30")
    credit_limit: Mapped[float] = mapped_column(Float, default=25000)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Carrier(Base):
    __tablename__ = "carriers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    modes: Mapped[str] = mapped_column(String(120), default="Ocean FCL")
    on_time_target: Mapped[float] = mapped_column(Float, default=95.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Shipment(Base):
    __tablename__ = "shipments"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    reference: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    carrier_id: Mapped[int] = mapped_column(ForeignKey("carriers.id"), index=True)
    mode: Mapped[str] = mapped_column(String(40), default="Ocean FCL")
    status: Mapped[str] = mapped_column(String(40), default="Booked", index=True)
    origin: Mapped[str] = mapped_column(String(180), nullable=False)
    destination: Mapped[str] = mapped_column(String(180), nullable=False)
    origin_code: Mapped[str] = mapped_column(String(12), default="")
    destination_code: Mapped[str] = mapped_column(String(12), default="")
    origin_lat: Mapped[float] = mapped_column(Float, default=0)
    origin_lon: Mapped[float] = mapped_column(Float, default=0)
    destination_lat: Mapped[float] = mapped_column(Float, default=0)
    destination_lon: Mapped[float] = mapped_column(Float, default=0)
    cargo_description: Mapped[str] = mapped_column(String(240), default="General cargo")
    container_no: Mapped[str] = mapped_column(String(40), default="")
    container_type: Mapped[str] = mapped_column(String(30), default="40HC")
    weight_kg: Mapped[float] = mapped_column(Float, default=0)
    volume_cbm: Mapped[float] = mapped_column(Float, default=0)
    incoterm: Mapped[str] = mapped_column(String(8), default="FOB")
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    etd: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    eta: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    actual_delivery: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    buy_cost: Mapped[float] = mapped_column(Float, default=0)
    sell_price: Mapped[float] = mapped_column(Float, default=0)
    gross_profit: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    customer: Mapped[Customer] = relationship()
    carrier: Mapped[Carrier] = relationship()
    milestones: Mapped[list["Milestone"]] = relationship(back_populates="shipment", cascade="all, delete-orphan")


class Quote(Base):
    __tablename__ = "quotes"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    quote_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    origin: Mapped[str] = mapped_column(String(180))
    destination: Mapped[str] = mapped_column(String(180))
    mode: Mapped[str] = mapped_column(String(40))
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    freight_cost: Mapped[float] = mapped_column(Float, default=0)
    fuel_surcharge: Mapped[float] = mapped_column(Float, default=0)
    origin_handling: Mapped[float] = mapped_column(Float, default=0)
    destination_handling: Mapped[float] = mapped_column(Float, default=0)
    customs_cost: Mapped[float] = mapped_column(Float, default=0)
    insurance_cost: Mapped[float] = mapped_column(Float, default=0)
    other_cost: Mapped[float] = mapped_column(Float, default=0)
    total_buy: Mapped[float] = mapped_column(Float, default=0)
    margin_pct: Mapped[float] = mapped_column(Float, default=18)
    sell_price: Mapped[float] = mapped_column(Float, default=0)
    gross_profit: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="Draft", index=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    customer: Mapped[Customer] = relationship()


class Milestone(Base):
    __tablename__ = "milestones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shipment_id: Mapped[str] = mapped_column(ForeignKey("shipments.id"), index=True)
    event_code: Mapped[str] = mapped_column(String(60))
    event_name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(180), default="")
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    source: Mapped[str] = mapped_column(String(60), default="NEXUS Demo")
    note: Mapped[str] = mapped_column(Text, default="")
    shipment: Mapped[Shipment] = relationship(back_populates="milestones")


class ExceptionRecord(Base):
    __tablename__ = "exceptions"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    shipment_id: Mapped[str] = mapped_column(ForeignKey("shipments.id"), index=True)
    category: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str] = mapped_column(String(20), default="Medium")
    description: Mapped[str] = mapped_column(Text)
    recommended_action: Mapped[str] = mapped_column(Text, default="Review shipment and contact carrier.")
    owner: Mapped[str] = mapped_column(String(100), default="Operations Desk")
    status: Mapped[str] = mapped_column(String(30), default="Open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DocumentRecord(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    shipment_id: Mapped[str | None] = mapped_column(ForeignKey("shipments.id"), nullable=True, index=True)
    filename: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(60), default="Other")
    mime_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    extracted_fields_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(30), default="Processed")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    shipment_id: Mapped[str] = mapped_column(ForeignKey("shipments.id"), index=True)
    invoice_number: Mapped[str] = mapped_column(String(40), unique=True)
    invoice_type: Mapped[str] = mapped_column(String(20))  # Receivable or Payable
    amount: Mapped[float] = mapped_column(Float, default=0)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    status: Mapped[str] = mapped_column(String(30), default="Outstanding")
    issue_date: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    due_date: Mapped[datetime] = mapped_column(DateTime)
    paid_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    actor: Mapped[str] = mapped_column(String(100), default="Demo User")
    action: Mapped[str] = mapped_column(String(120))
    entity_type: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[str] = mapped_column(String(60))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


@lru_cache(maxsize=4)
def get_engine(url: str | None = None):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_url = url or database_url()
    kwargs: dict[str, Any] = {"pool_pre_ping": True}
    if db_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in db_url:
            kwargs["poolclass"] = StaticPool
    return create_engine(db_url, **kwargs)


@lru_cache(maxsize=4)
def get_session_factory(url: str | None = None):
    return sessionmaker(bind=get_engine(url), autoflush=False, expire_on_commit=False)


def init_db(url: str | None = None) -> None:
    Base.metadata.create_all(get_engine(url))


def db_health(url: str | None = None) -> dict[str, Any]:
    engine = get_engine(url)
    try:
        with engine.connect() as conn:
            conn.execute(select(func.count()).select_from(Organization))
        return {"ok": True, "dialect": engine.dialect.name, "url_type": "external database" if engine.dialect.name != "sqlite" else "local SQLite"}
    except Exception as exc:
        return {"ok": False, "dialect": engine.dialect.name, "error": str(exc)[:240]}
