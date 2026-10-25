"""Deterministic paper-trading safety tests; no network calls."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest

from paper_trading.engine import PaperTrader, Quote


NOW = datetime(2026, 10, 25, 14, 0, tzinfo=timezone.utc)


def quote(symbol="MU", bid="1.99", ask="2.00", time=NOW):
    return Quote(symbol, Decimal(bid), Decimal(ask), time)


def test_starting_cash_and_no_real_trades():
    p = PaperTrader()
    assert p.cash == Decimal("10.00")
    assert p.report()["mode"] == "PAPER_ONLY"
    assert not p.trades


def test_requires_approval():
    p = PaperTrader()
    with pytest.raises(PermissionError):
        p.buy(quote(), "2", NOW)
    assert p.cash == Decimal("10.00")


def test_buy_tracks_cash_and_holdings():
    p = PaperTrader()
    t = p.buy(quote(), "5", NOW, approved=True)
    assert t.simulated is True
    assert p.cash == Decimal("5.00")
    assert p.holdings["MU"] == Decimal("2.500000")


def test_max_order():
    with pytest.raises(ValueError, match="per-trade"):
        PaperTrader().buy(quote(), "5.01", NOW, approved=True)


def test_reserve():
    p = PaperTrader()
    p.cash = Decimal("5.50")
    with pytest.raises(ValueError, match="reserve"):
        p.buy(quote(), "5", NOW, approved=True)


def test_one_entry_per_day():
    p = PaperTrader()
    p.buy(quote(), "2", NOW, approved=True)
    with pytest.raises(ValueError, match="entry"):
        p.buy(quote("AMD"), "2", NOW, approved=True)


def test_rejects_stale_quote():
    p = PaperTrader()
    with pytest.raises(ValueError, match="Stale"):
        p.buy(quote(time=NOW - timedelta(minutes=2)), "2", NOW, approved=True)


def test_rejects_wide_spread():
    p = PaperTrader()
    with pytest.raises(ValueError, match="spread"):
        p.buy(quote(bid="1.50", ask="2.00"), "2", NOW, approved=True)


def test_sell_only_owned_shares():
    p = PaperTrader()
    with pytest.raises(ValueError, match="more shares"):
        p.sell(quote(), "1", NOW, approved=True)
    p.buy(quote(), "2", NOW, approved=True)
    t = p.sell(quote(), "1", NOW, approved=True)
    assert t.simulated and t.side == "SELL"
    assert "MU" not in p.holdings  # Fully sold positions are removed


def test_halt_blocks_orders():
    p = PaperTrader()
    p.stop()
    with pytest.raises(ValueError, match="halted"):
        p.buy(quote(), "2", NOW, approved=True)


def test_daily_loss_halts():
    p = PaperTrader()
    p.buy(quote(), "5", NOW, approved=True)
    # Loss is marked at the bid, not at an optimistic midpoint.
    p.marks["MU"] = Decimal("1.80")
    with pytest.raises(ValueError, match="Daily loss"):
        p.buy(quote("AMD"), "1", NOW, approved=True)
    assert p.halted


def test_no_shorting():
    p = PaperTrader()
    with pytest.raises(ValueError):
        p.sell(quote(), "0.01", NOW, approved=True)
