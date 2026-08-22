"""AI Stocks Made Simple - neon mobile dashboard + live Top 20 + flexible recurring-investment simulator."""
from __future__ import annotations
import calendar,json
from datetime import date,timedelta
from pathlib import Path
import pandas as pd
import streamlit as st
import yfinance as yf

APP_VERSION="2.2.5-beta"; ROBINHOOD_REFERRAL_URL="https://join.robinhood.com/steveng-15bac4"
UNIVERSE=["NVDA","MSFT","AVGO","PLTR","AMD","GOOGL","AMZN","META","ORCL","TSM","ASML","ARM","CRWD","PANW","ANET","VRT","SNOW","DDOG","NET","NOW","MDB","PATH","MU","AMAT","MRVL","DELL","SMCI","CRDO","TER","ACMR"]
NAMES=dict(zip(UNIVERSE,["NVIDIA","Microsoft","Broadcom","Palantir","AMD","Alphabet","Amazon","Meta","Oracle","TSMC","ASML","Arm","CrowdStrike","Palo Alto Networks","Arista Networks","Vertiv","Snowflake","Datadog","Cloudflare","ServiceNow","MongoDB","UiPath","Micron","Applied Materials","Marvell","Dell","Super Micro Computer","Credo","Teradyne","ACM Research"]))
DOMAINS=dict(zip(UNIVERSE,["nvidia.com","microsoft.com","broadcom.com","palantir.com","amd.com","google.com","amazon.com","meta.com","oracle.com","tsmc.com","asml.com","arm.com","crowdstrike.com","paloaltonetworks.com","arista.com","vertiv.com","snowflake.com","datadoghq.com","cloudflare.com","servicenow.com","mongodb.com","uipath.com","micron.com","appliedmaterials.com","marvell.com","dell.com","supermicro.com","credosemi.com","teradyne.com","acmrcsh.com"]))

