"""Apply explicitly sourced qualitative research without fabricating missing inputs."""
from __future__ import annotations
import json
from pathlib import Path
from .models import CompanyData

ALLOWED_FIELDS = {"industry_growth", "competitive_advantage", "inflation_resilience", "catalysts", "risk_factors"}

def apply_qualitative_research(companies: list[CompanyData], path: str | Path) -> list[CompanyData]:
    p = Path(path)
    if not p.exists():
        return companies
    raw = json.loads(p.read_text(encoding="utf-8"))
    for company in companies:
        item = raw.get(company.ticker.upper())
        if not isinstance(item, dict):
            continue
        sources = item.get("sources", [])
        if not sources:
            company.metadata["qualitative_research_warning"] = "Research ignored: no sources supplied"
            continue
        for field in ALLOWED_FIELDS:
            if field in item:
                setattr(company, field, item[field])
        company.metadata["qualitative_research_date"] = item.get("as_of")
        company.metadata["qualitative_sources"] = sources
        company.metadata["verified_catalysts"] = item.get("catalysts", [])
        company.data_sources.extend(str(x) for x in sources if str(x) not in company.data_sources)
    return companies
