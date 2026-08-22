from __future__ import annotations
import calendar, json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf
from PIL import Image

APP_VERSION = "2.3.0-beta"
ROBINHOOD_REFERRAL_URL = "https://join.robinhood.com/steveng-15bac4"
NAMES={"MU":"Micron","TSM":"TSMC","CRDO":"Credo","ANET":"Arista Networks","PLTR":"Palantir","TER":"Teradyne","NVDA":"NVIDIA","DELL":"Dell","PATH":"UiPath","AMD":"AMD","GOOGL":"Alphabet","AMAT":"Applied Materials","DDOG":"Datadog","AVGO":"Broadcom","SNOW":"Snowflake","AMZN":"Amazon","MDB":"MongoDB","NET":"Cloudflare","ACMR":"ACM Research","VRT":"Vertiv","ASML":"ASML","SMCI":"Super Micro Computer","MSFT":"Microsoft","PANW":"Palo Alto Networks","ARM":"Arm","META":"Meta","CRWD":"CrowdStrike","MRVL":"Marvell","NOW":"ServiceNow","ORCL":"Oracle"}
DOMAINS={"MU":"micron.com","TSM":"tsmc.com","CRDO":"credosemi.com","ANET":"arista.com","PLTR":"palantir.com","TER":"teradyne.com","NVDA":"nvidia.com","DELL":"dell.com","PATH":"uipath.com","AMD":"amd.com","GOOGL":"google.com","AMAT":"appliedmaterials.com","DDOG":"datadoghq.com","AVGO":"broadcom.com","SNOW":"snowflake.com","AMZN":"amazon.com","MDB":"mongodb.com","NET":"cloudflare.com","ACMR":"acmrcsh.com","VRT":"vertiv.com","ASML":"asml.com","SMCI":"supermicro.com","MSFT":"microsoft.com","PANW":"paloaltonetworks.com","ARM":"arm.com","META":"meta.com","CRWD":"crowdstrike.com","MRVL":"marvell.com","NOW":"servicenow.com","ORCL":"oracle.com"}

