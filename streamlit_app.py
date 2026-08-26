from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

APP_VERSION = "3.5.1-recovery"
ROBINHOOD_URL = "https://join.robinhood.com/steveng-15bac4"
NAMES={"MU":"Micron","TSM":"TSMC","CRDO":"Credo","ANET":"Arista Networks","PLTR":"Palantir","TER":"Teradyne","NVDA":"NVIDIA","DELL":"Dell","PATH":"UiPath","AMD":"AMD","GOOGL":"Alphabet","AMAT":"Applied Materials","DDOG":"Datadog","AVGO":"Broadcom","SNOW":"Snowflake","AMZN":"Amazon","MDB":"MongoDB","NET":"Cloudflare","ACMR":"ACM Research","VRT":"Vertiv","ASML":"ASML","SMCI":"Super Micro Computer","MSFT":"Microsoft","PANW":"Palo Alto Networks","ARM":"Arm","META":"Meta","CRWD":"CrowdStrike","MRVL":"Marvell","NOW":"ServiceNow","ORCL":"Oracle"}
INFO={
"NVDA":("Makes GPUs and AI computing platforms.","Its chips power much of modern AI training and inference.","High expectations and competition can make the stock volatile."),
"MSFT":("Builds Windows, Microsoft 365, Azure and enterprise software.","Azure and Copilot put AI into widely used business products.","Large-company growth can be steadier, but valuation still matters."),
"GOOGL":("Owns Google Search, YouTube, Android and Google Cloud.","Gemini and AI are used across search, cloud, ads and consumer products.","AI competition could change search and advertising economics."),
"PLTR":("Builds data and analytics software for companies and governments.","AIP helps organizations use AI with their own operational data.","The stock can trade at a high valuation."),
"AMD":("Designs CPUs, GPUs and data-center processors.","Its Instinct accelerators compete in AI computing.","It faces intense competition from NVIDIA and others."),
"AMZN":("Runs Amazon retail and AWS cloud computing.","AWS sells AI infrastructure, models and services.","Heavy spending and cloud competition can pressure margins."),
"META":("Owns Facebook, Instagram, WhatsApp and Threads.","Uses AI for recommendations, ads and the Llama model family.","Large AI infrastructure spending may take time to pay off."),
"TSM":("Manufactures advanced chips designed by other companies.","Many leading AI processors depend on TSMC manufacturing.","Geopolitical risk around Taiwan is important."),
"AVGO":("Designs semiconductors and infrastructure software.","Custom AI accelerators and networking are important in AI data centers.","Customer concentration and chip cycles can create swings.")}

