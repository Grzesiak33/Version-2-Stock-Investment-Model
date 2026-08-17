from src.models import CompanyData
from src.ranking import rank_companies,recommended_candidate

def test_high_risk_candidate_can_be_blocked():
    high=CompanyData("AAA",company_name="A",revenue_growth=.4,free_cash_flow=100,cash=1,debt=100,price_to_sales=25,
                     data_sources=["x"],data_timestamp="2026-08-17T12:00:00+00:00")
    safe=CompanyData("BBB",company_name="B",revenue_growth=.1,free_cash_flow=10,cash=100,debt=1,price_to_sales=5,
                     data_sources=["x"],data_timestamp="2026-08-17T12:00:00+00:00")
    rows=rank_companies([high,safe])
    pick=recommended_candidate(rows,min_confidence=0)
    assert pick is not None and pick.risks.severity != "HIGH"
