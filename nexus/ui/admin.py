from __future__ import annotations

import streamlit as st
import pandas as pd

from ..db import db_health, get_engine
from ..config import database_url, app_mode
from .common import page_header, safe_dataframe


def render(actor: str, role: str, permissions: list[str], data: dict[str, pd.DataFrame], on_reset) -> None:
    page_header("PLATFORM ADMINISTRATION", "System & architecture", "Deployment health, integration catalogue, data architecture and commercial packaging.")
    health = db_health()
    a, b, c, d = st.columns(4)
    a.metric("Application mode", app_mode().upper())
    b.metric("Database engine", health.get("dialect", "unknown").upper())
    c.metric("Database status", "Connected" if health.get("ok") else "Error")
    d.metric("Demo actor", role)
    if health.get("ok"):
        st.success(f"Database connection healthy · {health.get('url_type')}")
    else:
        st.error(f"Database check failed: {health.get('error', 'Unknown error')}")

    tab_arch, tab_integrations, tab_data, tab_admin = st.tabs(["System architecture", "Integration catalogue", "Data model", "Admin controls"])
    with tab_arch:
        st.subheader("Logical system architecture")
        st.markdown("""
        ```mermaid
        flowchart TB
          subgraph Channels[Experience layer]
            OPS[Operations workspace]
            CUSTOMER[Customer portal - roadmap]
            API[Partner API / Webhooks]
          end
          subgraph App[Application layer]
            AUTH[Identity & tenant context]
            WORK[Shipment workflow service]
            QUOTE[Rating & quotation engine]
            DOC[Document intelligence]
            EX[Exception & SLA engine]
            FIN[Freight finance]
          end
          subgraph Data[Data & event layer]
            PG[(PostgreSQL operational store)]
            OBJ[(Object storage)]
            QUEUE[[Job queue / event bus]]
            AUDIT[(Append-only audit log)]
          end
          subgraph Partners[External ecosystem]
            TMS[Existing TMS / ERP]
            CARRIER[Carrier / visibility APIs]
            CUSTOMS[Customs / e-document partners]
            AI[LLM / OCR providers - optional]
            PAY[Payment provider - optional]
          end
          OPS --> AUTH --> WORK
          CUSTOMER --> AUTH
          API --> WORK
          WORK --> QUOTE
          WORK --> DOC
          WORK --> EX
          WORK --> FIN
          WORK <--> PG
          DOC <--> OBJ
          WORK --> QUEUE
          WORK --> AUDIT
          QUEUE <--> CARRIER
          QUEUE <--> TMS
          DOC <--> AI
          FIN <--> PAY
          DOC <--> CUSTOMS
        ```
        """)
        st.markdown("#### Architecture principles")
        st.markdown("""
        - **Modular monolith first:** separate domain modules in one deployable application; split workers/services only when throughput or team ownership justifies it.
        - **Event-driven operations:** milestones are append-only events; shipment status is a current projection derived from accepted events and workflow rules.
        - **Tenant-aware by design:** every customer-owned record carries `organization_id`; production requires database Row Level Security or equivalent tenant enforcement.
        - **Human approvals:** commercial commitments, carrier bookings, release instructions and payment actions require authorised approval.
        - **Provider adapters:** map partner-specific payloads into a canonical internal event model; do not let each provider dictate the domain schema.
        - **Idempotency:** inbound events use provider event IDs / idempotency keys to prevent duplicate milestone and invoice processing.
        """)
        st.subheader("Deployment topology")
        st.code("""Browser / Streamlit UI
       │
       ▼
Streamlit app (presentation + application services)
       │
       ├── Domain services: quote, shipment, exception, document, finance
       ├── Job queue adapter (production)
       ├── Partner adapters: DCSA / IATA / TMS / carrier / customs
       │
       ├── PostgreSQL (tenant-scoped operational records)
       ├── Object storage (documents, proofs, exports)
       └── Observability (logs, traces, metrics, audit)

Production evolution:
Streamlit demo → API/backend service + worker pool → multi-region SaaS""", language="text")
        st.info("This package is a classroom-ready Streamlit prototype. The partner adapters, queue, identity provider and object storage are documented interfaces, not live carrier or customs connections.")

    with tab_integrations:
        st.subheader("Integration catalogue")
        integrations = pd.DataFrame([
            {"Integration": "DCSA Track & Trace", "Purpose": "Ocean shipment / container event exchange", "Pattern": "REST / event adapter", "Status": "Standards-ready design", "Production dependency": "Partner credentials + conformance testing"},
            {"Integration": "IATA ONE Record", "Purpose": "Air cargo single-record data exchange", "Pattern": "Secured API / JSON-LD model mapping", "Status": "Standards-ready design", "Production dependency": "Air cargo partner onboarding"},
            {"Integration": "Carrier APIs", "Purpose": "Schedules, booking, milestones, rates", "Pattern": "Provider-specific adapters", "Status": "Not connected", "Production dependency": "Commercial API access per carrier"},
            {"Integration": "Existing TMS / ERP", "Purpose": "Customer, job, accounting and master data", "Pattern": "REST, EDI, CSV/SFTP", "Status": "Not connected", "Production dependency": "Customer mapping + integration tests"},
            {"Integration": "OCR / LLM provider", "Purpose": "Complex document extraction and classification", "Pattern": "Async API adapter", "Status": "Local rules-based demo", "Production dependency": "Provider credentials, DPA, evaluation set"},
            {"Integration": "Object storage", "Purpose": "Bills of lading, invoices, proof of delivery", "Pattern": "S3-compatible private bucket", "Status": "Local demo only", "Production dependency": "Bucket, KMS, signed URLs, retention policy"},
            {"Integration": "Email / WhatsApp", "Purpose": "Quote requests and exception notifications", "Pattern": "Webhook + approved outbound templates", "Status": "Not connected", "Production dependency": "Meta / email provider approval"},
            {"Integration": "Payments", "Purpose": "Subscription billing and customer payments", "Pattern": "Hosted checkout + verified webhooks", "Status": "Not connected", "Production dependency": "Provider underwriting and webhook secrets"},
        ])
        safe_dataframe(integrations, height=360)
        st.markdown("#### Standards references")
        st.markdown("- DCSA Track & Trace: standardised event exchange across shipment, transport, equipment, IoT and reefer events.")
        st.markdown("- IATA ONE Record: standardised, secured API and data model for digital air cargo data sharing.")
        st.markdown("- DCSA Shipment Journey: lifecycle coverage from booking and documentation through release and invoice settlement.")

    with tab_data:
        st.subheader("Core entity relationship map")
        st.code("""organizations 1──N customers
organizations 1──N carriers
organizations 1──N shipments
customers    1──N shipments
carriers     1──N shipments
shipments    1──N milestones        (append-only operational events)
shipments    1──N exceptions       (issue, severity, owner, resolution)
shipments    1──N documents        (extracted metadata + secure object ref in production)
shipments    1──N invoices         (receivable / payable)
customers    1──N quotes
organizations 1──N audit_logs     (actor, action, entity, timestamp)

Canonical Shipment fields:
reference, organization_id, customer_id, carrier_id, mode, status,
origin/destination UN/LOCODE or IATA code, ETD, ETA, cargo, equipment,
Incoterm, currency, buy_cost, sell_price, gross_profit

Canonical Event fields (DCSA-inspired mapping):
provider_event_id, event_code, event_type, shipment/container reference,
location, event_time, received_time, source, raw_payload_hash, schema_version""", language="text")
        counts = pd.DataFrame([
            {"Entity": "Shipments", "Records": len(data["shipments"]), "Purpose": "Core shipment/job record"},
            {"Entity": "Milestones", "Records": _count_model("Milestone"), "Purpose": "Operational event history"},
            {"Entity": "Exceptions", "Records": len(data["exceptions"]), "Purpose": "Risk, owner and resolution"},
            {"Entity": "Quotes", "Records": len(data["quotes"]), "Purpose": "Commercial rating and approval"},
            {"Entity": "Customers", "Records": len(data["customers"]), "Purpose": "Account and payment terms"},
            {"Entity": "Invoices", "Records": len(data["invoices"]), "Purpose": "Receivable / payable control"},
        ])
        safe_dataframe(counts)
        st.caption("The included SQLAlchemy models are executable. The production schema should add normalized address/location tables, raw event payload storage, idempotency keys, user/role membership and document object references.")

    with tab_admin:
        st.subheader("Demo controls")
        st.write(f"**Active actor:** {actor} · **Persona:** {role} · **Permissions:** {', '.join(permissions)}")
        st.warning("Resetting data deletes classroom actions and restores the synthetic seed network. Do not use demo reset against a production database.")
        if st.button("Reset synthetic demo dataset", type="secondary", disabled=role != "Operations Manager"):
            on_reset()
            st.success("Synthetic demo dataset restored.")
            st.rerun()
        st.markdown("#### Security and go-live checklist")
        checks = [
            "Replace demo persona selector with SSO/OIDC and tenant-scoped roles.",
            "Use managed PostgreSQL with tenant isolation / Row Level Security.",
            "Move documents to private object storage with short-lived signed URLs and malware scanning.",
            "Add queue-backed workers, retries, dead-letter handling and idempotency keys.",
            "Connect only authorised carrier/TMS/customs endpoints; complete DCSA/IATA conformance where applicable.",
            "Implement observability, backups, restore tests, incident response and retention/deletion policies.",
            "Perform penetration testing, privacy review, DPIA where applicable and disaster-recovery testing.",
            "Validate quote rating and financial postings with real customer contracts and local tax rules.",
        ]
        for item in checks:
            st.checkbox(item, key=f"go_live_{hash(item)}")


def _count_model(model_name: str) -> int:
    try:
        from sqlalchemy import select, func
        from ..db import get_session_factory, Milestone
        Session = get_session_factory()
        with Session() as db:
            return db.scalar(select(func.count()).select_from(Milestone)) or 0
    except Exception:
        return 0
