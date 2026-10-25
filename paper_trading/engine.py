"""Simulation-only $10 trading engine. No brokerage connectivity or real orders."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from typing import Optional

CENT = Decimal("0.01")
SHARE_STEP = Decimal("0.000001")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(CENT)


def shares(value) -> Decimal:
    return Decimal(str(value)).quantize(SHARE_STEP, rounding=ROUND_DOWN)


@dataclass(frozen=True)
class Rules:
    starting_cash: Decimal = Decimal("10.00")
    max_order: Decimal = Decimal("5.00")
    min_cash_reserve: Decimal = Decimal("1.00")
    max_entries_per_day: int = 1
    daily_loss_limit: Decimal = Decimal("0.20")
    max_spread_pct: Decimal = Decimal("0.01")
    max_quote_age_seconds: int = 60
    fractional_shares_allowed: bool = True


@dataclass(frozen=True)
class Quote:
    symbol: str
    bid: Decimal
    ask: Decimal
    timestamp: datetime
    asset_type: str = "stock"

    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            raise ValueError("Quote timestamp must include timezone")
        if self.bid <= 0 or self.ask <= 0 or self.ask < self.bid:
            raise ValueError("Invalid bid/ask")
        if self.asset_type not in ("stock", "crypto"):
            raise ValueError("Unsupported asset type")


@dataclass(frozen=True)
class Trade:
    time: datetime
    side: str
    symbol: str
    quantity: Decimal
    price: Decimal
    notional: Decimal
    reason: str
    simulated: bool = True


@dataclass
class PaperTrader:
    rules: Rules = field(default_factory=Rules)
    cash: Decimal = field(init=False)
    holdings: dict[str, Decimal] = field(default_factory=dict)
    trades: list[Trade] = field(default_factory=list)
    marks: dict[str, Decimal] = field(default_factory=dict)
    day_start_equity: dict[str, Decimal] = field(default_factory=dict)
    halted: bool = False

    def __post_init__(self):
        self.cash = money(self.rules.starting_cash)

    def equity(self) -> Decimal:
        return money(self.cash + sum(
            (qty * self.marks.get(symbol, Decimal("0")))
            for symbol, qty in self.holdings.items()
        ))

    def update_mark(self, quote: Quote, now: datetime) -> None:
        self._check_quote(quote, now)
        self.marks[quote.symbol] = quote.bid

    def _check_quote(self, quote: Quote, now: datetime) -> None:
        if now.tzinfo is None:
            raise ValueError("Current time must include timezone")
        age = (now - quote.timestamp).total_seconds()
        if age < 0 or age > self.rules.max_quote_age_seconds:
            raise ValueError("Stale or future quote")
        if (quote.ask - quote.bid) / quote.ask > self.rules.max_spread_pct:
            raise ValueError("Bid/ask spread too wide")

    def _day_key(self, now: datetime) -> str:
        return now.astimezone(timezone.utc).date().isoformat()

    def _check_daily_loss(self, now: datetime) -> None:
        key = self._day_key(now)
        if key not in self.day_start_equity:
            self.day_start_equity[key] = self.equity()
        if self.day_start_equity[key] - self.equity() >= self.rules.daily_loss_limit:
            self.halted = True
            raise ValueError("Daily loss limit reached; trading halted")

    def buy(self, quote: Quote, dollars, now: datetime, *, approved: bool = False,
            reason: str = "") -> Trade:
        """Paper entry; explicit approval required even though no real orders exist."""
        if not approved:
            raise PermissionError("Explicit trade approval required")
        if self.halted:
            raise ValueError("Trading halted")
        self.update_mark(quote, now)
        self._check_daily_loss(now)
        key = self._day_key(now)
        entries = sum(t.side == "BUY" and self._day_key(t.time) == key for t in self.trades)
        if entries >= self.rules.max_entries_per_day:
            raise ValueError("Daily entry limit reached")
        amount = money(dollars)
        if amount <= 0 or amount > self.rules.max_order:
            raise ValueError("Order exceeds per-trade limits")
        if self.cash - amount < self.rules.min_cash_reserve:
            raise ValueError("Insufficient available cash after reserve")
        qty = shares(amount / quote.ask) if self.rules.fractional_shares_allowed else Decimal(
            int(amount / quote.ask)
        )
        if qty <= 0:
            raise ValueError("Order too small")
        cost = money(qty * quote.ask)
        if cost <= 0:
            raise ValueError("Order below cent precision")
        if self.cash - cost < self.rules.min_cash_reserve:
            raise ValueError("Insufficient cash")
        self.cash = money(self.cash - cost)
        self.holdings[quote.symbol] = self.holdings.get(quote.symbol, Decimal("0")) + qty
        trade = Trade(now, "BUY", quote.symbol, qty, quote.ask, cost, reason)
        self.trades.append(trade)
        return trade

    def sell(self, quote: Quote, quantity, now: datetime, *, approved: bool = False,
             reason: str = "") -> Trade:
        if not approved:
            raise PermissionError("Explicit trade approval required")
        if self.halted:
            raise ValueError("Trading halted")
        self.update_mark(quote, now)
        self._check_daily_loss(now)
        qty = shares(quantity)
        held = self.holdings.get(quote.symbol, Decimal("0"))
        if qty <= 0 or qty > held:
            raise ValueError("Cannot sell more shares than held")
        proceeds = money(qty * quote.bid)
        self.holdings[quote.symbol] = held - qty
        if self.holdings[quote.symbol] == 0:
            del self.holdings[quote.symbol]
        self.cash = money(self.cash + proceeds)
        trade = Trade(now, "SELL", quote.symbol, qty, quote.bid, proceeds, reason)
        self.trades.append(trade)
        return trade

    def stop(self) -> None:
        self.halted = True

    def report(self) -> dict:
        return {
            "mode": "PAPER_ONLY",
            "cash": str(self.cash),
            "equity_at_last_bids": str(self.equity()),
            "holdings": {k: str(v) for k, v in self.holdings.items()},
            "trades": len(self.trades),
            "halted": self.halted,
        }
