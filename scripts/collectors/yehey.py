from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from core.browser import open_page
from models import RateSnapshot

URL = "https://yeheyremit.jp/"


def to_number(value):
    return float(value.replace(",", "").strip())


def collect():
    playwright, browser, page = open_page(URL)

    try:
        page.wait_for_timeout(8000)

        inputs = page.locator("input")

        send_amount = to_number(inputs.nth(0).get_attribute("value"))
        receive_amount = to_number(inputs.nth(1).get_attribute("value"))

        if not send_amount or not receive_amount:
            raise Exception("Could not read Yehey calculator amounts.")

        rate = receive_amount / send_amount

        text = page.locator("body").inner_text()

        return RateSnapshot(
            company="Yehey Remit",
            rate=round(rate, 6),
            source_url=URL,
            service_fee=0,
            deposit_method="Online",
            metadata={
                "method": "homepage calculator",
                "send_amount": send_amount,
                "receive_amount": receive_amount,
                "text_match": re.search(r"1 JPY =.*?NPR", text, re.S).group(0)
                if re.search(r"1 JPY =.*?NPR", text, re.S)
                else None
            }
        )

    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    print(collect())