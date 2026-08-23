from __future__ import annotations
import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

APP_VERSION = "3.2.0"

st.set_page_config(page_title="AI Stocks Made Simple", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.block-container{padding:.55rem .55rem 0!important;max-width:960px!important}
.stApp{background:#020711}header,footer{visibility:hidden}
[data-testid="stImage"] img{border-radius:24px;border:1px solid #244e80;box-shadow:0 0 28px #0ea5e92b;background:#020711}
.hero-copy{border:1px solid #244e80;border-radius:24px;padding:20px;background:radial-gradient(circle at 20% 20%,#ff7a1835,transparent 28%),radial-gradient(circle at 80% 10%,#2563eb50,transparent 35%),linear-gradient(135deg,#02050c,#071b38 52%,#18072e);min-height:100%}
.hero-title{font-size:clamp(2.5rem,7vw,4.7rem);font-weight:1000;line-height:.88;font-style:italic;margin:.35rem 0;background:linear-gradient(90deg,#22d3ee,#818cf8,#e879f9);-webkit-background-clip:text;color:transparent}.hero-sub{font-size:clamp(1.1rem,3vw,1.8rem);font-weight:950;font-style:italic;color:white}.eyebrow{font-size:.72rem;letter-spacing:.2em;color:#9fb4ce;font-weight:900}.cyan{color:#22d3ee}.pink{color:#e879f9}.fine{font-size:.78rem;color:#91a7c0}.callout{margin-top:14px;border:1px solid #1d4ed8;border-radius:13px;background:#07152ddd;padding:11px;color:white;font-weight:900}.snake{margin-top:9px;border:1px solid #22d3ee;border-radius:12px;background:#061727;padding:9px;text-align:center;color:white;font-weight:900}
</style>
""", unsafe_allow_html=True)

# Latest saved ranking snapshot: no network call during startup.
def latest_snapshot():
    p = Path("data/historical/rankings")
    files = sorted(p.glob("*.json")) if p.exists() else []
    if not files:
        return [], "unavailable"
    try:
        return json.loads(files[-1].read_text(encoding="utf-8")), files[-1].stem
    except Exception:
        return [], "unavailable"

rows, snapshot = latest_snapshot()
rows = sorted(rows, key=lambda r: r.get("rank", 999))[:20]
if not rows:
    st.error("The saved Top-20 ranking snapshot could not be loaded.")
    st.stop()

names = {
    "MU":"Micron","TSM":"TSMC","CRDO":"Credo","ANET":"Arista Networks","PLTR":"Palantir","TER":"Teradyne","NVDA":"NVIDIA","DELL":"Dell","PATH":"UiPath","AMD":"AMD","GOOGL":"Alphabet","AMAT":"Applied Materials","DDOG":"Datadog","AVGO":"Broadcom","SNOW":"Snowflake","AMZN":"Amazon","MDB":"MongoDB","NET":"Cloudflare","ACMR":"ACM Research","VRT":"Vertiv","ASML":"ASML","SMCI":"Super Micro Computer","MSFT":"Microsoft","PANW":"Palo Alto Networks","ARM":"Arm","META":"Meta","CRWD":"CrowdStrike","MRVL":"Marvell","NOW":"ServiceNow","ORCL":"Oracle"
}
stocks = []
for r in rows:
    t = r.get("ticker", "")
    stocks.append({
        "rank": r.get("rank", 0),
        "ticker": t,
        "name": names.get(t, t),
        "score": round(float(r.get("score", 0) or 0), 1),
        "price": round(float(r.get("price", 0) or 0), 2),
        "risk": r.get("risk", "—"),
    })

# Native Streamlit image rendering is much more reliable on mobile than embedding a
# large base64 JPEG inside the custom component iframe.
hero_path = Path("assets/hero_production.jpg")
hero_left, hero_right = st.columns([.9, 1.1], gap="medium", vertical_alignment="center")
with hero_left:
    if hero_path.exists():
        st.image(str(hero_path), use_container_width=True)
with hero_right:
    st.markdown(f"""
    <div class='hero-copy'>
      <div class='eyebrow'>AI STOCKS MADE SIMPLE • VERSION {APP_VERSION}</div>
      <div class='hero-title'>AI STOCKS<br>MADE SIMPLE</div>
      <div class='hero-sub'><span class='cyan'>AI POWERED.</span><br><span class='pink'>DATA DRIVEN.</span><br>SMARTER INVESTING.</div>
      <div class='callout'>◆ BUILD A PAYCHECK PLAN<br><span class='fine'>SINGLE STOCK OR ROTATE MULTIPLE STOCKS</span></div>
      <div class='snake'>🐍👓 PYTHON POWERED &nbsp; • &nbsp; 🥤 RED POP ENERGY</div>
    </div>
    """, unsafe_allow_html=True)

stocks_json = json.dumps(stocks)

html = f'''<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><style>
*{{box-sizing:border-box}}html,body{{margin:0;background:#020711;color:#edf7ff;font-family:Arial,Helvetica,sans-serif}}body{{padding:8px 4px 90px}}.app{{max-width:920px;margin:auto}}.cyan{{color:#22d3ee}}.pink{{color:#e879f9}}.green{{color:#4ade80}}.orange{{color:#fb923c}}.muted{{color:#8fa6bf;font-size:13px}}
.status{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:4px 0 12px}}.stat{{background:#07111f;border:1px solid #17365f;border-radius:15px;padding:12px}}.stat small{{display:block;color:#8fa6bf;font-weight:900;font-size:9px}}.stat strong{{font-size:16px}}
.panel{{background:linear-gradient(180deg,#081322,#030812);border:1px solid #17365f;border-radius:22px;padding:16px;margin:12px 0}}h2{{margin:0 0 5px;font-size:24px}}.stocks{{display:grid;grid-template-columns:repeat(2,1fr);gap:9px;margin-top:12px}}.stock{{display:flex;align-items:center;gap:10px;text-align:left;background:#07111f;border:1px solid #17365f;border-radius:15px;padding:12px;color:white;cursor:pointer}}.stock.active{{border-color:#22d3ee;background:#09253b;box-shadow:0 0 18px #22d3ee33}}.badge{{min-width:38px;height:38px;border-radius:50%;display:grid;place-items:center;border:2px solid #22c55e;color:#4ade80;font-weight:900}}.stockMain{{flex:1}}.stockName{{font-weight:900;font-size:15px}}.ticker{{color:#8fa6bf;font-size:12px}}.price{{font-weight:900}}.risk{{font-size:11px;color:#facc15}}
.plan{{background:radial-gradient(circle at 10% 15%,#ec489944,transparent 27%),linear-gradient(120deg,#24104d,#07345b,#481c08);border-color:#a855f7}}label{{display:block;font-size:12px;font-weight:900;color:#b7c9dd;margin:12px 0 6px}}select,input{{width:100%;background:#06101d;border:1px solid #315177;color:white;border-radius:13px;padding:13px;font-size:16px;outline:none}}.quick{{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}}button{{border:1px solid #275078;border-radius:13px;background:#07111f;color:white;padding:12px;font-weight:900;cursor:pointer}}button.active,button.primary{{background:linear-gradient(90deg,#0ea5e9,#7c3aed);border-color:#22d3ee}}.mode{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}.selected{{margin-top:10px;background:#052d23;border:1px solid #22c55e;border-radius:14px;padding:12px;font-weight:900}}.rotation{{display:none;margin-top:10px;padding:12px;border:1px solid #7c3aed;border-radius:15px;background:#120b2b}}.rotation.show{{display:block}}.rotgrid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}.route{{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}}.pill{{padding:7px 10px;border-radius:999px;background:#0a2338;border:1px solid #22d3ee;color:#b8efff;font-size:12px;font-weight:900}}
.results{{display:none}}.results.show{{display:block}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px}}.card{{background:#07111f;border:1px solid #17365f;border-radius:15px;padding:12px}}.card small{{display:block;color:#8fa6bf;font-size:9px;font-weight:900}}.card strong{{font-size:19px}}.chart{{height:190px;display:flex;align-items:end;gap:4px;margin:16px 0;border-bottom:1px solid #21405f;padding:10px}}.bar{{flex:1;background:linear-gradient(#22d3ee,#7c3aed);border-radius:4px 4px 0 0;min-height:3px}}.upcoming,.breakdown{{background:#07111f;border:1px solid #17365f;border-radius:15px;padding:12px}}.deposit,.breakrow{{display:flex;justify-content:space-between;gap:8px;padding:7px 0;border-bottom:1px solid #14263a;font-size:13px}}.breakrow span:first-child{{font-weight:900}}.learn{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}}.learn div{{background:#07111f;border:1px solid #17365f;border-radius:16px;padding:14px;min-height:120px}}.ref{{border:1px solid #22c55e;background:linear-gradient(120deg,#052e16,#07182c);border-radius:18px;padding:15px;margin-top:12px}}.ref a{{display:block;text-align:center;text-decoration:none;background:#22c55e;color:#03210f;font-weight:1000;border-radius:13px;padding:13px;margin-top:10px}}
.nav{{position:fixed;bottom:8px;left:50%;transform:translateX(-50%);width:min(94%,780px);display:flex;justify-content:space-around;background:#07111ff4;border:1px solid #17365f;border-radius:18px;padding:10px;z-index:99;box-shadow:0 0 30px #000}}.nav a{{color:#9fb6d3;text-decoration:none;font-size:10px;font-weight:900;text-align:center}}.nav span{{display:block;color:#22d3ee;font-size:19px}}
@media(max-width:650px){{.status{{grid-template-columns:repeat(2,1fr)}}.stocks{{grid-template-columns:1fr}}.cards{{grid-template-columns:repeat(2,1fr)}}.learn{{grid-template-columns:repeat(2,1fr)}}.rotgrid{{grid-template-columns:1fr}}.two{{grid-template-columns:1fr 1fr}}}}
</style></head><body><div class="app" id="home">
<div class="status"><div class="stat"><small>MARKET DATA</small><strong class="green">SNAPSHOT</strong></div><div class="stat"><small>LAST UPDATED</small><strong>{snapshot}</strong></div><div class="stat"><small>MODEL VERSION</small><strong class="cyan">{APP_VERSION}</strong></div><div class="stat"><small>AI STOCKS</small><strong class="orange">20</strong></div></div>
<div class="panel" id="top20"><h2>🔥 TOP AI STOCKS TODAY</h2><div class="muted">Tap any company to load it into the planner.</div><div class="stocks" id="stocks"></div></div>
<div class="panel plan" id="simulate"><h2>💵 BUILD YOUR PAYCHECK PLAN</h2><div class="muted">Use one stock every time, or rotate a sequence like NVDA → MSFT → GOOGL → repeat.</div><div class="mode"><button id="singleMode" class="active">ONE STOCK</button><button id="rotationMode">ROTATION MODE</button></div><div id="selectedBox" class="selected"></div><label>1. Primary stock</label><select id="stockSelect"></select><div class="rotation" id="rotationBox"><label>Choose your rotation order (2–5 stocks)</label><div class="rotgrid"><select id="rot2"></select><select id="rot3"></select><select id="rot4"></select><select id="rot5"></select></div><div class="route" id="routePreview"></div></div><label>2. Investment amount each paycheck</label><div class="quick" id="quick"></div><input id="amount" type="number" min="1" step="1" value="10"><label>3. Frequency</label><select id="freq"><option value="14">Every 2 weeks / payday</option><option value="7">Every Friday</option><option value="30">Every month</option><option value="1">Custom days</option></select><div id="customWrap" style="display:none"><label>Custom number of days</label><input id="customDays" type="number" min="1" value="14"></div><div class="two"><div><label>4. Start date</label><input id="start" type="date"></div><div><label>5. End date</label><input id="end" type="date" value="2026-12-31"></div></div><button class="primary" id="run" style="width:100%;margin-top:14px">🚀 SHOW ME HOW THIS ADDS UP</button></div>
<div class="panel results" id="results"><h2>📈 YOUR SIMULATION RESULTS</h2><div class="muted" id="resultSub"></div><div class="cards"><div class="card"><small>TOTAL CONTRIBUTED</small><strong class="green" id="total"></strong></div><div class="card"><small># OF DEPOSITS</small><strong class="pink" id="count"></strong></div><div class="card"><small>TOTAL SHARES</small><strong class="cyan" id="shares"></strong></div><div class="card"><small>VALUE AT SHOWN PRICES</small><strong class="orange" id="value"></strong></div></div><div class="two"><div><h3>Portfolio Growth</h3><div class="chart" id="chart"></div></div><div><h3>Portfolio by Stock</h3><div class="breakdown" id="breakdown"></div></div></div><h3>Upcoming Paychecks</h3><div class="upcoming" id="upcoming"></div><div class="muted" style="margin-top:10px">Future stock prices will change. This illustration holds each selected stock at its displayed price so the contribution/share math is easy to understand.</div></div>
<div class="panel" id="learn"><h2>🎓 START SMALL. LEARN AS YOU GO.</h2><div class="learn"><div><h3 class="pink">🚀 START SMALL</h3>$5, $10 or $25 at a time. Fractional shares can make small investing approachable.</div><div><h3 class="cyan">🧠 LEARN</h3>Plain-English AI and investing explanations without Wall Street jargon.</div><div><h3 class="green">🎯 ROTATE SMART</h3>Spread recurring deposits across several AI companies instead of buying the same one every payday.</div><div><h3 class="orange">🛡️ RISK FIRST</h3>Stocks can fall. Rankings are research signals, not guarantees.</div></div></div>
<div class="ref"><b class="green">Robinhood • Sponsored / Referral</b><div>Optional brokerage referral. Sponsorship never changes model rankings or simulator results.</div><a href="https://join.robinhood.com/steveng-15bac4" target="_blank">OPEN ROBINHOOD</a><div class="muted">I may receive a referral reward if you sign up or qualify through this link.</div></div>
</div><div class="nav"><a href="#home"><span>⌂</span>HOME</a><a href="#top20"><span>☷</span>TOP 20</a><a href="#simulate"><span>🧮</span>SIMULATE</a><a href="#learn"><span>🎓</span>LEARN</a><a href="#home"><span>⚙</span>SETTINGS</a></div>
<script>
const stocks={stocks_json};let selected=stocks.find(x=>x.ticker==='NVDA')||stocks[0];let amount=10;let rotation=false;
const $=id=>document.getElementById(id);const money=n=>'$'+Number(n||0).toLocaleString(undefined,{{minimumFractionDigits:2,maximumFractionDigits:2}});const optionHtml=(withNone=false)=> (withNone?'<option value="">— none —</option>':'')+stocks.map(s=>`<option value="${{s.ticker}}">${{s.name}} (${{s.ticker}})</option>`).join('');
function stockByTicker(t){{return stocks.find(s=>s.ticker===t)}}
function renderStocks(){{$('stocks').innerHTML=stocks.map(s=>`<button class="stock ${{s.ticker===selected.ticker?'active':''}}" data-t="${{s.ticker}}"><span class="badge">${{Math.round(s.score)}}</span><span class="stockMain"><span class="stockName">#${{s.rank}} ${{s.name}}</span><span class="ticker">${{s.ticker}} • ${{s.risk}} risk</span></span><span class="price">${{money(s.price)}}</span></button>`).join('');document.querySelectorAll('.stock').forEach(b=>b.onclick=()=>selectStock(b.dataset.t));}}
function renderSelects(){{$('stockSelect').innerHTML=optionHtml(false);$('stockSelect').value=selected.ticker;['rot2','rot3','rot4','rot5'].forEach(id=>$(id).innerHTML=optionHtml(true));if(!$('rot2').value)$('rot2').value=stocks.find(s=>s.ticker==='MSFT')?'MSFT':'';if(!$('rot3').value)$('rot3').value=stocks.find(s=>s.ticker==='GOOGL')?'GOOGL':'';updateRoute();}}
function selectStock(t){{selected=stockByTicker(t)||selected;$('stockSelect').value=selected.ticker;renderStocks();$('selectedBox').innerHTML=`${{selected.name}} (${{selected.ticker}}) • displayed price <b>${{money(selected.price)}}</b>`;updateRoute();document.getElementById('simulate').scrollIntoView({{behavior:'smooth',block:'start'}});}}
function rotationList(){{let arr=[selected.ticker];if(rotation){{['rot2','rot3','rot4','rot5'].forEach(id=>{{const v=$(id).value;if(v&&!arr.includes(v))arr.push(v)}})}}return arr}}
function updateRoute(){{$('routePreview').innerHTML=rotationList().map((t,i)=>`<span class="pill">${{i+1}}. ${{t}}</span>`).join('')+(rotation?'<span class="pill">↻ repeat</span>':'');}}
$('stockSelect').onchange=e=>selectStock(e.target.value);['rot2','rot3','rot4','rot5'].forEach(id=>$(id).onchange=updateRoute);
$('singleMode').onclick=()=>{{rotation=false;$('singleMode').classList.add('active');$('rotationMode').classList.remove('active');$('rotationBox').classList.remove('show');updateRoute();}};$('rotationMode').onclick=()=>{{rotation=true;$('rotationMode').classList.add('active');$('singleMode').classList.remove('active');$('rotationBox').classList.add('show');updateRoute();}};
$('quick').innerHTML=[5,10,25,50,100].map(v=>`<button data-a="${{v}}">$${{v}}</button>`).join('');document.querySelectorAll('#quick button').forEach(b=>b.onclick=()=>{{amount=Number(b.dataset.a);$('amount').value=amount;document.querySelectorAll('#quick button').forEach(x=>x.classList.toggle('active',x===b));}});$('amount').oninput=e=>amount=Number(e.target.value||0);
const today=new Date();const iso=d=>d.toISOString().slice(0,10);const friday=new Date(today);friday.setDate(today.getDate()+((5-today.getDay()+7)%7));$('start').value=iso(friday);$('freq').onchange=e=>$('customWrap').style.display=e.target.value==='1'?'block':'none';
$('run').onclick=()=>{{const start=new Date($('start').value+'T12:00:00');const end=new Date($('end').value+'T12:00:00');if(!amount||amount<1){{alert('Enter an investment amount.');return}}if(end<start){{alert('End date must be after start date.');return}}let step=Number($('freq').value);if(step===1)step=Math.max(1,Number($('customDays').value||14));const route=rotationList();if(rotation&&route.length<2){{alert('Choose at least two different stocks for Rotation Mode.');return}}let dates=[];let d=new Date(start);while(d<=end){{dates.push(new Date(d));d.setDate(d.getDate()+step);if(dates.length>2000)break}}let totals={{}};let ledger=[];dates.forEach((dt,i)=>{{const t=route[i%route.length];const s=stockByTicker(t);const qty=s&&s.price>0?amount/s.price:0;if(!totals[t])totals[t]={{deposit:0,shares:0,value:0,stock:s}};totals[t].deposit+=amount;totals[t].shares+=qty;totals[t].value=totals[t].shares*(s?s.price:0);ledger.push({{date:dt,ticker:t,amount,shares:qty}})}});const total=ledger.length*amount;const totalShares=Object.values(totals).reduce((a,x)=>a+x.shares,0);const value=Object.values(totals).reduce((a,x)=>a+x.value,0);$('results').classList.add('show');$('resultSub').textContent=`${{rotation?'Rotation: '+route.join(' → ')+' → repeat':selected.name}} • through ${{$('end').value}}`;$('total').textContent=money(total);$('count').textContent=ledger.length;$('shares').textContent=totalShares.toFixed(4);$('value').textContent=money(value);const max=Math.max(1,ledger.length);$('chart').innerHTML=ledger.map((x,i)=>`<div class="bar" title="${{x.ticker}}" style="height:${{Math.max(3,((i+1)/max)*170)}}px"></div>`).join('');$('breakdown').innerHTML=Object.entries(totals).map(([t,x])=>`<div class="breakrow"><span>${{t}}</span><span>${{money(x.deposit)}} • ${{x.shares.toFixed(4)}} shares</span></div>`).join('');$('upcoming').innerHTML=ledger.slice(0,10).map(x=>`<div class="deposit"><span>${{x.date.toLocaleDateString()}} • <b>${{x.ticker}}</b></span><span>${{money(x.amount)}} → ${{x.shares.toFixed(4)}} sh</span></div>`).join('')+(ledger.length>10?`<div class="muted" style="padding-top:8px">+ ${{ledger.length-10}} more scheduled paychecks</div>`:'');$('results').scrollIntoView({{behavior:'smooth',block:'start'}});}};
renderSelects();selectStock(selected.ticker);renderStocks();
</script></body></html>'''

components.html(html, height=4700, scrolling=False)
