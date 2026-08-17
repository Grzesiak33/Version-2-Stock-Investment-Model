from .models import CompanyData
from .fundamentals import clamp

def momentum_score(d):
    vals=[d.one_month_return,d.three_month_return,d.six_month_return,d.one_year_return]
    vals=[v for v in vals if v is not None]
    if not vals:return 0.0
    # Saturates to prevent hype/chasing; negative trends score poorly.
    parts=[clamp((v+0.15)/0.55) for v in vals]
    return round(10*sum(parts)/len(parts),2)
