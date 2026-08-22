"""Beginner-first mobile web experience for the AI stock research model."""
from __future__ import annotations
import json
from pathlib import Path
import streamlit as st

APP_VERSION = "2.2-beta"
COMPANY_NAMES = {
    "NVDA": "NVIDIA", "MSFT": "Microsoft", "AVGO": "Broadcom", "PLTR": "Palantir",
    "AMD": "AMD", "GOOGL": "Alphabet", "AMZN": "Amazon", "META": "Meta",
    "ORCL": "Oracle", "TSM": "TSMC", "ASML": "ASML", "ARM": "Arm",
    "CRWD": "CrowdStrike", "PANW": "Palo Alto Networks", "ANET": "Arista Networks",
    "VRT": "Vertiv", "SNOW": "Snowflake", "DDOG": "Datadog", "NET": "Cloudflare",
    "NOW": "ServiceNow", "MDB": "MongoDB", "PATH": "UiPath", "MU": "Micron",
    "AMAT": "Applied Materials", "MRVL": "Marvell", "DELL": "Dell",
    "SMCI": "Super Micro Computer", "CRDO": "Credo Technology", "TER": "Teradyne",
    "ACMR": "ACM Research",
}
AI_ROLES = {
    "NVDA": "Builds the GPUs and computing platforms used to train and run many AI systems.",
    "MSFT": "Provides Azure cloud infrastructure and AI software used by businesses worldwide.",
    "AVGO": "Supplies networking and custom chips used in large AI data centers.",
    "PLTR": "Builds enterprise software that helps organizations use data and AI in operations.",
    "AMD": "Competes in AI accelerators, CPUs and data-center computing.",
    "GOOGL": "Operates Google Cloud and develops AI models, chips and consumer AI products.",
    "AMZN": "Provides AI infrastructure and services through Amazon Web Services.",
    "META": "Uses AI across advertising, recommendation systems and its open-source Llama models.",
    "ORCL": "Provides cloud infrastructure and databases increasingly used for AI workloads.",
    "TSM": "Manufactures many of the advanced chips used by leading AI companies.",
    "ASML": "Makes the lithography machines required to manufacture advanced semiconductors.",
}

st.set_page_config(page_title="AI Stocks Made Simple", page_icon="🤖", layout="centered")

st.markdown("# 🤖 AI Stocks Made Simple")
st.markdown("### A simpler way to understand the companies powering artificial intelligence.")
st.caption(f"{APP_VERSION} • Educational research only • No trades are placed • Not personalized investment advice")

rank_dir = Path("data/historical/rankings")
files = sorted(rank_dir.glob("*.json")) if rank_dir.exists() else []
latest_file = files[-1] if files else None
rows = json.loads(latest_file.read_text(encoding="utf-8")) if latest_file else []

if rows:
    latest_date = latest_file.stem
    st.success(f"Latest model snapshot: {latest_date}")
else:
    st.info("The first live ranking snapshot has not been saved yet. The learning sections below are still available.")

nav = st.radio(
    "Choose a section",
    ["🏆 Top AI Stocks", "💵 Start Small", "🎓 Learn", "🔎 How the Model Works"],
    horizontal=False,
    label_visibility="collapsed",
)

if nav == "🏆 Top AI Stocks":
    st.markdown("## Today's highest-ranked AI stocks")
    st.write("The model compares the same evidence categories across the entire AI-stock universe. Higher scores mean the current evidence fits the model better—not that a stock is guaranteed to rise.")
    amount = st.select_slider(
        "Learning amount",
        options=[5, 10, 25, 50, 100],
        value=10,
        format_func=lambda x: f"${x}",
    )

    if rows:
        for row in rows[:5]:
            ticker = row["ticker"]
            name = COMPANY_NAMES.get(ticker, ticker)
            score = float(row["score"])
            price = row.get("price")
            risk = str(row.get("risk", "Unknown")).title()
            confidence = float(row.get("confidence", 0) or 0)
            ret = row.get("return_since_experiment_start")
            classification = row.get("classification", "Research")

            with st.container(border=True):
                st.markdown(f"### #{row['rank']} {name} ({ticker})")
                st.markdown(f"**Model score: {score:.1f}/100 · {classification}**")
                st.progress(max(0.0, min(score / 100.0, 1.0)))
                metrics = st.columns(3)
                metrics[0].metric("Risk", risk)
                metrics[1].metric("Data confidence", f"{confidence:.0f}%")
                metrics[2].metric("Since Aug. 14", "—" if ret is None else f"{ret:+.1%}")

                st.write(AI_ROLES.get(ticker, "Participates in the AI ecosystem through semiconductors, cloud, software, infrastructure or related technology."))

                if price:
                    shares = amount / float(price)
                    st.markdown(f"**Small-dollar example:** ${amount} ÷ ${float(price):.2f} ≈ **{shares:.4f} shares**")
                    st.caption("This is math for learning only. Fractional-share availability varies by brokerage.")

                with st.expander("Why can this ranking change?"):
                    st.write("Scores can move when revenue growth, earnings, cash flow, valuation, momentum, ownership data, documented catalysts, competitive position or other model inputs change.")
    else:
        st.warning("No live rankings are available yet, so the app will not invent a Top 5 list.")

