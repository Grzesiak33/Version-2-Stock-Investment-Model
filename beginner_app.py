"""AI Stocks Made Simple - mobile-first beginner research, simulation and education app."""
from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st
import yfinance as yf

APP_VERSION="2.2.3-beta"
ROBINHOOD_REFERRAL_URL="https://join.robinhood.com/steveng-15bac4"
UNIVERSE=["NVDA","MSFT","AVGO","PLTR","AMD","GOOGL","AMZN","META","ORCL","TSM","ASML","ARM","CRWD","PANW","ANET","VRT","SNOW","DDOG","NET","NOW","MDB","PATH","MU","AMAT","MRVL","DELL","SMCI","CRDO","TER","ACMR"]
NAMES={"NVDA":"NVIDIA","MSFT":"Microsoft","AVGO":"Broadcom","PLTR":"Palantir","AMD":"AMD","GOOGL":"Alphabet","AMZN":"Amazon","META":"Meta","ORCL":"Oracle","TSM":"TSMC","ASML":"ASML","ARM":"Arm","CRWD":"CrowdStrike","PANW":"Palo Alto Networks","ANET":"Arista Networks","VRT":"Vertiv","SNOW":"Snowflake","DDOG":"Datadog","NET":"Cloudflare","NOW":"ServiceNow","MDB":"MongoDB","PATH":"UiPath","MU":"Micron","AMAT":"Applied Materials","MRVL":"Marvell","DELL":"Dell","SMCI":"Super Micro Computer","CRDO":"Credo","TER":"Teradyne","ACMR":"ACM Research"}
DOMAINS={"NVDA":"nvidia.com","MSFT":"microsoft.com","AVGO":"broadcom.com","PLTR":"palantir.com","AMD":"amd.com","GOOGL":"google.com","AMZN":"amazon.com","META":"meta.com","ORCL":"oracle.com","TSM":"tsmc.com","ASML":"asml.com","ARM":"arm.com","CRWD":"crowdstrike.com","PANW":"paloaltonetworks.com","ANET":"arista.com","VRT":"vertiv.com","SNOW":"snowflake.com","DDOG":"datadoghq.com","NET":"cloudflare.com","NOW":"servicenow.com","MDB":"mongodb.com","PATH":"uipath.com","MU":"micron.com","AMAT":"appliedmaterials.com","MRVL":"marvell.com","DELL":"dell.com","SMCI":"supermicro.com","CRDO":"credosemi.com","TER":"teradyne.com","ACMR":"acmrcsh.com"}
AI_ROLES={"NVDA":"AI chips & accelerated computing","MSFT":"Azure cloud & enterprise AI","AVGO":"AI networking & custom silicon","PLTR":"Enterprise AI software","AMD":"AI accelerators & data-center CPUs","GOOGL":"Cloud, models & AI chips","AMZN":"AWS AI infrastructure","META":"AI models, ads & recommendations","ORCL":"Cloud infrastructure & databases","TSM":"Advanced AI-chip manufacturing","ASML":"Chipmaking lithography systems"}

