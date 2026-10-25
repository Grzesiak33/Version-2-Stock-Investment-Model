"""Bridge scanner candidates into a PAPER-ONLY trade preview.

The scanner score is a research heuristic, not an order instruction.
Actual bid/ask values must be entered explicitly; historical closes are NOT executable quotes.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from paper_trading.engine import PaperTrader, Quote

def preview(symbol: str, bid: str, ask: str, dollars: str = "2.00", approved: bool = False) -> dict:
    """Show or simulate one trade using manually supplied quotes; never contacts a broker."""
    now = datetime.now(timezone.utc)
    paper = PaperTrader()
    q = Quote(symbol.upper(), Decimal(bid), Decimal(ask), now)
    paper.update_mark(q, now)  # validates spread and timestamp
    before = paper.report()
    if not approved:
        return {"mode": "PAPER_ONLY", "status": "PREVIEW_ONLY", "symbol": q.symbol,
                "bid": str(q.bid), "ask": str(q.ask), "requested_dollars": dollars,
                "starting_account": before, "requires_paper_approval": True}
    trade = paper.buy(q, dollars, now, approved=True, reason="manually approved PAPER simulation")
    return {"mode": "PAPER_ONLY", "status": "SIMULATED", "trade": {
        "symbol": trade.symbol, "side": trade.side, "shares": str(trade.quantity),
        "simulated_fill": str(trade.price), "notional": str(trade.notional),
        "simulated": trade.simulated}, "account": paper.report()}

def main():
    p = argparse.ArgumentParser(description="Simulated trade preview; never sends real orders")
    p.add_argument("--symbol", required=True)
    p.add_argument("--bid", required=True, help="Manually supplied current bid; not scanner close")
    p.add_argument("--ask", required=True, help="Manually supplied current ask; not scanner close")
    p.add_argument("--dollars", default="2.00")
    p.add_argument("--approve-paper", action="store_true", help="Simulate only; does not place real orders")
    args = p.parse_args()
    print(json.dumps(preview(args.symbol, args.bid, args.ask, args.dollars, args.approve_paper), indent=2))

if __name__ == "__main__":
    main()
