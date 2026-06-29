from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://www.remit.co.jp/kaigaisoukin/simulation/"

playwright, browser, page = open_page(URL)

print("=" * 80)
print("TITLE")
print("=" * 80)
print(page.title())

print("\n" + "=" * 80)
print("URL")
print("=" * 80)
print(page.url)

print("\n" + "=" * 80)
print("BODY")
print("=" * 80)
print(page.locator("body").inner_text()[:8000])

browser.close()
playwright.stop()