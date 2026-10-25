"""No-network tests for the scanner-to-paper preview boundary."""
import pytest
from paper_trade_preview import preview

def test_preview_never_places_order():
    result = preview("AMD", "1.99", "2.00")
    assert result["mode"] == "PAPER_ONLY"
    assert result["status"] == "PREVIEW_ONLY"
    assert result["starting_account"]["trades"] == 0

def test_manual_paper_approval_only():
    result = preview("AMD", "1.99", "2.00", approved=True)
    assert result["status"] == "SIMULATED"
    assert result["trade"]["simulated"] is True
    assert result["account"]["trades"] == 1

def test_wide_spread_is_rejected():
    with pytest.raises(ValueError, match="spread"):
        preview("AMD", "1.00", "2.00", approved=True)

def test_oversized_order_rejected():
    with pytest.raises(ValueError, match="per-trade"):
        preview("AMD", "1.99", "2.00", "6", approved=True)