elif nav == "💵 Start Small":
    st.markdown("## Learn with small numbers first")
    st.write("A beginner does not need to think in whole-share prices. Many brokerages support fractional shares, which makes it easier to understand what $5, $10, $25, $50 or $100 represents.")
    amount = st.select_slider("Choose an example amount", [5, 10, 25, 50, 100], value=10, format_func=lambda x: f"${x}")

    if rows:
        st.markdown("### What that amount looks like across today's Top 5")
        for row in rows[:5]:
            price = row.get("price")
            if not price:
                continue
            ticker = row["ticker"]
            st.write(f"**{COMPANY_NAMES.get(ticker, ticker)} ({ticker})** — about {amount/float(price):.4f} shares at ${float(price):.2f}/share")
    else:
        st.write("Once a live ranking is saved, this section will automatically calculate fractional-share examples across the Top 5.")

    st.markdown("### Three beginner rules")
    st.write("1. Small does not mean risk-free. A $10 stock investment can still lose value.")
    st.write("2. A high model score is research evidence, not a promise or guarantee.")
    st.write("3. Money needed for bills, emergencies or near-term obligations should not be treated like experimental investing money.")

elif nav == "🎓 Learn":
    st.markdown("## AI investing in plain English")
    with st.expander("What is an AI stock?", expanded=True):
        st.write("A public company whose products or services materially participate in artificial intelligence. That can include chips, cloud computing, data centers, networking, databases, cybersecurity and AI software—not just companies that build chatbots.")
    with st.expander("Why not just buy the stock that went up the most?"):
        st.write("Past price movement is only one input. The model also checks business growth, profits and cash flow, financial strength, valuation and other evidence so momentum does not dominate the decision.")
    with st.expander("What is valuation?"):
        st.write("Valuation asks how much investors are paying for the company's profits, sales and cash flow. A great business can still be an expensive stock.")
    with st.expander("What is momentum?"):
        st.write("Momentum measures recent price trends. Strong momentum can be useful evidence, but the model caps its influence so a rapidly rising stock cannot win on hype alone.")
    with st.expander("What does data confidence mean?"):
        st.write("Confidence measures how complete and trustworthy the available inputs are. It is separate from the investment score. A stock can look attractive while still having incomplete data.")
    with st.expander("Why diversify?"):
        st.write("Owning only one company exposes you to company-specific risk. Diversification spreads risk across multiple investments, although it cannot eliminate market losses.")

elif nav == "🔎 How the Model Works":
    st.markdown("## The 100-point research model")
    categories = [
        ("Revenue Growth", 15, "How quickly the business is growing sales."),
        ("Earnings / Free Cash Flow", 15, "Profitability and real cash generation."),
        ("Industry Growth", 15, "How attractive the company's broader market opportunity is."),
        ("Balance Sheet", 10, "Cash, debt and financial durability."),
        ("Valuation", 10, "How expensive the stock is relative to earnings, sales and cash flow."),
        ("Competitive Advantage", 10, "Evidence of a durable moat or strategic advantage."),
        ("Momentum", 10, "Price trend across multiple time windows."),
        ("Insider / Institutional", 5, "Ownership-related evidence."),
        ("Catalysts", 5, "Documented events that could materially affect the business."),
        ("Inflation Resilience", 5, "Evidence of pricing power and resilience."),
    ]
    for title, points, description in categories:
        st.markdown(f"**{title} — {points} points**")
        st.caption(description)

    st.markdown("### What the model deliberately does not do")
    st.write("• It does not award bonus points just because a stock has a low share price.")
    st.write("• It does not guarantee future returns.")
    st.write("• It does not know your income, debts, emergency savings, goals or risk tolerance.")
    st.write("• It does not place trades or connect to a brokerage account.")

st.divider()
st.caption("AI Stocks Made Simple is a beginner-facing educational interface powered by the Stock Investment Model. Rankings are research outputs, not individualized recommendations. Stocks can lose value.")
