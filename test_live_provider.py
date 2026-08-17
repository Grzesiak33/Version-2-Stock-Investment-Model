import pandas as pd
import src.data_loader as dl

def test_return_at_handles_history():
    idx=pd.date_range("2025-01-01", periods=400, freq="D")
    s=pd.Series(range(100,500),index=idx,dtype=float)
    assert dl._return_at(s,30) is not None

def test_clean_missing():
    assert dl._clean(None) is None
    assert dl._clean(float("nan")) is None
    assert dl._clean("12.5")==12.5
