"""Command-line entry point."""
from __future__ import annotations
import argparse
import logging
from pathlib import Path
from .config import TICKERS, EXPERIMENT_START, QUALITATIVE_RESEARCH_PATH
from .data_loader import DemoProvider, JsonProvider, LiveProvider
from .data_validation import validate_company
from .ranking import rank_companies, recommended_candidate
from .reporting import save_report
from .excel_reporting import export_workbook
from .tracking import SnapshotStore, PredictionTracker, RankingHistory, rank_changes
from .qualitative import apply_qualitative_research
from .experiment import attach_experiment_start_prices

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log=logging.getLogger(__name__)

def parse_args():
    ap=argparse.ArgumentParser(description="AI-assisted investment research and stock-scoring system")
    ap.add_argument("--ticker",action="append",help="Analyze one ticker; repeat flag for multiple")
    ap.add_argument("--provider",choices=["live","demo","json"],default="demo")
    ap.add_argument("--data",default="data/demo_companies.json",help="JSON path for demo/json providers")
    ap.add_argument("--no-sec",action="store_true",help="Disable SEC cross-check for live provider")
    ap.add_argument("--qualitative",default=QUALITATIVE_RESEARCH_PATH,help="Sourced qualitative research JSON")
    ap.add_argument("--excel",default="reports/investment_dashboard.xlsx")
    ap.add_argument("--save-snapshot",action="store_true")
    ap.add_argument("--save-decision",action="store_true")
    ap.add_argument("--save-ranking",action="store_true")
    return ap.parse_args()

def main():
    args=parse_args()
    tickers=args.ticker or (TICKERS if args.provider=="live" else None)
    if args.provider=="live": provider=LiveProvider(use_sec=not args.no_sec)
    elif args.provider=="json": provider=JsonProvider(args.data)
    else: provider=DemoProvider(args.data)
    companies=provider.load(tickers)
    if not companies: raise SystemExit("No matching company data found")
    companies=apply_qualitative_research(companies,args.qualitative)
    if args.provider=="live": companies=attach_experiment_start_prices(companies,EXPERIMENT_START)
    for company in companies:
        for warning in validate_company(company).warnings: log.warning("%s: %s",company.ticker,warning)
    ranked=rank_companies(companies)
    history=RankingHistory(); changes=rank_changes(ranked,history.previous())
    pick=recommended_candidate(ranked)
    for row in ranked:
        delta=changes[row.company.ticker]; move="NEW" if delta is None else (f"+{delta}" if delta>0 else str(delta))
        base=row.company.metadata.get("experiment_start_price"); price=row.company.share_price
        ret=None if base in (None,0) or price is None else price/base-1
        ret_text="n/a" if ret is None else f"{ret:+.2%}"
        print(f"{row.rank:>2}. {row.company.ticker:<6} {row.score.total_score:>6.2f} {row.score.classification:<11} Move={move:<4} SinceStart={ret_text:<8} Risk={row.risks.severity:<6} Confidence={row.quality.confidence:>5.1f}")
        save_report(row,Path("reports")/f"{row.company.ticker}_report.txt")
    workbook=export_workbook(ranked,args.excel,pick)
    print("\nRecommended candidate:",pick.company.ticker if pick else "None (risk/data-quality screen blocked all candidates)")
    print("Excel dashboard:",workbook)
    if args.save_snapshot:
        try: print("Snapshot:",SnapshotStore().save(companies))
        except FileExistsError as exc: log.warning(str(exc))
    if args.save_ranking:
        try: print("Ranking history:",history.save(ranked))
        except FileExistsError as exc: log.warning(str(exc))
    if args.save_decision and pick:
        try: print("Prediction:",PredictionTracker().save(pick))
        except FileExistsError as exc: log.warning(str(exc))

if __name__=="__main__": main()
