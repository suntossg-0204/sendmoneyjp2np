from pathlib import Path
import sys
import requests

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from models import RateSnapshot

URL = "https://exchange.city-remit.net/api/rates"


def collect():
    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    rates = data.get("rates", [])

    normal = next(
        item for item in rates
        if item.get("name") == "NEPAL"
        and item.get("currency") == "NPR"
    )

    golden = next(
        (
            item for item in rates
            if item.get("name") == "GOLDENRATE"
            and item.get("currency") == "NPR"
        ),
        None
    )

    return RateSnapshot(
        company="City Express",
        rate=float(normal["rate"]),
        source_url=URL,
        service_fee=0,
        deposit_method="Online",
        metadata={
            "updated_at": data.get("updated_at"),
            "normal_rate": normal,
            "golden_rate": golden
        }
    )


if __name__ == "__main__":
    print(collect())