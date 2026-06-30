from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from core.browser import open_page
from models import RateSnapshot

URL = "https://ires.remit.co.jp/IRESWeb/MainCommissionSimulator_Input.jsf"


def collect():
    playwright, browser, page = open_page(URL)

    try:
        page.wait_for_timeout(3000)

        page.locator("select").nth(1).select_option(label="NEPAL")
        page.wait_for_timeout(3000)

        page.locator("select").nth(2).select_option(label="NPR")
        page.wait_for_timeout(2000)

        page.locator("select").nth(3).select_option(label="BANK DIRECT NABIL")
        page.wait_for_timeout(2000)

        page.locator("input[type='radio']").nth(0).check()
        page.wait_for_timeout(1000)

        page.locator(
            "#common_main_Commission_Simulator_Input\\:frm\\:main\\:sendInput"
        ).fill("100000")

        page.wait_for_timeout(1000)

        page.locator("input[value='計算する']").click()
        page.wait_for_timeout(8000)

        text = page.locator("body").inner_text()

        rate_match = re.search(r"1\s*円\s*=\s*([0-9.]+)\s*NPR", text)
        fee_match = re.search(r"送金手数料\s*＊\s*([0-9,]+)\s*円", text)

        if not rate_match:
            raise Exception("Could not find SBI rate.")

        rate = float(rate_match.group(1))
        fee = float(fee_match.group(1).replace(",", "")) if fee_match else 1000

        return RateSnapshot(
            company="SBI Remit",
            rate=rate,
            source_url=URL,
            service_fee=fee,
            deposit_method="BANK DIRECT NABIL",
            metadata={
                "method": "simulator",
                "send_amount": 100000,
                "matched_rate": rate_match.group(0),
                "matched_fee": fee_match.group(0) if fee_match else None
            }
        )

    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    print(collect())