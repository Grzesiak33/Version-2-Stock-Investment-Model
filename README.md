# AI-Assisted Investment Research Model — Version 2.0

A transparent Python/Pandas research and decision-support system for ranking AI-related public companies across growth, financial quality, industry opportunity, balance sheet, valuation, competitive advantage, momentum, ownership activity, catalysts and inflation resilience.

**This project is research software, not a guarantee of returns, individualized fiduciary advice, or an automated trading system.** It never places trades or connects to a brokerage account.

## What Version 2 adds

Version 2 supports a real-market-data workflow. It pulls objective price/fundamental data through `yfinance`, optionally cross-checks selected annual financial facts against SEC EDGAR Company Facts, validates freshness and conflicts, calculates the fixed 0–100 score, keeps Data Confidence and Risk Level separate, ranks candidates, produces human-readable reports, writes an Excel dashboard, and can preserve immutable daily snapshots and payday predictions.

Unavailable information remains `None`/missing. The application does **not** manufacture moat, industry-growth, pricing-power, or speculative catalyst evidence merely to fill the score. This means early live scores can be deliberately conservative until qualitative research inputs are added from reliable sources.

## Fixed scoring weights

| Category | Points |
|---|---:|
| Revenue Growth | 15 |
| Earnings / Free Cash Flow | 15 |
| Industry Growth | 15 |
| Balance Sheet / Financial Strength | 10 |
| Valuation | 10 |
| Competitive Advantage / Moat | 10 |
| Price Trend / Momentum | 10 |
| Insider / Institutional Activity | 5 |
| Catalysts | 5 |
| Inflation Resilience / Pricing Power | 5 |
| **Total** | **100** |

Share price and small market capitalization receive **zero direct valuation/scoring bonus**.

## Classification

- 85–100: BUY
- 75–84: WATCH
- 65–74: INTERESTING
- 50–64: RESEARCH
- 0–49: REJECT

A BUY classification does not automatically become a purchase candidate. The independent recommendation screen can block a top scorer for high risk, provider errors or insufficient data confidence.

## Install locally

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run the safe demo

The bundled JSON is synthetic and is never presented as real market data.

```bash
python -m src.main --provider demo
```

This creates text reports and `reports/investment_dashboard.xlsx`.

## Run real market analysis

Analyze one ticker:

```bash
python -m src.main --provider live --ticker PLTR
```

Analyze several:

```bash
python -m src.main --provider live --ticker NVDA --ticker PLTR --ticker AMD
```

Analyze the full configured AI universe:

```bash
python -m src.main --provider live
```

Disable the SEC cross-check when you only want the faster Yahoo/yfinance collection path:

```bash
python -m src.main --provider live --no-sec
```

Save that day's source data as an immutable snapshot:

```bash
python -m src.main --provider live --save-snapshot
```

Save the eligible candidate as an immutable prediction:

```bash
python -m src.main --provider live --save-decision
```

A repeated save for the same date/ticker/model version raises an error instead of overwriting history.

## Excel dashboard

The workbook is the primary non-developer interface and includes:

- **Current Rankings** — rank, ticker, score, classification, risk, confidence, strengths and weaknesses.
- **Category Scores** — all ten scores; the final score is never shown alone.
- **Fundamentals** — normalized source data.
- **Data Quality** — completeness, confidence, missing fields, conflicts and sources.
- **Payday Decision** — the highest-ranked candidate that passes independent risk/data-quality screens.

The default output is `reports/investment_dashboard.xlsx`.

## Streamlit web dashboard

Run locally:

```bash
streamlit run app.py
```

A browser opens with ticker selection, a Run Live Analysis button, rankings, current eligible candidate and an Excel download button. This is the intended path to a phone-friendly interface.

## GitHub setup

Create a **private** GitHub repository, then from this project directory:

```bash
git init
git add .
git commit -m "Investment model v2.0"
git branch -M main
git remote add origin YOUR_PRIVATE_REPOSITORY_URL
git push -u origin main
```

Never commit `.env`, `.streamlit/secrets.toml`, brokerage credentials, passwords or API keys. Version 2 does not require a market-data API key for its default live provider.

`.github/workflows/test.yml` runs pytest on pushes and pull requests. `.github/workflows/daily_snapshot.yml` is an optional weekday collection workflow and can also be run manually from GitHub Actions. Scheduled GitHub Actions use UTC and can be delayed; this workflow is for research snapshots, not time-critical trading.

## Deploy with Streamlit Community Cloud

After the private GitHub repository exists, create a Streamlit Community Cloud app using the repository and choose `app.py` as the entry point. Keep any future credentials in Streamlit secrets rather than source code. Once deployed, the application can be opened from a phone browser.

## Payday experiment

The experiment start is `2026-08-14` and the next specified decision point is `2026-08-28`. The application can collect observations daily while keeping formal investment decisions on the intended decision/payday schedule. Historical predictions contain the contemporaneous score, ranking, classification, price, thesis, catalysts, risks, model version and data confidence.

## Data architecture

`DataProvider` is an abstract interface. Current providers:

- `DemoProvider` — synthetic/offline testing only.
- `JsonProvider` — normalized external JSON supplied by the user/system.
- `LiveProvider` — yfinance + optional SEC cross-check.

A future paid or specialized provider can be added without rewriting scoring logic.

## Data validity

Validation detects malformed tickers, impossible negative prices/financial balances, malformed ratios, questionable percentages, stale timestamps, provider failures and conflicting source values. Data Confidence is deliberately separate from the investment score.

SEC cross-check failures are non-fatal and visible in metadata. SEC figures are filing-based and can differ from trailing-twelve-month provider values, so large differences are flagged for review rather than automatically treated as fraud or data error.

## Predictive analytics and ML

`src/predictive.py` evaluates historical outcomes using observation count, mean return, win rate and Spearman correlation between score and realized return. It deliberately refuses to treat machine learning as justified until enough history exists (`enough_for_ml`, default threshold 100 observations). Future models should be evaluated out-of-sample against the deterministic baseline.

## Benchmarking

`src/benchmarking.py` supports percentage return, benchmark-relative return, maximum drawdown, win rate, ranking effectiveness, equal-weight candidate return, simple momentum and simple growth strategy comparisons. SPY is the configured S&P 500 proxy.

## Tests

```bash
pytest -q
```

Tests cover fixed weights, classification boundaries, category limits, share-price independence, missing data, deterministic ties, validation, data confidence, Excel generation, predictive diagnostics, recommendation risk screening, immutable predictions, immutable snapshots and benchmarking.

## Adding stocks

Edit `TICKERS` in `src/config.py`. Market capitalization itself never earns points, so the universe can include both large and small companies without a size bonus.

## Important limitations

Free data sources can be incomplete, delayed, restated, rate-limited or inconsistent. `yfinance` is an unofficial interface to Yahoo Finance and should be treated as a convenient research source rather than an institutional market-data feed. SEC filing data is authoritative for filings but may not represent the same time basis as trailing provider metrics. Qualitative categories require verifiable research evidence and are intentionally left missing when Version 2 cannot obtain them reliably. Transaction costs, taxes, slippage, personal financial circumstances and portfolio-level suitability are outside the current scoring model.

The system's purpose is to improve evidence, discipline and measurement — not to promise profitable recommendations.
