from pathlib import Path
exec(Path('beginner_app_core.py').read_text()) if Path('beginner_app_core.py').exists() else None
