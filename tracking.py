"""Immutable prediction and daily snapshot storage."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import date, datetime, timezone
from .ranking import RankedStock
from .models import CompanyData

class PredictionTracker:
    def __init__(self, root="data/historical"): self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def save(self, row: RankedStock, prediction_date=None):
        d=prediction_date or date.today().isoformat(); p=self.root/f"{d}_{row.company.ticker}_{row.score.model_version}.json"
        if p.exists(): raise FileExistsError(f"Historical prediction exists: {p}")
        payload={"date":d,"ticker":row.company.ticker,"score":row.score.total_score,"ranking":row.rank,
                 "classification":row.score.classification,"price_at_prediction":row.company.share_price,
                 "investment_thesis":row.company.metadata.get("investment_thesis",""),"catalysts":row.company.catalysts,
                 "risks":row.risks.flags,"risk_level":row.risks.severity,"data_confidence":row.quality.confidence,
                 "model_version":row.score.model_version,"data_sources":row.company.data_sources}
        p.write_text(json.dumps(payload,indent=2),encoding="utf-8"); return p
    def record_outcome(self,prediction_path,actual_price,benchmark_return=None,thesis_accuracy=None,catalyst_outcome=None):
        src=Path(prediction_path); base=json.loads(src.read_text(encoding="utf-8")); start=base.get("price_at_prediction")
        ret=None if start in (None,0) else (actual_price/start)-1
        out={**base,"actual_price":actual_price,"percentage_return":ret,"benchmark_return":benchmark_return,
             "relative_performance":None if ret is None or benchmark_return is None else ret-benchmark_return,
             "prediction_accuracy":None if ret is None else ret>0,"thesis_accuracy":thesis_accuracy,"catalyst_outcome":catalyst_outcome}
        p=src.with_name(src.stem+"_outcome.json")
        if p.exists(): raise FileExistsError(p)
        p.write_text(json.dumps(out,indent=2),encoding="utf-8"); return p

class SnapshotStore:
    def __init__(self, root="data/historical/snapshots"):
        self.root=Path(root); self.root.mkdir(parents=True, exist_ok=True)
    def save(self, companies: list[CompanyData], snapshot_date: str | None = None) -> Path:
        stamp = snapshot_date or datetime.now(timezone.utc).date().isoformat()
        path = self.root / f"{stamp}.json"
        if path.exists(): raise FileExistsError(f"Daily snapshot exists: {path}")
        path.write_text(json.dumps([x.to_dict() for x in companies], indent=2), encoding="utf-8")
        return path
