from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://ires.remit.co.jp/IRESWeb/MainCommissionSimulator_Input.jsf"

playwright, browser, page = open_page(URL)
page.wait_for_timeout(3000)

# Country
page.locator("select").nth(1).select_option(label="NEPAL")
page.wait_for_timeout(3000)

# Currency
page.locator("select").nth(2).select_option(label="NPR")
page.wait_for_timeout(2000)

# Delivery
page.locator("select").nth(3).select_option(label="BANK DIRECT NABIL")
page.wait_for_timeout(2000)

# Amount type: send JPY
page.locator("input[type='radio']").nth(0).check()
page.wait_for_timeout(1000)

# Amount
page.locator("#common_main_Commission_Simulator_Input\\:frm\\:main\\:sendInput").fill("100000")
page.wait_for_timeout(1000)

# Submit
page.locator("input[value='計算する']").click()
page.wait_for_timeout(8000)

text = page.locator("body").inner_text()

print("=" * 80)
print("RESULT")
print("=" * 80)
print(text[:15000])

page.screenshot(path="sbi_result.png", full_page=True)

browser.close()
playwright.stop()