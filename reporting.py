from pathlib import Path
from .ranking import RankedStock

def render_stock_report(r: RankedStock) -> str:
    s,c=r.score,r.company
    lines=[c.ticker,f"Score: {s.total_score}/100",f"Classification: {s.classification}",f"Risk Level: {r.risks.severity}",
           f"Data Confidence: {r.quality.confidence}/100 ({r.quality.level})","",
           f"Revenue Growth: {s.revenue_growth}/15",f"Earnings/FCF: {s.earnings_fcf}/15",f"Industry Growth: {s.industry_growth}/15",
           f"Balance Sheet: {s.balance_sheet}/10",f"Valuation: {s.valuation}/10",f"Moat: {s.competitive_advantage}/10",
           f"Momentum: {s.momentum}/10",f"Insider/Institutional: {s.insider_institutional}/5",f"Catalysts: {s.catalysts}/5",
           f"Inflation Resilience: {s.inflation_resilience}/5","","Major Strengths:"]+[f"- {x}" for x in r.strengths]+[
           "","Major Weaknesses:"]+[f"- {x}" for x in r.weaknesses]+["","Major Risks:"]+[f"- {x}" for x in (r.risks.flags or ["No explicit risk flags in supplied data"])]+[
           "","Key Catalysts:"]+[f"- {x}" for x in (c.catalysts or ["Unavailable — requires qualitative research; not fabricated"])]+[
           "","Investment Thesis:",c.metadata.get("investment_thesis","Unavailable — requires research; not fabricated."),"",
           "What Would Invalidate the Thesis:",c.metadata.get("thesis_invalidation","Unavailable — requires research."),"",
           f"Model Version: {s.model_version}",f"Data Sources: {', '.join(c.data_sources) or 'Unavailable'}",f"Data Timestamp: {c.data_timestamp or 'Unavailable'}",
           f"Missing Fields: {', '.join(r.quality.missing_fields) or 'None'}"]
    return "\n".join(lines)

def save_report(r,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(render_stock_report(r),encoding="utf-8"); return p
