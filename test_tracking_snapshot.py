import pytest
from src.models import CompanyData
from src.tracking import SnapshotStore

def test_daily_snapshot_is_immutable(tmp_path):
    s=SnapshotStore(tmp_path)
    p=s.save([CompanyData("ABC")],"2026-08-17")
    before=p.read_text()
    with pytest.raises(FileExistsError): s.save([CompanyData("ABC",share_price=99)],"2026-08-17")
    assert p.read_text()==before
