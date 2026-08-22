"""Experiment-baseline utilities.

Reconstructs only historical market price from the experiment start date. It does
not backfill historical fundamentals that were not preserved at inception.
"""
from __future__ import annotations
import pandas as pd
from .models import CompanyData

def attach_experiment_start_prices(companies: list[CompanyData], start_date: str) -> list[CompanyData]:
    import yfinance as yf
    start=pd.Timestamp(start_date)
    end=start+pd.Timedelta(days=5)
    for company in companies:
        try:
            hist=yf.Ticker(company.ticker).history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), auto_adjust=True)
            close=hist.get("Close")
            if close is not None and len(close):
                company.metadata["experiment_start_price"]=float(close.iloc[0])
                company.metadata["experiment_start_price_date"]=str(close.index[0].date())
                company.metadata["experiment_baseline_note"]="Historical adjusted close only; inception fundamentals were not archived."
        except Exception as exc:
            company.metadata["experiment_baseline_error"]=str(exc)
    return companies
