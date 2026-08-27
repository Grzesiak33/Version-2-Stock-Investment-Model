# STREAMLIT DEPLOYMENT BUILD: 3.3.1
# Keep the proven v3.3 UI, but remove the 10-row display cap from the
# paycheck schedule so long-term plans visibly run through the selected end date.
from pathlib import Path

entry = Path("beginner_app.py")
source = entry.read_text(encoding="utf-8")
source = source.replace("dates.slice(0,10).map", "dates.map")
source = source.replace('APP_VERSION = "3.3.0"', 'APP_VERSION = "3.3.1"')
exec(compile(source, str(entry), "exec"))
