from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://ires.remit.co.jp/IRESWeb/MainCommissionSimulator_Input.jsf"

playwright, browser, page = open_page(URL)
page.wait_for_timeout(5000)

print("=" * 80)
print("SELECTS")
print("=" * 80)

selects = page.locator("select")
for i in range(selects.count()):
    sel = selects.nth(i)
    print(f"\nSELECT #{i}")
    print("name:", sel.get_attribute("name"))
    print("id:", sel.get_attribute("id"))
    print("text:")
    print(sel.inner_text()[:2000])

print("=" * 80)
print("INPUTS")
print("=" * 80)

inputs = page.locator("input")
for i in range(inputs.count()):
    inp = inputs.nth(i)
    print(f"\nINPUT #{i}")
    print("type:", inp.get_attribute("type"))
    print("name:", inp.get_attribute("name"))
    print("id:", inp.get_attribute("id"))
    print("value:", inp.get_attribute("value"))

browser.close()
playwright.stop()