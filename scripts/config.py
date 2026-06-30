from pathlib import Path

HEADLESS = True
TIMEOUT = 60000

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0.0.0 Safari/537.36"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
EXPORT_DIR = PROJECT_ROOT / "exports"
DATABASE_DIR = PROJECT_ROOT / "database"
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"

for directory in [DATA_DIR, EXPORT_DIR, DATABASE_DIR, SCREENSHOT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)