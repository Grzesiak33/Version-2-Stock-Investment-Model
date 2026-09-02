from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

APP_VERSION = "2.4.0"
TODAY = date(2026, 9, 1)
DEFAULT_BALANCE = 20.71
DEFAULT_DEPOSIT = 10.0
DEFAULT_NEXT_PAYCHECK = date(2026, 9, 11)

# Trademark palette pulled from the stock/mobile app.
BLUE_TOP = "#087cf2"
BLUE_MID = "#075dcc"
BLUE_PANEL = "#075fd7"
BLUE_DEEP = "#0647aa"
CYAN = "#3bd7ff"
RED = "#e51b23"
ORANGE = "#ff6a00"
YELLOW = "#ffe600"
GREEN = "#24bd2d"
PURPLE = "#7a28ce"


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
    return (1 + apy) ** (1 / 365) - 1


def daily_interest(balance: float, cfg: AccountConfig) -> float:
    return min(balance, cfg.high_yield_limit) * daily_rate_from_apy(cfg.high_yield_apy) + max(balance - cfg.high_yield_limit, 0) * daily_rate_from_apy(cfg.excess_apy)


def project_savings(cfg: AccountConfig, amount: float, end_date: date) -> pd.DataFrame:
    d, balance, next_deposit = cfg.start_date, cfg.current_balance, cfg.next_paycheck_date
    rows = [{"date": d, "balance": balance, "deposit": 0.0, "interest": 0.0}]
    while d < end_date:
        d += timedelta(days=1)
        interest = daily_interest(balance, cfg)
        balance += interest
        dep = 0.0
        if d == next_deposit:
            dep = float(amount)
            balance += dep
            next_deposit += timedelta(days=cfg.paycheck_frequency_days)
        rows.append({"date": d, "balance": balance, "deposit": dep, "interest": interest})
    return pd.DataFrame(rows)


def first_goal_date(frame: pd.DataFrame, goal: float = 1000) -> date | None:
    hit = frame[frame["balance"] >= goal]
    return None if hit.empty else hit.iloc[0]["date"]


def deposit_scenarios(cfg: AccountConfig, amounts: list[float]) -> pd.DataFrame:
    rows = []
    for amount in amounts:
        f = project_savings(cfg, amount, cfg.start_date + timedelta(days=3650))
        hit = first_goal_date(f)
        if hit:
            thru = f[f["date"] <= hit]
            months = (hit - cfg.start_date).days / 30.4375
            rows.append({"Deposit / Paycheck": f"${amount:,.0f}", "Goal Date": hit.strftime("%b %d, %Y"), "Months": round(months, 1), "Interest": f"${thru['interest'].sum():,.2f}", "amount": amount, "months_raw": months})
    return pd.DataFrame(rows)


def project_two_bucket(cfg: AccountConfig, amount: float, next_apy: float, end_date: date) -> pd.DataFrame:
    d, orsa, bucket2, next_deposit = cfg.start_date, cfg.current_balance, 0.0, cfg.next_paycheck_date
    next_daily = daily_rate_from_apy(next_apy)
    rows = [{"date": d, "ORSA": orsa, "Bucket #2": bucket2, "Total": orsa + bucket2}]
    while d < end_date:
        old_month = d.month
        d += timedelta(days=1)
        orsa += daily_interest(orsa, cfg)
        bucket2 += bucket2 * next_daily
        if d == next_deposit:
            room = max(cfg.high_yield_limit - orsa, 0)
            to_orsa = min(amount, room) if room > 0 else 0
            bucket2 += max(amount - to_orsa, 0)
            orsa += to_orsa
            next_deposit += timedelta(days=cfg.paycheck_frequency_days)
        if d.month != old_month and orsa > cfg.high_yield_limit:
            bucket2 += orsa - cfg.high_yield_limit
            orsa = cfg.high_yield_limit
        rows.append({"date": d, "ORSA": orsa, "Bucket #2": bucket2, "Total": orsa + bucket2})
    return pd.DataFrame(rows)


