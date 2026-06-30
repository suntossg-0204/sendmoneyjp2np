from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

playwright, browser, page = open_page("https://www.worldremit.com/en")

def log_request(request):
    if "graphql" in request.url.lower():
        print("=" * 80)
        print("GRAPHQL REQUEST")
        print("=" * 80)
        print(request.method)
        print(request.url)
        print("\nPOST DATA:\n")
        print(request.post_data)

page.on("request", log_request)

print("Waiting 30 seconds...")
print("Open Currency Converter and calculate Japan → Nepal manually.")
page.wait_for_timeout(30000)

browser.close()
playwright.stop()