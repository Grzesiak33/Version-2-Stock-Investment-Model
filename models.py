"""Domain models used throughout the application."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import math
from .config import CATEGORY_MAX, MODEL_VERSION

@dataclass
class CompanyData:
    ticker: str
    company_name: str = ""
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    share_price: float | None = None
    revenue: float | None = None
    revenue_growth: float | None = None
    eps: float | None = None
    eps_growth: float | None = None
    free_cash_flow: float | None = None
    free_cash_flow_growth: float | None = None
    cash: float | None = None
    debt: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None
    pe_ratio: float | None = None
    price_to_sales: float | None = None
    price_to_fcf: float | None = None
    one_month_return: float | None = None
    three_month_return: float | None = None
    six_month_return: float | None = None
    one_year_return: float | None = None
    insider_activity: float | None = None
    institutional_activity: float | None = None
    industry_growth: float | None = None
    competitive_advantage: float | None = None
    catalysts: list[str] = field(default_factory=list)
    inflation_resilience: float | None = None
    risk_factors: list[str] = field(default_factory=list)
    data_timestamp: str | None = None
    data_sources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class DataQuality:
    completeness: float
    confidence: float
    stale: bool
    warning_count: int
    error_count: int
    missing_fields: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    @property
    def level(self) -> str:
        if self.confidence >= 85: return "HIGH"
        if self.confidence >= 70: return "MODERATE"
        if self.confidence >= 50: return "LOW"
        return "VERY LOW"

@dataclass
class StockScore:
    revenue_growth: float
    earnings_fcf: float
    industry_growth: float
    balance_sheet: float
    valuation: float
    competitive_advantage: float
    momentum: float
    insider_institutional: float
    catalysts: float
    inflation_resilience: float
    model_version: str = MODEL_VERSION
    total_score: float = field(init=False)
    classification: str = field(init=False)

    def __post_init__(self) -> None:
        for key, maximum in CATEGORY_MAX.items():
            value = getattr(self, key)
            if not isinstance(value, (int, float)) or math.isnan(value) or not 0 <= value <= maximum:
                raise ValueError(f"{key} must be between 0 and {maximum}")
        self.total_score = round(sum(getattr(self, key) for key in CATEGORY_MAX), 2)
        if self.total_score > 100:
            raise ValueError("total score exceeds 100")
        self.classification = classify(self.total_score)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def classify(score: float) -> str:
    if not 0 <= score <= 100: raise ValueError("score must be 0..100")
    if score >= 85: return "BUY"
    if score >= 75: return "WATCH"
    if score >= 65: return "INTERESTING"
    if score >= 50: return "RESEARCH"
    return "REJECT"
