from nexus.services import calculate_quote, ALLOWED_TRANSITIONS


def test_gross_margin_quote_math():
    result = calculate_quote(4000, 0, 0, 0, 0, 0, 0, 20)
    assert result["total_buy"] == 4000
    assert result["sell_price"] == 5000
    assert result["gross_profit"] == 1000
    assert result["gross_margin_pct"] == 20
    assert result["markup_pct"] == 25


def test_zero_margin_quote_math():
    result = calculate_quote(1000, 100, 0, 0, 0, 0, 0, 0)
    assert result["sell_price"] == 1100
    assert result["gross_profit"] == 0


def test_quote_rejects_negative_cost():
    try:
        calculate_quote(-1, 0, 0, 0, 0, 0, 0, 20)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_quote_rejects_excessive_margin():
    try:
        calculate_quote(100, 0, 0, 0, 0, 0, 0, 81)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_shipment_state_machine_has_terminal_states():
    assert ALLOWED_TRANSITIONS["Delivered"] == set()
    assert ALLOWED_TRANSITIONS["Cancelled"] == set()
    assert "In transit" in ALLOWED_TRANSITIONS["Booked"]
    assert "Booked" in ALLOWED_TRANSITIONS["Quoted"]
    assert "Delivered" in ALLOWED_TRANSITIONS["In transit"]
