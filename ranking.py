"""Deterministic ranking plus independent risk/data-quality decision screen."""
from dataclasses import dataclass
from .models import CompanyData, StockScore, DataQuality
from .risk_analysis import RiskReport, analyze_risk
from .data_validation import validate_company, assess_data_quality
from .scoring import score_company

@dataclass
class RankedStock:
    rank: int
    company: CompanyData
    score: StockScore
    risks: RiskReport
    quality: DataQuality
    strengths: list[str]
    weaknesses: list[str]

def rank_companies(companies: list[CompanyData]) -> list[RankedStock]:
    rows = []
    for company in companies:
        score = score_company(company)
        risk = analyze_risk(company)
        quality = assess_data_quality(company, validate_company(company))
        categories = {k: getattr(score, k) for k in (
            "revenue_growth", "earnings_fcf", "industry_growth", "balance_sheet", "valuation",
            "competitive_advantage", "momentum", "insider_institutional", "catalysts", "inflation_resilience")}
        maxima = {"revenue_growth":15,"earnings_fcf":15,"industry_growth":15,"balance_sheet":10,"valuation":10,
                  "competitive_advantage":10,"momentum":10,"insider_institutional":5,"catalysts":5,"inflation_resilience":5}
        strengths = [k.replace("_", " ").title() for k, v in categories.items() if v >= maxima[k] * .80]
        weaknesses = [k.replace("_", " ").title() for k, v in categories.items() if v <= maxima[k] * .40]
        rows.append((company, score, risk, quality, strengths, weaknesses))
    rows.sort(key=lambda x: (-x[1].total_score, x[0].ticker))
    return [RankedStock(i + 1, *row) for i, row in enumerate(rows)]

def recommended_candidate(ranked: list[RankedStock], min_confidence: float = 70.0) -> RankedStock | None:
    eligible = [x for x in ranked if x.risks.severity != "HIGH" and x.quality.confidence >= min_confidence and x.quality.error_count == 0]
    return eligible[0] if eligible else None
