"""Transparent predictive diagnostics. Not a claim of future-return reliability."""
from __future__ import annotations
import numpy as np
import pandas as pd

def forward_return_summary(history: pd.DataFrame) -> dict[str, float | None]:
    """Summarize historical prediction outcomes without fitting a predictive ML model."""
    if history.empty or "percentage_return" not in history: return {"observations": 0, "mean_return": None, "win_rate": None, "score_return_spearman": None}
    f=history.dropna(subset=["percentage_return"]).copy()
    corr=None
    if len(f)>=3 and "score" in f and f["score"].nunique()>1:
        corr=float(f["score"].corr(f["percentage_return"], method="spearman"))
    return {"observations":int(len(f)),"mean_return":float(f["percentage_return"].mean()) if len(f) else None,
            "win_rate":float((f["percentage_return"]>0).mean()) if len(f) else None,"score_return_spearman":corr}

def enough_for_ml(observations: int, minimum: int = 100) -> bool:
    """Conservative guardrail preventing premature ML claims."""
    return observations >= minimum
