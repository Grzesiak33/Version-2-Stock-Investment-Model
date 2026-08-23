from __future__ import annotations
from datetime import date, timedelta
import streamlit as st


def render_plan_builder(stocks):
    st.markdown("""
    <style>
    .v34{margin:.55rem 0;padding:18px;border:1px solid #7c3aed;border-radius:22px;background:radial-gradient(circle at 8% 10%,#ec489933,transparent 25%),radial-gradient(circle at 90% 10%,#0ea5e933,transparent 28%),linear-gradient(135deg,#13072c,#071a34 55%,#07111f)}
    .v34 h2{margin:0;color:white;font-size:1.65rem}.v34 p{color:#a9bdd2;margin:.3rem 0 0}.big-result{font-size:1.7rem;font-weight:900;color:#22d3ee}.scenario{padding:12px;border:1px solid #244e80;border-radius:14px;background:#06101d;margin:5px 0}.scenario b{color:#e879f9}.tiny{color:#8fa6bf;font-size:.75rem}
    </style><div class='v34'><h2>✨ BUILD MY AI PLAN</h2><p>Tell us what fits your payday. Build a simple rotation, then compare illustrative growth scenarios.</p></div>
    """, unsafe_allow_html=True)

    if not stocks:
        return
    tickers=[s['ticker'] for s in stocks]
    lookup={s['ticker']:s for s in stocks}
    c1,c2=st.columns(2)
    with c1:
        budget=st.number_input("Amount per payday", min_value=1.0, value=10.0, step=5.0, key="v34_budget")
        frequency=st.selectbox("How often?", ["Every 2 weeks","Every week","Monthly"], key="v34_freq")
    with c2:
        start=st.date_input("Start date", value=date.today(), key="v34_start")
        end=st.date_input("Target date", value=date(2026,12,31), key="v34_end")

    risk=st.segmented_control("How should the sample plan feel?", ["Steady","Balanced","Aggressive"], default="Balanced", key="v34_risk")
    default_n=3 if risk!="Steady" else 2
    chosen=st.multiselect("Choose 2–5 AI stocks for your rotation", tickers, default=tickers[:default_n], max_selections=5, key="v34_stocks")
    st.caption("Rotation follows the order shown above. Your existing detailed Rotation Mode remains available below.")

    scenario=st.segmented_control("Projection view", ["No Growth","Moderate 5%","Growth 10%"], default="Moderate 5%", key="v34_scenario")
    rates={"No Growth":0.0,"Moderate 5%":0.05,"Growth 10%":0.10}
    days={"Every 2 weeks":14,"Every week":7,"Monthly":30}[frequency]

    if st.button("BUILD MY PLAN →", type="primary", use_container_width=True, key="v34_go"):
        if len(chosen)<2:
            st.warning("Choose at least two stocks for a rotation plan.")
            return
        if end < start:
            st.warning("Target date must be after the start date.")
            return
        dates=[]; d=start
        while d<=end:
            dates.append(d); d+=timedelta(days=days)
        rate=rates[scenario]
        by={t:{"contrib":0.0,"shares":0.0,"buys":0,"future":0.0} for t in chosen}
        total_future=0.0
        for i,d in enumerate(dates):
            t=chosen[i%len(chosen)]; s=lookup[t]; years=max((end-d).days,0)/365.25
            future=budget*((1+rate)**years)
            by[t]["contrib"]+=budget; by[t]["shares"]+=budget/max(s['price'],.01); by[t]["buys"]+=1; by[t]["future"]+=future; total_future+=future
        contributed=budget*len(dates)
        a,b,c=st.columns(3)
        a.metric("YOU PUT IN", f"${contributed:,.2f}")
        b.metric("PAYDAYS INVESTED", f"{len(dates)}")
        c.metric("ILLUSTRATIVE VALUE", f"${total_future:,.2f}", f"${total_future-contributed:,.2f} scenario growth")
        st.markdown(f"<div class='scenario'><b>{scenario}</b><br><span class='tiny'>Illustration only. This applies a constant annual rate to each contribution; it is not a prediction of any stock's future return.</span></div>", unsafe_allow_html=True)
        st.subheader("Your rotation")
        st.markdown(" → ".join(f"**{t}**" for t in chosen)+" → repeat")
        for t in chosen:
            x=by[t]; s=lookup[t]
            st.write(f"**{s['name']} ({t})** — {x['buys']} buys • ${x['contrib']:,.2f} contributed • {x['shares']:.4f} shares at today's displayed price")
        st.subheader("Next paychecks")
        for i,d in enumerate(dates[:8]):
            t=chosen[i%len(chosen)]
            st.write(f"**{d.strftime('%b %d, %Y')}**  →  ${budget:,.2f} of **{t}**")
        st.caption("Educational planning tool only. Prices can change, returns are not guaranteed, and this is not individualized investment advice.")
