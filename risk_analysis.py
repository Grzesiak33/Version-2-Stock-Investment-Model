from dataclasses import dataclass
from .models import CompanyData

@dataclass
class RiskReport:
    flags: list[str]
    severity: str
    risk_count: int

def analyze_risk(d: CompanyData) -> RiskReport:
    flags = list(d.risk_factors)
    if d.price_to_sales is not None and d.price_to_sales > 20: flags.append("Excessive price-to-sales valuation")
    if d.pe_ratio is not None and d.pe_ratio > 100: flags.append("Very high earnings multiple")
    if d.free_cash_flow is not None and d.free_cash_flow < 0: flags.append("Negative free cash flow / unprofitable growth")
    if d.debt is not None and d.cash is not None and d.debt > d.cash * 3: flags.append("Debt materially exceeds cash")
    if d.metadata.get("dilution_rate", 0) > 0.10: flags.append("Severe dilution")
    if d.metadata.get("beta") is not None and d.metadata["beta"] > 2.0: flags.append("High market sensitivity / beta")
    if d.metadata.get("customer_concentration"): flags.append("Customer concentration")
    if d.metadata.get("regulatory_risk"): flags.append("Regulatory risk")
    if d.metadata.get("single_product_dependence"): flags.append("Dependence on one product")
    flags = list(dict.fromkeys(flags))
    severe = any(x in flags for x in ("Severe dilution", "Debt materially exceeds cash"))
    severity = "HIGH" if severe or len(flags) >= 4 else "MEDIUM" if len(flags) >= 2 else "LOW"
    return RiskReport(flags, severity, len(flags))
