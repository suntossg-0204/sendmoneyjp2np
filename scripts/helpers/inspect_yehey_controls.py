from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://yeheyremit.jp/"

playwright, browser, page = open_page(URL)
page.wait_for_timeout(8000)

print("=" * 80)
print("BUTTONS")
print("=" * 80)

buttons = page.locator("button")
for i in range(buttons.count()):
    print(i, buttons.nth(i).inner_text())

print("=" * 80)
print("SELECTS")
print("=" * 80)

selects = page.locator("select")
for i in range(selects.count()):
    print(i, selects.nth(i).inner_text())

print("=" * 80)
print("INPUTS")
print("=" * 80)

inputs = page.locator("input")
for i in range(inputs.count()):
    print(i, inputs.nth(i).get_attribute("type"), inputs.nth(i).get_attribute("value"), inputs.nth(i).get_attribute("placeholder"))

browser.close()
playwright.stop()