def hero_figure() -> go.Figure | None:
    p = Path("assets/hero_production.jpg")
    if not p.exists():
        return None
    img = Image.open(p).convert("RGB")
    w, h = img.size
    img = img.crop((0, int(h * 0.14), w, h))  # removes baked-in 9:41 status bar
    fig = go.Figure()
    fig.add_layout_image(dict(source=img, xref="paper", yref="paper", x=0, y=1, sizex=1, sizey=1, sizing="cover", xanchor="left", yanchor="top", layer="below"))
    fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color=YELLOW, width=5), fillcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False, range=[0, 1], fixedrange=True)
    fig.update_yaxes(visible=False, range=[0, 1], fixedrange=True)
    fig.update_layout(height=330, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", dragmode=False)
    return fig


def chart_layout(fig: go.Figure, height: int = 450):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=28, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BLUE_DEEP,
        font_color="white",
        xaxis=dict(gridcolor="#48bdf055", linecolor=CYAN, zeroline=False),
        yaxis=dict(gridcolor="#48bdf055", linecolor=CYAN, zeroline=False),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08),
    )


st.set_page_config(page_title="High-Yield Savings Project", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.stApp{background:linear-gradient(180deg,#087cf2,#075dcc 45%,#05378c 100%);color:#fff}
.block-container{max-width:1180px;padding:.35rem .45rem 3rem}header,footer{visibility:hidden}
.hero-copy{min-height:330px;padding:24px;border:3px solid #ffd31a;border-radius:20px;background:linear-gradient(125deg,#e51b23 0%,#d70d18 31%,#075edb 32%,#0647aa 72%,#7a28ce 100%);box-shadow:0 8px 24px #00296588;overflow:hidden}
.kicker{display:inline-block;padding:7px 11px;border-radius:999px;background:#ff6a00;border:2px solid #ffe600;color:white;font-size:.72rem;font-weight:1000}.hero-copy h1{margin:12px 0 6px;font-size:clamp(2.35rem,5vw,4.7rem);line-height:.92;letter-spacing:-.055em;font-weight:1000}.blue{color:#55efff}.red{color:#fff}.orange{color:#fff200}.hero-copy p{color:#fff;font-size:1rem;line-height:1.48}.hero-copy b{color:#fff200}
[data-testid="stMetric"]{background:linear-gradient(180deg,#075fd7,#0647aa);border:2px solid #3bd7ff;border-radius:17px;padding:14px;box-shadow:0 7px 18px #00296388}[data-testid="stMetricLabel"]{color:#fff!important;font-weight:900}[data-testid="stMetricValue"]{color:#fff!important;font-weight:1000}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:#075fd7;border:2px solid #3bd7ff;border-radius:15px;padding:6px}.stTabs [data-baseweb="tab"]{border-radius:11px;color:#fff;font-weight:950}.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#e51b23,#ff6a00)!important;color:white!important;border:2px solid #ffe600}
[data-testid="stPlotlyChart"]{border:2px solid #3bd7ff;border-radius:18px;overflow:hidden;box-shadow:0 7px 18px #00296388}
.goalbar{height:18px;background:#0647aa;border:2px solid #3bd7ff;border-radius:999px;overflow:hidden}.goalfill{height:100%;background:linear-gradient(90deg,#24bd2d,#55efff,#ff6a00,#e51b23);box-shadow:0 0 18px #fff200}.caption{font-size:.8rem;color:#fff;font-weight:800}.status{background:linear-gradient(90deg,#13a52a 0%,#087b21 35%,#075bd0 36%,#063e9d 100%);border:3px solid #ffe600;border-radius:18px;padding:14px 16px;margin:10px 0 14px;color:white;box-shadow:0 8px 22px #00275f99}.status strong{color:#fff200}.section{font-size:1.35rem;font-weight:1000;color:#fff}.sub{color:#e9f8ff;font-size:.88rem;font-weight:700;margin-bottom:.65rem}.next{border:2px solid #3bd7ff;background:linear-gradient(135deg,#0b72ed,#0649b0);border-radius:15px;padding:14px;margin:8px 0;box-shadow:0 4px 12px #00327a77}.step{display:inline-grid;place-items:center;width:29px;height:29px;border-radius:50%;background:#ff6a00;border:2px solid #ffe600;font-weight:1000;margin-right:8px}.note{border:3px solid #ffd31a;background:linear-gradient(120deg,#e51b23,#ff6a00);padding:12px 14px;border-radius:15px;color:#fff;font-weight:800}
[data-testid="stSlider"] [role="slider"]{box-shadow:0 0 0 4px #ffe600!important}
@media(max-width:760px){.block-container{padding:.25rem .3rem 2rem}.hero-copy{padding:17px;min-height:280px}.hero-copy h1{font-size:2.4rem}}
</style>
""", unsafe_allow_html=True)

left,right=st.columns([1.18,.82],gap="medium")
with left:
    st.markdown(f"<div class='hero-copy'><div class='kicker'>⚡ PERSONAL SAVINGS CONTROL CENTER • v{APP_VERSION}</div><h1><span class='blue'>HIGH-YIELD</span><br><span class='red'>SAVINGS</span> <span class='orange'>PROJECT</span></h1><p>Attack the <b>10% APY zone</b> first. Change the paycheck amount and watch your path to <b>$1,000</b> update instantly. Then keep the same saving habit and redirect the money to the next high-yield destination.</p></div>",unsafe_allow_html=True)
with right:
    hero=hero_figure()
    if hero is not None: st.plotly_chart(hero,use_container_width=True,config={"displayModeBar":False,"staticPlot":True})

c1,c2,c3,c4=st.columns([1.2,1,1,1])
with c1: deposit_amount=st.slider("Deposit every paycheck",5,150,int(DEFAULT_DEPOSIT),5)
with c2: starting_balance=st.number_input("Current balance",min_value=0.0,value=DEFAULT_BALANCE,step=5.0,format="%.2f")
with c3: next_paycheck=st.date_input("Next paycheck deposit",value=DEFAULT_NEXT_PAYCHECK)
with c4: paycheck_days=st.selectbox("Deposit frequency",[7,14,15,30],index=1,format_func=lambda x:{7:"Weekly",14:"Every 2 weeks",15:"About twice monthly",30:"Monthly"}[x])

cfg=AccountConfig(TODAY,float(starting_balance),float(deposit_amount),next_paycheck,int(paycheck_days))
frame=project_savings(cfg,float(deposit_amount),TODAY+timedelta(days=3650))
hit=first_goal_date(frame)
through=frame[frame["date"]<=hit] if hit else frame
interest_to_goal=float(through["interest"].sum()) if hit else 0
months=((hit-TODAY).days/30.4375) if hit else None
progress=min(float(starting_balance)/1000,1)
st.markdown(f"<div class='goalbar'><div class='goalfill' style='width:{progress*100:.2f}%'></div></div><div class='caption'>{progress*100:.1f}% of the $1,000 premium-rate zone filled</div>",unsafe_allow_html=True)

m1,m2,m3,m4,m5=st.columns(5)
m1.metric("CURRENT",f"${starting_balance:,.2f}");m2.metric("PER PAYCHECK",f"${deposit_amount}");m3.metric("10% ZONE LEFT",f"${max(1000-starting_balance,0):,.2f}");m4.metric("PROJECTED $1K",hit.strftime("%b %d, %Y") if hit else "Beyond model");m5.metric("INTEREST TO $1K",f"${interest_to_goal:,.2f}" if hit else "—")
if hit: st.markdown(f"<div class='status'>💥 <b>${deposit_amount} every {paycheck_days} days</b> projects to <strong>$1,000 on {hit.strftime('%B %d, %Y')}</strong> — about <b>{months:.1f} months</b>. Roughly <strong>${interest_to_goal:,.2f}</strong> of that climb comes from interest.</div>",unsafe_allow_html=True)

plan_tab,race_tab,next_tab,history_tab=st.tabs(["⚡ YOUR PLAN","🏁 DEPOSIT RACE","🚀 AFTER $1,000","🧾 ACTUAL HISTORY"])
with plan_tab:
    st.markdown("<div class='section'>Your Run to $1,000</div><div class='sub'>Bright cyan is your balance, orange dots are paycheck deposits, red is the $1,000 finish line.</div>",unsafe_allow_html=True)
    end=min(TODAY+timedelta(days=365*5),hit+timedelta(days=180) if hit else TODAY+timedelta(days=365*5));p=frame[frame["date"]<=end];deps=p[p["deposit"]>0]
    fig=go.Figure();fig.add_trace(go.Scatter(x=p["date"],y=p["balance"],mode="lines",name="Projected balance",line=dict(color="#55efff",width=6),fill="tozeroy",fillcolor="rgba(85,239,255,.22)"));fig.add_trace(go.Scatter(x=deps["date"],y=deps["balance"],mode="markers",name="Paycheck deposit",marker=dict(color=ORANGE,size=9,line=dict(color=YELLOW,width=2))));fig.add_hline(y=1000,line_dash="dash",line_color=RED,line_width=5,annotation_text="⚡ $1,000 PREMIUM ZONE FILLED",annotation_font_color="#fff200");chart_layout(fig);fig.update_yaxes(tickprefix="$");st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    gauge=go.Figure(go.Indicator(mode="gauge+number",value=min(starting_balance,1000),number={"prefix":"$","font":{"size":44,"color":"white"}},title={"text":"CURRENT PROGRESS TO $1,000","font":{"color":"white"}},gauge={"axis":{"range":[0,1000],"tickprefix":"$","tickcolor":"white"},"bar":{"color":"#55efff","thickness":.34},"bgcolor":"#075fd7","bordercolor":"#ffe600","steps":[{"range":[0,500],"color":"#0647aa"},{"range":[500,800],"color":"#7a28ce"},{"range":[800,1000],"color":"#ff6a00"}],"threshold":{"line":{"color":"#e51b23","width":7},"thickness":.9,"value":1000}}));gauge.update_layout(height=300,margin=dict(l=25,r=25,t=55,b=10),paper_bgcolor="rgba(0,0,0,0)",font_color="white");st.plotly_chart(gauge,use_container_width=True,config={"displayModeBar":False})
with race_tab:
    st.markdown("<div class='section'>How Much Faster if You Save More?</div><div class='sub'>Same vivid palette as the stock model — shorter bars mean faster to $1,000.</div>",unsafe_allow_html=True)
    amounts=sorted(set([5,10,15,20,25,30,40,50,75,100,125,150,int(deposit_amount)]));sc=deposit_scenarios(cfg,amounts);colors=[GREEN if a<25 else CYAN if a<50 else ORANGE if a<100 else RED for a in sc["amount"]]
    fig2=go.Figure(go.Bar(x=sc["amount"],y=sc["months_raw"],marker=dict(color=colors,line=dict(color=YELLOW,width=1)),text=sc["Months"].map(lambda x:f"{x:.1f} mo"),textposition="outside"));chart_layout(fig2,430);fig2.update_xaxes(title="Deposit each paycheck ($)");fig2.update_yaxes(title="Months to $1,000");st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False});st.dataframe(sc[["Deposit / Paycheck","Goal Date","Months","Interest"]],hide_index=True,use_container_width=True)
with next_tab:
    st.markdown("<div class='section'>Keep Capitalizing After $1,000</div><div class='sub'>Fill the ORSA premium zone, then keep the habit alive by redirecting future deposits.</div>",unsafe_allow_html=True)
    a,b=st.columns(2)
    with a: next_apy=st.number_input("Next account APY (%)",0.0,20.0,4.50,.10)
    with b: total_goal=st.number_input("Total cash-savings goal",1000.0,50000.0,5000.0,500.0)
    strategy=project_two_bucket(cfg,float(deposit_amount),next_apy/100,TODAY+timedelta(days=365*12));orsa_rows=strategy[strategy["ORSA"]>=1000];orsa_hit=None if orsa_rows.empty else orsa_rows.iloc[0]["date"];goal_rows=strategy[strategy["Total"]>=float(total_goal)];goal_hit=None if goal_rows.empty else goal_rows.iloc[0]["date"]
    q1,q2,q3,q4=st.columns(4);q1.metric("ORSA TARGET","$1,000");q2.metric("REDIRECT START",orsa_hit.strftime("%b %d, %Y") if orsa_hit else "—");q3.metric("TOTAL GOAL",f"${total_goal:,.0f}");q4.metric("GOAL DATE",goal_hit.strftime("%b %d, %Y") if goal_hit else "Beyond model")
    st.markdown("<div class='next'><span class='step'>1</span><b>Fill the 10% ORSA zone.</b></div><div class='next'><span class='step'>2</span><b>Redirect every new paycheck deposit.</b></div><div class='next'><span class='step'>3</span><b>Keep stacking toward the larger emergency fund.</b></div>",unsafe_allow_html=True)
    end2=min(TODAY+timedelta(days=365*6),goal_hit+timedelta(days=120) if goal_hit else TODAY+timedelta(days=365*6));s=strategy[strategy["date"]<=end2];fig3=go.Figure();fig3.add_trace(go.Scatter(x=s["date"],y=s["ORSA"],stackgroup="one",name="ORSA 10% bucket",line=dict(color=CYAN,width=3),fillcolor="rgba(85,239,255,.50)"));fig3.add_trace(go.Scatter(x=s["date"],y=s["Bucket #2"],stackgroup="one",name="Next HYSA bucket",line=dict(color=ORANGE,width=3),fillcolor="rgba(255,106,0,.55)"));fig3.add_hline(y=float(total_goal),line_dash="dot",line_color=YELLOW,line_width=4,annotation_text=f"🔥 ${total_goal:,.0f} TOTAL GOAL",annotation_font_color=YELLOW);chart_layout(fig3,470);fig3.update_yaxes(tickprefix="$");st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False});st.markdown("<div class='note'><b>Strategy:</b> once the 10% tier is full, change the destination — not the saving behavior.</div>",unsafe_allow_html=True)
with history_tab:
    st.markdown("<div class='section'>Actual ORSA History</div><div class='sub'>Real transactions remain separate from projections.</div>",unsafe_allow_html=True)
    p=Path("data/savings_transactions.csv")
    if p.exists():
        hist=pd.read_csv(p);hist["date"]=pd.to_datetime(hist["date"]);hist=hist.sort_values("date",ascending=False);st.dataframe(hist,hide_index=True,use_container_width=True);div=hist[hist["type"]=="dividend"].sort_values("date")
        if not div.empty:
            hc=[GREEN,CYAN,ORANGE,RED,PURPLE]*10;hf=go.Figure(go.Bar(x=div["date"],y=div["amount"],marker=dict(color=hc[:len(div)],line=dict(color=YELLOW,width=1)),text=div["amount"].map(lambda x:f"${x:.2f}"),textposition="outside"));chart_layout(hf,330);hf.update_yaxes(tickprefix="$");st.plotly_chart(hf,use_container_width=True,config={"displayModeBar":False})
st.markdown(f"<div class='caption' style='text-align:center;margin-top:20px'>High-Yield Savings Project v{APP_VERSION} • same trademark palette as the stock/mobile app</div>",unsafe_allow_html=True)
