from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://yeheyremit.jp/"

playwright, browser, page = open_page(URL)

responses = []

def log(response):
    url = response.url.lower()
    if any(k in url for k in ["api", "rate", "exchange", "fee", "npr", "php", "calculator"]):
        responses.append((response.status, response.url))

page.on("response", log)
page.wait_for_timeout(12000)

print("=" * 80)
print("YEHEY NETWORK")
print("=" * 80)

for status, url in sorted(set(responses)):
    print(status, url)

browser.close()
playwright.stop()