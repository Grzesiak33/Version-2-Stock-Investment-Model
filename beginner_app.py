from pathlib import Path
import re

core_path = Path("beginner_app_core.py")
source = core_path.read_text(encoding="utf-8")

# Replace the legacy emoji/CSS hero with the production artwork while leaving
# the real live-data, Top 20, simulator, learning, model and referral logic intact.
hero_pattern = re.compile(
    r"st\.markdown\(\"\"\"<div class='hero'>.*?</div></div></div>\"\"\",unsafe_allow_html=True\)",
    re.DOTALL,
)
replacement = "st.image('assets/hero_production.jpg', use_container_width=True)"
source, replacements = hero_pattern.subn(replacement, source, count=1)

if replacements != 1:
    raise RuntimeError("Production hero injection failed: legacy hero block not found")

exec(compile(source, str(core_path), "exec"))
