# STREAMLIT DEPLOYMENT BUILD: 2.2.6-20260822-1157
from pathlib import Path

entry = Path("beginner_app.py")
exec(compile(entry.read_text(encoding="utf-8"), str(entry), "exec"))
