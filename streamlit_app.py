# STREAMLIT DEPLOYMENT BUILD: 3.1.2-hero-layout-fix
from pathlib import Path

entry = Path("beginner_app.py")
source = entry.read_text(encoding="utf-8")

# Keep the image embedded locally, but create a browser Blob URL after the component loads.
old_hero = '''<div class="hero">''' + "''' + (f'<img src=\"{hero_src}\" alt=\"AI Stocks guide\">' if hero_src else '') + f'''" + '''<div class="heroText">'''
new_hero = '''<div class="hero"><img id="heroImg" alt="AI Stocks guide"><div class="heroText">'''
if old_hero in source:
    source = source.replace(old_hero, new_hero, 1)
else:
    raise RuntimeError("Hero markup patch target not found")

old_js = "const stocks={stocks_json};let selected="
new_js = 'const heroB64="{hero_b64}";const heroBytes=Uint8Array.from(atob(heroB64),c=>c.charCodeAt(0));document.getElementById("heroImg").src=URL.createObjectURL(new Blob([heroBytes],{{type:"image/jpeg"}}));const stocks={stocks_json};let selected='
if old_js in source:
    source = source.replace(old_js, new_js, 1)
else:
    raise RuntimeError("Hero JavaScript patch target not found")

# The prior CSS forced the portrait into a large cover-crop. On phones this could show
# only the top of the character. Preserve the full artwork instead.
source = source.replace(
    '.hero img{{position:absolute;left:0;bottom:0;width:47%;height:100%;object-fit:cover;object-position:18% center;filter:saturate(1.12) contrast(1.04)}}',
    '.hero img{{position:absolute;left:0;bottom:0;width:47%;height:100%;object-fit:contain;object-position:left bottom;filter:saturate(1.12) contrast(1.04);background:#020711;padding:6px}}'
)
source = source.replace(
    '.hero{{min-height:560px}}.hero img{{width:100%;height:58%;top:0;bottom:auto;object-position:18% center}}.heroText{{margin-left:0;padding:320px 16px 16px}}',
    '.hero{{min-height:0}}.hero img{{position:relative;left:auto;top:auto;bottom:auto;width:100%;height:auto;max-height:320px;object-fit:contain;object-position:center;background:#020711;padding:4px;display:block}}.heroText{{margin-left:0;padding:16px}}'
)

exec(compile(source, str(entry), "exec"))
