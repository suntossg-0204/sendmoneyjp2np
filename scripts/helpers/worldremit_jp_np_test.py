from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

playwright, browser, page = open_page("https://www.worldremit.com/en/currency-converter")

page.context.add_cookies([
    {
        "name": "selectFrom",
        "value": "jp",
        "domain": ".worldremit.com",
        "path": "/"
    },
    {
        "name": "selectTo",
        "value": "np",
        "domain": ".worldremit.com",
        "path": "/"
    }
])

def log_request(request):
    if "api.worldremit.com/graphql" in request.url.lower():
        print("=" * 80)
        print("GRAPHQL REQUEST")
        print("=" * 80)
        print(request.method)
        print(request.url)
        print(request.post_data)

page.on("request", log_request)

page.reload(wait_until="domcontentloaded")
page.wait_for_timeout(15000)

browser.close()
playwright.stop()