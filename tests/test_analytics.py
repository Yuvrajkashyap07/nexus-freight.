from datetime import datetime, date
from nexus.analytics import calculate_risk


def test_customs_hold_is_high_risk():
    row = {"status": "Customs hold", "eta": datetime(2026, 11, 20)}
    score, band, reasons = calculate_risk(row, date(2026, 11, 9))
    assert score >= 45
    assert band in {"High", "Critical"}
    assert "Customs hold is active" in reasons


def test_delivered_shipment_has_no_eta_overdue_risk():
    row = {"status": "Delivered", "eta": datetime(2026, 10, 20)}
    score, band, reasons = calculate_risk(row, date(2026, 11, 9))
    assert score == 0
    assert band == "Low"
