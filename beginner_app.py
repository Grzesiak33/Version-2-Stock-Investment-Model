from __future__ import annotations
import calendar
import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf

APP_VERSION = "2.2.6-beta"
ROBINHOOD_REFERRAL_URL = "https://join.robinhood.com/steveng-15bac4"
NAMES = {
    "MU":"Micron","TSM":"TSMC","CRDO":"Credo","ANET":"Arista Networks","PLTR":"Palantir",
    "TER":"Teradyne","NVDA":"NVIDIA","DELL":"Dell","PATH":"UiPath","AMD":"AMD",
    "GOOGL":"Alphabet","AMAT":"Applied Materials","DDOG":"Datadog","AVGO":"Broadcom",
    "SNOW":"Snowflake","AMZN":"Amazon","MDB":"MongoDB","NET":"Cloudflare","ACMR":"ACM Research",
    "VRT":"Vertiv","ASML":"ASML","SMCI":"Super Micro Computer","MSFT":"Microsoft","PANW":"Palo Alto Networks",
    "ARM":"Arm","META":"Meta","CRWD":"CrowdStrike","MRVL":"Marvell","NOW":"ServiceNow","ORCL":"Oracle"
}
DOMAINS = {
    "MU":"micron.com","TSM":"tsmc.com","CRDO":"credosemi.com","ANET":"arista.com","PLTR":"palantir.com",
    "TER":"teradyne.com","NVDA":"nvidia.com","DELL":"dell.com","PATH":"uipath.com","AMD":"amd.com",
    "GOOGL":"google.com","AMAT":"appliedmaterials.com","DDOG":"datadoghq.com","AVGO":"broadcom.com",
    "SNOW":"snowflake.com","AMZN":"amazon.com","MDB":"mongodb.com","NET":"cloudflare.com","ACMR":"acmrcsh.com",
    "VRT":"vertiv.com","ASML":"asml.com","SMCI":"supermicro.com","MSFT":"microsoft.com","PANW":"paloaltonetworks.com",
    "ARM":"arm.com","META":"meta.com","CRWD":"crowdstrike.com","MRVL":"marvell.com","NOW":"servicenow.com","ORCL":"oracle.com"
}

