# BUILD THIS ENTIRE PROJECT

You are the primary software engineer responsible for building this repository.

I want you to create the complete working Python project described below. Do not merely explain how to build it. **Actually create the files, write the code, create the tests, and configure the project.**

The project is an **AI-assisted investment research and stock-scoring system**.

The purpose is to identify publicly traded companies with the strongest combination of growth, financial quality, valuation, competitive advantage, catalysts, momentum, inflation resilience, and acceptable risk.

This is a research and decision-support system. It is NOT a guarantee of investment returns.

---

# 1. TECHNOLOGY REQUIREMENTS

Use:

- Python 3.11+
- pandas
- numpy
- pytest

Use additional open-source Python packages when they are genuinely useful.

The architecture must be modular and maintainable.

Create:

```
investment-model/
│
├── README.md
├── PROJECT_SPEC.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── historical/
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_validation.py
│   ├── fundamentals.py
│   ├── valuation.py
│   ├── momentum.py
│   ├── catalysts.py
│   ├── risk_analysis.py
│   ├── scoring.py
│   ├── ranking.py
│   ├── benchmarking.py
│   ├── tracking.py
│   └── reporting.py
│
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py
│   ├── test_valuation.py
│   ├── test_data_validation.py
│   ├── test_ranking.py
│   ├── test_tracking.py
│   └── test_benchmarking.py
│
├── reports/
│
└── notebooks/

```

If another structure is objectively better, you may improve it, but maintain the same separation of responsibilities.

---

# 2. CORE SCORING MODEL

Every stock receives a score from 0–100.

The exact weights are:

| CategoryPoints                       |         |
| ------------------------------------ | ------- |
| Revenue Growth                       | 15      |
| Earnings / Free Cash Flow            | 15      |
| Industry Growth                      | 15      |
| Balance Sheet / Financial Strength   | 10      |
| Valuation                            | 10      |
| Competitive Advantage / Moat         | 10      |
| Price Trend / Momentum               | 10      |
| Insider / Institutional Activity     | 5       |
| Catalysts                            | 5       |
| Inflation Resilience / Pricing Power | 5       |
| **TOTAL**                            | **100** |

The scoring engine must retain every individual category score.

Never produce only a final score.

---

# 3. ABSOLUTE MODEL RULES

These rules are mandatory.

## Rule A — Share price is NOT valuation

A $2 stock is not automatically cheaper than a $200 stock.

The absolute share price must NEVER directly increase the investment score.

If two companies are identical except for share price, changing the share price alone must not improve the fundamental investment score.

---

## Rule B — Do not chase hype

A stock that recently exploded upward must not automatically receive a high score.

Momentum is only one component.

---

## Rule C — Growth alone is insufficient

High revenue growth cannot compensate indefinitely for:

- terrible valuation
- unsustainable cash burn
- excessive debt
- severe dilution
- weak competitive position
- collapsing margins

---

## Rule D — Small-cap stocks are allowed

The model should be capable of discovering small-cap/high-growth opportunities.

However:

**small market capitalization itself receives zero bonus points.**

The company must earn its score through fundamentals, growth, valuation, moat, catalysts, etc.

---

## Rule E — Never fabricate data

If reliable data cannot be obtained:

- mark it unavailable
- identify the missing field
- do not invent a number
- do not silently substitute a fictional estimate

The system should record the date and source of important data.

---

# 4. FUNDAMENTAL ANALYSIS

Create functions/classes capable of evaluating:

### Revenue Growth

Consider:

- historical growth
- recent growth
- forward growth where available
- acceleration/deceleration
- consistency
- organic vs acquisition-driven growth

Maximum: 15 points.

---

### Earnings / Free Cash Flow

Consider:

- EPS growth
- profitability
- operating margins
- margin expansion
- free cash flow
- free cash flow growth
- operating leverage

Maximum: 15 points.

---

### Industry Growth

Consider:

- total addressable market
- industry growth
- secular trends
- technological disruption
- competitive intensity
- long-term demand

Maximum: 15 points.

---

### Balance Sheet

Consider:

- cash
- debt
- net debt
- liquidity
- debt/equity
- interest coverage
- dilution
- ability to finance growth

Maximum: 10 points.

---

### Valuation

Evaluate valuation relative to:

- revenue
- earnings
- free cash flow
- growth rate
- industry peers
- historical valuation
- expected future growth

Do NOT use absolute share price as a valuation metric.

Maximum: 10 points.

---

### Competitive Advantage

Consider:

- network effects
- switching costs
- brand
- proprietary technology
- patents/IP
- cost advantage
- distribution
- scale
- data advantage
- customer lock-in

Maximum: 10 points.

---

### Momentum

Consider:

- 1-month return
- 3-month return
- 6-month return
- 1-year return
- relative strength
- trend consistency
- volume
- breakouts/breakdowns

Maximum: 10 points.

