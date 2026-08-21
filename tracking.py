"""Immutable prediction, daily snapshot and ranking-history storage."""
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

class SnapshotStore:
    def __init__(self, root="data/historical/snapshots"):
        self.root=Path(root); self.root.mkdir(parents=True, exist_ok=True)
    def save(self, companies: list[CompanyData], snapshot_date: str | None = None) -> Path:
        stamp = snapshot_date or datetime.now(timezone.utc).date().isoformat()
        path = self.root / f"{stamp}.json"
        if path.exists(): raise FileExistsError(f"Daily snapshot exists: {path}")
        path.write_text(json.dumps([x.to_dict() for x in companies], indent=2), encoding="utf-8")
        return path

class RankingHistory:
    def __init__(self, root="data/historical/rankings"):
        self.root=Path(root); self.root.mkdir(parents=True, exist_ok=True)
    def save(self, ranked: list[RankedStock], run_date: str | None = None) -> Path:
        stamp=run_date or datetime.now(timezone.utc).date().isoformat(); path=self.root/f"{stamp}.json"
        if path.exists(): raise FileExistsError(f"Daily ranking exists: {path}")
        rows=[]
        for x in ranked:
            baseline=x.company.metadata.get("experiment_start_price")
            current=x.company.share_price
            since=None if baseline in (None,0) or current is None else current/baseline-1
            rows.append({"ticker":x.company.ticker,"rank":x.rank,"score":x.score.total_score,
                         "classification":x.score.classification,"price":current,"experiment_start_price":baseline,
                         "return_since_experiment_start":since,"confidence":x.quality.confidence,
                         "risk":x.risks.severity,"model_version":x.score.model_version})
        path.write_text(json.dumps(rows,indent=2),encoding="utf-8"); return path
    def previous(self, before_date: str | None = None):
        cutoff=before_date or date.today().isoformat()
        files=sorted(p for p in self.root.glob("*.json") if p.stem < cutoff)
        return None if not files else json.loads(files[-1].read_text(encoding="utf-8"))

def rank_changes(ranked: list[RankedStock], previous_rows) -> dict[str,int|None]:
    old={x["ticker"]:x["rank"] for x in (previous_rows or [])}
    return {x.company.ticker:(None if x.company.ticker not in old else old[x.company.ticker]-x.rank) for x in ranked}
