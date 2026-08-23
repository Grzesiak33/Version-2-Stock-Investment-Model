# STREAMLIT DEPLOYMENT BUILD: 3.2.0
# The production app now renders the hero with Streamlit's native image component
# and runs the interactive single-stock / multi-stock paycheck planner below it.
from pathlib import Path

entry = Path("beginner_app.py")
exec(compile(entry.read_text(encoding="utf-8"), str(entry), "exec"))
