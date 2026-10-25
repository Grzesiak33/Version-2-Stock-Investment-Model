# Agentic Trader — Phase 1 (simulation only)

This is a **separate, non-live** trading module. It does not connect to Robinhood, hold credentials, call brokerage APIs, or submit real orders. Existing Streamlit pages and ranking code remain unchanged.

## What exists
- `paper_trading/engine.py`: $10 virtual account, Decimal-based cash and fractional shares, simulated bid/ask fills, trade ledger, manual approval, position/cash limits, one new entry per UTC day, stale quote and spread checks, daily-loss halt and manual kill switch.
- `test_paper_trading.py`: deterministic safety tests.
- No price predictions or profit guarantees. Spread losses and minimum execution increments can overwhelm tiny gains.

## Run tests
From the repository root, with dependencies installed:

```bash
python -m pytest -q test_paper_trading.py
```

## Example (fictional prices; no broker connection)
```python
from datetime import datetime, timezone
from decimal import Decimal
from paper_trading.engine import PaperTrader, Quote

now = datetime.now(timezone.utc)
paper = PaperTrader()
q = Quote("DEMO", Decimal("1.99"), Decimal("2.00"), now)
paper.buy(q, "2.00", now, approved=True, reason="manual demo")
print(paper.report())
```

## Important boundaries
- Quotes must come from an independently validated source; no automatic execution from model `BUY` labels.
- Model rankings can become candidate suggestions later, **not** trade permissions.
- No Robinhood account, funds, holdings, or existing MU position are accessed or altered.
- This is an in-memory prototype: restarting resets virtual balances and logs. Persistent audit logs, quote sourcing, backtesting, market-hours/settlement restrictions, asset-specific trading rules, and brokerage reconciliation must be built and tested before any live integration.
- Daily loss limit is $0.20 on a $10 paper account; this is a conservative prototype setting, not a guarantee against losses.
