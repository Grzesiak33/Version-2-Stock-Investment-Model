"""Beginner-first mobile web experience for the AI stock research model."""
from __future__ import annotations
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="AI Stocks Made Simple", page_icon="🤖", layout="centered")

st.markdown("# 🤖 AI Stocks Made Simple")
st.markdown("### Understand AI investing without learning Wall Street first.")
st.caption("Educational research tool • Not personalized investment advice • No trades are placed")

amount = st.select_slider("If I wanted to learn with a small amount", options=[5, 10, 25, 50, 100], value=10, format_func=lambda x: f"${x}")

rank_dir = Path("data/historical/rankings")
files = sorted(rank_dir.glob("*.json")) if rank_dir.exists() else []
rows = json.loads(files[-1].read_text()) if files else []

if rows:
    st.markdown("## 🏆 Today's AI Stock Rankings")
    for row in rows[:5]:
        ticker = row["ticker"]
        score = row["score"]
        price = row.get("price")
        risk = row.get("risk", "Unknown")
        confidence = row.get("confidence", 0)
        ret = row.get("return_since_experiment_start")
        with st.container(border=True):
            st.markdown(f"### #{row['rank']}  {ticker} — {score:.1f}/100")
            cols = st.columns(3)
            cols[0].metric("Risk", str(risk).title())
            cols[1].metric("Data confidence", f"{confidence:.0f}%")
            cols[2].metric("Since Aug. 14", "—" if ret is None else f"{ret:+.1%}")
            if price:
                st.write(f"**Learning example:** ${amount} is about {amount/price:.4f} shares at ${price:.2f}/share. Fractional-share availability depends on the brokerage.")
            st.caption("The ranking combines growth, financial quality, valuation, momentum and documented qualitative research. It is not a promise of future returns.")
else:
    st.info("The first live Version 2.1 ranking is being generated. Once saved, the top five AI stocks will appear here automatically.")

st.markdown("## 💵 Start Small")
st.write("You do not need to buy a whole share to learn about investing. Many brokerages support fractional shares, so examples in this app use simple $5–$100 amounts.")

st.markdown("## 🎓 Learn Before You Invest")
with st.expander("What is an AI stock?"):
    st.write("A public company whose products or services materially participate in artificial intelligence—such as chips, cloud computing, data centers, software, networking or cybersecurity.")
with st.expander("What does the score mean?"):
    st.write("The model scores companies from 0–100 across ten categories. Higher means the evidence currently fits the model better; it does not mean the stock is guaranteed to rise.")
with st.expander("Why can a great company rank lower?"):
    st.write("Price matters. A fast-growing company can still rank lower when its valuation is extremely expensive, its momentum weakens, its balance sheet deteriorates or the available data is incomplete.")
with st.expander("What should a beginner remember?"):
    st.write("Stocks can lose money. Start with education, avoid investing money needed for bills or emergencies, understand diversification, and verify information before making your own decision.")

st.divider()
st.caption("AI Stocks Made Simple is an educational research interface powered by the Version 2.1 quantitative model. It does not know your personal finances, risk tolerance or investment objectives and does not provide individualized recommendations.")
