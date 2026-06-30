from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from core.browser import open_page
from models import RateSnapshot

URL = "https://www.payforex.net/remittance/simulator?ctry=Nepal"


def collect():
    playwright, browser, page = open_page(URL)

    try:
        page.wait_for_timeout(8000)
        text = page.locator("body").inner_text()

        match = re.search(r"1\s*JPY\s*=\s*([0-9.]+)\s*NPR", text)

        if not match:
            raise Exception("Could not find PayForex JPY-NPR rate.")

        rate = float(match.group(1))

        return RateSnapshot(
            company="PayForex",
            rate=rate,
            source_url=URL,
            service_fee=0,
            deposit_method="Online",
            metadata={
                "method": "simulator page",
                "matched_text": match.group(0)
            }
        )

    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    print(collect())