from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://www.smileswallet.com/"

playwright, browser, page = open_page(URL)

page.wait_for_timeout(6000)

print("=" * 80)
print("TITLE")
print("=" * 80)
print(page.title())

print("=" * 80)
print("URL")
print("=" * 80)
print(page.url)

print("=" * 80)
print("BODY")
print("=" * 80)
print(page.locator("body").inner_text()[:12000])

browser.close()
playwright.stop()