st.set_page_config(page_title="AI Stocks Made Simple",page_icon="⚡",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
html{scroll-behavior:smooth}.stApp{background:#030812;color:#eef7ff}.block-container{max-width:1080px;padding-top:.6rem;padding-bottom:6rem}.stButton>button,.stLinkButton>a{border-radius:14px!important;min-height:46px;font-weight:800}.stMetric{background:linear-gradient(180deg,#091525,#050b14);border:1px solid #17365f;border-radius:15px;padding:10px}.hero-card{border:1px solid #234a78;border-radius:26px;padding:22px;background:radial-gradient(circle at 12% 35%,#ff7a1838,transparent 28%),radial-gradient(circle at 80% 22%,#2563eb55,transparent 32%),linear-gradient(135deg,#02050c,#071b38 52%,#16072e);box-shadow:0 0 34px #0ea5e92a}.eyebrow{font-size:.75rem;letter-spacing:.22em;color:#a8bad1;font-weight:900}.hero-title{font-size:clamp(2.5rem,7vw,5.2rem);font-weight:1000;line-height:.88;font-style:italic;margin:.3rem 0;background:linear-gradient(90deg,#22d3ee,#818cf8,#d946ef);-webkit-background-clip:text;color:transparent}.hero-sub{font-size:clamp(1.1rem,3.4vw,2rem);font-weight:950;font-style:italic}.cyan{color:#22d3ee}.pink{color:#e879f9}.orange{color:#fb923c}.fine{font-size:.78rem;color:#8fa5bf}.statusbar{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0}.status{background:linear-gradient(180deg,#081526,#040a12);border:1px solid #17365f;border-radius:15px;padding:12px}.status b{font-size:.7rem;color:#92a7c0;display:block}.panel{background:linear-gradient(180deg,#081322,#030812);border:1px solid #17365f;border-radius:21px;padding:16px;margin:12px 0}.planhero{background:radial-gradient(circle at 10% 15%,#ec489944,transparent 27%),linear-gradient(120deg,#24104d,#07345b,#481c08);border:1px solid #a855f7;border-radius:22px;padding:18px;box-shadow:0 0 24px #7c3aed33}.selected{background:#052d23;border:1px solid #22c55e;border-radius:14px;padding:11px;margin:8px 0}.stock-shell{background:#07111f;border:1px solid #17365f;border-radius:16px;padding:9px;text-align:center;min-height:130px}.stock-shell img{width:46px;height:46px;border-radius:10px;background:white;padding:4px}.stock-shell strong{display:block}.score{color:#4ade80;font-weight:900}.risk{color:#facc15;font-size:.76rem}.quick-title{font-weight:900;color:#22d3ee;margin-top:.5rem}.result{background:linear-gradient(135deg,#052e16,#07345b);border:1px solid #22c55e;border-radius:20px;padding:16px}.learn-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.learn-card{border-radius:17px;padding:15px;min-height:135px;background:#07111f;border:1px solid #17365f}.bottom-nav{position:fixed;z-index:999;bottom:8px;left:50%;transform:translateX(-50%);width:min(94%,760px);display:flex;justify-content:space-around;background:#07111ff5;border:1px solid #17365f;border-radius:18px;padding:10px;box-shadow:0 0 30px #000}.bottom-nav a{color:#9fb6d3;text-decoration:none;font-size:.72rem;text-align:center;font-weight:800}.bottom-nav a span{display:block;font-size:1.15rem;color:#22d3ee}.mascot-card img{border-radius:22px;border:1px solid #234a78;box-shadow:0 0 25px #2563eb33}.python-chip{border:1px solid #22d3ee;border-radius:14px;padding:8px 10px;text-align:center;background:#061727;font-weight:900;margin-top:8px}@media(max-width:760px){.statusbar,.learn-grid{grid-template-columns:repeat(2,1fr)}.block-container{padding-left:.65rem;padding-right:.65rem}.stock-shell{min-height:115px}.hero-title{font-size:3rem}.hero-sub{font-size:1.15rem}}</style>""",unsafe_allow_html=True)

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
            except:pass
    except:pass
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
if "selected_stock" not in st.session_state: st.session_state.selected_stock="NVDA" if any(r.get("ticker")=="NVDA" for r in top20) else top20[0]["ticker"]
if "live_prices" not in st.session_state: st.session_state.live_prices={}
if "deposit_amount" not in st.session_state: st.session_state.deposit_amount=10.0

# HERO — real UI, not a screenshot
left,right=st.columns([1.35,.65],vertical_alignment="center")
with left:
    st.markdown("""<div class='hero-card'><div class='eyebrow'>AI STOCKS MADE SIMPLE</div><div class='hero-title'>AI STOCKS<br>MADE SIMPLE</div><div class='hero-sub'><span class='cyan'>AI POWERED.</span><br><span class='pink'>DATA DRIVEN.</span><br>SMARTER RESEARCH.</div><div style='margin-top:13px;padding:10px;border:1px solid #1d4ed8;border-radius:12px;background:#07152d'><b>◆ LIVE AI STOCK RANKINGS</b><br><span class='fine'>START SMALL • BUILD A ROUTINE • SEE THE MATH</span></div></div>""",unsafe_allow_html=True)
with right:
    asset=Path("assets/hero_production.jpg")
    if asset.exists():
        try:
            img=Image.open(asset); w,h=img.size; crop=img.crop((int(w*.58),0,w,h))
            st.image(crop,use_container_width=True)
        except: st.image(str(asset),use_container_width=True)
    st.markdown("<div class='python-chip'>🐍👓 Python + Red Pop 🥤</div>",unsafe_allow_html=True)

avg_conf=sum(float(r.get("confidence",0) or 0) for r in top20)/len(top20)
st.markdown(f"<div class='statusbar'><div class='status'><b>MARKET DATA</b><strong class='cyan'>{'LIVE' if st.session_state.live_prices else 'SNAPSHOT'}</strong><br><span class='fine'>tap refresh for current prices</span></div><div class='status'><b>RANKING DATE</b><strong>{snapshot}</strong></div><div class='status'><b>MODEL</b><strong class='pink'>{APP_VERSION}</strong></div><div class='status'><b>CONFIDENCE</b><strong class='orange'>{avg_conf:.0f}%</strong></div></div>",unsafe_allow_html=True)

st.markdown("<div id='top-ai-stocks'></div>",unsafe_allow_html=True)
head1,head2=st.columns([2.2,1])
with head1:
    st.markdown("## 🔥 TOP 20 AI STOCKS")
    st.caption("Tap SELECT on any company. That stock immediately becomes the active stock in Build Your Plan.")
with head2:
    if st.button("🔄 REFRESH LIVE PRICES",use_container_width=True):
        with st.spinner("Refreshing market prices…"):
            st.session_state.live_prices=fetch_live_prices(tuple(r["ticker"] for r in top20))
        st.rerun()

cols=st.columns(4)
for i,r in enumerate(top20):
    t=r["ticker"]; price=get_price(t,rows,st.session_state.live_prices); day=st.session_state.live_prices.get(t,{}).get("day")
    with cols[i%4]:
        daytxt=f"{day:+.2%} today" if day is not None else "snapshot price"
        st.markdown(f"<div class='stock-shell'><img src='{logo(t)}'><strong>#{r.get('rank')} {NAMES.get(t,t)}</strong><span class='fine'>{t}</span><div class='score'>Score {float(r.get('score',0)):.1f}</div><div><b>${price:,.2f}</b></div><div class='risk'>{daytxt} • {r.get('risk','—')} risk</div></div>",unsafe_allow_html=True)
        label="✓ SELECTED" if st.session_state.selected_stock==t else f"SELECT {t}"
        if st.button(label,key=f"pick_{t}",use_container_width=True,disabled=st.session_state.selected_stock==t):
            st.session_state.selected_stock=t; st.rerun()

st.markdown("<div id='build-plan'></div>",unsafe_allow_html=True)
selected=st.session_state.selected_stock; selected_price=get_price(selected,rows,st.session_state.live_prices)
st.markdown(f"<div class='planhero'><h2>💵 BUILD YOUR INVESTING PLAN</h2><p>Selected stock: <b>{NAMES.get(selected,selected)} ({selected})</b>. Choose your deposit amount, how often you want to invest, your start date, and how far you want to project it.</p></div>",unsafe_allow_html=True)
st.markdown(f"<div class='selected'><b>{NAMES.get(selected,selected)} ({selected})</b> • price used in illustration: <b>${selected_price:,.2f}</b> • <span class='fine'>{'refreshed live price' if selected in st.session_state.live_prices else 'latest saved market snapshot'}</span></div>",unsafe_allow_html=True)

st.markdown("<div class='quick-title'>QUICK AMOUNT</div>",unsafe_allow_html=True)
qcols=st.columns(5)
for idx,val in enumerate([5,10,25,50,100]):
    with qcols[idx]:
        if st.button(f"${val}",key=f"amt_{val}",use_container_width=True): st.session_state.deposit_amount=float(val); st.rerun()

with st.form("plan_form"):
    a,b=st.columns(2)
    amount=a.number_input("Deposit amount",min_value=1.0,max_value=100000.0,value=float(st.session_state.deposit_amount),step=5.0,format="$%.2f")
    freq=b.selectbox("How often?",["Every 2 weeks","Every Friday","Every payday (2 weeks)","Every month","Custom number of days"])
    custom=14
    if freq=="Custom number of days": custom=st.number_input("Every how many days?",1,365,14)
    d1,d2=st.columns(2)
    start=d1.date_input("Start date",value=next_friday(date.today()))
    end=d2.date_input("End date",value=date(2026,12,31),min_value=date.today())
    rotation=st.checkbox("Advanced: rotate this deposit through 3 stocks")
    stock_b=stock_c=None
    if rotation:
        choices=[r["ticker"] for r in top20]; r1,r2=st.columns(2)
        stock_b=r1.selectbox("Stock B",choices,index=1 if len(choices)>1 else 0,format_func=lambda x:f"{NAMES.get(x,x)} ({x})")
        stock_c=r2.selectbox("Stock C",choices,index=2 if len(choices)>2 else 0,format_func=lambda x:f"{NAMES.get(x,x)} ({x})")
    run=st.form_submit_button("⚡ SHOW ME HOW THIS ADDS UP",type="primary",use_container_width=True)

if run:
    st.session_state.deposit_amount=amount
    if end<start: st.error("End date must be after the start date.")
    elif selected_price<=0: st.error("No usable price is available for this stock. Refresh live prices and try again.")
    else:
        dates=schedule_dates(start,end,freq,custom); picks=[selected,stock_b,stock_c] if rotation else [selected]; picks=[p for p in picks if p]
        shares={p:0.0 for p in set(picks)}; invested={p:0.0 for p in set(picks)}; ledger=[]
        for i,d in enumerate(dates):
            t=picks[i%len(picks)]; p=get_price(t,rows,st.session_state.live_prices)
            if p<=0: continue
            qty=amount/p; shares[t]+=qty; invested[t]+=amount; ledger.append({"Deposit date":d,"Stock":t,"Deposit":amount,"Price used":p,"Shares added":qty})
        total=sum(invested.values()); value=sum(shares[t]*get_price(t,rows,st.session_state.live_prices) for t in shares)
        st.markdown(f"<div class='result'><h2>📈 YOUR PLAN THROUGH {end:%b %d, %Y}</h2><p>{len(ledger)} scheduled deposits using the displayed stock price for this illustration.</p></div>",unsafe_allow_html=True)
        k1,k2,k3,k4=st.columns(4); k1.metric("Total deposits",f"${total:,.2f}"); k2.metric("Deposits",len(ledger)); k3.metric("Shares",f"{sum(shares.values()):.4f}"); k4.metric("Value at shown price",f"${value:,.2f}")
        summary=pd.DataFrame([{"Stock":f"{NAMES.get(t,t)} ({t})","Deposited":invested[t],"Shares":shares[t],"Price used":get_price(t,rows,st.session_state.live_prices),"Value at shown price":shares[t]*get_price(t,rows,st.session_state.live_prices)} for t in shares])
        st.dataframe(summary,use_container_width=True,hide_index=True)
        if ledger:
            ldf=pd.DataFrame(ledger); st.area_chart(ldf.groupby("Deposit date")["Deposit"].sum().cumsum(),height=245)
            if not rotation: st.success(f"${amount:,.2f} into {NAMES.get(selected,selected)} on this schedule contributes ${total:,.2f} and accumulates about {shares[selected]:.4f} {selected} shares by {end:%b %d, %Y}, using today's displayed ${selected_price:,.2f} price for the math.")
            with st.expander("See every scheduled deposit"): st.dataframe(ldf,use_container_width=True,hide_index=True)
        st.info("Future prices will change. This is an educational accumulation illustration, not a prediction or guarantee of future account value.")

st.markdown("<div id='learn'></div>",unsafe_allow_html=True)
st.markdown("## 🎓 START SMALL. LEARN AS YOU GO.")
st.markdown("""<div class='learn-grid'><div class='learn-card'><h3 class='pink'>🚀 START SMALL</h3><p>$5, $10 or $25 at a time. Fractional shares make small recurring investments possible at many brokers.</p></div><div class='learn-card'><h3 class='cyan'>🧠 LEARN</h3><p>Plain-English AI and investing concepts without Wall Street jargon.</p></div><div class='learn-card'><h3 style='color:#4ade80'>🎯 BUILD A ROUTINE</h3><p>Weekly, payday, bi-weekly, monthly or a custom schedule.</p></div><div class='learn-card'><h3 class='orange'>🛡️ RISK FIRST</h3><p>Stocks can fall. Rankings are research signals, not guarantees.</p></div></div>""",unsafe_allow_html=True)

st.markdown("<div id='model'></div>",unsafe_allow_html=True)
with st.expander("⚙️ How the 100-point model works"):
    for n,p in [("Revenue Growth",15),("Earnings / Free Cash Flow",15),("Industry Growth",15),("Balance Sheet",10),("Valuation",10),("Competitive Advantage",10),("Momentum",10),("Insider / Institutional",5),("Catalysts",5),("Inflation Resilience",5)]: st.progress(p/15,text=f"{n} — {p} points")

st.divider(); st.markdown("### 💚 Optional Robinhood referral")
st.caption("Sponsored/referral relationship. It never changes rankings, scores, or simulator math.")
st.link_button("Open Robinhood referral",ROBINHOOD_REFERRAL_URL,use_container_width=True)
st.caption("Disclosure: I may receive a referral reward if you sign up or qualify through this link. Educational research only. No trades are placed.")

st.markdown("""<div class='bottom-nav'><a href='#top-ai-stocks'><span>⌂</span>TOP 20</a><a href='#build-plan'><span>◔</span>BUILD PLAN</a><a href='#learn'><span>♟</span>LEARN</a><a href='#model'><span>⚙</span>MODEL</a></div>""",unsafe_allow_html=True)
