# Changelog

All material methodology changes increment `MODEL_VERSION`; historical results are never rewritten.

## 2.0.0 — 2026-08-17

- Added replaceable live market-data provider using `yfinance`.
- Added optional SEC EDGAR Company Facts cross-checking for revenue, cash, and debt.
- Added an expanded, configurable AI-related stock universe.
- Added explicit Data Confidence and Data Completeness metrics outside the 0–100 investment score.
- Strengthened independent risk screening and recommendation eligibility logic.
- Added immutable daily market snapshots and enriched prediction records.
- Added Excel workbook/dashboard generation with rankings, category scores, fundamentals, data quality, and payday decision tabs.
- Added transparent historical predictive diagnostics and a guardrail preventing premature ML use.
- Added Streamlit web dashboard suitable for phone/browser use.
- Added GitHub Actions for tests and optional weekday market snapshots.
- Preserved share-price independence, deterministic rankings, fixed 100-point weights, and no-fabrication behavior.
- Live qualitative fields that cannot be reliably derived from free objective feeds remain unavailable rather than being invented.

## 1.0.0 — 2026-08-17

- Initial deterministic scoring, ranking, reporting, risk, benchmarking and immutable prediction tracking engine.
