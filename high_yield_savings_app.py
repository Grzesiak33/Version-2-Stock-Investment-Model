from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_VERSION = "2.0.0"
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


def project_two_bucket(
    cfg: AccountConfig,
    deposit_amount: float,
    next_apy: float,
    total_goal: float,
    sweep_overflow: bool,
    end_date: date,
) -> pd.DataFrame:
    d = cfg.start_date
    orsa = cfg.current_balance
    bucket2 = 0.0
    next_deposit = cfg.next_paycheck_date
    rows = [{"date": d, "ORSA": orsa, "Bucket #2": bucket2, "Total": orsa + bucket2}]
    next_daily = daily_rate_from_apy(next_apy)
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
        if orsa + bucket2 >= total_goal and d > cfg.start_date + timedelta(days=30):
            # Keep another 90 days for chart context.
            if d + timedelta(days=90) < end_date:
                end_date = d + timedelta(days=90)
    return pd.DataFrame(rows)


st.set_page_config(
    page_title="High-Yield Savings Project",
    page_icon="💥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root{--blue:#1677ff;--cyan:#00c8ff;--red:#ff263f;--yellow:#ffd21f;--green:#3dff8b;--muted:#9cb2cc}
.stApp{background:radial-gradient(circle at 13% 8%,rgba(22,119,255,.28),transparent 28%),radial-gradient(circle at 87% 5%,rgba(255,38,63,.23),transparent 28%),linear-gradient(180deg,#030816,#01040a);color:#f6f9ff}
.block-container{max-width:1180px;padding:.8rem .8rem 3rem}header,footer{visibility:hidden}
.hero{position:relative;overflow:hidden;border:1px solid #245ba7;border-radius:28px;padding:24px 26px 22px;margin-bottom:14px;background:linear-gradient(115deg,#0c2b64 0%,#061126 48%,#5a0a1d 100%);box-shadow:0 18px 60px #0009,0 0 38px rgba(22,119,255,.22)}
.hero:before{content:"";position:absolute;right:-85px;top:-105px;width:330px;height:330px;border-radius:50%;border:34px solid rgba(255,38,63,.24)}
.hero:after{content:"";position:absolute;right:125px;bottom:-180px;width:330px;height:330px;border-radius:50%;border:28px solid rgba(0,200,255,.18)}
.kicker{position:relative;z-index:2;display:inline-block;background:linear-gradient(90deg,#126fff,#ff263f);padding:7px 12px;border-radius:999px;font-size:.72rem;font-weight:900;letter-spacing:.07em}
.hero h1{position:relative;z-index:2;margin:10px 0 5px;font-size:clamp(2.2rem,5vw,4.5rem);line-height:.92;letter-spacing:-.055em;font-weight:1000}.hero .blue{color:#46aeff;text-shadow:0 0 22px #1677ff77}.hero .red{color:#ff3b51;text-shadow:0 0 22px #ff263f66}.hero p{position:relative;z-index:2;max-width:780px;color:#ccdbef;margin:.8rem 0 0}.hero b{color:#ffd21f}
[data-testid="stMetric"]{background:linear-gradient(150deg,rgba(15,47,91,.95),rgba(4,12,26,.98));border:1px solid #24538c;border-radius:18px;padding:14px 15px;box-shadow:inset 0 1px 0 #ffffff08}
[data-testid="stMetricLabel"]{color:#9eb5d2!important;font-weight:800}[data-testid="stMetricValue"]{color:#fff!important;font-weight:950;letter-spacing:-.03em}
.stTabs [data-baseweb="tab-list"]{gap:7px;background:#06101f;border:1px solid #18365d;border-radius:15px;padding:6px}.stTabs [data-baseweb="tab"]{border-radius:11px;color:#a8bdd6;font-weight:900}.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#126fff,#ff263f)!important;color:white!important}
.goalbar{height:16px;background:#101a2c;border:1px solid #224a7c;border-radius:999px;overflow:hidden}.goalfill{height:100%;background:linear-gradient(90deg,#126fff 0%,#00c8ff 56%,#ff263f 100%);box-shadow:0 0 20px #1677ff88}.caption{font-size:.77rem;color:#8fa8c7}.status{background:linear-gradient(120deg,rgba(22,119,255,.18),rgba(6,14,28,.92),rgba(255,38,63,.15));border:1px solid #2a5793;border-radius:18px;padding:14px 16px;margin:10px 0 14px}.status .b{color:#50b6ff;font-weight:950}.status .r{color:#ff5267;font-weight:950}.status .g{color:#4aff94;font-weight:950}.status strong{color:#ffd21f}
.section{font-size:1.35rem;font-weight:1000;margin:.25rem 0 .1rem}.sub{font-size:.86rem;color:#96acc8;margin-bottom:.6rem}.next{border:1px solid #5f2852;background:linear-gradient(135deg,#0e2a5d,#071122 55%,#410b1c);border-radius:18px;padding:15px 16px;margin:8px 0}.step{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#ff263f;color:#fff;font-weight:1000;margin-right:8px}.note{border-left:4px solid #ffd21f;background:#ffd21f12;padding:12px 14px;border-radius:12px;color:#d7e4f3;margin-top:10px}
@media(max-width:700px){.block-container{padding:.45rem .4rem 2rem}.hero{padding:18px 15px;border-radius:21px}.hero h1{font-size:2.35rem}[data-testid="stMetric"]{padding:10px}.stTabs [data-baseweb="tab"]{font-size:.72rem;padding:8px 7px}}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="hero">
<div class="kicker">💥 PERSONAL SAVINGS CONTROL CENTER • v{APP_VERSION}</div>
<h1><span class="blue">HIGH-YIELD</span><br><span class="red">SAVINGS PROJECT</span></h1>
<p>Fill the <b>10% APY $1,000 zone</b> first. Change the paycheck amount and instantly see how fast you get there — then keep the habit going by routing future savings to the next high-yield bucket.</p>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns([1.15, 1, 1, 1])
with c1:
    deposit_amount = st.slider("Deposit every paycheck", 5, 150, int(DEFAULT_DEPOSIT), 5)
with c2:
    starting_balance = st.number_input("Current balance", min_value=0.0, value=DEFAULT_BALANCE, step=5.0, format="%.2f")
with c3:
    next_paycheck = st.date_input("Next paycheck deposit", value=DEFAULT_NEXT_PAYCHECK)
with c4:
    paycheck_days = st.selectbox("Deposit frequency", [7, 14, 15, 30], index=1, format_func=lambda x: {7: "Weekly", 14: "Every 2 weeks", 15: "About twice monthly", 30: "Monthly"}[x])

cfg = AccountConfig(TODAY, float(starting_balance), float(deposit_amount), next_paycheck, int(paycheck_days))
frame = project_savings(cfg, float(deposit_amount), TODAY + timedelta(days=365 * 10))
hit = first_goal_date(frame)
through = frame[frame["date"] <= hit] if hit else frame
interest_to_goal = float(through["interest"].sum()) if hit else 0.0
deposits_to_goal = float(through["deposit"].sum()) if hit else 0.0
months = ((hit - TODAY).days / 30.4375) if hit else None
progress = min(float(starting_balance) / 1000.0, 1.0)

st.markdown(f"<div class='goalbar'><div class='goalfill' style='width:{progress*100:.2f}%'></div></div><div class='caption'>{progress*100:.1f}% of the $1,000 high-yield zone filled</div>", unsafe_allow_html=True)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Current Balance", f"${starting_balance:,.2f}")
m2.metric("Every Paycheck", f"${deposit_amount}")
m3.metric("10% Zone Left", f"${max(1000-starting_balance,0):,.2f}")
m4.metric("Projected $1K Date", hit.strftime("%b %d, %Y") if hit else "Beyond model")
m5.metric("Interest to $1K", f"${interest_to_goal:,.2f}" if hit else "—")

if hit:
    st.markdown(f"<div class='status'><span class='b'>CURRENT PLAN:</span> ${deposit_amount} every {paycheck_days} days gets you to <strong>$1,000 around {hit.strftime('%B %d, %Y')}</strong> — about <span class='r'>{months:.1f} months</span>. Projected interest contributes about <span class='g'>${interest_to_goal:,.2f}</span> along the way.</div>", unsafe_allow_html=True)

plan_tab, race_tab, next_tab, history_tab = st.tabs(["⚡ YOUR PLAN", "🏁 DEPOSIT RACE", "🚀 AFTER $1,000", "🧾 ACTUAL HISTORY"])

with plan_tab:
    st.markdown("<div class='section'>Projected Balance</div><div class='sub'>Blue is your balance. Red is the $1,000 premium-rate checkpoint.</div>", unsafe_allow_html=True)
    max_date = min(TODAY + timedelta(days=365 * 5), hit + timedelta(days=180) if hit else TODAY + timedelta(days=365 * 5))
    plot = frame[frame["date"] <= max_date]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot["date"], y=plot["balance"], mode="lines", name="Projected balance", line=dict(color="#2fa8ff", width=4), fill="tozeroy", fillcolor="rgba(47,168,255,.11)"))
    fig.add_hline(y=1000, line_dash="dash", line_color="#ff3048", line_width=3, annotation_text="$1,000 HIGH-YIELD TARGET", annotation_font_color="#ff6375")
    fig.update_layout(height=430, margin=dict(l=5, r=5, t=25, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#040b16", font_color="#dcecff", legend=dict(orientation="h", y=1.08), xaxis=dict(gridcolor="#11243b"), yaxis=dict(gridcolor="#11243b", tickprefix="$", rangemode="tozero"), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    y1 = frame[frame["date"] <= TODAY + timedelta(days=365)].iloc[-1]
    y2 = frame[frame["date"] <= TODAY + timedelta(days=730)].iloc[-1]
    a, b, c = st.columns(3)
    a.metric("1-Year Balance", f"${y1['balance']:,.2f}")
    b.metric("2-Year Balance", f"${y2['balance']:,.2f}")
    c.metric("Deposits by $1K", f"${deposits_to_goal:,.0f}" if hit else "—")

with race_tab:
    st.markdown("<div class='section'>Deposit Race to $1,000</div><div class='sub'>Move the slider above, or compare the common paycheck amounts below.</div>", unsafe_allow_html=True)
    amounts = sorted(set([5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 125, 150, int(deposit_amount)]))
    scenarios = deposit_scenarios(cfg, amounts)
    st.dataframe(scenarios[["Deposit / Paycheck", "Goal Date", "Months", "Interest"]], hide_index=True, use_container_width=True)
    fig2 = go.Figure(go.Bar(x=scenarios["amount"], y=scenarios["months_raw"], marker=dict(color=scenarios["amount"], colorscale=[[0, "#126fff"], [.55, "#00c8ff"], [1, "#ff263f"]]), text=scenarios["Months"].map(lambda x: f"{x:.1f} mo"), textposition="outside"))
    fig2.update_layout(height=390, margin=dict(l=5, r=5, t=20, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#040b16", font_color="#dcecff", xaxis_title="Deposit each paycheck ($)", yaxis_title="Months to $1,000", xaxis=dict(gridcolor="#11243b"), yaxis=dict(gridcolor="#11243b"))
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

with next_tab:
    st.markdown("<div class='section'>Keep Capitalizing After $1,000</div><div class='sub'>The $1,000 is checkpoint #1, not the finish line. Model the next savings bucket here.</div>", unsafe_allow_html=True)
    n1, n2, n3 = st.columns(3)
    with n1:
        next_apy_pct = st.number_input("Next account APY (%)", min_value=0.0, max_value=20.0, value=4.50, step=.10, help="Enter the actual APY of whatever second HYSA or money-market account you choose.")
    with n2:
        total_goal = st.number_input("Total cash-savings goal", min_value=1000.0, value=5000.0, step=500.0)
    with n3:
        sweep = st.toggle("Sweep ORSA overflow", value=True, help="Model moving any ORSA amount above $1,000 into Bucket #2 at the start of each month.")
    strategy = project_two_bucket(cfg, float(deposit_amount), next_apy_pct / 100.0, float(total_goal), sweep, TODAY + timedelta(days=365 * 12))
    orsa_hit_rows = strategy[strategy["ORSA"] >= 1000]
    orsa_hit = None if orsa_hit_rows.empty else orsa_hit_rows.iloc[0]["date"]
    goal_rows = strategy[strategy["Total"] >= float(total_goal)]
    goal_hit = None if goal_rows.empty else goal_rows.iloc[0]["date"]
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("ORSA Premium Target", "$1,000")
    q2.metric("Redirect Starts", orsa_hit.strftime("%b %d, %Y") if orsa_hit else "—")
    q3.metric("Total Goal", f"${total_goal:,.0f}")
    q4.metric("Projected Goal Date", goal_hit.strftime("%b %d, %Y") if goal_hit else "Beyond model")
    st.markdown("<div class='next'><span class='step'>1</span><b>Fill ORSA's 10% zone.</b><div class='caption'>Keep the automatic paycheck transfer focused there until the premium $1,000 is filled.</div></div><div class='next'><span class='step'>2</span><b>Redirect new paycheck deposits.</b><div class='caption'>After the premium zone is full, point future deposits to Bucket #2 instead of piling new cash into the low excess-rate tier.</div></div><div class='next'><span class='step'>3</span><b>Build the larger emergency-fund goal.</b><div class='caption'>Enter Bucket #2's real APY above and the model combines both balances.</div></div>", unsafe_allow_html=True)
    end_show = min(TODAY + timedelta(days=365 * 6), goal_hit + timedelta(days=120) if goal_hit else TODAY + timedelta(days=365 * 6))
    sp = strategy[strategy["date"] <= end_show]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=sp["date"], y=sp["ORSA"], stackgroup="one", name="ORSA", line=dict(color="#1677ff", width=2)))
    fig3.add_trace(go.Scatter(x=sp["date"], y=sp["Bucket #2"], stackgroup="one", name="Bucket #2", line=dict(color="#ff263f", width=2)))
    fig3.add_hline(y=float(total_goal), line_dash="dot", line_color="#ffd21f", annotation_text=f"${total_goal:,.0f} TOTAL GOAL", annotation_font_color="#ffd21f")
    fig3.update_layout(height=430, margin=dict(l=5, r=5, t=25, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#040b16", font_color="#dcecff", legend=dict(orientation="h", y=1.08), xaxis=dict(gridcolor="#11243b"), yaxis=dict(gridcolor="#11243b", tickprefix="$"), hovermode="x unified")
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    st.markdown("<div class='note'><b>The basic strategy:</b> keep the automatic saving behavior; only change the destination after the unusually strong rate tier is full.</div>", unsafe_allow_html=True)

with history_tab:
    st.markdown("<div class='section'>Actual ORSA History</div><div class='sub'>Your real deposits and dividends stay separate from the projections.</div>", unsafe_allow_html=True)
    p = Path("data/savings_transactions.csv")
    if p.exists():
        hist = pd.read_csv(p)
        hist["date"] = pd.to_datetime(hist["date"])
        hist = hist.sort_values("date", ascending=False)
        st.dataframe(hist, hide_index=True, use_container_width=True)
        div = hist[hist["type"] == "dividend"].copy()
        if not div.empty:
            hfig = go.Figure(go.Bar(x=div["date"], y=div["amount"], marker_color="#ff3048", text=div["amount"].map(lambda x: f"${x:.2f}"), textposition="outside"))
            hfig.update_layout(height=320, margin=dict(l=5, r=5, t=20, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#040b16", font_color="#dcecff", yaxis=dict(tickprefix="$", gridcolor="#11243b"), xaxis=dict(gridcolor="#11243b"))
            st.plotly_chart(hfig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Savings transaction file is not present yet.")

st.markdown(f"<div class='caption' style='text-align:center;margin-top:24px'>High-Yield Savings Project v{APP_VERSION} • Streamlit + Python • Planning estimates, not bank statements</div>", unsafe_allow_html=True)
