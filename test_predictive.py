import pandas as pd
from src.predictive import forward_return_summary,enough_for_ml

def test_predictive_summary():
    f=pd.DataFrame({"score":[60,70,80],"percentage_return":[-.1,.05,.2]})
    out=forward_return_summary(f)
    assert out["observations"]==3 and out["win_rate"]==2/3 and out["score_return_spearman"]>0

def test_ml_guardrail():
    assert not enough_for_ml(99)
    assert enough_for_ml(100)
