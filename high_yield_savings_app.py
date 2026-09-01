from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_VERSION = "2.1.0"
TODAY = date(2026, 9, 1)
DEFAULT_BALANCE = 20.71
DEFAULT_DEPOSIT = 10.0
DEFAULT_NEXT_PAYCHECK = date(2026, 9, 11)


@dataclass(frozen=True)
class AccountConfig:
    start_date: date
    current_balance: float
    automatic_deposit: float
    next_paycheck_date: date
    paycheck_frequency_days: int
    high_yield_apy: float = 0.10
    high_yield_limit: float = 1000.0
    excess_apy: float = 0.001


def daily_rate_from_apy(apy: float) -> float:
    return (1.0 + apy) ** (1.0 / 365.0) - 1.0


def daily_interest(balance: float, cfg: AccountConfig) -> float:
    high = min(balance, cfg.high_yield_limit)
    excess = max(balance - cfg.high_yield_limit, 0.0)
    return high * daily_rate_from_apy(cfg.high_yield_apy) + excess * daily_rate_from_apy(cfg.excess_apy)


def project_savings(cfg: AccountConfig, deposit_amount: float, end_date: date) -> pd.DataFrame:
    d = cfg.start_date
    balance = cfg.current_balance
    next_deposit = cfg.next_paycheck_date
    rows = [{"date": d, "balance": balance, "deposit": 0.0, "interest": 0.0}]
    while d < end_date:
        d += timedelta(days=1)
        interest = daily_interest(balance, cfg)
        balance += interest
        dep = 0.0
        if d == next_deposit:
            dep = float(deposit_amount)
            balance += dep
            next_deposit += timedelta(days=cfg.paycheck_frequency_days)
        rows.append({"date": d, "balance": balance, "deposit": dep, "interest": interest})
    return pd.DataFrame(rows)


def first_goal_date(frame: pd.DataFrame, goal: float = 1000.0) -> date | None:
    hit = frame[frame["balance"] >= goal]
    return None if hit.empty else hit.iloc[0]["date"]


def deposit_scenarios(cfg: AccountConfig, amounts: list[float]) -> pd.DataFrame:
    rows = []
    for amount in amounts:
        frame = project_savings(cfg, amount, cfg.start_date + timedelta(days=365 * 10))
        hit = first_goal_date(frame)
        if hit:
            through = frame[frame["date"] <= hit]
            days = (hit - cfg.start_date).days
            rows.append({
                "Deposit / Paycheck": f"${amount:,.0f}",
                "Goal Date": hit.strftime("%b %d, %Y"),
                "Months": round(days / 30.4375, 1),
                "Interest": f"${through['interest'].sum():,.2f}",
                "amount": amount,
                "months_raw": days / 30.4375,
            })
    return pd.DataFrame(rows)


def project_two_bucket(cfg: AccountConfig, deposit_amount: float, next_apy: float, total_goal: float, sweep_overflow: bool, end_date: date) -> pd.DataFrame:
    d = cfg.start_date
    orsa = cfg.current_balance
    bucket2 = 0.0
    next_deposit = cfg.next_paycheck_date
    next_daily = daily_rate_from_apy(next_apy)
    rows = [{"date": d, "ORSA": orsa, "Bucket #2": bucket2, "Total": orsa + bucket2}]
    while d < end_date:
        old_month = d.month
        d += timedelta(days=1)
        orsa += daily_interest(orsa, cfg)
        bucket2 += bucket2 * next_daily
        if d == next_deposit:
            if orsa < cfg.high_yield_limit:
                room = max(cfg.high_yield_limit - orsa, 0.0)
                to_orsa = min(deposit_amount, room)
                to_next = max(deposit_amount - to_orsa, 0.0)
            else:
                to_orsa = 0.0
                to_next = deposit_amount
            orsa += to_orsa
            bucket2 += to_next
            next_deposit += timedelta(days=cfg.paycheck_frequency_days)
        if sweep_overflow and d.month != old_month and orsa > cfg.high_yield_limit:
            bucket2 += orsa - cfg.high_yield_limit
            orsa = cfg.high_yield_limit
        rows.append({"date": d, "ORSA": orsa, "Bucket #2": bucket2, "Total": orsa + bucket2})
    return pd.DataFrame(rows)