Momentum must NOT dominate the model.

---

### Insider / Institutional Activity

Consider:

- insider buying
- insider selling
- institutional ownership
- institutional accumulation
- changes in institutional positioning

Maximum: 5 points.

---

### Catalysts

Identify genuine identifiable catalysts such as:

- earnings
- product launches
- new contracts
- regulatory approvals
- partnerships
- AI adoption
- capacity expansion
- new markets
- M&A
- industry changes

Maximum: 5 points.

Distinguish actual catalysts from speculation.

---

### Inflation Resilience

Consider:

- pricing power
- recurring revenue
- essential products/services
- ability to pass costs to customers
- gross margin stability
- input-cost sensitivity

Maximum: 5 points.

---

# 5. RISK ENGINE

Create a separate risk-analysis module.

Identify:

- excessive valuation
- debt
- dilution
- customer concentration
- regulatory risk
- competition
- commodity exposure
- dependence on one product
- unprofitable growth
- management concerns
- concentration risk
- macroeconomic sensitivity

Risk should be clearly visible in reports.

Do not hide risk inside a single mysterious score.

---

# 6. CLASSIFICATION

Use:

```
85–100 = BUY
75–84  = WATCH
65–74  = INTERESTING
50–64  = RESEARCH
0–49   = REJECT

```

The classification must be generated programmatically.

---

# 7. INITIAL STOCK UNIVERSE

Start with:

```
TICKERS = [
    "NVDA",
    "PLTR",
    "AMD",
    "AVGO",
    "AMAT",
    "MU",
    "ACMR",
    "CRDO",
    "TER",
    "CRWD",
    "PANW",
]

```

Make it easy to add additional stocks.

---

# 8. DATA ARCHITECTURE

Build the data layer so that data providers can be replaced.

Do not hard-code the entire model around one API.

Create normalized company data structures containing fields such as:

```
ticker
company_name
sector
industry
market_cap
share_price
revenue
revenue_growth
eps
eps_growth
free_cash_flow
free_cash_flow_growth
cash
debt
gross_margin
operating_margin
pe_ratio
price_to_sales
price_to_fcf
one_month_return
three_month_return
six_month_return
one_year_return
insider_activity
institutional_activity
industry_growth
competitive_advantage
catalysts
inflation_resilience
risk_factors
data_timestamp
data_sources

```

Use `None`/`NaN` appropriately for unavailable information.

---

# 9. SCORING ENGINE

Implement a clean scoring interface.

For example:

```
class StockScore:
    revenue_growth: float
    earnings_fcf: float
    industry_growth: float
    balance_sheet: float
    valuation: float
    competitive_advantage: float
    momentum: float
    insider_institutional: float
    catalysts: float
    inflation_resilience: float

    total_score: float
    classification: str

```

Validate that:

```
0 <= every category score <= category maximum
0 <= total_score <= 100

```

The total must equal the sum of the category scores.

---

# 10. RANKING

Create a ranking engine.

Given multiple companies, return:

1. highest score
2. second highest
3. third highest
4. etc.

Include:

- ticker
- company
- total score
- classification
- category scores
- major strengths
- major weaknesses
- risks
- catalysts

Tie handling must be deterministic.

---

# 11. REPORTING

Generate a human-readable report.

Example:

```
PLTR
Score: 87/100
Classification: BUY

Revenue Growth: 14/15
Earnings/FCF: 13/15
Industry Growth: 15/15
Balance Sheet: 10/10
Valuation: 5/10
Moat: 9/10
Momentum: 9/10
Insider/Institutional: 3/5
Catalysts: 5/5
Inflation Resilience: 4/5

Major Strengths:
- ...
- ...
- ...

Major Risks:
- ...
- ...

Key Catalysts:
- ...
- ...

Investment Thesis:
...

What Would Invalidate the Thesis:
...

```

The report must explain the reasoning behind the score.

---

# 12. HISTORICAL PREDICTION TRACKING

This is an ongoing experiment.

Every research cycle must save:

- date
- ticker
- score
- ranking
- classification
- price at prediction
- investment thesis
- catalysts
- risks

Later record:

- actual price
- percentage return
- benchmark return
- prediction accuracy
- thesis accuracy
- catalyst outcome

Never overwrite historical predictions.

---

# 13. 14-DAY EXPERIMENT

The current experiment begins:

**August 14, 2026**

The next decision point is:

**August 28, 2026**

At the decision point the system should identify the strongest candidate for a **$10 investment** based on current evidence.

The system must not automatically select the highest-scoring company if there is a major risk or data-quality issue.

The final report should explain why the selected candidate was chosen.

---

# 14. BENCHMARKING

Track the model against:

- S&P 500
- equal-weight candidate portfolio
- simple momentum strategy
- simple growth strategy

Calculate:

- return
- percentage return
- relative performance
- drawdown where possible
- win rate
- ranking effectiveness

