# STREAMLIT DEPLOYMENT BUILD: 3.3.2
# Preserve the proven v3.3 calculator and full long-term schedule.
# This wrapper applies the colorful Superman-blue UX treatment only.
from pathlib import Path

entry = Path("beginner_app.py")
source = entry.read_text(encoding="utf-8")

# Keep the long-term schedule fix: show every payday through the selected end date.
source = source.replace("dates.slice(0,10).map", "dates.map")
source = source.replace('APP_VERSION = "3.3.0"', 'APP_VERSION = "3.3.2"')

# Main Streamlit shell: bright Superman blue instead of near-black.
source = source.replace(
    '.block-container{padding:.35rem .45rem 0!important;max-width:960px!important}.stApp{background:#020711}header,footer{visibility:hidden}',
    '.block-container{padding:.35rem .45rem 0!important;max-width:960px!important}.stApp{background:linear-gradient(180deg,#087cff 0%,#0064df 32%,#0046b8 67%,#00358f 100%)}header,footer{visibility:hidden}'
)
source = source.replace(
    '.hero-note{margin:.35rem 0 .5rem;padding:8px 12px;border:1px solid #17365f;border-radius:12px;background:#07111f;color:#9fb4ce;font-size:.75rem;text-align:center}.hero-note b{color:#22d3ee}',
    '.hero-note{margin:.35rem 0 .5rem;padding:9px 12px;border:2px solid #ffd31a;border-radius:13px;background:linear-gradient(90deg,#e51b23,#ff6a00,#005ee8);color:#fff;font-size:.78rem;text-align:center;font-weight:800;box-shadow:0 0 18px #0ff5}.hero-note b{color:#fff200}'
)
source = source.replace(
    '• AI-powered paycheck investing simulator • ranking snapshot {snapshot}',
    '• 🐍👓 PYTHON POWERED • 🥤 RED POP ENERGY • paycheck investing simulator • ranking snapshot {snapshot}'
)