st.set_page_config(page_title="AI Stocks Made Simple", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.stApp{background:#030812;color:#eef7ff}.block-container{max-width:1080px;padding-top:.8rem;padding-bottom:4rem}
.hero-frame img{border-radius:24px;border:1px solid #17365f;box-shadow:0 0 30px #0ea5e933}
.glow{background:linear-gradient(135deg,#071426,#091731);border:1px solid #17365f;border-radius:18px;padding:14px}
.plan{background:radial-gradient(circle at 12% 10%,#ec489933,transparent 28%),linear-gradient(125deg,#16113c,#07345b,#381309);border:1px solid #9333ea;border-radius:22px;padding:18px;margin-top:14px}
.selected{border:1px solid #22c55e;background:#062e20;border-radius:14px;padding:12px}.fine{font-size:.8rem;color:#8ba3c1}
.stButton>button,.stLinkButton>a{min-height:46px;border-radius:13px!important;font-weight:800}.stMetric{background:#07111f;border:1px solid #17365f;padding:10px;border-radius:13px}
.stock-card{border:1px solid #17365f;background:#07111f;border-radius:15px;padding:9px;text-align:center;min-height:125px}.stock-card img{width:44px;height:44px;background:white;border-radius:9px;padding:4px}.score{color:#4ade80;font-weight:900}.risk{color:#fbbf24;font-size:.78rem}.sponsor{background:linear-gradient(120deg,#052e16,#07152e);border:1px solid #22c55e;border-radius:18px;padding:16px}
@media(max-width:760px){.block-container{padding-left:.65rem;padding-right:.65rem}.stock-card{min-height:110px}}
</style>
""", unsafe_allow_html=True)

# Render immediately. No network call is allowed to block the first screen.
st.markdown("<div class='hero-frame'>", unsafe_allow_html=True)
st.image("assets/hero_production.jpg", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


def latest_snapshot():
    p = Path("data/historical/rankings")
    files = sorted(p.glob("*.json")) if p.exists() else []
    if not files:
        return [], "none"
    try:
        return json.loads(files[-1].read_text(encoding="utf-8")), files[-1].stem
    except Exception:
        return [], "unavailable"

@st.cache_data(ttl=300, show_spinner=False)
def fetch_live_prices(tickers):
    out = {}
    try:
        raw = yf.download(list(tickers), period="5d", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=False, timeout=6)
        for t in tickers:
            try:
                close = raw[t]["Close"].dropna()
                if len(close):
                    p = float(close.iloc[-1]); prev = float(close.iloc[-2]) if len(close) > 1 else p
                    out[t] = {"price":p, "day":(p/prev-1 if prev else 0.0)}
            except Exception:
                pass
    except Exception:
        pass
    return out


def logo(t):
    return f"https://www.google.com/s2/favicons?domain={DOMAINS.get(t,'example.com')}&sz=64"

def next_friday(d):
    return d + timedelta(days=(4-d.weekday()) % 7)

def schedule_dates(start, end, freq, custom_days=14):
    dates=[]; d=start
    if freq == "Every Friday": d = next_friday(start)
    while d <= end:
        dates.append(d)
        if freq in ("Every 2 weeks", "Every payday (2 weeks)"): d += timedelta(days=14)
        elif freq == "Every Friday": d += timedelta(days=7)
        elif freq == "Every month":
            y,m = d.year, d.month+1
            if m == 13: y,m = y+1,1
            d = date(y,m,min(d.day,calendar.monthrange(y,m)[1]))
        else: d += timedelta(days=max(1,int(custom_days)))
    return dates

rows, snapshot_date = latest_snapshot()
rows = sorted(rows, key=lambda r: r.get("rank",999))
top20 = rows[:20]
if not top20:
    st.error("The ranking snapshot could not be loaded.")
    st.stop()

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "NVDA" if any(r.get("ticker")=="NVDA" for r in top20) else top20[0]["ticker"]
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}

h1,h2,h3,h4 = st.columns(4)
h1.metric("Model version", APP_VERSION)
h2.metric("Ranking snapshot", snapshot_date)
h3.metric("AI stocks", len(top20))
h4.metric("Selected", st.session_state.selected_stock)

c1,c2 = st.columns([2.2,1])
with c1:
    st.markdown("## 🔥 Top 20 AI stocks")
    st.caption("Tap any company below. That stock becomes the active stock in the simulator immediately.")
with c2:
    if st.button("🔄 Refresh live prices", use_container_width=True):
        with st.spinner("Refreshing prices…"):
            st.session_state.live_prices = fetch_live_prices(tuple(r["ticker"] for r in top20))
        st.rerun()

cols = st.columns(4)
for i, r in enumerate(top20):
    t = r["ticker"]; live = st.session_state.live_prices.get(t, {})
    price = live.get("price", r.get("price",0) or 0); day = live.get("day")
    with cols[i % 4]:
        st.markdown(f"<div class='stock-card'><img src='{logo(t)}'><div><b>#{r.get('rank')} {NAMES.get(t,t)}</b></div><div class='fine'>{t}</div><div class='score'>Score {float(r.get('score',0)):.1f}</div><div>${price:,.2f}</div><div class='risk'>{r.get('risk','—')} risk</div></div>", unsafe_allow_html=True)
        label = "✓ Selected" if st.session_state.selected_stock == t else f"Select {t}"
        if st.button(label, key=f"stock_{t}", use_container_width=True, disabled=(st.session_state.selected_stock==t)):
            st.session_state.selected_stock = t
            st.rerun()

selected = st.session_state.selected_stock
selected_row = next((r for r in rows if r.get("ticker")==selected), top20[0])
selected_live = st.session_state.live_prices.get(selected, {})
selected_price = float(selected_live.get("price", selected_row.get("price",0) or 0))
price_source = "refreshed live price" if selected in st.session_state.live_prices else f"latest model snapshot ({snapshot_date})"

st.markdown("<div class='plan'><h2>💵 Build your investing plan</h2><p>Pick a stock above, enter the amount you want to deposit, choose how often, and choose the dates. The app shows how that routine accumulates using the selected stock's current displayed price as the illustration.</p></div>", unsafe_allow_html=True)
st.markdown(f"<div class='selected'><b>Selected:</b> {NAMES.get(selected,selected)} ({selected}) &nbsp; • &nbsp; <b>Price used:</b> ${selected_price:,.2f} &nbsp; • &nbsp; <span class='fine'>{price_source}</span></div>", unsafe_allow_html=True)

with st.form("investment_plan"):
    a,b = st.columns(2)
    amount = a.number_input("Investment amount per deposit", min_value=1.0, max_value=100000.0, value=10.0, step=5.0, format="$%.2f")
    freq = b.selectbox("Frequency", ["Every 2 weeks", "Every Friday", "Every payday (2 weeks)", "Every month", "Custom number of days"])
    custom_days = 14
    if freq == "Custom number of days":
        custom_days = st.number_input("Deposit every how many days?", min_value=1, max_value=365, value=14)
    d1,d2 = st.columns(2)
    start_date = d1.date_input("Start date", value=next_friday(date.today()))
    end_date = d2.date_input("End date", value=date(2026,12,31), min_value=date.today())
    rotation = st.checkbox("Advanced: rotate this deposit across 3 stocks")
    stock_b = stock_c = None
    if rotation:
        choices = [r["ticker"] for r in top20]
        r1,r2 = st.columns(2)
        stock_b = r1.selectbox("Stock B", choices, index=1 if len(choices)>1 else 0, format_func=lambda x:f"{NAMES.get(x,x)} ({x})")
        stock_c = r2.selectbox("Stock C", choices, index=2 if len(choices)>2 else 0, format_func=lambda x:f"{NAMES.get(x,x)} ({x})")
    run = st.form_submit_button("🚀 SHOW ME HOW THIS ADDS UP", type="primary", use_container_width=True)

if run:
    if end_date < start_date:
        st.error("End date must be after the start date.")
    elif selected_price <= 0:
        st.error("No usable price is available for the selected stock. Tap Refresh live prices and try again.")
    else:
        dates = schedule_dates(start_date, end_date, freq, custom_days)
        picks = [selected, stock_b, stock_c] if rotation else [selected]
        picks = [p for p in picks if p]
        shares={p:0.0 for p in set(picks)}; invested={p:0.0 for p in set(picks)}; ledger=[]
        for i,d in enumerate(dates):
            t = picks[i % len(picks)]
            row = next((x for x in rows if x.get("ticker")==t), {})
            p = float(st.session_state.live_prices.get(t,{}).get("price", row.get("price",0) or 0))
            if p <= 0: continue
            qty = amount / p
            shares[t] += qty; invested[t] += amount
            ledger.append({"Deposit date":d,"Stock":t,"Deposit":amount,"Price used":p,"Shares added":qty})
        total = sum(invested.values())
        value = sum(shares[t] * float(st.session_state.live_prices.get(t,{}).get("price", next((x for x in rows if x.get("ticker")==t),{}).get("price",0) or 0)) for t in shares)
        st.markdown("## 📈 Your simulation results")
        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Total contributed", f"${total:,.2f}")
        k2.metric("# of deposits", len(ledger))
        k3.metric("Shares accumulated", f"{sum(shares.values()):.4f}")
        k4.metric("Value at displayed prices", f"${value:,.2f}")
        summary = pd.DataFrame([{
            "Stock":f"{NAMES.get(t,t)} ({t})","Deposited":invested[t],"Shares accumulated":shares[t],
            "Displayed price":float(st.session_state.live_prices.get(t,{}).get("price", next((x for x in rows if x.get("ticker")==t),{}).get("price",0) or 0)),
            "Value at displayed price":shares[t]*float(st.session_state.live_prices.get(t,{}).get("price", next((x for x in rows if x.get("ticker")==t),{}).get("price",0) or 0))
        } for t in shares])
        st.dataframe(summary, use_container_width=True, hide_index=True)
        if ledger:
            ldf = pd.DataFrame(ledger)
            cumulative = ldf.groupby("Deposit date")["Deposit"].sum().cumsum()
            st.area_chart(cumulative, height=250)
            if not rotation:
                st.success(f"{amount:,.2f} deposited into {NAMES.get(selected,selected)} on this schedule through {end_date:%b %d, %Y} contributes ${total:,.2f} and accumulates about {shares[selected]:.4f} {selected} shares using the displayed ${selected_price:,.2f} price for the illustration.")
            with st.expander("See every scheduled deposit"):
                st.dataframe(ldf, use_container_width=True, hide_index=True)
        st.info("Future stock prices will change. This simulator intentionally holds each stock at its displayed price so beginners can see the deposit/share math clearly; it is not a promise of future account value.")

st.divider()
st.markdown("<div class='sponsor'><b>SPONSORED / REFERRAL</b><h3>Robinhood</h3><p>Optional brokerage referral. Sponsorship never changes model rankings or simulator results.</p></div>", unsafe_allow_html=True)
st.link_button("Open Robinhood referral", ROBINHOOD_REFERRAL_URL, use_container_width=True)
st.caption("Disclosure: I may receive a referral reward if you sign up or qualify through this link. Educational research only; stocks can lose value and this app does not place trades.")
