from src.models import CompanyData
from src.ranking import rank_companies
def test_deterministic_ties():
    rows=[CompanyData("ZZZ"),CompanyData("AAA")]
    assert [x.company.ticker for x in rank_companies(rows)]==["AAA","ZZZ"]