st.set_page_config(page_title="AI Stocks Made Simple",page_icon="🤖",layout="wide")
st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#061126 0,#151d4b 26%,#6d28d9 40%,#f6f8fc 62%);}
.hero{padding:24px;border-radius:28px;background:radial-gradient(circle at 86% 12%,#ec4899 0,transparent 27%),radial-gradient(circle at 12% 16%,#f97316 0,transparent 31%),linear-gradient(135deg,#07152f,#0b3d82 43%,#3b0764 76%,#11143f);color:white;border:1px solid #38bdf8;box-shadow:0 18px 44px #0007;margin-bottom:18px;overflow:hidden}.hero-grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(220px,.65fr);gap:20px;align-items:center}.hero h1{font-size:clamp(2.3rem,7vw,4.8rem);line-height:.95;margin:8px 0;background:linear-gradient(90deg,#22d3ee,#c084fc,#fb923c);-webkit-background-clip:text;color:transparent}.hero p{font-size:1.05rem}.pill{display:inline-block;padding:7px 12px;border-radius:999px;background:#0b244d;border:1px solid #22d3ee;margin:4px 4px 4px 0}.mascot{background:linear-gradient(160deg,#0f172a,#312e81);border:1px solid #a855f7;border-radius:24px;padding:12px;text-align:center}.mascot svg{max-width:100%;height:auto}.rank{font-size:1.45rem;font-weight:800;color:#155eef}.tiny{font-size:.82rem;color:#64748b}.logo{width:36px;height:36px;border-radius:9px;background:white;padding:3px;vertical-align:middle;margin-right:8px;box-shadow:0 4px 14px #0002}.simbox{background:linear-gradient(135deg,#1e1b4b,#0c4a6e 50%,#7c2d12);color:white;border:1px solid #c084fc;border-radius:22px;padding:20px}.sponsorbox{background:linear-gradient(135deg,#052e16,#14532d 58%,#0f172a);color:white;border:1px solid #22c55e;border-radius:22px;padding:20px}.sponsorlabel{display:inline-block;font-size:.72rem;letter-spacing:.08em;font-weight:800;padding:5px 9px;border-radius:999px;background:#166534;color:#dcfce7;margin-bottom:8px}.disclaimer{font-size:.78rem;color:#64748b}.stTabs [data-baseweb="tab"]{font-size:16px;font-weight:800}.stButton>button,.stLinkButton>a{border-radius:14px!important}
@media(max-width:760px){.hero-grid{grid-template-columns:1fr}.mascot{max-width:320px;margin:auto}.stTabs [data-baseweb="tab"]{font-size:13px}}
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

rows,snapshot_date=latest_model_rows(); market=live_market(tuple(UNIVERSE)); rankmap={r.get("ticker"):r for r in rows}
ranked=[t for t in UNIVERSE if t in market]; ranked.sort(key=lambda t:(rankmap.get(t,{}).get("rank",999),-market[t].get("month",0)))

MASCOT="""<div class='mascot'><svg viewBox='0 0 320 300' role='img' aria-label='Cartoon guide with Python snake and red pop'><defs><linearGradient id='shirt' x1='0' x2='1'><stop stop-color='#0ea5e9'/><stop offset='1' stop-color='#f97316'/></linearGradient></defs><circle cx='155' cy='73' r='48' fill='#f1b38d'/><path d='M112 70c6-42 82-57 93 0-8-21-24-34-47-34-22 0-38 12-46 34z' fill='#1f2937'/><path d='M120 74c12 7 20 9 35 9s24-3 38-10c-4 43-17 61-37 61-21 0-34-19-36-60z' fill='#f1b38d'/><path d='M126 103c12 26 49 30 64-1-3 36-17 53-34 53-17 0-29-17-30-52z' fill='#3f2a25'/><rect x='98' y='139' width='118' height='115' rx='30' fill='url(#shirt)'/><path d='M105 169c-22 4-34 21-42 47l28 11 22-46zM210 168c26 7 36 27 43 49l-28 10-21-47z' fill='#f1b38d'/><path d='M113 157h92v28h-92z' fill='#1d4ed8'/><text x='159' y='176' text-anchor='middle' font-size='15' font-weight='800' fill='white'>AI STOCKS</text><path d='M250 87c34 4 41 36 15 45-26 8-43-13-29-28 10-12 32-6 30 8-2 11-17 11-21 4' fill='none' stroke='#22c55e' stroke-width='11' stroke-linecap='round'/><circle cx='252' cy='86' r='7' fill='#22c55e'/><circle cx='249' cy='83' r='1.7'/><circle cx='255' cy='83' r='1.7'/><rect x='240' y='82' width='9' height='6' rx='2' fill='none' stroke='black' stroke-width='2'/><rect x='254' y='82' width='9' height='6' rx='2' fill='none' stroke='black' stroke-width='2'/><rect x='42' y='168' width='38' height='93' rx='9' fill='#ef4444'/><rect x='47' y='176' width='28' height='49' rx='4' fill='white'/><text x='61' y='194' text-anchor='middle' font-size='9' font-weight='900' fill='#dc2626'>RED</text><text x='61' y='206' text-anchor='middle' font-size='9' font-weight='900' fill='#dc2626'>POP</text><circle cx='137' cy='72' r='13' fill='none' stroke='#111827' stroke-width='4'/><circle cx='176' cy='72' r='13' fill='none' stroke='#111827' stroke-width='4'/><path d='M150 72h13' stroke='#111827' stroke-width='4'/></svg><b>Your AI investing guide</b><div class='tiny' style='color:#cbd5e1'>Python-powered research, Red Pop energy.</div></div>"""

st.markdown(f"""<div class='hero'><div class='hero-grid'><div><div class='pill'>🐍 AI model + live market data</div><div class='pill'>🥤 Beginner friendly</div><div class='pill'>💸 Start small</div><h1>AI STOCKS<br>MADE SIMPLE</h1><p><b>AI powered. Data driven. Easier investing research.</b></p><p>See the AI-stock leaderboard, learn what each company does, and simulate how small bi-weekly contributions can build over time.</p><div class='tiny' style='color:#cbd5e1'>Prices refresh about every 5 minutes while active. Model rankings use the latest completed snapshot.</div></div>{MASCOT}</div></div>""",unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5=st.tabs(["🏆 TOP 20","💵 PAYDAY SIMULATOR","🎓 LEARN","⚙️ MODEL","💚 SPONSOR"])

with tab1:
    st.subheader("Top 20 AI-related stocks")
    st.caption("Rank order follows the latest model snapshot when available; market price, daily change and recent trend refresh from live market data.")
    if not market: st.error("Live market prices are temporarily unavailable. Please refresh shortly.")
    for i,t in enumerate(ranked[:20],1):
        m=market[t]; r=rankmap.get(t,{}); score=r.get("score")
        c1,c2,c3,c4=st.columns([2.4,1,1,1.2])
        with c1: st.markdown(f"<div class='rank'>#{i} <img class='logo' src='{logo(t)}'>{NAMES[t]} <span class='tiny'>{t}</span></div><div class='tiny'>{AI_ROLES.get(t,'AI ecosystem company')}</div>",unsafe_allow_html=True)
        c2.metric("Price",f"${m['price']:,.2f}",f"{m['day']:+.2%}"); c3.metric("1 mo",f"{m['month']:+.1%}"); c4.metric("AI score","—" if score is None else f"{float(score):.0f}/100")
        if len(m["spark"])>2: st.line_chart(pd.DataFrame({t:m["spark"]}),height=85)
        st.divider()

with tab2:
    st.markdown("<div class='simbox'><h2>💵 Payday Accumulation Simulator</h2><p>Choose up to three AI stocks, a bi-weekly amount, and an ending date. Rotate A → B → C every payday or buy all selected stocks each payday.</p></div>",unsafe_allow_html=True)
    available=ranked[:20] if ranked else UNIVERSE[:20]
    c1,c2,c3=st.columns(3)
    a=c1.selectbox("Stock A",available,index=available.index("MSFT") if "MSFT" in available else 0,format_func=lambda x:f"{NAMES[x]} ({x})")
    b=c2.selectbox("Stock B",available,index=available.index("NVDA") if "NVDA" in available else min(1,len(available)-1),format_func=lambda x:f"{NAMES[x]} ({x})")
    c=c3.selectbox("Stock C",available,index=available.index("GOOGL") if "GOOGL" in available else min(2,len(available)-1),format_func=lambda x:f"{NAMES[x]} ({x})")
    amount=st.number_input("Amount invested each payday",min_value=1.0,max_value=10000.0,value=10.0,step=5.0,format="$%.2f")
    d1,d2=st.columns(2); start=d1.date_input("First payday",value=date.today()); end=d2.date_input("Simulate through",value=date(2026,12,31),min_value=date.today())
    mode=st.radio("Purchase plan",["Rotate A → B → C every payday","Buy all selected stocks every payday"])
    if end<start: st.warning("End date must be after the first payday.")
    elif st.button("🚀 Run my simulation",use_container_width=True,type="primary"):
        picks=[a,b,c]; dates=payday_dates(start,end); ledger=[]; shares={x:0.0 for x in picks}; invested={x:0.0 for x in picks}
        for i,d in enumerate(dates):
            targets=[picks[i%len(picks)]] if mode.startswith("Rotate") else list(dict.fromkeys(picks))
            for t in targets:
                price=market.get(t,{}).get("price")
                if not price: continue
                qty=amount/price; shares[t]+=qty; invested[t]+=amount; ledger.append({"Date":d,"Stock":t,"Contribution":amount,"Price assumption":price,"Shares added":qty})
        total=sum(invested.values()); value=sum(shares[t]*market.get(t,{}).get("price",0) for t in shares)
        st.success(f"By {end:%b %d, %Y}, this schedule includes {len(dates)} bi-weekly payday cycles.")
        k1,k2,k3=st.columns(3); k1.metric("Total contributed",f"${total:,.2f}"); k2.metric("Value at today's prices",f"${value:,.2f}"); k3.metric("Purchases",str(len(ledger)))
        summary=[]
        for t in dict.fromkeys(picks):
            p=market.get(t,{}).get("price",0); summary.append({"Stock":f"{NAMES[t]} ({t})","Invested":invested[t],"Shares accumulated":shares[t],"Value at today's price":shares[t]*p})
        sdf=pd.DataFrame(summary).set_index("Stock"); st.dataframe(sdf.style.format({"Invested":"${:,.2f}","Shares accumulated":"{:.4f}","Value at today's price":"${:,.2f}"}),use_container_width=True)
        if ledger:
            ldf=pd.DataFrame(ledger); chart=ldf.groupby("Date")["Contribution"].sum().cumsum(); st.markdown("### How your contributions build"); st.area_chart(chart,height=230)
            with st.expander("See every simulated payday"): st.dataframe(ldf,use_container_width=True,hide_index=True)
        st.info("This simulation holds today's stock prices constant. It illustrates contribution and share accumulation; it is not a forecast of future stock prices or returns.")

with tab3:
    st.subheader("AI investing in plain English")
    st.markdown("### 🐍 Meet your Python-powered guide")
    st.write("The model checks the same evidence across every company instead of chasing whatever stock is getting the most hype.")
    for q,a_text in [("What is an AI stock?","A company materially involved in AI chips, cloud computing, data centers, networking, cybersecurity, databases or AI software."),("Why invest small amounts repeatedly?","Regular contributions can make investing easier to budget and reduce the pressure to guess one perfect entry day. It does not eliminate risk."),("What are fractional shares?","They let you buy part of a share. A brokerage that supports fractional shares may let you invest $10 even when a whole share costs hundreds of dollars."),("Why can rankings change?","Growth, profitability, valuation, price momentum, competitive position, catalysts and other evidence change over time.")]:
        with st.expander(q): st.write(a_text)

with tab4:
    st.subheader("How the 100-point model works")
    for n,p in [("Revenue Growth",15),("Earnings / Free Cash Flow",15),("Industry Growth",15),("Balance Sheet",10),("Valuation",10),("Competitive Advantage",10),("Momentum",10),("Insider / Institutional",5),("Catalysts",5),("Inflation Resilience",5)]: st.progress(p/15,text=f"{n} — {p} points")
    st.caption(f"App {APP_VERSION} • Latest model snapshot: {snapshot_date or 'not yet available'}")

with tab5:
    st.markdown("<div class='sponsorbox'><div class='sponsorlabel'>SPONSORED / REFERRAL</div><h2>Ready to explore a brokerage?</h2><p>AI Stocks Made Simple keeps sponsorships separate from research. A sponsor cannot buy a higher ranking, model score, or simulator result.</p></div>",unsafe_allow_html=True)
    st.markdown("### Robinhood")
    st.link_button("Open my Robinhood referral",ROBINHOOD_REFERRAL_URL,use_container_width=True,type="primary")
    st.caption("Disclosure: I may receive a referral reward if you sign up or qualify using this link. This financial relationship does not affect any stock ranking, model score, market data, or simulator output shown in this app.")
    st.divider(); st.markdown("### Future optional Pro features")
    st.write("• Saved payday simulations and portfolios")
    st.write("• Model-change and price alerts")
    st.write("• Historical rankings and deeper comparison tools")
    st.write("• Additional clearly labeled sponsors that never influence rankings")

st.divider(); st.markdown("<div class='disclaimer'>Educational research only. The app does not know your personal financial circumstances, does not place trades, and does not guarantee returns. Live prices may be delayed by the market-data provider. Stocks can lose value. Sponsored/referral placements are labeled and do not influence rankings.</div>",unsafe_allow_html=True)
