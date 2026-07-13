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


def find_npr_rate(text: str):
    """
    Extract the Japan Remit Finance JPY → NPR rate
    from visible page text.
    """

    # Normalize non-breaking spaces and repeated whitespace.
    normalized_text = text.replace("\u00a0", " ")
    normalized_text = re.sub(r"[ \t]+", " ", normalized_text)

    patterns = [
        r"NPR\s*[-–—]\s*Nepal\s+([0-9]+(?:\.[0-9]+)?)",
        r"Nepal\s*[-–—]?\s*\(?NPR\)?\s+([0-9]+(?:\.[0-9]+)?)",
        r"NPR\s+([0-9]+\.[0-9]+)",
        r"Nepal[\s\S]{0,120}?([0-9]+\.[0-9]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_text, re.IGNORECASE)

        if match:
            return match

    return None


def collect():
    playwright, browser, page = open_page(URL)

    try:
        # Give JavaScript-rendered content time to appear.
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass

        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            # Some websites never become fully idle.
            pass

        match = None
        text = ""

        # Retry because the rates table may appear after page load.
        for attempt in range(1, 6):
            text = page.locator("body").inner_text(timeout=10000)
            match = find_npr_rate(text)

            if match:
                break

            print(
                f"JRF rate not found on attempt {attempt}/5. "
                f"Waiting before retry..."
            )

            page.wait_for_timeout(3000)

        if not match:
            print("=" * 80)
            print("JRF DEBUG INFORMATION")
            print("=" * 80)
            print(f"Page URL: {page.url}")
            print(f"Page title: {page.title()}")
            print("-" * 80)
            print("Body preview:")
            print(text[:4000])
            print("=" * 80)

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