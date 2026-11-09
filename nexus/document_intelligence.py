"""Local document extraction. No customer files are sent to an external AI service."""
from __future__ import annotations

import csv
import io
import json
import re
from typing import Any

from docx import Document as DocxDocument
from openpyxl import load_workbook
from pypdf import PdfReader


MAX_FILE_BYTES = 15 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "docx", "xlsx", "csv", "txt"}


def extract_text(filename: str, payload: bytes) -> tuple[str, str]:
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("File exceeds the 15 MB demo limit.")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: .{ext}. Use PDF, DOCX, XLSX, CSV or TXT.")
    if ext == "pdf":
        reader = PdfReader(io.BytesIO(payload))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text, "application/pdf"
    if ext == "docx":
        doc = DocxDocument(io.BytesIO(payload))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(parts), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if ext == "xlsx":
        book = load_workbook(io.BytesIO(payload), read_only=True, data_only=True)
        lines = []
        for sheet in book.worksheets[:5]:
            lines.append(f"[SHEET: {sheet.title}]")
            for row in sheet.iter_rows(min_row=1, max_row=min(sheet.max_row or 1, 300), values_only=True):
                values = [str(v) for v in row if v is not None]
                if values:
                    lines.append(" | ".join(values))
        return "\n".join(lines), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if ext == "csv":
        decoded = payload.decode("utf-8-sig", errors="replace")
        rows = list(csv.reader(io.StringIO(decoded)))[:500]
        return "\n".join(" | ".join(row) for row in rows), "text/csv"
    return payload.decode("utf-8-sig", errors="replace"), "text/plain"


def classify_document(text: str, filename: str = "") -> str:
    source = f"{filename} {text[:5000]}".lower()
    checks = [
        ("Commercial Invoice", ["commercial invoice", "invoice number", "invoice no", "amount due"]),
        ("Packing List", ["packing list", "packages", "gross weight", "net weight"]),
        ("Bill of Lading", ["bill of lading", "b/l no", "port of loading", "port of discharge"]),
        ("Air Waybill", ["air waybill", "air waybill number", "awb no", "airport of departure"]),
        ("Booking Confirmation", ["booking confirmation", "booking no", "booking number", "vessel/voyage"]),
        ("Customs Document", ["customs declaration", "hs code", "customs entry", "declaration number"]),
    ]
    for label, keys in checks:
        if any(k in source for k in keys):
            return label
    return "Other / General"


def _first(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip(" :\t\r\n")[:160]
    return None


def extract_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "shipment_reference": _first([r"(?:shipment|job|file)\s*(?:ref(?:erence)?|no\.?|#)\s*[:#-]?\s*([A-Z0-9/_-]{5,30})", r"\b(NXS-\d{4,})\b"], text),
        "booking_reference": _first([r"booking\s*(?:ref(?:erence)?|no\.?|#)\s*[:#-]?\s*([A-Z0-9/_-]{5,30})"], text),
        "container_number": _first([r"\b([A-Z]{4}\d{7})\b"], text),
        "invoice_number": _first([r"invoice\s*(?:no\.?|number|#)\s*[:#-]?\s*([A-Z0-9/_-]{4,30})"], text),
        "origin": _first([r"(?:port|place|airport)\s+of\s+(?:loading|receipt|departure)\s*[:\-]?\s*([^\n,;]+)", r"origin\s*[:\-]\s*([^\n,;]+)"], text),
        "destination": _first([r"(?:port|place|airport)\s+of\s+(?:discharge|delivery|destination|arrival)\s*[:\-]?\s*([^\n,;]+)", r"destination\s*[:\-]\s*([^\n,;]+)"], text),
        "shipper": _first([r"shipper\s*[:\-]\s*([^\n]+)"], text),
        "consignee": _first([r"consignee\s*[:\-]\s*([^\n]+)"], text),
        "weight": _first([r"(?:gross\s+)?weight\s*[:\-]?\s*([\d,.]+\s*(?:kg|kgs|mt|tonnes?)?)"], text),
        "volume": _first([r"(?:measurement|volume)\s*[:\-]?\s*([\d,.]+\s*(?:cbm|m3)?)"], text),
        "etd": _first([r"(?:etd|departure\s+date)\s*[:\-]?\s*([^\n]+)"], text),
        "eta": _first([r"(?:eta|arrival\s+date)\s*[:\-]?\s*([^\n]+)"], text),
        "currency_and_total": _first([r"(?:total\s+amount|grand\s+total|amount\s+due)\s*[:\-]?\s*([A-Z]{3}\s*[\d,.]+|[$€£]\s*[\d,.]+)"], text),
    }
    return {k: v for k, v in fields.items() if v is not None}


def analyse_document(filename: str, payload: bytes, use_ai: bool = False) -> dict[str, Any]:
    text, mime = extract_text(filename, payload)
    category = classify_document(text, filename)
    fields = extract_fields(text)
    extraction_mode = "Local rules-based extraction"
    warnings = []
    if use_ai and text.strip():
        try:
            from .ai_adapter import openai_extract_fields
            ai_fields = openai_extract_fields(text)
            fields = ai_fields or fields
            extraction_mode = "OpenAI structured extraction"
        except Exception as exc:
            warnings.append(f"Optional AI extraction failed; local rules were retained: {str(exc)[:220]}")
    field_coverage = min(0.96, 0.34 + len(fields) * 0.055)
    if not text.strip():
        warnings.append("No selectable text found. Scanned PDFs require OCR integration.")
    if not fields:
        warnings.append("No recognised logistics fields found. Review the extracted text manually.")
    if category == "Other / General":
        warnings.append("Document type was not confidently classified.")
    return {"text": text, "mime_type": mime, "category": category, "fields": fields, "field_coverage": round(field_coverage, 2), "warnings": warnings, "extraction_mode": extraction_mode}
