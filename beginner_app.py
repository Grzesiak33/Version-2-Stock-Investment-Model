from __future__ import annotations
import calendar, json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf

APP_VERSION="3.0.1"
ROBINHOOD_REFERRAL_URL="https://join.robinhood.com/steveng-15bac4"
HERO_URL="https://raw.githubusercontent.com/Grzesiak33/Version-2-Stock-Investment-Model/main/assets/hero_production.jpg"
NAMES={"MU":"Micron","TSM":"TSMC","CRDO":"Credo","ANET":"Arista Networks","PLTR":"Palantir","TER":"Teradyne","NVDA":"NVIDIA","DELL":"Dell","PATH":"UiPath","AMD":"AMD","GOOGL":"Alphabet","AMAT":"Applied Materials","DDOG":"Datadog","AVGO":"Broadcom","SNOW":"Snowflake","AMZN":"Amazon","MDB":"MongoDB","NET":"Cloudflare","ACMR":"ACM Research","VRT":"Vertiv","ASML":"ASML","SMCI":"Super Micro Computer","MSFT":"Microsoft","PANW":"Palo Alto Networks","ARM":"Arm","META":"Meta","CRWD":"CrowdStrike","MRVL":"Marvell","NOW":"ServiceNow","ORCL":"Oracle"}
DOMAINS={"MU":"micron.com","TSM":"tsmc.com","CRDO":"credosemi.com","ANET":"arista.com","PLTR":"palantir.com","TER":"teradyne.com","NVDA":"nvidia.com","DELL":"dell.com","PATH":"uipath.com","AMD":"amd.com","GOOGL":"google.com","AMAT":"appliedmaterials.com","DDOG":"datadoghq.com","AVGO":"broadcom.com","SNOW":"snowflake.com","AMZN":"amazon.com","MDB":"mongodb.com","NET":"cloudflare.com","ACMR":"acmrcsh.com","VRT":"vertiv.com","ASML":"asml.com","SMCI":"supermicro.com","MSFT":"microsoft.com","PANW":"paloaltonetworks.com","ARM":"arm.com","META":"meta.com","CRWD":"crowdstrike.com","MRVL":"marvell.com","NOW":"servicenow.com","ORCL":"oracle.com"}

