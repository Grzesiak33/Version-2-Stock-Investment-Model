"""Streamlit front end for the investment research model."""
import streamlit as st
from src.config import TICKERS, MODEL_VERSION, NEXT_DECISION_POINT
from src.data_loader import LiveProvider
from src.ranking import rank_companies, recommended_candidate
from src.excel_reporting import export_workbook

st.set_page_config(page_title="AI Investment Research Model",layout="wide")
st.title("AI Investment Research Model")
st.caption(f"Model {MODEL_VERSION} • Research/decision support only • Next experiment decision point: {NEXT_DECISION_POINT}")
selected=st.multiselect("Ticker universe",TICKERS,default=TICKERS[:11])
use_sec=st.checkbox("Cross-check fundamentals with SEC EDGAR",value=True)
if st.button("Run live analysis",type="primary"):
    with st.spinner("Collecting and validating market data..."):
        rows=rank_companies(LiveProvider(use_sec=use_sec).load(selected))
        pick=recommended_candidate(rows)
        st.subheader("Current Rankings")
        st.dataframe([{ "Rank":r.rank,"Ticker":r.company.ticker,"Score":r.score.total_score,"Class":r.score.classification,
                        "Risk":r.risks.severity,"Confidence":r.quality.confidence,"Price":r.company.share_price} for r in rows],use_container_width=True)
        if pick:
            st.success(f"Current eligible candidate: {pick.company.ticker} — score {pick.score.total_score}, risk {pick.risks.severity}, confidence {pick.quality.confidence}%")
        else: st.warning("No candidate passes the independent risk/data-confidence screen.")
        path=export_workbook(rows,"reports/investment_dashboard.xlsx",pick)
        with open(path,"rb") as fh: st.download_button("Download Excel dashboard",fh,file_name="investment_dashboard.xlsx")
        st.warning("This tool is research and decision support, not a guarantee of returns or personalized fiduciary advice.")
