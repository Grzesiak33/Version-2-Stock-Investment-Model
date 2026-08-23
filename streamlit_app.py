# STREAMLIT DEPLOYMENT BUILD: 3.5.0
# Compact colorful beginner UX: one-stock / rotation planner, tappable company education,
# optional growth scenarios, and simplified mobile-first navigation.
from pathlib import Path

entry = Path("beginner_app.py")
exec(compile(entry.read_text(encoding="utf-8"), str(entry), "exec"))