st.set_page_config(page_title="AI Stocks Made Simple",page_icon="⚡",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
header[data-testid='stHeader']{background:transparent}.stApp{background:#030812;color:#eef7ff}.block-container{max-width:1050px;padding-top:1rem;padding-bottom:5rem}.hero{border:1px solid #17365f;border-radius:26px;padding:24px;background:radial-gradient(circle at 12% 35%,#f9731644,transparent 28%),radial-gradient(circle at 82% 25%,#2563eb66,transparent 30%),linear-gradient(135deg,#02050c,#071b38 52%,#16072e);box-shadow:0 0 35px #0ea5e933}.hero-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:14px;align-items:center}.brand{font-size:.82rem;letter-spacing:.22em;color:#9fb6d3;font-weight:800}.hero h1{font-size:clamp(2.4rem,8vw,5rem);line-height:.9;margin:.35rem 0;background:linear-gradient(90deg,#16d9ff,#6d7cff,#d946ef);-webkit-background-clip:text;color:transparent;font-style:italic}.tag{font-size:clamp(1.2rem,4vw,2.1rem);font-weight:900;font-style:italic}.cyan{color:#22d3ee}.pink{color:#d946ef}.orange{color:#fb923c}.pick{display:inline-block;margin-top:14px;padding:10px 15px;border:1px solid #1d4ed8;border-radius:12px;background:#07152dcc;box-shadow:0 0 18px #2563eb55;font-weight:800}.mascot{text-align:center;font-size:5.5rem}.mascot small{display:block;font-size:.8rem;color:#9fb6d3}.status-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:14px 0}.status,.panel,.tile{background:linear-gradient(180deg,#071424,#050b14);border:1px solid #17365f;border-radius:16px;padding:14px}.status b{display:block;font-size:.7rem;color:#9fb6d3}.status strong{font-size:1.1rem}.panel{margin:12px 0}.stockrow{display:grid;grid-template-columns:2.2fr .8fr .9fr .9fr;gap:8px;align-items:center;padding:12px 5px;border-bottom:1px solid #13233a}.stockname{font-weight:900}.ticker,.fine{font-size:.75rem;color:#7890ac}.logo{width:34px;height:34px;border-radius:8px;background:white;padding:3px;vertical-align:middle;margin-right:8px}.score{display:inline-grid;place-items:center;width:48px;height:48px;border-radius:50%;border:4px solid #22c55e;color:#4ade80;font-weight:900;box-shadow:0 0 15px #22c55e66}.up{color:#4ade80;font-weight:800}.down{color:#fb7185;font-weight:800}.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.tile{min-height:140px}.purple{border-color:#9333ea}.blue{border-color:#0ea5e9}.green{border-color:#22c55e}.gold{border-color:#f59e0b}.simhero{padding:18px;border-radius:20px;background:radial-gradient(circle at 10% 10%,#ec489955,transparent 30%),linear-gradient(120deg,#24104d,#07345b,#4a1d08);border:1px solid #a855f7;box-shadow:0 0 28px #9333ea33}.logo-grid-title{margin-top:16px;font-weight:900;color:#22d3ee}.select-card{background:linear-gradient(180deg,#071424,#050b14);border:1px solid #17365f;border-radius:16px;padding:8px;text-align:center}.result-card{background:linear-gradient(135deg,#052e16,#063354);border:1px solid #22c55e;border-radius:20px;padding:18px;margin:14px 0}.sponsor{padding:18px;border-radius:18px;background:linear-gradient(120deg,#052e16,#0b1d32);border:1px solid #22c55e}.stTabs [data-baseweb='tab']{background:#07111f;border:1px solid #17365f;border-radius:12px;font-weight:800}.stMetric{background:#07111f;border:1px solid #17365f;padding:10px;border-radius:12px}.stButton>button,.stLinkButton>a{border-radius:14px!important;min-height:44px}.footer-nav{position:fixed;bottom:8px;left:50%;transform:translateX(-50%);z-index:999;width:min(94%,760px);display:flex;justify-content:space-around;background:#07111ff2;border:1px solid #17365f;border-radius:18px;padding:10px}.footer-nav span{color:#9fb6d3;font-size:.72rem;text-align:center}.footer-nav b{display:block;font-size:1.2rem;color:#22d3ee}@media(max-width:760px){.hero-grid{grid-template-columns:1fr .4fr}.mascot{font-size:4rem}.status-grid,.tiles{grid-template-columns:repeat(2,1fr)}.stockrow{grid-template-columns:2fr .7fr .8fr}.hide-mobile{display:none}.block-container{padding-left:.7rem;padding-right:.7rem}.stTabs [data-baseweb='tab']{font-size:10px}}</style>""",unsafe_allow_html=True)

@st.cache_data(ttl=300,show_spinner=False)
def live_market(tickers):
 out={}
 try:
  raw=yf.download(list(tickers),period="6mo",interval="1d",group_by="ticker",auto_adjust=False,progress=False,threads=True)
  for t in tickers:
   try:
    close=raw[t]["Close"].dropna();p=float(close.iloc[-1]);prev=float(close.iloc[-2]);m=float(close.iloc[-22]) if len(close)>=22 else float(close.iloc[0]);out[t]={"price":p,"day":p/prev-1,"month":p/m-1}
   except:pass
 except:pass
 return out

def model_rows():
 p=Path("data/historical/rankings");fs=sorted(p.glob("*.json")) if p.exists() else []
 if not fs:return [],None
 try:return json.loads(fs[-1].read_text()),fs[-1].stem
 except:return [],None

def logo(t):return f"https://www.google.com/s2/favicons?domain={DOMAINS[t]}&sz=64"
def next_friday(d):return d+timedelta(days=(4-d.weekday())%7)
def schedule_dates(start,end,freq,custom_days=14):
 dates=[];d=start
 if freq=="Every Friday":d=next_friday(start)
 while d<=end:
  dates.append(d)
  if freq=="Every Friday":d+=timedelta(days=7)
  elif freq in ("Every 2 weeks","Every payday (2 weeks)"):d+=timedelta(days=14)
  elif freq=="Every month":
   y,m=d.year,d.month+1
   if m==13:y,m=y+1,1
   d=date(y,m,min(d.day,calendar.monthrange(y,m)[1]))
  else:d+=timedelta(days=max(1,int(custom_days)))
 return dates

rows,snap=model_rows();market=live_market(tuple(UNIVERSE));rankmap={r.get("ticker"):r for r in rows};ranked=[t for t in UNIVERSE if t in market];ranked.sort(key=lambda t:(rankmap.get(t,{}).get("rank",999),-market[t]["month"]));conf=sum(float(r.get("confidence",0) or 0) for r in rows)/len(rows) if rows else 0;avg=sum(x["day"] for x in market.values())/len(market) if market else 0;mood="BULLISH" if avg>.003 else "BEARISH" if avg<-.003 else "MIXED"

st.markdown("""<div class='hero'><div class='hero-grid'><div><div class='brand'>AI STOCKS MADE SIMPLE</div><h1>AI STOCKS<br>MADE SIMPLE</h1><div class='tag'><span class='cyan'>AI POWERED.</span><br><span class='pink'>DATA DRIVEN.</span><br>SMARTER RESEARCH.</div><div class='pick'>◆ LIVE AI STOCK RANKINGS<br><span class='fine'>START SMALL • BUILD A ROUTINE • SEE THE MATH</span></div></div><div class='mascot'>👨🏽‍💻<div>🐍👓 🥤</div><small>Your AI guide<br>Python + Red Pop energy</small></div></div></div>""",unsafe_allow_html=True)
st.markdown(f"<div class='status-grid'><div class='status'><b>MARKET STATUS</b><strong class='up'>{mood}</strong><br><span class='fine'>AI universe today</span></div><div class='status'><b>LAST UPDATED</b><strong>{date.today():%b %d, %Y}</strong><br><span class='fine'>5 minute cache</span></div><div class='status'><b>MODEL VERSION</b><strong class='cyan'>{APP_VERSION}</strong><br><span class='fine'>Scoring engine</span></div><div class='status'><b>DATA CONFIDENCE</b><strong class='orange'>{conf:.0f}%</strong><br><span class='fine'>Latest snapshot</span></div></div>",unsafe_allow_html=True)

top,sim,learn,model,sponsor=st.tabs(["🏠 HOME / TOP 20","💵 BUILD MY PLAN","🎓 LEARN","⚙️ MODEL","💚 SPONSOR"])
with top:
 st.markdown("<div class='panel'><h2>TOP AI STOCKS TODAY</h2><div class='fine'>Real market prices + latest model ranking. Use the Build My Plan tab to simulate recurring deposits.</div>",unsafe_allow_html=True)
 if not market:st.error("Live market data is temporarily unavailable.")
 for i,t in enumerate(ranked[:20],1):
  m=market[t];score=rankmap.get(t,{}).get("score");trend=m["month"];scorehtml=f"<span class='score'>{round(float(score))}</span>" if score is not None else "<span class='ticker'>pending</span>"
  st.markdown(f"<div class='stockrow'><div><b style='color:#facc15'>#{i}</b> <img class='logo' src='{logo(t)}'><span class='stockname'>{NAMES[t]}</span><div class='ticker'>{t}</div></div><div>{scorehtml}</div><div class='{'up' if trend>=0 else 'down'}'>{trend:+.1%}<div class='ticker'>1 month</div></div><div class='hide-mobile'><b>${m['price']:,.2f}</b><div class='{'up' if m['day']>=0 else 'down'}'>{m['day']:+.2%}</div></div></div>",unsafe_allow_html=True)
 st.markdown("</div><div class='tiles'><div class='tile purple'><h3 class='pink'>🚀 START SMALL</h3><p>$5 or $10 at a time. Fractional shares made simple.</p></div><div class='tile blue'><h3 class='cyan'>🧠 LEARN</h3><p>AI & investing 101 in plain English.</p></div><div class='tile green'><h3 class='up'>🎯 BUILD A ROUTINE</h3><p>Weekly, every payday, bi-weekly or monthly.</p></div><div class='tile gold'><h3 class='orange'>🛡️ RISK FIRST</h3><p>Stocks can fall. The simulator is not a guarantee.</p></div></div>",unsafe_allow_html=True)

with sim:
 st.markdown("<div class='simhero'><h2>💵 BUILD MY INVESTING PLAN</h2><p>1. Tap a stock. 2. Enter your deposit. 3. Pick how often. 4. Pick an end date. 5. See how many shares that routine could accumulate using today's price.</p></div>",unsafe_allow_html=True)
 avail=ranked[:20] or UNIVERSE[:20]
 if "plan_stock" not in st.session_state:st.session_state.plan_stock="NVDA" if "NVDA" in avail else avail[0]
 st.markdown("<div class='logo-grid-title'>1️⃣ Pick your stock</div>",unsafe_allow_html=True)
 featured=[t for t in ["NVDA","MSFT","GOOGL","AMZN","META","AMD","AVGO","PLTR"] if t in avail]
 cols=st.columns(4)
 for i,t in enumerate(featured):
  with cols[i%4]:
   st.image(logo(t),width=54)
   if st.button(f"{NAMES[t]}\n{t}",key=f"pick_{t}",use_container_width=True):st.session_state.plan_stock=t
 selected=st.selectbox("Or choose any Top 20 AI stock",avail,index=avail.index(st.session_state.plan_stock) if st.session_state.plan_stock in avail else 0,format_func=lambda x:f"{NAMES[x]} ({x})")
 if selected!=st.session_state.plan_stock:st.session_state.plan_stock=selected
 selected=st.session_state.plan_stock; price=market.get(selected,{}).get("price")
 if price:st.success(f"Selected: {NAMES[selected]} ({selected}) • today's market price used in this illustration: ${price:,.2f}")
 st.markdown("<div class='logo-grid-title'>2️⃣ Set your automatic-deposit routine</div>",unsafe_allow_html=True)
 c1,c2=st.columns(2);amount=c1.number_input("Deposit amount",min_value=1.0,max_value=10000.0,value=10.0,step=5.0,format="$%.2f");freq=c2.selectbox("How often?",["Every 2 weeks","Every Friday","Every payday (2 weeks)","Every month","Custom number of days"])
 custom=14
 if freq=="Custom number of days":custom=st.number_input("Deposit every how many days?",min_value=1,max_value=365,value=14,step=1)
 default_start=next_friday(date.today());d1,d2=st.columns(2);start=d1.date_input("Start date",value=default_start);end=d2.date_input("End date",value=date(2026,12,31),min_value=date.today())
 rotation=st.toggle("Advanced: rotate through 3 stocks instead of buying one stock")
 B=C=None
 if rotation:
  r1,r2=st.columns(2);B=r1.selectbox("Stock B",avail,index=avail.index("MSFT") if "MSFT" in avail else min(1,len(avail)-1),format_func=lambda x:f"{NAMES[x]} ({x})");C=r2.selectbox("Stock C",avail,index=avail.index("GOOGL") if "GOOGL" in avail else min(2,len(avail)-1),format_func=lambda x:f"{NAMES[x]} ({x})")
 if end<start:st.warning("End date must be after the start date.")
 elif st.button("⚡ SHOW ME HOW THIS ADDS UP",type="primary",use_container_width=True):
  dates=schedule_dates(start,end,freq,custom);picks=[selected,B,C] if rotation else [selected];picks=[x for x in picks if x];shares={t:0.0 for t in set(picks)};invested={t:0.0 for t in set(picks)};ledger=[]
  for i,d in enumerate(dates):
   t=picks[i%len(picks)];p=market.get(t,{}).get("price")
   if not p:continue
   qty=amount/p;shares[t]+=qty;invested[t]+=amount;ledger.append({"Deposit date":d,"Stock":t,"Deposit":amount,"Today's price used":p,"Shares added":qty})
  total=sum(invested.values());value=sum(shares[t]*market.get(t,{}).get("price",0) for t in shares)
  st.markdown(f"<div class='result-card'><h2>📈 Your simulated plan through {end:%b %d, %Y}</h2><p>Using today's price for each scheduled purchase, your routine makes <b>{len(dates)} deposits</b>.</p></div>",unsafe_allow_html=True)
  k1,k2,k3=st.columns(3);k1.metric("Automatic deposits",f"${total:,.2f}");k2.metric("Shares accumulated",f"{sum(shares.values()):.4f}");k3.metric("Value at today's prices",f"${value:,.2f}")
  summary=pd.DataFrame([{"Stock":f"{NAMES[t]} ({t})","Deposited":invested[t],"Shares accumulated":shares[t],"Today's price":market.get(t,{}).get("price",0),"Value at today's price":shares[t]*market.get(t,{}).get("price",0)} for t in shares]);st.dataframe(summary,use_container_width=True,hide_index=True)
  if ledger:
   ldf=pd.DataFrame(ledger);st.area_chart(ldf.groupby("Deposit date")["Deposit"].sum().cumsum(),height=240)
   if not rotation:st.success(f"If you deposited ${amount:,.2f} into {NAMES[selected]} on this schedule through {end:%b %d, %Y}, the plan would contribute ${total:,.2f} and accumulate about {shares[selected]:.4f} shares using today's ${market[selected]['price']:,.2f} price for the illustration.")
   else:st.success("Your deposits rotate through "+" → ".join(picks)+" and repeat for each scheduled contribution.")
   with st.expander("See every scheduled deposit"):st.dataframe(ldf,use_container_width=True,hide_index=True)
  st.info("Important: future stock prices will not stay fixed. The dollar value shown above uses today's market price for every future purchase so you can clearly see the deposit/share accumulation. Actual future account value can be higher or lower.")

with learn:
 st.header("🎓 Learn without Wall Street jargon")
 for q,a in [("What is an AI stock?","A company materially involved in AI chips, cloud, data centers, networking, cybersecurity, databases or AI software."),("Why recurring deposits?","A recurring schedule can make investing easier to budget and removes the need to remember every purchase. It does not prevent losses."),("What is a fractional share?","Part of one share. It can allow a $5 or $10 purchase even when a whole share costs hundreds, if the brokerage supports fractional shares.")]:
  with st.expander(q):st.write(a)
with model:
 st.header("⚙️ The 100-point model")
 for n,p in [("Revenue Growth",15),("Earnings / Free Cash Flow",15),("Industry Growth",15),("Balance Sheet",10),("Valuation",10),("Competitive Advantage",10),("Momentum",10),("Insider / Institutional",5),("Catalysts",5),("Inflation Resilience",5)]:st.progress(p/15,text=f"{n} — {p} points")
 st.caption(f"Latest model snapshot: {snap or 'pending'}")
with sponsor:
 st.markdown("<div class='sponsor'><b>SPONSORED / REFERRAL</b><h2>Robinhood</h2><p>Optional brokerage referral. Sponsorship never changes rankings, scores or simulations.</p></div>",unsafe_allow_html=True);st.link_button("Open my Robinhood referral",ROBINHOOD_REFERRAL_URL,use_container_width=True,type="primary");st.caption("Disclosure: I may receive a referral reward if you sign up or qualify through this link. It does not affect rankings or research.")
st.markdown("<div class='footer-nav'><span><b>⌂</b>HOME</span><span><b>☷</b>TOP 20</span><span><b>◔</b>BUILD PLAN</span><span><b>♟</b>LEARN</span><span><b>⚙</b>MODEL</span></div>",unsafe_allow_html=True);st.caption("Educational research only. No personalized investment advice. No trades are placed. Stocks can lose value. Market data may be delayed.")