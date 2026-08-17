"""Validation and explicit data-quality scoring."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import math
import re
from .config import CONFIDENCE_FIELDS
from .models import CompanyData, DataQuality

@dataclass
class ValidationResult:
    warnings: list[str]
    @property
    def valid(self) -> bool: return not any(w.startswith("ERROR:") for w in self.warnings)

def validate_company(d: CompanyData, stale_days: int = 3) -> ValidationResult:
    w: list[str] = []
    if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", d.ticker): w.append("ERROR: malformed ticker symbol")
    if not d.company_name: w.append("WARNING: company_name missing")
    if not d.data_sources: w.append("WARNING: data_sources missing")
    if d.metadata.get("provider_error"): w.append(f"ERROR: provider failure: {d.metadata['provider_error']}")
    for name in ("market_cap", "share_price", "revenue", "cash", "debt"):
        v = getattr(d, name)
        if v is not None and (not math.isfinite(v) or v < 0): w.append(f"ERROR: invalid {name}")
    for name in ("gross_margin", "operating_margin", "revenue_growth", "eps_growth", "free_cash_flow_growth", "industry_growth",
                 "one_month_return", "three_month_return", "six_month_return", "one_year_return", "institutional_activity", "insider_activity"):
        v = getattr(d, name)
        if v is not None and (not math.isfinite(v) or v < -1.0 or v > 10.0): w.append(f"WARNING: questionable percentage {name}={v}")
    for name in ("pe_ratio", "price_to_sales", "price_to_fcf"):
        v = getattr(d, name)
        if v is not None and (not math.isfinite(v) or abs(v) > 10000): w.append(f"ERROR: invalid ratio {name}")
    if d.data_timestamp:
        try:
            dt = datetime.fromisoformat(d.data_timestamp.replace("Z", "+00:00")); dt = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 86400
            if age > stale_days: w.append(f"WARNING: stale data ({int(age)} days old)")
        except ValueError: w.append("ERROR: invalid data_timestamp")
    else: w.append("WARNING: data_timestamp missing")
    if d.debt is not None and d.cash is not None and d.cash > 0 and d.debt > d.cash * 20: w.append("WARNING: debt materially exceeds cash")
    conflicts = d.metadata.get("conflicting_fields", [])
    if conflicts: w.append("WARNING: conflicting provider data: " + ", ".join(map(str, conflicts)))
    return ValidationResult(w)

def assess_data_quality(d: CompanyData, validation: ValidationResult | None = None) -> DataQuality:
    validation = validation or validate_company(d)
    missing = [name for name in CONFIDENCE_FIELDS if getattr(d, name) is None]
    completeness = 100.0 * (len(CONFIDENCE_FIELDS) - len(missing)) / len(CONFIDENCE_FIELDS)
    errors = sum(x.startswith("ERROR:") for x in validation.warnings)
    warnings = len(validation.warnings) - errors
    conflicts = list(d.metadata.get("conflicting_fields", []))
    stale = any("stale data" in x for x in validation.warnings)
    # Explicit penalty schedule; confidence never changes the fundamental 0-100 score.
    confidence = completeness - errors * 25 - warnings * 4 - len(conflicts) * 8 - (10 if stale else 0)
    confidence = round(max(0.0, min(100.0, confidence)), 1)
    return DataQuality(round(completeness, 1), confidence, stale, warnings, errors, missing, conflicts)
