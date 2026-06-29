from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from models import RateSnapshot
from core.api import APIClient

URL = "https://prod.pandaremit.com/pricing/rate/JPY/NPR"


def collect():

    client = APIClient()

    data = client.get_json(URL)

    model = data["model"]

    return RateSnapshot(
        company="Panda Remit",
        rate=float(model["pandaRate"]),
        source_url=URL,
        service_fee=400,
        metadata=model
    )


if __name__ == "__main__":
    snapshot = collect()

    print(snapshot)