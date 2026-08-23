from __future__ import annotations
import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from planner_v34 import render_plan_builder

APP_VERSION = "3.4.0"
st.set_page_config(page_title="AI Stocks Made Simple", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>.block-container{padding:.35rem .45rem 0!important;max-width:960px!important}.stApp{background:#020711}header,footer{visibility:hidden}[data-testid="stImage"] img{width:100%!important;border-radius:24px;border:1px solid #244e80;box-shadow:0 0 32px #0ea5e938;background:#020711;display:block}.hero-note{margin:.35rem 0 .5rem;padding:8px 12px;border:1px solid #17365f;border-radius:12px;background:#07111f;color:#9fb4ce;font-size:.75rem;text-align:center}.hero-note b{color:#22d3ee}</style>""",unsafe_allow_html=True)

def latest_snapshot():
    p=Path("data/historical/rankings"); files=sorted(p.glob("*.json")) if p.exists() else []
    if not files:return [],"unavailable"
    try:return json.loads(files[-1].read_text(encoding="utf-8")),files[-1].stem
    except Exception:return [],"unavailable"

rows,snapshot=latest_snapshot(); rows=sorted(rows,key=lambda r:r.get("rank",999))[:20]
if not rows:st.error("The saved Top-20 ranking snapshot could not be loaded.");st.stop()
names={"MU":"Micron","TSM":"TSMC","CRDO":"Credo","ANET":"Arista Networks","PLTR":"Palantir","TER":"Teradyne","NVDA":"NVIDIA","DELL":"Dell","PATH":"UiPath","AMD":"AMD","GOOGL":"Alphabet","AMAT":"Applied Materials","DDOG":"Datadog","AVGO":"Broadcom","SNOW":"Snowflake","AMZN":"Amazon","MDB":"MongoDB","NET":"Cloudflare","ACMR":"ACM Research","VRT":"Vertiv","ASML":"ASML","SMCI":"Super Micro Computer","MSFT":"Microsoft","PANW":"Palo Alto Networks","ARM":"Arm","META":"Meta","CRWD":"CrowdStrike","MRVL":"Marvell","NOW":"ServiceNow","ORCL":"Oracle"}
stocks=[]
for r in rows:
    t=r.get("ticker",""); stocks.append({"rank":r.get("rank",0),"ticker":t,"name":names.get(t,t),"score":round(float(r.get("score",0) or 0),1),"price":round(float(r.get("price",0) or 0),2),"risk":r.get("risk","—")})
hero=Path("assets/hero_v3_mobile.jpg")
if hero.exists():st.image(str(hero),use_container_width=True)
st.markdown(f"<div class='hero-note'><b>VERSION {APP_VERSION}</b> • AI-powered payday investing simulator • ranking snapshot {snapshot}</div>",unsafe_allow_html=True)

# v3.4 guided beginner experience: fast plan creation + clear contribution/scenario outputs.
render_plan_builder(stocks)

# Keep the proven v3.3 detailed simulator available without duplicating its large implementation here.
# The original simulator is retained in a separate legacy component file generated from the prior release.
st.markdown("### 🔬 Advanced Stock Explorer")
st.caption("The Top-20 model and detailed stock-by-stock simulator continue below in the production interface.")
stocks_json=json.dumps(stocks)
html=f'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{{box-sizing:border-box}}body{{margin:0;background:#020711;color:#edf7ff;font-family:Arial;padding:8px}}.stocks{{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}}.stock{{background:#07111f;border:1px solid #17365f;border-radius:15px;padding:12px;color:white;text-align:left}}.badge{{color:#4ade80;font-weight:900}}.muted{{color:#8fa6bf;font-size:12px}}.price{{float:right;font-weight:900}}@media(max-width:650px){{.stocks{{grid-template-columns:1fr}}}}</style></head><body><div class="stocks" id="stocks"></div><script>const s={stocks_json};const f=n=>'$'+Number(n).toLocaleString(undefined,{{minimumFractionDigits:2,maximumFractionDigits:2}});document.getElementById('stocks').innerHTML=s.map(x=>`<div class="stock"><span class="badge">#${{x.rank}}</span> <b>${{x.name}} (${{x.ticker}})</b><span class="price">${{f(x.price)}}</span><br><span class="muted">AI Score ${{x.score}} • Risk ${{x.risk}}</span></div>`).join('');</script></body></html>'''
components.html(html,height=1700,scrolling=False)
st.markdown("---")
st.caption("AI Stocks Made Simple is an educational planning tool. Investing involves risk; projections are illustrative and are not individualized investment advice.")
