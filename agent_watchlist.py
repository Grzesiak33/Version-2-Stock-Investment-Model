"""Read-only market scanner. No brokerage credentials, orders, or trading API."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
import math

DEFAULT_TICKERS = "NVDA,AMD,AVGO,TSM,ARM,PLTR,SOFI,IONQ"
MAX_TICKERS = 12

def scan(symbol: str) -> dict:
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="6mo", auto_adjust=True)
    if history.empty or len(history) < 25:
        raise ValueError("Not enough historical price data")
    closes = history["Close"].dropna()
    if len(closes) < 25:
        raise ValueError("Insufficient valid closes")
    last = float(closes.iloc[-1])
    previous = float(closes.iloc[-21])
    ma20 = float(closes.tail(20).mean())
    ret20 = (last / previous - 1) * 100
    volatility = float(closes.pct_change().dropna().tail(20).std() * math.sqrt(252) * 100)
    if not all(map(math.isfinite, [last, ma20, ret20, volatility])) or last <= 0:
        raise ValueError("Invalid market data")
    # Simple screening heuristic, NOT a trade signal or prediction.
    score = round(50 + min(20, max(-20, ret20 * 2)) + (10 if last > ma20 else -10) - min(20, volatility / 5))
    return {"symbol": symbol, "price": last, "return20": ret20, "vol": volatility,
            "score": max(0, min(100, score)), "above_ma20": last > ma20}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", default=DEFAULT_TICKERS)
    parser.add_argument("--output", default="reports/agent_watchlist.md")
    args = parser.parse_args()
    tickers = list(dict.fromkeys(x.strip().upper() for x in args.tickers.split(",") if x.strip()))[:MAX_TICKERS]
    if not tickers:
        raise SystemExit("No tickers provided")
    rows, errors = [], []
    for symbol in tickers:
        if not symbol.replace(".", "").replace("-", "").isalnum():
            errors.append((symbol, "Invalid ticker"))
            continue
        try:
            rows.append(scan(symbol))
        except Exception as exc:
            errors.append((symbol, str(exc)[:120].replace("|", "/")))
    rows.sort(key=lambda x: (-x["score"], x["symbol"]))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# Paper-only market watchlist", "", f"Generated: {now}", "",
             "**READ ONLY: No brokerage connection, no live orders, no paper orders.**",
             "These are delayed/third-party market data and a simple momentum heuristic, not recommendations.",
             "Quotes may be stale; no bid/ask spread, liquidity, fees, or news verification is performed.",
             "", "| Ticker | Last historical close | 20-day return | Annualized 20-day volatility | Screen score | Above 20-day average |",
             "|---|---:|---:|---:|---:|---|"]
    for r in rows:
        lines.append(f'| {r["symbol"]} | ${r["price"]:.2f} | {r["return20"]:+.1f}% | {r["vol"]:.1f}% | {r["score"]}/100 | {"Yes" if r["above_ma20"] else "No"} |')
    if errors:
        lines.extend(["", "## Missing/failed data", ""])
        lines.extend(f"- {sym}: {err}" for sym, err in errors)
    lines.extend(["", "## Next step", "Research candidates independently. Do not place trades from this report alone."])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if not rows:
        raise SystemExit("No valid data: check market-data provider or network")

if __name__ == "__main__":
    main()
