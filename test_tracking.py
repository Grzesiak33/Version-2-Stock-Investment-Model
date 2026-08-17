import json,pytest
from src.models import CompanyData
from src.ranking import rank_companies
from src.tracking import PredictionTracker
def test_prediction_immutable(tmp_path):
    t=PredictionTracker(tmp_path); r=rank_companies([CompanyData("ABC",share_price=10)])[0]
    p=t.save(r,"2026-08-14"); before=p.read_text()
    with pytest.raises(FileExistsError): t.save(r,"2026-08-14")
    assert p.read_text()==before
    out=t.record_outcome(p,11,.01,True,"occurred")
    assert p.read_text()==before and json.loads(out.read_text())["percentage_return"]==pytest.approx(.1)
