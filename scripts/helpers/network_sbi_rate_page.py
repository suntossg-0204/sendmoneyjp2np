from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://ires.remit.co.jp/IRESWeb/Exchange_Rate.jsf"

playwright, browser, page = open_page(URL)

responses = []

def log_response(response):
    url = response.url.lower()
    if any(k in url for k in ["exchange", "rate", "jsf", "ajax", "npr", "nepal"]):
        responses.append((response.status, response.url))

page.on("response", log_response)

page.reload(wait_until="domcontentloaded")
page.wait_for_timeout(8000)

print("=" * 80)
print("NETWORK")
print("=" * 80)

for status, url in responses:
    print(status, url)

browser.close()
playwright.stop()