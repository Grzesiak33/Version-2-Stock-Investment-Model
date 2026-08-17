import pandas as pd
import numpy as np

def percentage_return(start,end): return (end/start)-1 if start else np.nan
def max_drawdown(prices):
    s=pd.Series(prices,dtype=float); peak=s.cummax(); return float(((s/peak)-1).min()) if len(s) else np.nan
def compare_return(model_return,benchmark_return): return model_return-benchmark_return
def win_rate(returns):
    s=pd.Series(returns,dtype=float).dropna(); return float((s>0).mean()) if len(s) else np.nan
def ranking_effectiveness(scores,returns):
    a=pd.Series(scores,dtype=float); b=pd.Series(returns,dtype=float)
    return float(a.corr(b,method="spearman")) if len(a)>=2 else np.nan
def equal_weight_return(returns): return float(pd.Series(returns,dtype=float).mean())
def strategy_returns(frame):
    """Expected columns: ticker, return, momentum, growth. Returns benchmark-ready simple strategy metrics."""
    f=frame.copy()
    return {"equal_weight":float(f["return"].mean()),
            "momentum":float(f.nlargest(max(1,len(f)//3),"momentum")["return"].mean()),
            "growth":float(f.nlargest(max(1,len(f)//3),"growth")["return"].mean())}
