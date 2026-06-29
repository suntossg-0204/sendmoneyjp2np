from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://www.remit.co.jp/kaigaisoukin/exchangeratecommission/exchange/"

playwright, browser, page = open_page(URL)

with open("sbi_page.html", "w", encoding="utf-8") as f:
    f.write(page.content())

print("Saved: sbi_page.html")

browser.close()
playwright.stop()