"""AI Stocks Made Simple - mobile-first beginner research and simulation app."""
from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st
import yfinance as yf

APP_VERSION="2.2.1-beta"
UNIVERSE=["NVDA","MSFT","AVGO","PLTR","AMD","GOOGL","AMZN","META","ORCL","TSM","ASML","ARM","CRWD","PANW","ANET","VRT","SNOW","DDOG","NET","NOW","MDB","PATH","MU","AMAT","MRVL","DELL","SMCI","CRDO","TER","ACMR"]
NAMES={"NVDA":"NVIDIA","MSFT":"Microsoft","AVGO":"Broadcom","PLTR":"Palantir","AMD":"AMD","GOOGL":"Alphabet","AMZN":"Amazon","META":"Meta","ORCL":"Oracle","TSM":"TSMC","ASML":"ASML","ARM":"Arm","CRWD":"CrowdStrike","PANW":"Palo Alto Networks","ANET":"Arista Networks","VRT":"Vertiv","SNOW":"Snowflake","DDOG":"Datadog","NET":"Cloudflare","NOW":"ServiceNow","MDB":"MongoDB","PATH":"UiPath","MU":"Micron","AMAT":"Applied Materials","MRVL":"Marvell","DELL":"Dell","SMCI":"Super Micro Computer","CRDO":"Credo","TER":"Teradyne","ACMR":"ACM Research"}
DOMAINS={"NVDA":"nvidia.com","MSFT":"microsoft.com","AVGO":"broadcom.com","PLTR":"palantir.com","AMD":"amd.com","GOOGL":"google.com","AMZN":"amazon.com","META":"meta.com","ORCL":"oracle.com","TSM":"tsmc.com","ASML":"asml.com","ARM":"arm.com","CRWD":"crowdstrike.com","PANW":"paloaltonetworks.com","ANET":"arista.com","VRT":"vertiv.com","SNOW":"snowflake.com","DDOG":"datadoghq.com","NET":"cloudflare.com","NOW":"servicenow.com","MDB":"mongodb.com","PATH":"uipath.com","MU":"micron.com","AMAT":"appliedmaterials.com","MRVL":"marvell.com","DELL":"dell.com","SMCI":"supermicro.com","CRDO":"credosemi.com","TER":"teradyne.com","ACMR":"acmrcsh.com"}
AI_ROLES={"NVDA":"AI chips & accelerated computing","MSFT":"Azure cloud & enterprise AI","AVGO":"AI networking & custom silicon","PLTR":"Enterprise AI software","AMD":"AI accelerators & data-center CPUs","GOOGL":"Cloud, models & AI chips","AMZN":"AWS AI infrastructure","META":"AI models, ads & recommendations","ORCL":"Cloud infrastructure & databases","TSM":"Advanced AI-chip manufacturing","ASML":"Chipmaking lithography systems"}

