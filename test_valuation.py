from src.models import CompanyData
from src.valuation import valuation_score
def test_share_price_not_used():
    a=CompanyData("AAA",share_price=1,pe_ratio=20,price_to_sales=4,price_to_fcf=20,revenue_growth=.2)
    b=CompanyData("AAA",share_price=1000,pe_ratio=20,price_to_sales=4,price_to_fcf=20,revenue_growth=.2)
    assert valuation_score(a)==valuation_score(b)
def test_missing_ok(): assert valuation_score(CompanyData("AAA"))==0
