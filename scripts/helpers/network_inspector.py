from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "scripts"))

from core.browser import open_page

URL = "https://www.pandaremit.com/en/jpn/send-money-to-nepal"


def inspect_network():
    playwright, browser, page = open_page(URL)

    interesting = []

    def log_response(response):
        url = response.url.lower()

        keywords = [
            "rate",
            "exchange",
            "quote",
            "currency",
            "remit",
            "fee",
            "jpy",
            "npr",
            "nepal"
        ]

        if any(k in url for k in keywords):
            interesting.append({
                "status": response.status,
                "url": response.url
            })

    page.on("response", log_response)

    page.wait_for_timeout(10000)

    print("=" * 80)
    print("PAGE TITLE")
    print("=" * 80)
    print(page.title())

    print("\n" + "=" * 80)
    print("FINAL URL")
    print("=" * 80)
    print(page.url)

    print("\n" + "=" * 80)
    print("INTERESTING NETWORK RESPONSES")
    print("=" * 80)

    for item in interesting:
        print(item["status"], item["url"])

    browser.close()
    playwright.stop()


if __name__ == "__main__":
    inspect_network()