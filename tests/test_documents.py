from nexus.document_intelligence import analyse_document, classify_document, extract_fields


def test_classify_commercial_invoice():
    text = "COMMERCIAL INVOICE\nInvoice No: INV-2026-88412\nTotal Amount Due: USD 18,750.00"
    assert classify_document(text, "invoice.txt") == "Commercial Invoice"


def test_extract_logistics_fields():
    text = """PACKING LIST
Shipment Ref: NXS-202600012
Port of Loading: Shanghai, China
Port of Discharge: Rotterdam, Netherlands
Gross Weight: 18,450 kg
Container: NEXU4812057
"""
    fields = extract_fields(text)
    assert fields["shipment_reference"] == "NXS-202600012"
    assert fields["container_number"] == "NEXU4812057"
    assert fields["weight"] == "18,450 kg"
    assert "origin" in fields
    assert "destination" in fields


def test_analysis_returns_warnings_for_empty_document():
    result = analyse_document("blank.txt", b"")
    assert result["text"] == ""
    assert result["warnings"]


def test_ai_schema_is_explicit_and_closed():
    from nexus.ai_adapter import FIELD_NAMES, SCHEMA
    assert set(SCHEMA["properties"]) == set(FIELD_NAMES)
    assert SCHEMA["additionalProperties"] is False
    assert set(SCHEMA["required"]) == set(FIELD_NAMES)
