from .models import CompanyData
from .fundamentals import clamp

def valuation_score(d: CompanyData) -> float:
    # Deliberately excludes absolute share_price and market_cap. Multiples and growth drive valuation.
    parts=[]
    if d.pe_ratio is not None and d.pe_ratio>0: parts.append(clamp((50-d.pe_ratio)/40))
    if d.price_to_sales is not None and d.price_to_sales>=0: parts.append(clamp((15-d.price_to_sales)/13))
    if d.price_to_fcf is not None and d.price_to_fcf>0: parts.append(clamp((50-d.price_to_fcf)/40))
    if d.revenue_growth is not None and d.price_to_sales is not None and d.price_to_sales>0:
        parts.append(clamp((d.revenue_growth*100/d.price_to_sales)/5))
    return round(10*(sum(parts)/len(parts) if parts else 0),2)