st.set_page_config(page_title="AI Stocks Made Simple",page_icon="⚡",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
html{scroll-behavior:smooth}.stApp{background:#020711;color:#eef7ff}.block-container{max-width:1120px;padding-top:.55rem;padding-bottom:6.5rem}.stButton>button,.stLinkButton>a{border-radius:14px!important;min-height:46px;font-weight:900}.stMetric{background:#07111f;border:1px solid #17365f;border-radius:15px;padding:10px}.glass{background:linear-gradient(180deg,#081322,#030812);border:1px solid #17365f;border-radius:20px;padding:15px}.hero{display:grid;grid-template-columns:.95fr 1.05fr;gap:18px;align-items:stretch;border:1px solid #244e80;border-radius:28px;padding:16px;background:radial-gradient(circle at 15% 35%,#ff7a1840,transparent 28%),radial-gradient(circle at 80% 20%,#2563eb55,transparent 33%),linear-gradient(135deg,#02050c,#071b38 52%,#18072e);box-shadow:0 0 34px #0ea5e92b}.hero-img{width:100%;height:360px;object-fit:cover;object-position:18% center;border-radius:22px;border:1px solid #315b8f;box-shadow:0 0 25px #2563eb44}.eyebrow{font-size:.75rem;letter-spacing:.2em;color:#9fb4ce;font-weight:900}.hero-title{font-size:clamp(2.7rem,6.6vw,5rem);font-weight:1000;line-height:.86;font-style:italic;margin:.35rem 0;background:linear-gradient(90deg,#22d3ee,#818cf8,#e879f9);-webkit-background-clip:text;color:transparent}.hero-sub{font-size:clamp(1.2rem,3vw,2rem);font-weight:950;font-style:italic}.cyan{color:#22d3ee}.pink{color:#e879f9}.green{color:#4ade80}.orange{color:#fb923c}.fine{font-size:.77rem;color:#91a7c0}.snake{margin-top:14px;padding:11px;border:1px solid #22d3ee;border-radius:14px;background:#061727;text-align:center;font-weight:900}.statusbar{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:12px 0}.status{background:linear-gradient(180deg,#081526,#040a12);border:1px solid #17365f;border-radius:15px;padding:12px}.status b{font-size:.68rem;color:#92a7c0;display:block}.section-title{font-size:1.45rem;font-weight:950;margin:.2rem 0}.plan{background:radial-gradient(circle at 10% 15%,#ec489944,transparent 27%),linear-gradient(120deg,#24104d,#07345b,#481c08);border:1px solid #a855f7;border-radius:22px;padding:17px;box-shadow:0 0 24px #7c3aed2d}.selected{background:#052d23;border:1px solid #22c55e;border-radius:14px;padding:11px;margin:9px 0}.stockrow{display:grid;grid-template-columns:2fr .75fr .8fr .75fr;gap:7px;align-items:center;padding:9px 4px;border-bottom:1px solid #15253b}.logo{width:34px;height:34px;border-radius:8px;background:white;padding:3px;vertical-align:middle;margin-right:7px}.stockname{font-weight:900}.score{display:inline-grid;place-items:center;width:44px;height:44px;border-radius:50%;border:3px solid #22c55e;color:#4ade80;font-weight:900}.quick-title{font-size:.77rem;font-weight:900;color:#22d3ee;margin-top:5px}.result-head{background:linear-gradient(135deg,#052e16,#07345b);border:1px solid #22c55e;border-radius:19px;padding:15px;margin-top:12px}.result-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:10px 0}.result-card{border-radius:16px;padding:13px;background:#07111f;border:1px solid #17365f}.result-card b{display:block;font-size:.69rem;color:#8fa5bf}.result-card strong{font-size:1.25rem}.upcoming{background:#07111f;border:1px solid #17365f;border-radius:17px;padding:13px}.learn-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.learn{border-radius:17px;padding:14px;min-height:125px;background:#07111f;border:1px solid #17365f}.referral{background:linear-gradient(120deg,#052e16,#08182c);border:1px solid #22c55e;border-radius:18px;padding:15px}.bottom-nav{position:fixed;z-index:999;bottom:8px;left:50%;transform:translateX(-50%);width:min(95%,800px);display:flex;justify-content:space-around;background:#07111ff5;border:1px solid #17365f;border-radius:18px;padding:10px;box-shadow:0 0 30px #000}.bottom-nav a{color:#9fb6d3;text-decoration:none;font-size:.68rem;text-align:center;font-weight:900}.bottom-nav a span{display:block;font-size:1.15rem;color:#22d3ee}@media(max-width:760px){.hero{grid-template-columns:1fr}.hero-img{height:300px}.statusbar,.learn-grid,.result-grid{grid-template-columns:repeat(2,1fr)}.stockrow{grid-template-columns:1.9fr .7fr .75fr}.hide-mobile{display:none}.block-container{padding-left:.62rem;padding-right:.62rem}.hero-title{font-size:3.1rem}.hero-sub{font-size:1.17rem}}</style>""",unsafe_allow_html=True)

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
            except Exception:pass
    except Exception:pass
    return out

def logo(t):return f"https://www.google.com/s2/favicons?domain={DOMAINS.get(t,'example.com')}&sz=64"
def next_friday(d):return d+timedelta(days=(4-d.weekday())%7)
def schedule_dates(start,end,freq,custom=14):
    d=next_friday(start) if freq=="Every Friday" else start; dates=[]
    while d<=end:
        dates.append(d)
        if freq=="Every Friday":d+=timedelta(days=7)
        elif freq in ("Every 2 weeks","Every payday (2 weeks)"):d+=timedelta(days=14)
        elif freq=="Every month":
            y,m=d.year,d.month+1
            if m==13:y,m=y+1,1
            d=date(y,m,min(d.day,calendar.monthrange(y,m)[1]))
        else:d+=timedelta(days=max(1,int(custom)))
    return dates

def get_price(t,rows,live):
    row=next((r for r in rows if r.get("ticker")==t),{})
    return float(live.get(t,{}).get("price",row.get("price",0) or 0))

def choose_stock(t):
    st.session_state.selected_stock=t
    st.session_state.stock_select=t

def choose_amount(v):
    st.session_state.amount_input=float(v)

rows,snapshot=latest_snapshot(); rows=sorted(rows,key=lambda r:r.get("rank",999)); top20=rows[:20]
if not top20:st.error("Ranking snapshot could not be loaded.");st.stop()
choices=[r["ticker"] for r in top20]
if "selected_stock" not in st.session_state:st.session_state.selected_stock="NVDA" if "NVDA" in choices else choices[0]
if "stock_select" not in st.session_state:st.session_state.stock_select=st.session_state.selected_stock
if "live_prices" not in st.session_state:st.session_state.live_prices={}
if "amount_input" not in st.session_state:st.session_state.amount_input=10.0

# HERO — actual project artwork, cropped to emphasize the illustrated character.
st.markdown(f"""<div id='home' class='hero'><img class='hero-img' src='{HERO_URL}'><div style='padding:10px 4px'><div class='eyebrow'>AI STOCKS MADE SIMPLE • VERSION {APP_VERSION}</div><div class='hero-title'>AI STOCKS<br>MADE SIMPLE</div><div class='hero-sub'><span class='cyan'>AI POWERED.</span><br><span class='pink'>DATA DRIVEN.</span><br>SMARTER INVESTING.</div><div style='margin-top:13px;padding:10px;border:1px solid #1d4ed8;border-radius:12px;background:#07152d'><b>◆ LIVE AI STOCK RANKINGS</b><br><span class='fine'>START SMALL • BUILD A ROUTINE • SEE THE MATH</span></div><div class='snake'>🐍👓 Python-powered guide &nbsp; • &nbsp; 🥤 Red Pop energy</div></div></div>""",unsafe_allow_html=True)
avg_conf=sum(float(r.get("confidence",0) or 0) for r in top20)/len(top20)
st.markdown(f"<div class='statusbar'><div class='status'><b>AI MODEL SIGNAL</b><strong class='green'>ACTIVE</strong><br><span class='fine'>Top-20 scoring engine</span></div><div class='status'><b>LAST UPDATED</b><strong>{snapshot}</strong></div><div class='status'><b>MODEL VERSION</b><strong class='cyan'>{APP_VERSION}</strong></div><div class='status'><b>DATA CONFIDENCE</b><strong class='orange'>{avg_conf:.0f}%</strong></div></div>",unsafe_allow_html=True)

# Main desktop layout follows the approved mockup: rankings on left, simulator on right.
st.markdown("<div id='simulate'></div>",unsafe_allow_html=True)
left,right=st.columns([1.13,.87],gap="large")
with left:
    st.markdown("<div class='section-title'>🔥 TOP 20 AI STOCKS TODAY</div><div class='fine'>Tap USE to load a company into the simulator.</div>",unsafe_allow_html=True)
    for r in top20:
        t=r["ticker"]; price=get_price(t,rows,st.session_state.live_prices); day=st.session_state.live_prices.get(t,{}).get("day")
        c1,c2=st.columns([4,1])
        with c1:
            trend=f"{day:+.2%}" if day is not None else "—"
            st.markdown(f"<div class='stockrow'><div><img class='logo' src='{logo(t)}'><span class='stockname'>#{r.get('rank')} {NAMES.get(t,t)}</span><div class='fine'>{t}</div></div><div><b>${price:,.2f}</b></div><div><span class='score'>{float(r.get('score',0)):.0f}</span></div><div class='hide-mobile'><span class='green'>{trend}</span><div class='fine'>{r.get('risk','—')} risk</div></div></div>",unsafe_allow_html=True)
        with c2:
            st.button("✓" if st.session_state.selected_stock==t else "USE",key=f"use_{t}",use_container_width=True,disabled=st.session_state.selected_stock==t,on_click=choose_stock,args=(t,))
with right:
    st.markdown("<div class='plan'><div class='section-title'>💵 BUILD YOUR PLAN</div><div class='fine'>See how small, consistent deposits can add up.</div></div>",unsafe_allow_html=True)
    selected=st.selectbox("1. Pick Your Stock",choices,key="stock_select",format_func=lambda x:f"{NAMES.get(x,x)} ({x})")
    st.session_state.selected_stock=selected
    selected_price=get_price(selected,rows,st.session_state.live_prices)
    st.markdown(f"<div class='selected'><b>{NAMES.get(selected,selected)} ({selected})</b><br>Displayed price: <b>${selected_price:,.2f}</b> <span class='fine'>({'live refresh' if selected in st.session_state.live_prices else 'saved market snapshot'})</span></div>",unsafe_allow_html=True)
    st.markdown("<div class='quick-title'>2. INVESTMENT AMOUNT</div>",unsafe_allow_html=True)
    q=st.columns(5)
    for i,v in enumerate([5,10,25,50,100]):
        q[i].button(f"${v}",key=f"q_{v}",use_container_width=True,on_click=choose_amount,args=(v,))
    amount=st.number_input("Custom amount",min_value=1.0,max_value=100000.0,step=1.0,key="amount_input",format="$%.2f")
    freq=st.selectbox("3. Frequency",["Every 2 weeks","Every Friday","Every payday (2 weeks)","Every month","Custom number of days"],key="frequency")
    custom=14
    if freq=="Custom number of days":custom=st.number_input("Every how many days?",1,365,14,key="custom_days")
    start=st.date_input("4. Start Date",value=next_friday(date.today()),key="start_date")
    end=st.date_input("5. End Date",value=date(2026,12,31),min_value=date.today(),key="end_date")
    rotation=st.toggle("Rotate 3 stocks",key="rotation")
    stock_b=stock_c=None
    if rotation:
        stock_b=st.selectbox("Stock B",choices,index=min(1,len(choices)-1),format_func=lambda x:f"{NAMES.get(x,x)} ({x})",key="stock_b")
        stock_c=st.selectbox("Stock C",choices,index=min(2,len(choices)-1),format_func=lambda x:f"{NAMES.get(x,x)} ({x})",key="stock_c")
    run=st.button("🚀 SHOW ME HOW THIS ADDS UP",type="primary",use_container_width=True,key="run_sim")
    if st.button("🔄 Refresh Live Prices",use_container_width=True,key="refresh_prices"):
        with st.spinner("Refreshing prices…"):st.session_state.live_prices=fetch_live_prices(tuple(choices))
        st.rerun()

if run:
    if end<start:st.error("End date must be after the start date.")
    elif selected_price<=0:st.error("No usable price is available. Refresh live prices and try again.")
    else:
        dates=schedule_dates(start,end,freq,custom); picks=[selected,stock_b,stock_c] if rotation else [selected]; picks=[p for p in picks if p]
        shares={p:0.0 for p in set(picks)}; invested={p:0.0 for p in set(picks)}; ledger=[]
        for i,d in enumerate(dates):
            t=picks[i%len(picks)]; p=get_price(t,rows,st.session_state.live_prices)
            if p<=0:continue
            qty=float(amount)/p; shares[t]+=qty; invested[t]+=float(amount); ledger.append({"Deposit date":d,"Stock":t,"Deposit":float(amount),"Price used":p,"Shares added":qty})
        total=sum(invested.values()); value=sum(shares[t]*get_price(t,rows,st.session_state.live_prices) for t in shares)
        st.markdown(f"<div class='result-head'><div class='section-title'>📈 YOUR SIMULATION RESULTS</div><div class='fine'>Based on the displayed price(s) • through {end:%b %d, %Y}</div></div>",unsafe_allow_html=True)
        st.markdown(f"<div class='result-grid'><div class='result-card'><b>TOTAL CONTRIBUTED</b><strong class='green'>${total:,.2f}</strong></div><div class='result-card'><b># OF DEPOSITS</b><strong class='pink'>{len(ledger)}</strong></div><div class='result-card'><b>SHARES ACCUMULATED</b><strong class='cyan'>{sum(shares.values()):.4f}</strong></div><div class='result-card'><b>VALUE AT SHOWN PRICE</b><strong class='orange'>${value:,.2f}</strong></div></div>",unsafe_allow_html=True)
        if ledger:
            ldf=pd.DataFrame(ledger)
            chart_col,list_col=st.columns([1.6,1])
            with chart_col:
                st.markdown("### Portfolio Growth (Estimated)")
                st.area_chart(ldf.groupby("Deposit date")["Deposit"].sum().cumsum(),height=270)
            with list_col:
                st.markdown(f"### Upcoming Deposits ({len(ledger)} total)")
                st.dataframe(ldf.head(5)[["Deposit date","Stock","Deposit","Shares added"]],use_container_width=True,hide_index=True)
                st.info("💡 Pro Tip: consistent small contributions can make the habit easier to maintain. Future prices will vary.")
            if not rotation:st.success(f"${amount:,.2f} into {NAMES.get(selected,selected)} on this schedule contributes ${total:,.2f} and accumulates about {shares[selected]:.4f} {selected} shares by {end:%b %d, %Y}, using the displayed ${selected_price:,.2f} price for the illustration.")
            with st.expander("See every scheduled deposit"):st.dataframe(ldf,use_container_width=True,hide_index=True)
        st.caption("Future stock prices will change. This is an educational accumulation illustration, not a prediction or guarantee of future account value.")

st.markdown("<div id='learn'></div>",unsafe_allow_html=True)
st.markdown("## 🎓 START SMALL. LEARN AS YOU GO.")
st.markdown("""<div class='learn-grid'><div class='learn'><h3 class='pink'>🚀 START SMALL</h3><p>$5, $10 or $25 can be enough to begin learning with fractional shares.</p></div><div class='learn'><h3 class='cyan'>🧠 LEARN</h3><p>Plain-English AI and investing concepts without Wall Street jargon.</p></div><div class='learn'><h3 class='green'>🎯 BUILD A ROUTINE</h3><p>Weekly, payday, bi-weekly, monthly or custom schedules.</p></div><div class='learn'><h3 class='orange'>🛡️ RISK FIRST</h3><p>Stocks can fall. Rankings are research signals, not guarantees.</p></div></div>""",unsafe_allow_html=True)

st.markdown("<div id='model'></div>",unsafe_allow_html=True)
with st.expander("⚙️ How the 100-point model works"):
    for n,p in [("Revenue Growth",15),("Earnings / Free Cash Flow",15),("Industry Growth",15),("Balance Sheet",10),("Valuation",10),("Competitive Advantage",10),("Momentum",10),("Insider / Institutional",5),("Catalysts",5),("Inflation Resilience",5)]:st.progress(p/15,text=f"{n} — {p} points")

st.markdown("<div class='referral'><b class='green'>Robinhood • Sponsored / Referral</b><h3>Start investing with Robinhood</h3><span class='fine'>I may receive a referral reward if you sign up using my link. This never changes rankings or simulator math.</span></div>",unsafe_allow_html=True)
st.link_button("Open Robinhood",ROBINHOOD_REFERRAL_URL,use_container_width=True)
st.caption("Educational research only. No trades are placed. Stocks can lose value.")
st.markdown("""<div class='bottom-nav'><a href='#home'><span>⌂</span>HOME</a><a href='#simulate'><span>☷</span>TOP 20</a><a href='#simulate'><span>🧮</span>SIMULATE</a><a href='#learn'><span>🎓</span>LEARN</a><a href='#model'><span>⚙</span>SETTINGS</a></div>""",unsafe_allow_html=True)
