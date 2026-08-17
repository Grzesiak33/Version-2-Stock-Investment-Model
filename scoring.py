from .models import CompanyData, StockScore
from .fundamentals import revenue_growth_score,earnings_fcf_score,industry_growth_score,balance_sheet_score,moat_score,inflation_score
from .valuation import valuation_score
from .momentum import momentum_score
from .catalysts import catalyst_score,activity_score

def score_company(d: CompanyData) -> StockScore:
    return StockScore(revenue_growth_score(d),earnings_fcf_score(d),industry_growth_score(d),balance_sheet_score(d),
        valuation_score(d),moat_score(d),momentum_score(d),activity_score(d),catalyst_score(d),inflation_score(d))
