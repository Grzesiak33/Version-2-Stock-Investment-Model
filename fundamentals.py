from .models import CompanyData

def clamp(x, lo=0.0, hi=1.0): return max(lo,min(hi,x))
def linear(v, low, high): return 0.0 if v is None else clamp((v-low)/(high-low))
def revenue_growth_score(d): return round(15*linear(d.revenue_growth, -0.05, 0.35),2)
def earnings_fcf_score(d):
    parts=[]
    if d.free_cash_flow is not None: parts.append(1.0 if d.free_cash_flow>0 else 0.0)
    if d.free_cash_flow_growth is not None: parts.append(linear(d.free_cash_flow_growth,-0.1,0.4))
    if d.eps_growth is not None: parts.append(linear(d.eps_growth,-0.1,0.35))
    if d.operating_margin is not None: parts.append(linear(d.operating_margin,0,0.3))
    return round(15*(sum(parts)/len(parts) if parts else 0),2)
def industry_growth_score(d): return round(15*linear(d.industry_growth,0,0.20),2)
def balance_sheet_score(d):
    parts=[]
    if d.cash is not None and d.debt is not None: parts.append(clamp((d.cash-d.debt)/(abs(d.cash)+abs(d.debt)+1)*0.5+0.5))
    if d.free_cash_flow is not None: parts.append(1 if d.free_cash_flow>0 else 0)
    return round(10*(sum(parts)/len(parts) if parts else 0),2)
def moat_score(d):
    v=d.competitive_advantage
    if v is None:return 0.0
    return round(10*clamp(v if v<=1 else v/10),2)
def inflation_score(d):
    v=d.inflation_resilience
    if v is None:return 0.0
    return round(5*clamp(v if v<=1 else v/5),2)
