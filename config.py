from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "database" / "rates.db"
SCREENSHOT_DIR = BASE_DIR / "screenshots"
LOG_DIR = BASE_DIR / "logs"

HEADLESS = True
TIMEOUT = 60000
RETRY_COUNT = 2

USER_AGENT = "RemitTrackerJP/0.2"
