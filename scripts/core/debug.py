from datetime import datetime
from pathlib import Path
from config import SCREENSHOT_DIR


def save_failure_screenshot(page, company_name):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = company_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    path = SCREENSHOT_DIR / f"{safe_name}_failed_{timestamp}.png"

    page.screenshot(path=str(path), full_page=True)

    print(f"Failure screenshot saved: {path}")

    return path