# Custom component color system. Functional HTML/JS stays unchanged.
source = source.replace(
    '*{{box-sizing:border-box}}html,body{{margin:0;background:#020711;color:#edf7ff;font-family:Arial,Helvetica,sans-serif}}body{{padding:8px 4px 90px}}.app{{max-width:920px;margin:auto}}',
    '*{{box-sizing:border-box}}html,body{{margin:0;background:#005bd8;color:#ffffff;font-family:Arial,Helvetica,sans-serif}}body{{padding:8px 4px 90px;background:linear-gradient(180deg,#087cff 0%,#0061dc 35%,#0046b8 70%,#003484 100%) fixed}}.app{{max-width:920px;margin:auto}}'
)
source = source.replace(
    '.cyan{{color:#22d3ee}}.green{{color:#4ade80}}.muted{{color:#8fa6bf;font-size:13px}}',
    '.cyan{{color:#42f5ff}}.green{{color:#62ff54}}.muted{{color:#d5ebff;font-size:13px}}'
)
source = source.replace(
    '.stat,.panel{{background:linear-gradient(180deg,#081322,#030812);border:1px solid #17365f;border-radius:18px;padding:14px;margin:10px 0}}',
    '.stat,.panel{{background:linear-gradient(180deg,#075fda,#0649ae);border:2px solid #20c8ff;border-radius:18px;padding:14px;margin:10px 0;box-shadow:0 8px 20px #00286566,0 0 16px #28cfff33}}'
)
source = source.replace(
    '.stat small{{display:block;color:#8fa6bf;font-size:9px;font-weight:900}}',
    '.stat small{{display:block;color:#d9eeff;font-size:9px;font-weight:900}}'
)
source = source.replace(
    '.stock{{display:flex;align-items:center;gap:10px;text-align:left;background:#07111f;border:1px solid #17365f;border-radius:15px;padding:12px;color:white;cursor:pointer}}',
    '.stock{{display:flex;align-items:center;gap:10px;text-align:left;background:linear-gradient(135deg,#0a68ed,#0647b2);border:2px solid #2dcfff;border-radius:15px;padding:12px;color:white;cursor:pointer;box-shadow:0 5px 12px #00327b66}}'
)
source = source.replace(
    '.stock.active{{border-color:#22d3ee;background:#09253b;box-shadow:0 0 18px #22d3ee33}}',
    '.stock.active{{border-color:#ffe600;background:linear-gradient(135deg,#ff6a00,#e51b23);box-shadow:0 0 20px #ffd00077}}'
)
source = source.replace(
    '.badge{{min-width:38px;height:38px;border-radius:50%;display:grid;place-items:center;border:2px solid #22c55e;color:#4ade80;font-weight:900}}',
    '.badge{{min-width:38px;height:38px;border-radius:50%;display:grid;place-items:center;border:3px solid #ffe600;background:#07348e;color:#ffffff;font-weight:900;box-shadow:0 0 12px #ffe60055}}'
)
source = source.replace(
    '.ticker{{color:#8fa6bf;font-size:12px}}',
    '.ticker{{color:#d7edff;font-size:12px}}'
)
source = source.replace(
    '.plan{{background:radial-gradient(circle at 10% 15%,#ec489944,transparent 27%),linear-gradient(120deg,#24104d,#07345b,#481c08);border-color:#a855f7}}',
    '.plan{{background:radial-gradient(circle at 8% 18%,#ffcc0044,transparent 25%),linear-gradient(125deg,#e51b23 0%,#cf101b 35%,#075ee8 36%,#0647b8 100%);border-color:#ffe600;box-shadow:0 8px 24px #002b7566,0 0 18px #ffd00044}}'
)
source = source.replace(
    'select,input{{width:100%;background:#06101d;border:1px solid #315177;color:white;border-radius:13px;padding:13px;font-size:16px}}',
    'select,input{{width:100%;background:#f8fbff;border:2px solid #8fdcff;color:#05245d;border-radius:13px;padding:13px;font-size:16px;font-weight:800}}'
)
source = source.replace(
    'button{{border:1px solid #275078;border-radius:13px;background:#07111f;color:white;padding:12px;font-weight:900;cursor:pointer}}button.active,button.primary{{background:linear-gradient(90deg,#0ea5e9,#7c3aed);border-color:#22d3ee}}',
    'button{{border:2px solid #62d8ff;border-radius:13px;background:linear-gradient(180deg,#0b68e8,#0648b1);color:white;padding:12px;font-weight:900;cursor:pointer;box-shadow:0 4px 10px #002a6a66}}button.active{{background:linear-gradient(90deg,#e51b23,#ff6a00);border-color:#ffe600}}button.primary{{background:linear-gradient(180deg,#35d126,#078c10);border-color:#baff54;color:white;box-shadow:0 0 18px #2cff5066}}'
)
source = source.replace(
    '.selected{{margin-top:10px;background:#052d23;border:1px solid #22c55e;border-radius:14px;padding:12px;font-weight:900}}',
    '.selected{{margin-top:10px;background:linear-gradient(90deg,#0b8e28,#075f20);border:2px solid #72ff6a;border-radius:14px;padding:12px;font-weight:900;box-shadow:0 0 14px #34ff5544}}'
)
source = source.replace(
    '.rotation{{display:none;margin-top:10px;padding:12px;border:1px solid #7c3aed;border-radius:15px;background:#120b2b}}',
    '.rotation{{display:none;margin-top:10px;padding:12px;border:2px solid #ff65e8;border-radius:15px;background:linear-gradient(135deg,#6b19c8,#3421a6)}}'
)
source = source.replace(
    '.pill{{padding:7px 10px;border-radius:999px;background:#0a2338;border:1px solid #22d3ee;color:#b8efff;font-size:12px;font-weight:900}}',
    '.pill{{padding:7px 10px;border-radius:999px;background:#ff6a00;border:2px solid #ffe600;color:#ffffff;font-size:12px;font-weight:900}}'
)
source = source.replace(
    '.card,.upcoming,.breakdown{{background:#07111f;border:1px solid #17365f;border-radius:15px;padding:12px}}',
    '.card,.upcoming,.breakdown{{background:linear-gradient(180deg,#0759cf,#043b96);border:2px solid #36d6ff;border-radius:15px;padding:12px;box-shadow:0 5px 14px #00286355}}.cards .card:nth-child(1){{background:linear-gradient(180deg,#20b62d,#087818);border-color:#74ff6b}}.cards .card:nth-child(2){{background:linear-gradient(180deg,#0c7cff,#0750bd);border-color:#58d8ff}}.cards .card:nth-child(3){{background:linear-gradient(180deg,#ff8a00,#ef5600);border-color:#ffd135}}.cards .card:nth-child(4){{background:linear-gradient(180deg,#8c36df,#5720a8);border-color:#e47aff}}'
)
source = source.replace(
    '.card small{{display:block;color:#8fa6bf;font-size:9px}}',
    '.card small{{display:block;color:#ffffff;font-size:9px;font-weight:900}}'
)
source = source.replace(
    '.deposit,.breakrow{{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #14263a;font-size:13px}}',
    '.deposit,.breakrow{{display:flex;justify-content:space-between;padding:8px 6px;border-bottom:1px solid #45cfff66;font-size:13px;color:#ffffff}}.deposit:nth-child(even),.breakrow:nth-child(even){{background:#0b67d955;border-radius:7px}}'
)
source = source.replace(
    '.ref{{border:1px solid #22c55e;background:linear-gradient(120deg,#052e16,#07182c);border-radius:18px;padding:15px;margin-top:12px}}.ref a{{display:block;text-align:center;text-decoration:none;background:#22c55e;color:#03210f;font-weight:1000;border-radius:13px;padding:13px;margin-top:10px}}',
    '.ref{{border:2px solid #ffe600;background:linear-gradient(120deg,#e51b23,#ff6a00);border-radius:18px;padding:15px;margin-top:12px;box-shadow:0 0 18px #ffb00055}}.ref a{{display:block;text-align:center;text-decoration:none;background:linear-gradient(180deg,#35d126,#078c10);border:2px solid #baff54;color:white;font-weight:1000;border-radius:13px;padding:13px;margin-top:10px}}'
)

exec(compile(source, str(entry), "exec"))
