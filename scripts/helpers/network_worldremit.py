from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://www.worldremit.com/"

playwright, browser, page = open_page(URL)

responses = []

def log(response):
    url = response.url.lower()
    if any(k in url for k in ["rate", "quote", "corridor", "currency", "api", "nepal", "npr", "japan", "jpy"]):
        responses.append((response.status, response.url))

page.on("response", log)
page.wait_for_timeout(12000)

print("=" * 80)
print("WORLDREMIT NETWORK")
print("=" * 80)

for status, url in responses:
    print(status, url)

browser.close()
playwright.stop()