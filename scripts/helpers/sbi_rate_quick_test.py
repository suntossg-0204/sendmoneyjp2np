from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://ires.remit.co.jp/IRESWeb/Exchange_Rate.jsf"

playwright, browser, page = open_page(URL)
page.wait_for_timeout(7000)

text = page.locator("body").inner_text()

print("=" * 80)
print("BODY")
print("=" * 80)
print(text[:12000])

print("=" * 80)
print("NPR MATCHES")
print("=" * 80)

for match in re.finditer(r".{0,60}(NPR|NEPAL|ネパール).{0,60}", text, re.IGNORECASE):
    print(match.group(0))

browser.close()
playwright.stop()