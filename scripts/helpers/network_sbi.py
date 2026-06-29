from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://www.remit.co.jp/kaigaisoukin/exchangeratecommission/exchange/"


def inspect_network():
    playwright, browser, page = open_page(URL)

    responses = []

    def log_response(response):
        url = response.url.lower()
        keywords = [
            "rate",
            "exchange",
            "commission",
            "currency",
            "npr",
            "nepal",
            "api",
            "json",
            "php",
            "ajax"
        ]

        if any(k in url for k in keywords):
            responses.append((response.status, response.url))

    page.on("response", log_response)
    page.wait_for_timeout(10000)

    print("=" * 80)
    print("SBI NETWORK RESPONSES")
    print("=" * 80)

    for status, url in responses:
        print(status, url)

    browser.close()
    playwright.stop()


if __name__ == "__main__":
    inspect_network()