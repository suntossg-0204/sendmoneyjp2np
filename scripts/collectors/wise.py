from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from collectors.base import BaseCollector


class WiseCollector(BaseCollector):
    COMPANY = "Wise"
    URL = "https://wise.com/gb/currency-converter/jpy-to-npr-rate"
    SERVICE_FEE = 0
    ATM_FEE = 0
    DEPOSIT_METHOD = "Online"

    def extract_rate(self, page):
        text = page.inner_text("body")

        match = re.search(r"1\s+JPY\s*=\s*([0-9.]+)\s+NPR", text)

        if not match:
            raise Exception("Could not find Wise rate on page.")

        return float(match.group(1))


def collect():
    return WiseCollector().collect()


if __name__ == "__main__":
    snapshot = collect()
    print(snapshot)