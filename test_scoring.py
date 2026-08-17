import pytest
from src.config import CATEGORY_MAX
from src.models import StockScore,classify,CompanyData
from src.scoring import score_company

def base(**kw):
    d=dict(revenue_growth=5,earnings_fcf=5,industry_growth=5,balance_sheet=5,valuation=5,competitive_advantage=5,momentum=5,insider_institutional=2,catalysts=2,inflation_resilience=2); d.update(kw); return d
def test_weights_sum_100(): assert sum(CATEGORY_MAX.values())==100
def test_negative_rejected():
    with pytest.raises(ValueError): StockScore(**base(revenue_growth=-1))
def test_over_max_rejected():
    with pytest.raises(ValueError): StockScore(**base(valuation=11))
def test_total_equals_sum():
    s=StockScore(**base()); assert s.total_score==sum(getattr(s,k) for k in CATEGORY_MAX); assert s.total_score<=100
@pytest.mark.parametrize("n,label",[(85,"BUY"),(84,"WATCH"),(75,"WATCH"),(74,"INTERESTING"),(65,"INTERESTING"),(64,"RESEARCH"),(50,"RESEARCH"),(49,"REJECT")])
def test_classification(n,label): assert classify(n)==label
def test_share_price_independence():
    a=CompanyData("AAA",share_price=2,revenue_growth=.2,price_to_sales=5,pe_ratio=25,price_to_fcf=25)
    b=CompanyData("AAA",share_price=200,revenue_growth=.2,price_to_sales=5,pe_ratio=25,price_to_fcf=25)
    assert score_company(a).total_score==score_company(b).total_score