st.set_page_config(page_title="High-Yield Savings Project", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
:root{--super:#0866ff;--electric:#18c8ff;--red:#ef233c;--orange:#ff7a00;--gold:#ffd23f;--green:#49ff9a;--ink:#02050b}
.stApp{background:
radial-gradient(circle at 9% 5%,rgba(8,102,255,.34),transparent 29%),
radial-gradient(circle at 91% 8%,rgba(239,35,60,.28),transparent 27%),
radial-gradient(circle at 80% 48%,rgba(255,122,0,.10),transparent 22%),
linear-gradient(180deg,#030817 0%,#02050c 48%,#020307 100%);color:#f7fbff}
.block-container{max-width:1240px;padding:.55rem .65rem 3rem}header,footer{visibility:hidden}
[data-testid="stImage"] img{border-radius:24px;border:2px solid #1676ff;box-shadow:0 0 0 1px rgba(255,255,255,.06),0 0 32px rgba(8,102,255,.38),0 0 70px rgba(239,35,60,.15)}
.hero-copy{min-height:100%;padding:25px 24px;border-radius:26px;border:1px solid #1c5ec7;background:linear-gradient(135deg,rgba(9,65,160,.92),rgba(5,15,37,.96) 48%,rgba(112,8,25,.88));box-shadow:0 14px 55px #000a,0 0 50px rgba(8,102,255,.18);position:relative;overflow:hidden}
.hero-copy:after{content:"";position:absolute;right:-70px;bottom:-90px;width:220px;height:220px;border:28px solid rgba(255,122,0,.22);border-radius:50%}
.kicker{display:inline-block;background:linear-gradient(90deg,#0866ff,#ef233c,#ff7a00);padding:7px 12px;border-radius:999px;font-size:.72rem;font-weight:1000;letter-spacing:.06em}.hero-copy h1{margin:12px 0 4px;font-size:clamp(2.35rem,5.1vw,4.8rem);line-height:.91;letter-spacing:-.06em;font-weight:1000}.blue{color:#42b5ff;text-shadow:0 0 26px rgba(8,102,255,.8)}.red{color:#ff3b4f;text-shadow:0 0 26px rgba(239,35,60,.65)}.orange{color:#ff941f;text-shadow:0 0 24px rgba(255,122,0,.48)}.hero-copy p{max-width:680px;color:#d3e5ff;font-size:1rem;line-height:1.48}.hero-copy b{color:#ffd23f}
[data-testid="stMetric"]{background:linear-gradient(160deg,rgba(14,55,126,.96),rgba(4,10,22,.98));border:1px solid #1d64c9;border-radius:18px;padding:14px 15px;box-shadow:inset 0 1px 0 #ffffff0e,0 8px 24px #0006}.metric-red [data-testid="stMetric"]{border-color:#e72d46}.metric-orange [data-testid="stMetric"]{border-color:#f07c15}
[data-testid="stMetricLabel"]{color:#a9c0df!important;font-weight:900}[data-testid="stMetricValue"]{color:#fff!important;font-weight:1000;letter-spacing:-.04em}
.stSlider [data-baseweb="slider"] div[role="slider"]{background:#fff!important;box-shadow:0 0 18px #18c8ff!important}.stSlider [data-baseweb="slider"]>div>div{background:linear-gradient(90deg,#0866ff,#18c8ff,#ef233c)!important}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:#06101f;border:1px solid #244d82;border-radius:16px;padding:6px}.stTabs [data-baseweb="tab"]{border-radius:12px;color:#afc3dd;font-weight:950}.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#0866ff,#ef233c)!important;color:white!important;box-shadow:0 0 22px rgba(8,102,255,.28)}
.goalbar{height:17px;background:#10192a;border:1px solid #244f88;border-radius:999px;overflow:hidden;box-shadow:inset 0 0 14px #0009}.goalfill{height:100%;background:linear-gradient(90deg,#0866ff 0%,#18c8ff 38%,#ff7a00 70%,#ef233c 100%);box-shadow:0 0 24px #18c8ff}.caption{font-size:.78rem;color:#8fa9ca}.status{background:linear-gradient(90deg,rgba(8,102,255,.18),rgba(255,122,0,.10),rgba(239,35,60,.17));border:1px solid #2c5d9a;border-radius:17px;padding:14px 16px;margin:11px 0 14px}.status strong{color:#ffd23f}.section{font-size:1.35rem;font-weight:1000}.sub{color:#91a9c8;font-size:.86rem;margin-bottom:.6rem}.next{border:1px solid #663848;background:linear-gradient(135deg,#0d2f72,#07101f 52%,#4d0a18);border-radius:18px;padding:15px;margin:8px 0}.step{display:inline-grid;place-items:center;width:29px;height:29px;border-radius:50%;background:linear-gradient(135deg,#0866ff,#ef233c);font-weight:1000;margin-right:8px}.note{border-left:4px solid #ff7a00;background:#ff7a0014;padding:12px 14px;border-radius:11px}
@media(max-width:760px){.block-container{padding:.35rem .35rem 2rem}.hero-copy{padding:18px 16px}.hero-copy h1{font-size:2.45rem}}
</style>
""", unsafe_allow_html=True)

left, right = st.columns([1.18, .82], gap="medium")
with left:
    st.markdown(f"""
    <div class="hero-copy">
      <div class="kicker">⚡ PERSONAL SAVINGS CONTROL CENTER • v{APP_VERSION}</div>
      <h1><span class="blue">HIGH-YIELD</span><br><span class="red">SAVINGS</span> <span class="orange">PROJECT</span></h1>
      <p>Attack the <b>10% APY zone</b> first. Change the paycheck amount and watch your path to <b>$1,000</b> update instantly. Then keep the exact same saving habit and redirect the money to the next high-yield destination.</p>
    </div>
    """, unsafe_allow_html=True)
with right:
    hero = Path("assets/hero_production.jpg")
    if hero.exists() and hero.stat().st_size > 1000:
        st.image(str(hero), use_container_width=True)
    else:
        st.markdown("<div class='hero-copy'><h2>⚡ KEEP STACKING</h2><p>Your hero image file is missing from the deployment.</p></div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1.2,1,1,1])
with c1:
    deposit_amount = st.slider("Deposit every paycheck", 5, 150, int(DEFAULT_DEPOSIT), 5)
with c2:
    starting_balance = st.number_input("Current balance", min_value=0.0, value=DEFAULT_BALANCE, step=5.0, format="%.2f")
with c3:
    next_paycheck = st.date_input("Next paycheck deposit", value=DEFAULT_NEXT_PAYCHECK)
with c4:
    paycheck_days = st.selectbox("Deposit frequency", [7,14,15,30], index=1, format_func=lambda x:{7:"Weekly",14:"Every 2 weeks",15:"About twice monthly",30:"Monthly"}[x])

cfg = AccountConfig(TODAY, float(starting_balance), float(deposit_amount), next_paycheck, int(paycheck_days))
frame = project_savings(cfg, float(deposit_amount), TODAY + timedelta(days=365*10))
hit = first_goal_date(frame)
through = frame[frame["date"] <= hit] if hit else frame
interest_to_goal = float(through["interest"].sum()) if hit else 0.0
deposits_to_goal = float(through["deposit"].sum()) if hit else 0.0
months = ((hit-TODAY).days/30.4375) if hit else None
progress = min(float(starting_balance)/1000.0,1.0)

st.markdown(f"<div class='goalbar'><div class='goalfill' style='width:{progress*100:.2f}%'></div></div><div class='caption'>{progress*100:.1f}% of the $1,000 premium-rate zone filled</div>", unsafe_allow_html=True)

m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("CURRENT", f"${starting_balance:,.2f}")
m2.metric("PER PAYCHECK", f"${deposit_amount}")
m3.metric("10% ZONE LEFT", f"${max(1000-starting_balance,0):,.2f}")
m4.metric("PROJECTED $1K", hit.strftime("%b %d, %Y") if hit else "Beyond model")
m5.metric("INTEREST TO $1K", f"${interest_to_goal:,.2f}" if hit else "—")

if hit:
    st.markdown(f"<div class='status'>💥 <b>${deposit_amount} every {paycheck_days} days</b> projects to <strong>$1,000 on {hit.strftime('%B %d, %Y')}</strong> — about <b>{months:.1f} months</b>. Roughly <strong>${interest_to_goal:,.2f}</strong> of that climb comes from interest.</div>", unsafe_allow_html=True)

plan_tab, race_tab, next_tab, history_tab = st.tabs(["⚡ YOUR PLAN","🏁 DEPOSIT RACE","🚀 AFTER $1,000","🧾 ACTUAL HISTORY"])

with plan_tab:
    st.markdown("<div class='section'>Your Run to $1,000</div><div class='sub'>Electric blue is your balance. Orange markers are paycheck deposits. Red is the premium-rate finish line.</div>", unsafe_allow_html=True)
    max_date = min(TODAY+timedelta(days=365*5), hit+timedelta(days=180) if hit else TODAY+timedelta(days=365*5))
    plot = frame[frame["date"] <= max_date].copy()
    deposits = plot[plot["deposit"] > 0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot["date"], y=plot["balance"], mode="lines", line=dict(color="rgba(24,200,255,.18)", width=13), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=plot["date"], y=plot["balance"], mode="lines", name="Projected balance", line=dict(color="#18c8ff", width=4), fill="tozeroy", fillcolor="rgba(8,102,255,.17)"))
    fig.add_trace(go.Scatter(x=deposits["date"], y=deposits["balance"], mode="markers", name="Paycheck deposit", marker=dict(color="#ff7a00", size=8, line=dict(color="#ffd23f", width=1))))
    fig.add_hline(y=1000, line_dash="dash", line_color="#ef233c", line_width=4, annotation_text="⚡ $1,000 PREMIUM ZONE FILLED", annotation_font_color="#ff6677")
    fig.update_layout(height=470, margin=dict(l=5,r=5,t=30,b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#030916", font_color="#eaf4ff", legend=dict(orientation="h",y=1.08), xaxis=dict(gridcolor="#122a48",showline=True,linecolor="#24517f"), yaxis=dict(gridcolor="#122a48",tickprefix="$",rangemode="tozero"), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    gauge = go.Figure(go.Indicator(mode="gauge+number", value=min(starting_balance,1000), number={"prefix":"$","font":{"size":44,"color":"#ffffff"}}, title={"text":"CURRENT PROGRESS TO $1,000","font":{"color":"#9fc7ff"}}, gauge={"axis":{"range":[0,1000],"tickprefix":"$","tickcolor":"#789"},"bar":{"color":"#18c8ff","thickness":.32},"bgcolor":"#040b17","bordercolor":"#1f61b9","steps":[{"range":[0,500],"color":"#082958"},{"range":[500,800],"color":"#153b6c"},{"range":[800,1000],"color":"#55101c"}],"threshold":{"line":{"color":"#ef233c","width":6},"thickness":.85,"value":1000}}))
    gauge.update_layout(height=300, margin=dict(l=25,r=25,t=55,b=10), paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar":False})

with race_tab:
    st.markdown("<div class='section'>How Much Faster if You Save More?</div><div class='sub'>The shorter the bar, the faster you hit the $1,000 premium-rate zone.</div>", unsafe_allow_html=True)
    amounts = sorted(set([5,10,15,20,25,30,40,50,75,100,125,150,int(deposit_amount)]))
    scenarios = deposit_scenarios(cfg, amounts)
    colors = ["#0866ff" if a < 25 else "#18c8ff" if a < 50 else "#ff7a00" if a < 100 else "#ef233c" for a in scenarios["amount"]]
    fig2 = go.Figure(go.Bar(x=scenarios["amount"], y=scenarios["months_raw"], marker=dict(color=colors, line=dict(color="#ffffff",width=.4)), text=scenarios["Months"].map(lambda x:f"{x:.1f} mo"), textposition="outside", hovertemplate="$%{x}/paycheck<br>%{y:.1f} months<extra></extra>"))
    fig2.update_layout(height=430, margin=dict(l=5,r=5,t=20,b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#030916", font_color="#eaf4ff", xaxis_title="Deposit each paycheck ($)", yaxis_title="Months to $1,000", xaxis=dict(gridcolor="#122a48"), yaxis=dict(gridcolor="#122a48"))
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
    st.dataframe(scenarios[["Deposit / Paycheck","Goal Date","Months","Interest"]], hide_index=True, use_container_width=True)

with next_tab:
    st.markdown("<div class='section'>Keep Capitalizing After $1,000</div><div class='sub'>Checkpoint #1 is filling the 10% zone. Checkpoint #2 is redirecting every future deposit instead of letting the habit stop.</div>", unsafe_allow_html=True)
    n1,n2,n3 = st.columns(3)
    with n1:
        next_apy_pct = st.number_input("Next account APY (%)", min_value=0.0, max_value=20.0, value=4.50, step=.10)
    with n2:
        total_goal = st.number_input("Total cash-savings goal", min_value=1000.0, value=5000.0, step=500.0)
    with n3:
        sweep = st.toggle("Sweep ORSA overflow", value=True)
    strategy = project_two_bucket(cfg, float(deposit_amount), next_apy_pct/100.0, float(total_goal), sweep, TODAY+timedelta(days=365*12))
    orsa_rows = strategy[strategy["ORSA"] >= 1000]
    orsa_hit = None if orsa_rows.empty else orsa_rows.iloc[0]["date"]
    goal_rows = strategy[strategy["Total"] >= float(total_goal)]
    goal_hit = None if goal_rows.empty else goal_rows.iloc[0]["date"]
    q1,q2,q3,q4 = st.columns(4)
    q1.metric("ORSA TARGET","$1,000")
    q2.metric("REDIRECT START",orsa_hit.strftime("%b %d, %Y") if orsa_hit else "—")
    q3.metric("TOTAL GOAL",f"${total_goal:,.0f}")
    q4.metric("GOAL DATE",goal_hit.strftime("%b %d, %Y") if goal_hit else "Beyond model")
    st.markdown("<div class='next'><span class='step'>1</span><b>Fill the 10% ORSA zone.</b><div class='caption'>Keep your automatic paycheck deposit pointed there until the $1,000 tier is full.</div></div><div class='next'><span class='step'>2</span><b>Redirect new deposits immediately.</b><div class='caption'>Keep ORSA's premium $1,000 working while new paycheck money flows to Bucket #2.</div></div><div class='next'><span class='step'>3</span><b>Grow the emergency fund without losing momentum.</b><div class='caption'>The behavior stays automatic; only the destination changes.</div></div>", unsafe_allow_html=True)
    end_show = min(TODAY+timedelta(days=365*6), goal_hit+timedelta(days=120) if goal_hit else TODAY+timedelta(days=365*6))
    sp = strategy[strategy["date"] <= end_show]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=sp["date"],y=sp["ORSA"],stackgroup="one",name="ORSA 10% bucket",line=dict(color="#0866ff",width=3),fillcolor="rgba(8,102,255,.50)"))
    fig3.add_trace(go.Scatter(x=sp["date"],y=sp["Bucket #2"],stackgroup="one",name="Next HYSA bucket",line=dict(color="#ef233c",width=3),fillcolor="rgba(239,35,60,.42)"))
    fig3.add_hline(y=float(total_goal),line_dash="dot",line_color="#ff7a00",line_width=3,annotation_text=f"🔥 ${total_goal:,.0f} TOTAL GOAL",annotation_font_color="#ff9f35")
    fig3.update_layout(height=470, margin=dict(l=5,r=5,t=30,b=5),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#030916",font_color="#eaf4ff",legend=dict(orientation="h",y=1.08),xaxis=dict(gridcolor="#122a48"),yaxis=dict(gridcolor="#122a48",tickprefix="$"),hovermode="x unified")
    st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})
    st.markdown("<div class='note'><b>Strategy:</b> keep the automatic savings habit. Once the high-rate tier is full, change the destination — not the behavior.</div>", unsafe_allow_html=True)

with history_tab:
    st.markdown("<div class='section'>Actual ORSA History</div><div class='sub'>Real transactions remain separate from projections.</div>", unsafe_allow_html=True)
    p = Path("data/savings_transactions.csv")
    if p.exists():
        hist = pd.read_csv(p)
        hist["date"] = pd.to_datetime(hist["date"])
        hist = hist.sort_values("date",ascending=False)
        st.dataframe(hist,hide_index=True,use_container_width=True)
        div = hist[hist["type"] == "dividend"].sort_values("date")
        if not div.empty:
            hfig = go.Figure(go.Bar(x=div["date"],y=div["amount"],marker=dict(color=["#0866ff" if i%3==0 else "#ff7a00" if i%3==1 else "#ef233c" for i in range(len(div))]),text=div["amount"].map(lambda x:f"${x:.2f}"),textposition="outside"))
            hfig.update_layout(height=330,margin=dict(l=5,r=5,t=20,b=5),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#030916",font_color="#eaf4ff",yaxis=dict(tickprefix="$",gridcolor="#122a48"),xaxis=dict(gridcolor="#122a48"))
            st.plotly_chart(hfig,use_container_width=True,config={"displayModeBar":False})
    else:
        st.info("Savings transaction file is not present yet.")

st.markdown(f"<div class='caption' style='text-align:center;margin-top:24px'>High-Yield Savings Project v{APP_VERSION} • Streamlit + Python • Planning estimates, not bank statements</div>", unsafe_allow_html=True)
