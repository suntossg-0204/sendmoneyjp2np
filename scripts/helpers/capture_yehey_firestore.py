from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://yeheyremit.jp/"

playwright, browser, page = open_page(URL)

def log_response(response):
    if "firestore.googleapis.com" in response.url:
        print("=" * 80)
        print(response.url)
        print("=" * 80)
        try:
            print(response.text()[:5000])
        except Exception as e:
            print("Could not read response:", e)

page.on("response", log_response)
page.wait_for_timeout(15000)

browser.close()
playwright.stop()