from __future__ import annotations
import calendar, json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf

APP_VERSION = "3.0.0"
ROBINHOOD_REFERRAL_URL = "https://join.robinhood.com/steveng-15bac4"
NAMES={"MU":"Micron","TSM":"TSMC","CRDO":"Credo","ANET":"Arista Networks","PLTR":"Palantir","TER":"Teradyne","NVDA":"NVIDIA","DELL":"Dell","PATH":"UiPath","AMD":"AMD","GOOGL":"Alphabet","AMAT":"Applied Materials","DDOG":"Datadog","AVGO":"Broadcom","SNOW":"Snowflake","AMZN":"Amazon","MDB":"MongoDB","NET":"Cloudflare","ACMR":"ACM Research","VRT":"Vertiv","ASML":"ASML","SMCI":"Super Micro Computer","MSFT":"Microsoft","PANW":"Palo Alto Networks","ARM":"Arm","META":"Meta","CRWD":"CrowdStrike","MRVL":"Marvell","NOW":"ServiceNow","ORCL":"Oracle"}
DOMAINS={"MU":"micron.com","TSM":"tsmc.com","CRDO":"credosemi.com","ANET":"arista.com","PLTR":"palantir.com","TER":"teradyne.com","NVDA":"nvidia.com","DELL":"dell.com","PATH":"uipath.com","AMD":"amd.com","GOOGL":"google.com","AMAT":"appliedmaterials.com","DDOG":"datadoghq.com","AVGO":"broadcom.com","SNOW":"snowflake.com","AMZN":"amazon.com","MDB":"mongodb.com","NET":"cloudflare.com","ACMR":"acmrcsh.com","VRT":"vertiv.com","ASML":"asml.com","SMCI":"supermicro.com","MSFT":"microsoft.com","PANW":"paloaltonetworks.com","ARM":"arm.com","META":"meta.com","CRWD":"crowdstrike.com","MRVL":"marvell.com","NOW":"servicenow.com","ORCL":"oracle.com"}

