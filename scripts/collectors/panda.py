from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from core.browser import open_page

PANDA_URL = "https://www.pandaremit.com/jp/"


def inspect():
    playwright, browser, page = open_page(PANDA_URL)

    print("=" * 80)
    print("TITLE")
    print("=" * 80)
    print(page.title())

    print("\n" + "=" * 80)
    print("URL")
    print("=" * 80)
    print(page.url)

    print("\n" + "=" * 80)
    print("FIRST 3000 CHARACTERS")
    print("=" * 80)
    print(page.inner_text("body")[:3000])

    browser.close()
    playwright.stop()


if __name__ == "__main__":
    inspect()