from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

playwright, browser, page = open_page(
    "https://ires.remit.co.jp/IRESWeb/MainCommissionSimulator_Input.jsf"
)

page.wait_for_timeout(3000)

country = page.locator("select").nth(1)
country.select_option(label="NEPAL")

page.wait_for_timeout(3000)

print("=" * 80)
print("SELECTS AFTER CHOOSING NEPAL")
print("=" * 80)

selects = page.locator("select")

# Country
selects.nth(1).select_option(label="NEPAL")
page.wait_for_timeout(2000)

# Currency
selects = page.locator("select")
selects.nth(2).select_option(label="NPR")
page.wait_for_timeout(2000)

# Delivery Method
selects = page.locator("select")
selects.nth(3).select_option(label="BANK DIRECT NABIL")
page.wait_for_timeout(2000)

# Choose "Send Amount (JPY)"
page.locator("input[type='radio']").first.check()
page.wait_for_timeout(1000)

# Amount
amount = page.locator("input[type='text']").last
amount.fill("100000")

page.wait_for_timeout(1000)

# Screenshot before calculation
page.screenshot(path="before_calculate.png", full_page=True)

# Click Calculate
page.get_by_role("button", name="計算する").click()

page.wait_for_timeout(6000)

# Screenshot after calculation
page.screenshot(path="after_calculate.png", full_page=True)

print("=" * 80)
print(page.locator("body").inner_text()[:15000])