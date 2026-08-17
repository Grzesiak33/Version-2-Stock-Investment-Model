"""Replaceable market-data providers.

LiveProvider uses yfinance for current market/fundamental data and can optionally
cross-check annual revenue/cash/debt against SEC Company Facts. Missing fields stay
None; the provider never fabricates values.
"""
from __future__ import annotations
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd
from .models import CompanyData

log = logging.getLogger(__name__)

def _clean(value):
    if value is None: return None
    try:
        if pd.isna(value) or not np.isfinite(float(value)): return None
        return float(value)
    except (TypeError, ValueError):
        return None

def _return_at(history: pd.Series, days: int) -> float | None:
    s = history.dropna()
    if len(s) < 2: return None
    cutoff = s.index[-1] - pd.Timedelta(days=days)
    eligible = s.loc[s.index <= cutoff]
    if eligible.empty or eligible.iloc[-1] == 0: return None
    return float(s.iloc[-1] / eligible.iloc[-1] - 1)

class DataProvider(ABC):
    @abstractmethod
    def load(self, tickers: Iterable[str] | None = None) -> list[CompanyData]: ...

class JsonProvider(DataProvider):
    def __init__(self, path: str | Path): self.path = Path(path)
    def load(self, tickers=None) -> list[CompanyData]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        rows = [CompanyData(**x) for x in raw]
        wanted = {x.upper() for x in tickers} if tickers else None
        return [x for x in rows if not wanted or x.ticker.upper() in wanted]

class DemoProvider(JsonProvider):
    """Synthetic data for tests/examples. Never represents real market data."""

class LiveProvider(DataProvider):
    def __init__(self, use_sec: bool = True, sec_user_agent: str | None = None):
        self.use_sec = use_sec
        self.sec_user_agent = sec_user_agent or "investment-model research@example.com"

    def load(self, tickers=None) -> list[CompanyData]:
        if not tickers: raise ValueError("LiveProvider requires at least one ticker")
        rows = []
        for ticker in tickers:
            try:
                rows.append(self._load_one(str(ticker).upper()))
            except Exception as exc:  # isolate provider/network failures per symbol
                log.warning("Live data failed for %s: %s", ticker, exc)
                rows.append(CompanyData(
                    ticker=str(ticker).upper(), company_name=str(ticker).upper(),
                    data_timestamp=datetime.now(timezone.utc).isoformat(),
                    data_sources=[], metadata={"provider_error": str(exc), "data_quality_issue": True},
                ))
        return rows

    def _load_one(self, ticker: str) -> CompanyData:
        import yfinance as yf
        obj = yf.Ticker(ticker)
        info = obj.info or {}
        hist = obj.history(period="18mo", auto_adjust=True)
        close = hist.get("Close", pd.Series(dtype=float))
        price = _clean(close.iloc[-1]) if len(close) else _clean(info.get("currentPrice"))
        market_cap = _clean(info.get("marketCap"))
        fcf = _clean(info.get("freeCashflow"))
        price_to_fcf = (market_cap / fcf) if market_cap is not None and fcf and fcf > 0 else None
        company = CompanyData(
            ticker=ticker,
            company_name=info.get("longName") or info.get("shortName") or ticker,
            sector=info.get("sector"), industry=info.get("industry"),
            market_cap=market_cap, share_price=price,
            revenue=_clean(info.get("totalRevenue")),
            revenue_growth=_clean(info.get("revenueGrowth")),
            eps=_clean(info.get("trailingEps")), eps_growth=_clean(info.get("earningsGrowth")),
            free_cash_flow=fcf,
            free_cash_flow_growth=None,
            cash=_clean(info.get("totalCash")), debt=_clean(info.get("totalDebt")),
            gross_margin=_clean(info.get("grossMargins")), operating_margin=_clean(info.get("operatingMargins")),
            pe_ratio=_clean(info.get("trailingPE")), price_to_sales=_clean(info.get("priceToSalesTrailing12Months")),
            price_to_fcf=_clean(price_to_fcf),
            one_month_return=_return_at(close, 30), three_month_return=_return_at(close, 91),
            six_month_return=_return_at(close, 182), one_year_return=_return_at(close, 365),
            institutional_activity=_clean(info.get("heldPercentInstitutions")),
            insider_activity=_clean(info.get("heldPercentInsiders")),
            # Qualitative categories require explicit research rather than invented proxies.
            industry_growth=None, competitive_advantage=None, catalysts=[], inflation_resilience=None,
            risk_factors=[], data_timestamp=datetime.now(timezone.utc).isoformat(),
            data_sources=["Yahoo Finance via yfinance"],
            metadata={
                "provider": "yfinance", "quote_type": info.get("quoteType"),
                "beta": _clean(info.get("beta")), "shares_outstanding": _clean(info.get("sharesOutstanding")),
                "recommendation_key": info.get("recommendationKey"),
            },
        )
        if self.use_sec:
            self._sec_cross_check(company)
        return company

    def _sec_cross_check(self, company: CompanyData) -> None:
        """Cross-check selected annual facts; failures are visible but non-fatal."""
        try:
            import requests
            headers = {"User-Agent": self.sec_user_agent, "Accept-Encoding": "gzip, deflate"}
            tickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers, timeout=15)
            tickers.raise_for_status()
            mapping = tickers.json()
            match = next((v for v in mapping.values() if v.get("ticker", "").upper() == company.ticker), None)
            if not match: return
            cik = str(match["cik_str"]).zfill(10)
            resp = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers, timeout=20)
            resp.raise_for_status()
            facts = resp.json().get("facts", {}).get("us-gaap", {})
            sec_values = {}
            aliases = {
                "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
                "cash": ["CashAndCashEquivalentsAtCarryingValue"],
                "debt": ["LongTermDebtAndFinanceLeaseObligationsCurrent", "LongTermDebtCurrent", "LongTermDebtNoncurrent"],
            }
            for field, tags in aliases.items():
                values = []
                for tag in tags:
                    units = facts.get(tag, {}).get("units", {}).get("USD", [])
                    annual = [x for x in units if x.get("form") in {"10-K", "20-F"} and x.get("val") is not None]
                    if annual:
                        latest = max(annual, key=lambda x: x.get("filed", ""))
                        values.append(float(latest["val"]))
                if values: sec_values[field] = sum(values) if field == "debt" else values[0]
            conflicts = []
            for field, sec_value in sec_values.items():
                live = getattr(company, field)
                if live is not None and sec_value and abs(live - sec_value) / max(abs(sec_value), 1) > 0.35:
                    conflicts.append(field)
            company.metadata["sec_cross_check"] = sec_values
            if conflicts: company.metadata["conflicting_fields"] = conflicts
            company.data_sources.append("SEC EDGAR Company Facts")
        except Exception as exc:
            company.metadata["sec_cross_check_error"] = str(exc)