st.set_page_config(page_title="AI Stocks Made Simple",page_icon="⚡",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
html{scroll-behavior:smooth}.stApp{background:#020711;color:#f4f8ff}.block-container{max-width:1040px;padding-top:.55rem;padding-bottom:6.5rem}.stButton>button,.stLinkButton>a{border-radius:14px!important;min-height:48px;font-weight:900}.stMetric{background:#07111f;border:1px solid #17365f;border-radius:15px;padding:10px}.hero{display:grid;grid-template-columns:1.45fr .55fr;gap:16px;align-items:center;border:1px solid #234a78;border-radius:28px;padding:23px;background:radial-gradient(circle at 10% 35%,#ff7a183d,transparent 28%),radial-gradient(circle at 80% 22%,#2563eb55,transparent 34%),linear-gradient(135deg,#02050c,#071b38 52%,#17072e);box-shadow:0 0 34px #0ea5e92d}.eyebrow{font-size:.75rem;letter-spacing:.22em;color:#a8bad1;font-weight:900}.hero-title{font-size:clamp(2.6rem,7vw,5.2rem);font-weight:1000;line-height:.87;font-style:italic;margin:.32rem 0;background:linear-gradient(90deg,#22d3ee,#818cf8,#e879f9);-webkit-background-clip:text;color:transparent}.hero-sub{font-size:clamp(1.1rem,3.2vw,1.9rem);font-weight:950;font-style:italic}.cyan{color:#22d3ee}.pink{color:#e879f9}.orange{color:#fb923c}.fine{font-size:.78rem;color:#92a8c1}.avatar{min-height:245px;border:1px solid #315b8f;border-radius:24px;background:linear-gradient(180deg,#0a1d36,#07111f);display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 0 24px #2563eb2e}.head{width:94px;height:94px;border-radius:50%;background:#d5a17f;position:relative;box-shadow:inset 0 -14px 0 #7b4e3a}.beard{width:88px;height:42px;border-radius:0 0 42px 42px;background:#4a3027;position:absolute;left:3px;top:62px}.shirt{width:135px;height:92px;border-radius:28px 28px 14px 14px;background:#1565c0;margin-top:10px;position:relative}.shirt:after{content:'BCT';position:absolute;right:13px;top:18px;color:white;font-size:.7rem;font-weight:900}.tattoo{font-size:1.6rem;margin-top:-5px}.guide{font-weight:900;color:#dcecff;margin-top:8px}.python{margin-top:7px;border:1px solid #22d3ee;background:#061727;border-radius:13px;padding:8px 11px;font-weight:900}.statusbar{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:12px 0}.status{background:linear-gradient(180deg,#081526,#040a12);border:1px solid #17365f;border-radius:15px;padding:11px}.status b{font-size:.67rem;color:#92a7c0;display:block}.plan{background:radial-gradient(circle at 10% 15%,#ec489944,transparent 27%),linear-gradient(120deg,#24104d,#07345b,#481c08);border:1px solid #a855f7;border-radius:24px;padding:18px;margin:12px 0;box-shadow:0 0 25px #7c3aed30}.selected{background:#052d23;border:1px solid #22c55e;border-radius:14px;padding:12px;margin:10px 0}.quick-title{font-size:.78rem;color:#22d3ee;font-weight:900;margin-top:5px}.stock-card{background:#07111f;border:1px solid #17365f;border-radius:16px;padding:10px;text-align:center;min-height:128px}.stock-card img{width:45px;height:45px;border-radius:9px;background:white;padding:4px}.stock-card strong{display:block}.score{color:#4ade80;font-weight:900}.risk{color:#facc15;font-size:.74rem}.result{background:linear-gradient(135deg,#052e16,#07345b);border:1px solid #22c55e;border-radius:20px;padding:16px;margin-top:12px}.learn-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.learn{border-radius:17px;padding:14px;min-height:130px;background:#07111f;border:1px solid #17365f}.bottom-nav{position:fixed;z-index:999;bottom:8px;left:50%;transform:translateX(-50%);width:min(94%,760px);display:flex;justify-content:space-around;background:#07111ff4;border:1px solid #17365f;border-radius:18px;padding:10px;box-shadow:0 0 30px #000}.bottom-nav a{color:#9fb6d3;text-decoration:none;font-size:.72rem;text-align:center;font-weight:900}.bottom-nav a span{display:block;font-size:1.15rem;color:#22d3ee}@media(max-width:760px){.hero{grid-template-columns:1fr}.avatar{min-height:190px}.statusbar,.learn-grid{grid-template-columns:repeat(2,1fr)}.block-container{padding-left:.65rem;padding-right:.65rem}.hero-title{font-size:3.15rem}.hero-sub{font-size:1.18rem}.stock-card{min-height:115px}}</style>""",unsafe_allow_html=True)

def latest_snapshot():
    p=Path("data/historical/rankings"); files=sorted(p.glob("*.json")) if p.exists() else []
    if not files:return [],"none"
    try:return json.loads(files[-1].read_text(encoding="utf-8")),files[-1].stem
    except:return [],"unavailable"

@st.cache_data(ttl=300,show_spinner=False)
def fetch_live_prices(tickers):
    out={}
    try:
        raw=yf.download(list(tickers),period="5d",interval="1d",group_by="ticker",auto_adjust=False,progress=False,threads=False,timeout=6)
        for t in tickers:
            try:
                close=raw[t]["Close"].dropna()
                if len(close):
                    p=float(close.iloc[-1]); prev=float(close.iloc[-2]) if len(close)>1 else p
                    out[t]={"price":p,"day":p/prev-1 if prev else 0.0}
            except Exception: pass
    except Exception: pass
    return out

def logo(t):return f"https://www.google.com/s2/favicons?domain={DOMAINS.get(t,'example.com')}&sz=64"
def next_friday(d):return d+timedelta(days=(4-d.weekday())%7)
def schedule_dates(start,end,freq,custom=14):
    d=next_friday(start) if freq=="Every Friday" else start; dates=[]
    while d<=end:
        dates.append(d)
        if freq=="Every Friday": d+=timedelta(days=7)
        elif freq in ("Every 2 weeks","Every payday (2 weeks)"): d+=timedelta(days=14)
        elif freq=="Every month":
            y,m=d.year,d.month+1
            if m==13:y,m=y+1,1
            d=date(y,m,min(d.day,calendar.monthrange(y,m)[1]))
        else:d+=timedelta(days=max(1,int(custom)))
    return dates

def get_price(t,rows,live):
    row=next((r for r in rows if r.get("ticker")==t),{})
    return float(live.get(t,{}).get("price",row.get("price",0) or 0))

rows,snapshot=latest_snapshot(); rows=sorted(rows,key=lambda r:r.get("rank",999)); top20=rows[:20]
if not top20: st.error("Ranking snapshot could not be loaded."); st.stop()
choices=[r["ticker"] for r in top20]
if "selected_stock" not in st.session_state: st.session_state.selected_stock="NVDA" if "NVDA" in choices else choices[0]
if "live_prices" not in st.session_state: st.session_state.live_prices={}
if "deposit_amount" not in st.session_state: st.session_state.deposit_amount=10.0

st.markdown("""<div class='hero'><div><div class='eyebrow'>AI STOCKS MADE SIMPLE • VERSION 3.0</div><div class='hero-title'>AI STOCKS<br>MADE SIMPLE</div><div class='hero-sub'><span class='cyan'>AI POWERED.</span><br><span class='pink'>DATA DRIVEN.</span><br>SMARTER RESEARCH.</div><div style='margin-top:13px;padding:10px;border:1px solid #1d4ed8;border-radius:12px;background:#07152d'><b>◆ LIVE AI STOCK RANKINGS</b><br><span class='fine'>START SMALL • BUILD A ROUTINE • SEE THE MATH</span></div></div><div class='avatar'><div class='head'><div class='beard'></div></div><div class='shirt'></div><div class='tattoo'>〰️ 〰️</div><div class='guide'>YOUR AI STOCK GUIDE</div><div class='python'>🐍👓 Python + Red Pop 🥤</div></div></div>""",unsafe_allow_html=True)
avg_conf=sum(float(r.get("confidence",0) or 0) for r in top20)/len(top20)
st.markdown(f"<div class='statusbar'><div class='status'><b>MARKET DATA</b><strong class='cyan'>{'LIVE' if st.session_state.live_prices else 'SNAPSHOT'}</strong></div><div class='status'><b>RANKING DATE</b><strong>{snapshot}</strong></div><div class='status'><b>MODEL</b><strong class='pink'>V{APP_VERSION}</strong></div><div class='status'><b>CONFIDENCE</b><strong class='orange'>{avg_conf:.0f}%</strong></div></div>",unsafe_allow_html=True)

# PRIMARY SIMULATOR — intentionally before the Top 20 grid for mobile usability.
st.markdown("<div id='build-plan'></div>",unsafe_allow_html=True)
st.markdown("<div class='plan'><h2>💵 BUILD YOUR INVESTING PLAN</h2><p>Choose a stock, enter your amount, set the schedule and dates, then run the simulation.</p></div>",unsafe_allow_html=True)
stock_index=choices.index(st.session_state.selected_stock) if st.session_state.selected_stock in choices else 0
selected=st.selectbox("1. Pick your AI stock",choices,index=stock_index,format_func=lambda x:f"{NAMES.get(x,x)} ({x})",key="main_stock_selector")
if selected!=st.session_state.selected_stock: st.session_state.selected_stock=selected
selected=st.session_state.selected_stock; selected_price=get_price(selected,rows,st.session_state.live_prices)
st.markdown(f"<div class='selected'><b>{NAMES.get(selected,selected)} ({selected})</b> • displayed price used: <b>${selected_price:,.2f}</b> • <span class='fine'>{'live refresh' if selected in st.session_state.live_prices else 'saved market snapshot'}</span></div>",unsafe_allow_html=True)

st.markdown("<div class='quick-title'>2. QUICK AMOUNT</div>",unsafe_allow_html=True)
qcols=st.columns(5)
for i,val in enumerate([5,10,25,50,100]):
    with qcols[i]:
        if st.button(f"${val}",key=f"quick_{val}",use_container_width=True): st.session_state.deposit_amount=float(val)
amount=st.number_input("Or type your own deposit amount",min_value=1.0,max_value=100000.0,value=float(st.session_state.deposit_amount),step=1.0,format="$%.2f",key="amount_input")
st.session_state.deposit_amount=float(amount)

f1,f2=st.columns(2)
freq=f1.selectbox("3. How often?",["Every 2 weeks","Every Friday","Every payday (2 weeks)","Every month","Custom number of days"],key="frequency")
custom=14
if freq=="Custom number of days": custom=f2.number_input("Every how many days?",1,365,14,key="custom_days")
else: f2.markdown("<div style='padding-top:2rem' class='fine'>You can change this anytime.</div>",unsafe_allow_html=True)
d1,d2=st.columns(2)
start=d1.date_input("4. Start date",value=next_friday(date.today()),key="start_date")
end=d2.date_input("5. End date",value=date(2026,12,31),min_value=date.today(),key="end_date")
rotation=st.toggle("Advanced: rotate this deposit through 3 stocks",key="rotation")
stock_b=stock_c=None
if rotation:
    r1,r2=st.columns(2)
    stock_b=r1.selectbox("Stock B",choices,index=min(1,len(choices)-1),format_func=lambda x:f"{NAMES.get(x,x)} ({x})",key="stock_b")
    stock_c=r2.selectbox("Stock C",choices,index=min(2,len(choices)-1),format_func=lambda x:f"{NAMES.get(x,x)} ({x})",key="stock_c")
run=st.button("⚡ RUN MY SIMULATION",type="primary",use_container_width=True,key="run_sim")

if run:
    if end<start: st.error("End date must be after the start date.")
    elif selected_price<=0: st.error("No usable price is available. Tap Refresh Live Prices below and try again.")
    else:
        dates=schedule_dates(start,end,freq,custom); picks=[selected,stock_b,stock_c] if rotation else [selected]; picks=[p for p in picks if p]
        shares={p:0.0 for p in set(picks)}; invested={p:0.0 for p in set(picks)}; ledger=[]
        for i,d in enumerate(dates):
            t=picks[i%len(picks)]; p=get_price(t,rows,st.session_state.live_prices)
            if p<=0: continue
            qty=float(amount)/p; shares[t]+=qty; invested[t]+=float(amount); ledger.append({"Deposit date":d,"Stock":t,"Deposit":float(amount),"Price used":p,"Shares added":qty})
        total=sum(invested.values()); value=sum(shares[t]*get_price(t,rows,st.session_state.live_prices) for t in shares)
        st.markdown(f"<div class='result'><h2>📈 YOUR PLAN THROUGH {end:%b %d, %Y}</h2><p>{len(ledger)} scheduled deposits based on your inputs.</p></div>",unsafe_allow_html=True)
        k1,k2,k3,k4=st.columns(4); k1.metric("Total deposits",f"${total:,.2f}"); k2.metric("Deposits",len(ledger)); k3.metric("Shares",f"{sum(shares.values()):.4f}"); k4.metric("Value at shown price",f"${value:,.2f}")
        summary=pd.DataFrame([{"Stock":f"{NAMES.get(t,t)} ({t})","Deposited":invested[t],"Shares":shares[t],"Price used":get_price(t,rows,st.session_state.live_prices),"Value at shown price":shares[t]*get_price(t,rows,st.session_state.live_prices)} for t in shares])
        st.dataframe(summary,use_container_width=True,hide_index=True)
        if ledger:
            ldf=pd.DataFrame(ledger); st.area_chart(ldf.groupby("Deposit date")["Deposit"].sum().cumsum(),height=245)
            if not rotation: st.success(f"${amount:,.2f} into {NAMES.get(selected,selected)} on this schedule contributes ${total:,.2f} and accumulates about {shares[selected]:.4f} {selected} shares by {end:%b %d, %Y}, using the displayed ${selected_price:,.2f} price for the illustration.")
            with st.expander("See every scheduled deposit"): st.dataframe(ldf,use_container_width=True,hide_index=True)
        st.info("Future stock prices will change. This educational simulation holds each stock at the displayed price so the deposit/share math is easy to understand. It is not a guarantee of future account value.")

st.markdown("<div id='top-ai-stocks'></div>",unsafe_allow_html=True)
head1,head2=st.columns([2.1,1])
with head1:
    st.markdown("## 🔥 TOP 20 AI STOCKS")
    st.caption("These cards are shortcuts. The dropdown above is always available if a card tap is awkward on mobile.")
with head2:
    if st.button("🔄 REFRESH LIVE PRICES",use_container_width=True,key="refresh_prices"):
        with st.spinner("Refreshing prices…"): st.session_state.live_prices=fetch_live_prices(tuple(choices))
        st.rerun()

cols=st.columns(4)
for i,r in enumerate(top20):
    t=r["ticker"]; price=get_price(t,rows,st.session_state.live_prices); day=st.session_state.live_prices.get(t,{}).get("day")
    with cols[i%4]:
        daytxt=f"{day:+.2%} today" if day is not None else "snapshot price"
        st.markdown(f"<div class='stock-card'><img src='{logo(t)}'><strong>#{r.get('rank')} {NAMES.get(t,t)}</strong><span class='fine'>{t}</span><div class='score'>Score {float(r.get('score',0)):.1f}</div><div><b>${price:,.2f}</b></div><div class='risk'>{daytxt} • {r.get('risk','—')} risk</div></div>",unsafe_allow_html=True)
        if st.button("✓ SELECTED" if selected==t else f"USE {t}",key=f"card_{t}",use_container_width=True,disabled=selected==t):
            st.session_state.selected_stock=t
            st.session_state.main_stock_selector=t
            st.rerun()

st.markdown("<div id='learn'></div>",unsafe_allow_html=True)
st.markdown("## 🎓 START SMALL. LEARN AS YOU GO.")
st.markdown("""<div class='learn-grid'><div class='learn'><h3 class='pink'>🚀 START SMALL</h3><p>$5, $10 or $25 can be enough to begin learning with fractional shares.</p></div><div class='learn'><h3 class='cyan'>🧠 LEARN</h3><p>Plain-English AI and investing concepts without Wall Street jargon.</p></div><div class='learn'><h3 style='color:#4ade80'>🎯 BUILD A ROUTINE</h3><p>Weekly, payday, bi-weekly, monthly or custom schedules.</p></div><div class='learn'><h3 class='orange'>🛡️ RISK FIRST</h3><p>Stocks can fall. Rankings are research signals, not guarantees.</p></div></div>""",unsafe_allow_html=True)

st.markdown("<div id='model'></div>",unsafe_allow_html=True)
with st.expander("⚙️ How the 100-point model works"):
    for n,p in [("Revenue Growth",15),("Earnings / Free Cash Flow",15),("Industry Growth",15),("Balance Sheet",10),("Valuation",10),("Competitive Advantage",10),("Momentum",10),("Insider / Institutional",5),("Catalysts",5),("Inflation Resilience",5)]: st.progress(p/15,text=f"{n} — {p} points")
st.divider(); st.markdown("### 💚 Optional Robinhood referral"); st.caption("Sponsored/referral relationship. It never changes rankings, scores, or simulator math."); st.link_button("Open Robinhood referral",ROBINHOOD_REFERRAL_URL,use_container_width=True); st.caption("Disclosure: I may receive a referral reward if you sign up or qualify through this link. Educational research only. No trades are placed.")
st.markdown("""<div class='bottom-nav'><a href='#build-plan'><span>◔</span>BUILD PLAN</a><a href='#top-ai-stocks'><span>⌂</span>TOP 20</a><a href='#learn'><span>♟</span>LEARN</a><a href='#model'><span>⚙</span>MODEL</a></div>""",unsafe_allow_html=True)
