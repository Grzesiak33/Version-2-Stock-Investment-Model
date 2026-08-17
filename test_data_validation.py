from src.models import CompanyData
from src.data_validation import validate_company
def test_bad_ticker(): assert not validate_company(CompanyData("bad ticker")).valid
def test_missing_does_not_crash(): assert validate_company(CompanyData("ABC")).valid
def test_impossible_price(): assert not validate_company(CompanyData("ABC",share_price=-1)).valid
