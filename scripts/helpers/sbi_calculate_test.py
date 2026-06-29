from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://ires.remit.co.jp/IRESWeb/MainCommissionSimulator_Input.jsf"

playwright, browser, page = open_page(URL)
page.wait_for_timeout(3000)

selects = page.locator("select")

selects.nth(1).select_option(label="NEPAL")
page.wait_for_timeout(3000)

selects = page.locator("select")
selects.nth(2).select_option(label="NPR")
page.wait_for_timeout(2000)

# Try delivery method if available
selects = page.locator("select")
if selects.count() > 3:
    options = selects.nth(3).inner_text().strip()
    print("Delivery options:")
    print(options)
    if options:
        selects.nth(3).select_option(index=1)
        page.wait_for_timeout(2000)

page.locator("#common_main_Commission_Simulator_Input\\:frm\\:main\\:sendInput").fill("100000")
page.locator("input[type='submit'][value='計算する']").click()

page.wait_for_timeout(5000)

text = page.locator("body").inner_text()

print("=" * 80)
print("RESULT BODY")
print("=" * 80)
print(text[:10000])

browser.close()
playwright.stop()