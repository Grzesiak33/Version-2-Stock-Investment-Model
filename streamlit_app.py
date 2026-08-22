from pathlib import Path

entry = Path("beginner_app.py")
exec(compile(entry.read_text(encoding="utf-8"), str(entry), "exec"))
