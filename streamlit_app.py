# STREAMLIT DEPLOYMENT BUILD: 3.1.1-hero-fix
from pathlib import Path

entry = Path("beginner_app.py")
source = entry.read_text(encoding="utf-8")

# Streamlit's embedded iframe was not reliably rendering the large data:image URL.
# Keep the image bytes embedded, but create a browser Blob URL after the component loads.
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

exec(compile(source, str(entry), "exec"))