st.set_page_config(page_title="AI Stocks Made Simple",page_icon="🤖",layout="wide")
st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#071124 0,#101b3d 25%,#f6f8fc 58%);}
.hero{padding:22px;border-radius:24px;background:radial-gradient(circle at 80% 10%,#c026d3 0,transparent 28%),radial-gradient(circle at 12% 20%,#ff7a00 0,transparent 30%),linear-gradient(135deg,#07152f,#092c5f 48%,#11143f);color:white;border:1px solid #38bdf8;box-shadow:0 12px 38px #0006;margin-bottom:18px}.hero h1{font-size:clamp(2rem,7vw,4rem);margin:0;background:linear-gradient(90deg,#22d3ee,#a855f7,#f97316);-webkit-background-clip:text;color:transparent}.hero p{font-size:1.05rem}.pill{display:inline-block;padding:7px 12px;border-radius:999px;background:#0b244d;border:1px solid #22d3ee;margin:4px 4px 4px 0}.stockcard{background:#0a1328;color:white;border:1px solid #23345e;border-radius:18px;padding:14px;margin:8px 0}.rank{font-size:1.5rem;font-weight:800;color:#22d3ee}.tiny{font-size:.8rem;color:#a9bad8}.logo{width:34px;height:34px;border-radius:8px;background:white;padding:3px;vertical-align:middle;margin-right:8px}.simbox{background:linear-gradient(135deg,#171042,#082a4d);color:white;border:1px solid #a855f7;border-radius:20px;padding:18px}.disclaimer{font-size:.78rem;color:#64748b}.stTabs [data-baseweb="tab"]{font-size:16px;font-weight:700}
</style>""",unsafe_allow_html=True)

@st.cache_data(ttl=300,show_spinner=False)
def live_market(tickers):
    out={}
    try:
        raw=yf.download(tickers=list(tickers),period="6mo",interval="1d",group_by="ticker",auto_adjust=False,progress=False,threads=True)
        for t in tickers:
            try:
                d=raw[t] if len(tickers)>1 else raw
                close=d["Close"].dropna()
                if len(close):
                    p=float(close.iloc[-1]); prev=float(close.iloc[-2]) if len(close)>1 else p
                    m=float(close.iloc[-22]) if len(close)>=22 else float(close.iloc[0])
                    out[t]={"price":p,"day":p/prev-1 if prev else 0,"month":p/m-1 if m else 0,"spark":close.tail(30).tolist()}
            except Exception: pass
    except Exception: pass
    return out

def latest_model_rows():
    p=Path("data/historical/rankings")
    files=sorted(p.glob("*.json")) if p.exists() else []
    if not files:return [],None
    try:return json.loads(files[-1].read_text(encoding="utf-8")),files[-1].stem
    except Exception:return [],None

def logo(t): return f"https://www.google.com/s2/favicons?domain={DOMAINS.get(t,'example.com')}&sz=64"

def payday_dates(start,end):
    d=start; arr=[]
    while d<=end:
        arr.append(d); d+=timedelta(days=14)
    return arr

rows,snapshot_date=latest_model_rows()
market=live_market(tuple(UNIVERSE))
rankmap={r.get("ticker"):r for r in rows}
ranked=[t for t in UNIVERSE if t in market]
ranked.sort(key=lambda t:(rankmap.get(t,{}).get("rank",999),-market[t].get("month",0)))

st.markdown(f"""<div class='hero'><div class='pill'>🐍 AI model + live market data</div><div class='pill'>🥤 Beginner friendly</div><h1>AI STOCKS<br>MADE SIMPLE</h1><p><b>AI powered. Data driven. Easier investing research.</b></p><p>See the AI-stock leaderboard, learn what each company does, and simulate how small bi-weekly contributions can accumulate over time.</p><div class='tiny'>Prices refresh about every 5 minutes while the app is active. Model rankings use the latest completed model snapshot.</div></div>""",unsafe_allow_html=True)

tab1,tab2,tab3,tab4=st.tabs(["🏆 TOP 20","💵 PAYDAY SIMULATOR","🎓 LEARN","⚙️ MODEL"])

with tab1:
    st.subheader("Top 20 AI-related stocks")
    st.caption("Rank order follows the latest model snapshot when available; price, daily change and recent trend refresh from market data.")
    if not market: st.error("Live market prices are temporarily unavailable. Please refresh shortly.")
    for i,t in enumerate(ranked[:20],1):
        m=market[t]; r=rankmap.get(t,{})
        score=r.get("score")
        c1,c2,c3,c4=st.columns([2.4,1,1,1.2])
        with c1:
            st.markdown(f"<div class='rank'>#{i} <img class='logo' src='{logo(t)}'>{NAMES[t]} <span class='tiny'>{t}</span></div><div class='tiny'>{AI_ROLES.get(t,'AI ecosystem company')}</div>",unsafe_allow_html=True)
        c2.metric("Price",f"${m['price']:,.2f}",f"{m['day']:+.2%}")
        c3.metric("1 mo",f"{m['month']:+.1%}")
        c4.metric("AI score","—" if score is None else f"{float(score):.0f}/100")
        if len(m["spark"])>2: st.line_chart(pd.DataFrame({t:m["spark"]}),height=85)
        st.divider()

with tab2:
    st.markdown("<div class='simbox'><h2>💵 Payday Accumulation Simulator</h2><p>Pick up to three AI stocks, choose how much you want to simulate investing every two weeks, and rotate the purchase from A → B → C on each payday.</p></div>",unsafe_allow_html=True)
    available=ranked[:20] if ranked else UNIVERSE[:20]
    c1,c2,c3=st.columns(3)
    a=c1.selectbox("Stock A",available,index=available.index("MSFT") if "MSFT" in available else 0,format_func=lambda x:f"{NAMES[x]} ({x})")
    b=c2.selectbox("Stock B",available,index=available.index("NVDA") if "NVDA" in available else min(1,len(available)-1),format_func=lambda x:f"{NAMES[x]} ({x})")
    c=c3.selectbox("Stock C",available,index=available.index("GOOGL") if "GOOGL" in available else min(2,len(available)-1),format_func=lambda x:f"{NAMES[x]} ({x})")
    amount=st.number_input("Amount invested each payday",min_value=1.0,max_value=10000.0,value=10.0,step=5.0,format="$%.2f")
    d1,d2=st.columns(2)
    start=d1.date_input("First payday",value=date.today())
    end=d2.date_input("Simulate through",value=date(2026,12,31),min_value=date.today())
    mode=st.radio("Purchase plan",["Rotate A → B → C every payday","Buy all selected stocks every payday"],horizontal=False)
    if end<start:
        st.warning("End date must be after the first payday.")
    elif st.button("🚀 Run my simulation",use_container_width=True,type="primary"):
        picks=[a,b,c]; dates=payday_dates(start,end); ledger=[]; shares={x:0.0 for x in picks}; invested={x:0.0 for x in picks}
        for i,d in enumerate(dates):
            targets=[picks[i%len(picks)]] if mode.startswith("Rotate") else list(dict.fromkeys(picks))
            for t in targets:
                price=market.get(t,{}).get("price")
                if not price: continue
                qty=amount/price; shares[t]+=qty; invested[t]+=amount
                ledger.append({"Date":d,"Stock":t,"Contribution":amount,"Price assumption":price,"Shares added":qty})
        total=sum(invested.values()); value=sum(shares[t]*market.get(t,{}).get("price",0) for t in shares)
        st.success(f"By {end:%b %d, %Y}, this schedule makes {len(dates)} bi-weekly payday cycles.")
        k1,k2,k3=st.columns(3); k1.metric("Total contributed",f"${total:,.2f}"); k2.metric("Value at today's prices",f"${value:,.2f}"); k3.metric("Purchases",str(len(ledger)))
        summary=[]
        for t in dict.fromkeys(picks):
            p=market.get(t,{}).get("price",0); summary.append({"Stock":f"{NAMES[t]} ({t})","Invested":invested[t],"Shares accumulated":shares[t],"Value at today's price":shares[t]*p})
        sdf=pd.DataFrame(summary).set_index("Stock")
        st.dataframe(sdf.style.format({"Invested":"${:,.2f}","Shares accumulated":"{:.4f}","Value at today's price":"${:,.2f}"}),use_container_width=True)
        if ledger:
            ldf=pd.DataFrame(ledger); chart=ldf.groupby("Date")["Contribution"].sum().cumsum(); st.markdown("### How your contributions build") ; st.area_chart(chart,height=220)
            with st.expander("See every simulated payday"): st.dataframe(ldf,use_container_width=True,hide_index=True)
        st.info("This simulation holds today's stock prices constant so you can see the contribution/share accumulation clearly. It is not a forecast of what these stocks will be worth in the future.")

with tab3:
    st.subheader("AI investing in plain English")
    st.markdown("### 🐍 Meet the model's Python helper")
    st.write("Think of the model like a nerdy Python with glasses: it checks the same evidence across every company instead of chasing whatever stock is getting the most hype.")
    for q,a in [("What is an AI stock?","A company materially involved in AI chips, cloud computing, data centers, networking, cybersecurity, databases or AI software."),("Why invest small amounts repeatedly?","Regular contributions can make investing easier to budget and reduce the pressure to guess one perfect entry day. It does not eliminate the risk of loss."),("What are fractional shares?","They let you buy part of a share. If Microsoft costs hundreds of dollars, a brokerage that supports fractional shares may still let you invest $10."),("Why can rankings change?","Growth, profitability, valuation, price momentum, competitive position, catalysts and other evidence change over time.")]:
        with st.expander(q):st.write(a)

with tab4:
    st.subheader("How the 100-point model works")
    cats=[("Revenue Growth",15),("Earnings / Free Cash Flow",15),("Industry Growth",15),("Balance Sheet",10),("Valuation",10),("Competitive Advantage",10),("Momentum",10),("Insider / Institutional",5),("Catalysts",5),("Inflation Resilience",5)]
    for n,p in cats: st.progress(p/15,text=f"{n} — {p} points")
    st.caption(f"App {APP_VERSION} • Latest model snapshot: {snapshot_date or 'not yet available'}")

st.divider(); st.markdown("<div class='disclaimer'>Educational research only. The app does not know your personal financial circumstances, does not place trades, and does not guarantee returns. Live prices may be delayed by the market-data provider. Stocks can lose value.</div>",unsafe_allow_html=True)