The objective is to determine whether this scoring system actually adds value.

---

# 15. MACHINE LEARNING

Do NOT immediately build a complicated machine-learning model.

Initially use a transparent deterministic scoring system.

As historical observations accumulate, prepare the architecture for:

- regression
- classification
- ranking models
- NLP
- sentiment analysis
- Hugging Face models

Only introduce ML when enough historical data exists to train and evaluate it properly.

Never claim that an ML model is reliable simply because it produces predictions.

---

# 16. TEST-DRIVEN DEVELOPMENT

Write pytest tests.

At minimum test:

### Score validation

- scores cannot be negative
- scores cannot exceed maximum
- total cannot exceed 100
- total equals category sum

### Weight validation

Verify all category maximums sum to exactly 100.

### Share-price independence

Changing only the absolute share price must NOT artificially increase the fundamental investment score.

### Classification

Test:

```
85 -> BUY
84 -> WATCH
75 -> WATCH
74 -> INTERESTING
65 -> INTERESTING
64 -> RESEARCH
50 -> RESEARCH
49 -> REJECT

```

### Missing data

Verify missing financial information does not crash the system.

### Ranking

Identical input should produce deterministic rankings.

### Historical tracking

Historical predictions must remain unchanged after later model updates.

---

# 17. DATA VALIDATION

Create a dedicated validation layer.

The validation system should detect:

- impossible values
- missing required fields
- stale data
- conflicting data
- malformed ticker symbols
- invalid percentages
- invalid financial ratios

Generate warnings instead of silently accepting questionable information.

---

# 18. MODEL VERSIONING

Every scoring methodology must have a version.

Example:

```
MODEL_VERSION = "1.0.0"

```

When scoring weights or methodology change:

- increment the version
- document the change
- preserve old results
- never rewrite historical scores as though the new methodology existed previously

Create a:

```
CHANGELOG.md

```

---

# 19. README

Create a complete README explaining:

- what the project does
- installation
- environment setup
- how to run the model
- how to add stocks
- how scoring works
- how reports are generated
- how tests are run
- how historical results are tracked
- limitations
- responsible-use disclaimer

Include examples.

---

# 20. COMMAND-LINE INTERFACE

Create a simple CLI so I can eventually run commands such as:

```
python -m src.main

```

and receive:

- current rankings
- individual scores
- recommended candidate
- risks
- catalysts
- report location

Also support something similar to:

```
python -m src.main --ticker PLTR

```

to analyze a specific company.

---

# 21. CODE QUALITY

Use:

- type hints
- docstrings
- clear variable names
- small functions
- modular design
- error handling
- logging where appropriate

Avoid:

- giant monolithic files
- duplicated scoring logic
- hard-coded magic numbers throughout the code
- silent failures
- fake financial data

Put scoring weights in one central configuration location.

---

# 22. IMPORTANT DEVELOPMENT INSTRUCTION

Do not stop after creating a skeleton.

**Actually implement the working code.**

After creating the files:

1. Install dependencies.
2. Run pytest.
3. Fix failures.
4. Run the application.
5. Fix runtime errors.
6. Verify the scoring engine.
7. Verify ranking.
8. Verify missing-data handling.
9. Verify historical tracking.
10. Update README with actual usage instructions.

If external market-data APIs require credentials, make the application gracefully support a demo/mock dataset so the tests and core scoring system can still run without credentials.

Clearly separate:

**real market data**

from

**test/demo data**.

Never present demo data as real market data.

---

# 23. FIRST IMPLEMENTATION GOAL

Build Version 1.0 as a **fully functioning research and scoring engine**.

Do not over-engineer it.

The first successful milestone is:

```
Input company data
        ↓
Validate data
        ↓
Analyze fundamentals
        ↓
Analyze valuation
        ↓
Analyze momentum
        ↓
Analyze risk
        ↓
Calculate 0–100 score
        ↓
Assign classification
        ↓
Rank candidates
        ↓
Generate explanation/report
        ↓
Save historical prediction

```

---

# 24. FINAL PRINCIPLE

The purpose of this project is NOT to find the stock with the lowest share price.

It is NOT to find whatever stock is currently hyped.

It is NOT to blindly buy the highest-growth company.

It is NOT to guarantee profit.

The objective is:

**Identify companies where the combination of future growth potential, business quality, financial strength, valuation, competitive advantage, catalysts, and risk creates an attractive risk-adjusted investment opportunity.**

The model must favor evidence over hype and maintain a historical record so we can determine whether the methodology actually works.

---

# YOUR TASK

Build this repository now.

Create the files.

Write the Python code.

Write the tests.

Run the tests.

Fix the errors.

Create the README.

Create PROJECT\_SPEC.md containing this specification.

Create CHANGELOG.md.

Do not merely tell me what code I should write.

**You are the developer. Build Version 1.0.**