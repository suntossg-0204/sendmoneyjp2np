from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT))

from core.browser import open_page

URL = "https://yeheyremit.jp/"

playwright, browser, page = open_page(URL)
page.wait_for_timeout(8000)

# Try clicking/selecting NPR if visible
text = page.locator("body").inner_text()

print("=" * 80)
print("INITIAL MATCHES")
print("=" * 80)
for m in re.finditer(r".{0,80}(NPR|0\.929|1 JPY).{0,80}", text):
    print(m.group(0))

# Screenshot for visual check
page.screenshot(path="yehey_npr_test.png", full_page=True)

browser.close()
playwright.stop()