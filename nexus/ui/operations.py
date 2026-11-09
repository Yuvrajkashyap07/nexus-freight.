from __future__ import annotations

import json
import pandas as pd
import streamlit as st
from sqlalchemy import select, desc

from ..constants import EXCEPTION_STATUSES, SEVERITIES
from ..db import get_session_factory, ExceptionRecord, Shipment, DocumentRecord
from ..document_intelligence import analyse_document
from ..config import get_setting
from ..services import add_document, update_exception, create_exception
from .common import page_header, safe_dataframe


def render_exceptions(data: dict[str, pd.DataFrame], actor: str, permissions: list[str]) -> None:
    page_header("CONTROL TOWER", "Exception management", "Prioritise disruptions, assign an owner and keep the shipment audit trail intact.")
    ex = data["exceptions"].copy()
    if ex.empty:
        st.success("No exception records found.")
        return
    open_ex = ex[ex.status.isin(["Open", "In progress", "Escalated"])]
    c = st.columns(4)
    c[0].metric("Total exceptions", len(ex))
    c[1].metric("Open / in progress", len(open_ex))
    c[2].metric("Critical", int((open_ex.severity == "Critical").sum()))
    c[3].metric("Resolved", int((ex.status == "Resolved").sum()))
    sev_filter = st.multiselect("Severity", SEVERITIES, default=[])
    status_filter = st.multiselect("Exception status", EXCEPTION_STATUSES, default=["Open", "In progress", "Escalated"])
    filtered = ex.copy()
    if sev_filter:
        filtered = filtered[filtered.severity.isin(sev_filter)]
    if status_filter:
        filtered = filtered[filtered.status.isin(status_filter)]
    join = filtered.rename(columns={"id": "exception_id"}).merge(data["shipments"][["id", "reference", "customer", "origin", "destination", "eta"]], left_on="shipment_id", right_on="id", how="left")
    table = join[["reference", "customer", "category", "severity", "status", "owner", "eta", "description"]].rename(columns={"reference":"Shipment", "customer":"Customer", "category":"Category", "severity":"Severity", "status":"Status", "owner":"Owner", "eta":"ETA", "description":"Description"})
    safe_dataframe(table, height=270)
    st.markdown("#### Work an exception")
    options = {f"{r.reference} · {r.category} · {r.severity}": r.exception_id for _, r in join.iterrows()}
    if options and "resolve_exception" in permissions:
        label = st.selectbox("Select exception", list(options.keys()))
        exception_id = options[label]
        record = join[join.exception_id == exception_id].iloc[0]
        with st.form("exception_update_form"):
            a, b = st.columns(2)
            status = a.selectbox("New status", EXCEPTION_STATUSES, index=EXCEPTION_STATUSES.index(record.status) if record.status in EXCEPTION_STATUSES else 0)
            owner = b.text_input("Assigned owner", value=record.owner or "Operations Desk")
            note = st.text_area("Resolution / hand-off note", placeholder="Describe carrier response, mitigation or follow-up…")
            if st.form_submit_button("Save exception update", type="primary"):
                try:
                    update_exception(exception_id, status, owner, note, actor)
                    st.success("Exception updated and audit event recorded.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        with st.expander("Recommended action"):
            st.write(record.recommended_action)
    elif "resolve_exception" not in permissions:
        st.info("Exception updates require the Operations Manager demo persona.")

    with st.expander("Raise a new exception manually"):
        if "write" not in permissions:
            st.caption("Your persona does not have write permission.")
        else:
            shipment_map = {f"{r.reference} · {r.origin} → {r.destination}": r.id for _, r in data["shipments"].iterrows()}
            with st.form("raise_exception_form"):
                a, b, c = st.columns(3)
                shipment_label = a.selectbox("Shipment", list(shipment_map.keys()))
                category = b.selectbox("Category", ["ETA at risk", "Customs documentation", "Capacity / rollover", "Damage / shortage", "Milestone gap", "Invoice mismatch", "Other"])
                severity = c.selectbox("Severity", SEVERITIES, index=2)
                description = st.text_area("What happened?", "Operational team flagged a shipment issue requiring review.")
                action = st.text_area("Recommended next step", "Validate the latest partner update, contact the responsible operator and document the resolution.")
                if st.form_submit_button("Create exception"):
                    try:
                        create_exception(shipment_map[shipment_label], category, severity, description, action, actor)
                        st.success("Exception created.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))


def render_documents(data: dict[str, pd.DataFrame], actor: str, permissions: list[str]) -> None:
    page_header("DOCUMENT INTELLIGENCE", "Document desk", "Extract operational fields from shipping documents and attach them to the shipment record.")
    st.info("Local extraction is the default. If you explicitly enable the optional AI checkbox, extracted text (not the original file) is sent to the configured OpenAI API. The parser is rules-based without that option; scanned PDFs need an OCR adapter for production. Do not upload real personal or confidential customer documents to a public classroom demo.")
    uploaded = st.file_uploader("Upload a logistics document", type=["pdf", "docx", "xlsx", "csv", "txt"], help="Maximum 15 MB. Supported: PDF, DOCX, XLSX, CSV and TXT.")
    ai_available = bool(get_setting("OPENAI_API_KEY"))
    use_ai = st.checkbox("Use optional OpenAI structured extraction (sends extracted text to the configured API)", value=False, disabled=not ai_available, help="Local parsing is used by default. The original file is not sent to the AI provider.")
    if not ai_available:
        st.caption("Optional AI extraction is not configured. Local rules-based extraction remains available without API charges.")
    if uploaded:
        try:
            result = analyse_document(uploaded.name, uploaded.getvalue(), use_ai=use_ai)
            left, right = st.columns([1.25, 1])
            with left:
                st.markdown("#### Extraction preview")
                st.metric("Detected document type", result["category"])
                st.metric("Field coverage (heuristic)", f"{result['field_coverage']:.0%}")
                st.caption(f"Extraction mode: {result['extraction_mode']}")
                if result["warnings"]:
                    for warning in result["warnings"]:
                        st.warning(warning)
                st.text_area("Extracted text", result["text"][:15000], height=260)
            with right:
                st.markdown("#### Detected logistics fields")
                st.json(result["fields"] if result["fields"] else {"message": "No known fields detected"})
                shipment_map = {"Unlinked document": None}
                shipment_map.update({f"{r.reference} · {r.origin} → {r.destination}": r.id for _, r in data["shipments"].iterrows()})
                selected = st.selectbox("Attach to shipment", list(shipment_map.keys()), key="doc_shipment_link")
                category_options = list(dict.fromkeys([result["category"], "Commercial Invoice", "Packing List", "Bill of Lading", "Air Waybill", "Booking Confirmation", "Customs Document", "Other / General"]))
                category = st.selectbox("Confirm document type", category_options)
                if st.button("Save document record", type="primary", disabled="write" not in permissions):
                    try:
                        doc_id = add_document(uploaded.name, category, result["mime_type"], result["text"], json.dumps(result["fields"]), shipment_map[selected])
                        st.success(f"Document record saved: {doc_id[:8]}")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
        except Exception as exc:
            st.error(f"Document could not be processed: {exc}")

    st.divider()
    st.subheader("Document register")
    Session = get_session_factory()
    with Session() as db:
        docs = db.scalars(select(DocumentRecord).where(DocumentRecord.organization_id == "nexus-demo-org").order_by(desc(DocumentRecord.uploaded_at))).all()
    if docs:
        docs_df = pd.DataFrame([{"Filename": d.filename, "Type": d.category, "Shipment ID": (d.shipment_id or "—")[:12], "Status": d.status, "Uploaded": d.uploaded_at.strftime("%d %b %Y %H:%M")} for d in docs])
        safe_dataframe(docs_df, height=240)
        doc_options = {f"{d.filename} · {d.category} · {d.uploaded_at:%d %b %H:%M}": d for d in docs}
        label = st.selectbox("Inspect saved document", list(doc_options.keys()))
        chosen = doc_options[label]
        with st.expander("Saved extracted fields and text"):
            st.json(json.loads(chosen.extracted_fields_json or "{}"))
            st.text(chosen.extracted_text[:6000])
    else:
        st.caption("No documents saved yet. Upload a sample file to populate the register.")
