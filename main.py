"""Command-line entry point."""
from __future__ import annotations
import argparse
import logging
from pathlib import Path
from .config import TICKERS
from .data_loader import DemoProvider, JsonProvider, LiveProvider
from .data_validation import validate_company
from .ranking import rank_companies, recommended_candidate
from .reporting import save_report
from .excel_reporting import export_workbook
from .tracking import SnapshotStore, PredictionTracker

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log=logging.getLogger(__name__)

def parse_args():
    ap=argparse.ArgumentParser(description="AI-assisted investment research and stock-scoring system")
    ap.add_argument("--ticker",action="append",help="Analyze one ticker; repeat flag for multiple")
    ap.add_argument("--provider",choices=["live","demo","json"],default="demo")
    ap.add_argument("--data",default="data/demo_companies.json",help="JSON path for demo/json providers")
    ap.add_argument("--no-sec",action="store_true",help="Disable SEC cross-check for live provider")
    ap.add_argument("--excel",default="reports/investment_dashboard.xlsx")
    ap.add_argument("--save-snapshot",action="store_true")
    ap.add_argument("--save-decision",action="store_true")
    return ap.parse_args()

def main():
    args=parse_args()
    tickers=args.ticker or (TICKERS if args.provider=="live" else None)
    if args.provider=="live": provider=LiveProvider(use_sec=not args.no_sec)
    elif args.provider=="json": provider=JsonProvider(args.data)
    else: provider=DemoProvider(args.data)
    companies=provider.load(tickers)
    if not companies: raise SystemExit("No matching company data found")
    for company in companies:
        for warning in validate_company(company).warnings: log.warning("%s: %s",company.ticker,warning)
    ranked=rank_companies(companies)
    pick=recommended_candidate(ranked)
    for row in ranked:
        print(f"{row.rank:>2}. {row.company.ticker:<6} {row.score.total_score:>6.2f} {row.score.classification:<11} Risk={row.risks.severity:<6} Confidence={row.quality.confidence:>5.1f}")
        save_report(row,Path("reports")/f"{row.company.ticker}_report.txt")
    workbook=export_workbook(ranked,args.excel,pick)
    print("\nRecommended candidate:",pick.company.ticker if pick else "None (risk/data-quality screen blocked all candidates)")
    print("Excel dashboard:",workbook)
    if args.save_snapshot:
        try: print("Snapshot:",SnapshotStore().save(companies))
        except FileExistsError as exc: log.warning(str(exc))
    if args.save_decision and pick:
        try: print("Prediction:",PredictionTracker().save(pick))
        except FileExistsError as exc: log.warning(str(exc))

if __name__=="__main__": main()
