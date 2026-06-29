from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from core.debug import save_failure_screenshot
from models import RateSnapshot
from core.browser import open_page

WISE_URL = "https://wise.com/gb/currency-converter/jpy-to-npr-rate"


def collect():
    playwright = None
    browser = None
    page = None

    try:
        playwright, browser, page = open_page(WISE_URL)

        text = page.inner_text("body")

        match = re.search(r"1\s+JPY\s*=\s*([0-9.]+)\s+NPR", text)

        if not match:
            save_failure_screenshot(page, "Wise")
            raise Exception("Could not find Wise rate on page.")

        rate = float(match.group(1))

        return RateSnapshot(
            company="Wise",
            rate=rate,
            source_url=WISE_URL,
            service_fee=0,
            atm_fee=0,
            deposit_method="Online"
        )

    except Exception:
        if page:
            save_failure_screenshot(page, "Wise")
        raise

    finally:
        if browser:
            browser.close()
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    snapshot = collect()
    print(snapshot)