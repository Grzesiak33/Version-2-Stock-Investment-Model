from datetime import datetime, timezone
from src.models import CompanyData
from src.data_validation import assess_data_quality, validate_company

def test_complete_data_has_higher_confidence_than_empty():
    full=CompanyData("ABC",company_name="ABC",revenue=1,revenue_growth=.2,eps=1,eps_growth=.1,free_cash_flow=1,cash=1,debt=0,
                     gross_margin=.5,operating_margin=.2,pe_ratio=20,price_to_sales=5,price_to_fcf=25,one_month_return=.01,
                     three_month_return=.02,six_month_return=.03,one_year_return=.04,institutional_activity=.5,
                     data_timestamp=datetime.now(timezone.utc).isoformat(),data_sources=["test"])
    empty=CompanyData("XYZ")
    assert assess_data_quality(full).confidence > assess_data_quality(empty).confidence

def test_conflicts_reduce_confidence():
    base=dict(company_name="ABC",revenue=1,revenue_growth=.2,eps=1,eps_growth=.1,free_cash_flow=1,cash=1,debt=0,gross_margin=.5,
              operating_margin=.2,pe_ratio=20,price_to_sales=5,price_to_fcf=25,one_month_return=.01,three_month_return=.02,
              six_month_return=.03,one_year_return=.04,institutional_activity=.5,data_timestamp=datetime.now(timezone.utc).isoformat(),data_sources=["test"])
    a=CompanyData("ABC",**base); b=CompanyData("ABC",**base,metadata={"conflicting_fields":["revenue"]})
    assert assess_data_quality(b).confidence < assess_data_quality(a).confidence
