from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from core.browser import open_page
from models import RateSnapshot

URL = "https://www.jpremit.com/today-rates"


def collect():
    playwright, browser, page = open_page(URL)

    try:
        text = page.locator("body").inner_text()

        patterns = [
            r"NPR\s*-\s*Nepal\s+([0-9.]+)",
            r"Nepal\s*\(?NPR\)?\s*([0-9.]+)",
            r"NPR\s+([0-9]+\.[0-9]+)",
            r"Nepal[\s\S]{0,80}?([0-9]+\.[0-9]+)",
        ]

        match = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                break

        if not match:
            raise Exception("Could not find JRF NPR rate.")

        rate = float(match.group(1))

        if rate < 0.7 or rate > 1.2:
            raise Exception(f"Invalid JRF rate detected: {rate}")

        return RateSnapshot(
            company="Japan Remit Finance",
            rate=rate,
            source_url=URL,
            service_fee=1500,
            deposit_method="Online",
            metadata={
                "method": "today-rates page",
                "matched_text": match.group(0),
            },
        )

    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    print(collect())