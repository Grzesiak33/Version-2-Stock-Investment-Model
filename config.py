"""Central configuration for the investment model."""
from __future__ import annotations

MODEL_VERSION = "2.0.0"
EXPERIMENT_START = "2026-08-14"
NEXT_DECISION_POINT = "2026-08-28"
BENCHMARK_TICKER = "SPY"

# Seed universe focused on AI compute, infrastructure, software and security.
# Market capitalization is NOT a scoring input and earns no bonus.
TICKERS = [
    "NVDA", "PLTR", "AMD", "AVGO", "AMAT", "MU", "ACMR", "CRDO", "TER",
    "CRWD", "PANW", "MSFT", "GOOGL", "AMZN", "META", "ORCL", "TSM", "ASML",
    "ARM", "MRVL", "ANET", "DELL", "VRT", "SMCI", "SNOW", "DDOG", "NET",
    "NOW", "MDB", "PATH",
]

CATEGORY_MAX = {
    "revenue_growth": 15.0,
    "earnings_fcf": 15.0,
    "industry_growth": 15.0,
    "balance_sheet": 10.0,
    "valuation": 10.0,
    "competitive_advantage": 10.0,
    "momentum": 10.0,
    "insider_institutional": 5.0,
    "catalysts": 5.0,
    "inflation_resilience": 5.0,
}
assert sum(CATEGORY_MAX.values()) == 100.0

# Fields used to calculate data completeness. Narrative fields can remain unavailable
# without crashing the model, but lower confidence must remain visible.
CONFIDENCE_FIELDS = [
    "revenue", "revenue_growth", "eps", "eps_growth", "free_cash_flow",
    "cash", "debt", "gross_margin", "operating_margin", "pe_ratio",
    "price_to_sales", "price_to_fcf", "one_month_return", "three_month_return",
    "six_month_return", "one_year_return", "institutional_activity",
]