st.set_page_config(page_title="AI Stocks Made Simple",page_icon="⚡",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
.stApp{background:#020711;color:#f3f8ff}.block-container{max-width:1050px;padding-top:.55rem;padding-bottom:4rem}.hero{padding:18px;border-radius:24px;border:1px solid #315b8f;background:radial-gradient(circle at 12% 20%,#ec489944,transparent 25%),radial-gradient(circle at 88% 20%,#0ea5e944,transparent 28%),linear-gradient(135deg,#06152c,#171044,#3b0b38);box-shadow:0 0 28px #0ea5e92c}.hero h1{margin:0;font-size:clamp(2.5rem,7vw,5rem);line-height:.9;font-style:italic;background:linear-gradient(90deg,#22d3ee,#818cf8,#e879f9);-webkit-background-clip:text;color:transparent}.hero p{font-size:1.05rem;color:#c3d5e8}.chip{display:inline-block;padding:6px 10px;margin:3px;border:1px solid #22d3ee;border-radius:999px;background:#071a2b;color:#c7f5ff;font-weight:800}.panel{padding:15px;border:1px solid #17365f;border-radius:18px;background:#07111f;margin:.7rem 0}.selected{padding:11px;border:1px solid #22c55e;border-radius:13px;background:#052d23}.small{font-size:.8rem;color:#92a8c0}.stButton>button,.stLinkButton>a{border-radius:13px!important;font-weight:800;min-height:44px}.stMetric{background:#07111f;border:1px solid #17365f;border-radius:14px;padding:10px}
</style>""",unsafe_allow_html=True)

def latest_snapshot():
    p=Path("data/historical/rankings"); files=sorted(p.glob("*.json")) if p.exists() else []
    if not files:return [],"unavailable"
    try:return json.loads(files[-1].read_text(encoding="utf-8")),files[-1].stem
    except Exception:return [],"unavailable"

def schedule(start,end,days):
    out=[]; d=start
    while d<=end and len(out)<1000:
        out.append(d); d+=timedelta(days=days)
    return out

rows,snapshot=latest_snapshot(); rows=sorted(rows,key=lambda r:r.get("rank",999))[:20]
if not rows:
    st.error("The saved market ranking snapshot could not be loaded."); st.stop()
stocks=[]
for r in rows:
    t=r.get("ticker","")
    stocks.append({"ticker":t,"name":NAMES.get(t,t),"rank":int(r.get("rank",0) or 0),"score":float(r.get("score",0) or 0),"price":float(r.get("price",0) or 0),"risk":r.get("risk","—")})
lookup={s["ticker"]:s for s in stocks}; tickers=list(lookup)
hero=Path("assets/hero_v3_mobile.jpg")
if hero.exists():
    try: st.image(str(hero),use_container_width=True)
    except Exception: pass
st.markdown(f"<div class='hero'><h1>AI STOCKS<br>MADE SIMPLE</h1><p>Pick a stock. Pick an amount. Build a payday routine. See how it adds up.</p><span class='chip'>VERSION {APP_VERSION}</span><span class='chip'>🔥 TOP 20 AI STOCKS</span><span class='chip'>🔄 ROTATION MODE</span><span class='chip'>Snapshot {snapshot}</span></div>",unsafe_allow_html=True)

st.markdown("## 🎯 Build your payday plan")
mode=st.radio("Choose a mode",["ONE STOCK","ROTATION MODE"],horizontal=True)
if mode=="ONE STOCK":
    selected=st.selectbox("Pick your stock",tickers,format_func=lambda t:f"{lookup[t]['name']} ({t}) — ${lookup[t]['price']:,.2f}")
    plan=[selected]
    st.markdown(f"<div class='selected'><b>{lookup[selected]['name']} ({selected})</b> • ${lookup[selected]['price']:,.2f} • Model score {lookup[selected]['score']:.1f}</div>",unsafe_allow_html=True)
else:
    plan=st.multiselect("Choose 2–5 stocks in rotation order",tickers,default=tickers[:3],max_selections=5,format_func=lambda t:f"{lookup[t]['name']} ({t})")
    if plan: st.markdown("**Rotation:** "+" → ".join(plan)+" → repeat")
if "amount" not in st.session_state: st.session_state.amount=10.0
cols=st.columns(5)
for c,val in zip(cols,[5,10,25,50,100]):
    if c.button(f"${val}",use_container_width=True,key=f"q{val}"): st.session_state.amount=float(val)
amount=st.number_input("Amount each payday",min_value=1.0,value=float(st.session_state.amount),step=1.0); st.session_state.amount=amount
c1,c2,c3=st.columns(3)
freq=c1.selectbox("How often?",["Every 2 weeks","Every Friday / weekly","Monthly"]); days={"Every 2 weeks":14,"Every Friday / weekly":7,"Monthly":30}[freq]
start=c2.date_input("Start date",value=date.today()); end=c3.date_input("Project through",value=date(2026,12,31),min_value=date.today())
with st.expander("Optional: growth scenario"):
    scenario=st.selectbox("Illustrative annual growth",["No growth","Moderate 5%","Growth 10%"]); st.caption("Illustration only. This is not a forecast of any stock's future return.")
rate={"No growth":0.0,"Moderate 5%":0.05,"Growth 10%":0.10}[scenario]
if st.button("⚡ SHOW ME HOW THIS ADDS UP",type="primary",use_container_width=True):
    if end<start: st.error("End date must be after start date.")
    elif not plan or (mode=="ROTATION MODE" and len(plan)<2): st.error("Choose at least two stocks for Rotation Mode.")
    else:
        dates=schedule(start,end,days); by={t:{"contrib":0.0,"shares":0.0,"buys":0} for t in plan}; ledger=[]; total_future=0.0
        for i,d in enumerate(dates):
            t=plan[i%len(plan)]; p=max(lookup[t]["price"],0.01); years=max((end-d).days,0)/365.25; total_future+=amount*((1+rate)**years); by[t]["contrib"]+=amount; by[t]["shares"]+=amount/p; by[t]["buys"]+=1; ledger.append({"Payday":d,"Stock":t,"Amount":amount,"Price used":p,"Shares":amount/p})
        contributed=amount*len(dates); m1,m2,m3,m4=st.columns(4); m1.metric("YOU PUT IN",f"${contributed:,.2f}"); m2.metric("PAYDAYS",len(dates)); m3.metric("STOCKS",len(plan)); m4.metric("ILLUSTRATIVE VALUE",f"${total_future:,.2f}")
        st.markdown("### By stock"); st.dataframe(pd.DataFrame([{"Stock":f"{lookup[t]['name']} ({t})","Buys":x["buys"],"Contributed":x["contrib"],"Shares":x["shares"]} for t,x in by.items()]),hide_index=True,use_container_width=True)
        st.markdown("### Next paycheck purchases"); st.dataframe(pd.DataFrame(ledger).head(10),hide_index=True,use_container_width=True); st.caption("Future prices will change. This is an educational planning illustration, not individualized investment advice or a guarantee.")

st.markdown("## 🔥 Top 20 AI stocks"); st.caption("Open any company to see a beginner-friendly explanation.")
for s in stocks:
    t=s["ticker"]
    with st.expander(f"#{s['rank']}  {s['name']} ({t})  •  ${s['price']:,.2f}  •  Score {s['score']:.1f}"):
        what,why,risk=INFO.get(t,(f"{s['name']} participates in the broader technology and AI ecosystem.","Its products or services have exposure to AI-related demand.","Business performance and the stock price can change significantly.")); st.markdown(f"**What they do:** {what}"); st.markdown(f"**Why AI cares:** {why}"); st.markdown(f"**Key risk:** {risk}"); st.caption(f"Model risk label: {s['risk']}")
st.markdown("## 🎓 Start small. Learn as you go.")
cols=st.columns(4)
for c,title,text in zip(cols,["🚀 Start Small","🧠 Learn","🎯 Build a Routine","🛡️ Risk First"],["$5 or $10 is enough to learn the habit.","Company explanations use plain English.","Use one stock or rotate several each payday.","Stocks can fall. Rankings are not guarantees."]): c.markdown(f"<div class='panel'><b>{title}</b><br><span class='small'>{text}</span></div>",unsafe_allow_html=True)
st.markdown("### 🌱 Optional Robinhood referral"); st.caption("This referral never changes rankings or simulator results."); st.link_button("Open Robinhood",ROBINHOOD_URL,use_container_width=True); st.caption("I may receive a referral reward if you sign up or qualify through this link. Educational research only; no trades are placed.")