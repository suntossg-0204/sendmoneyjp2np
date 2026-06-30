import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from core.pricing import calculate_total_cost

DATA_DIR = Path("data")
TARGET_NPR = 100000
DEPOSIT_METHOD = "bank_transfer"


def generate_dashboard():
    latest = json.loads((DATA_DIR / "latest.json").read_text(encoding="utf-8"))

    companies = []

    for company in latest.values():
        pricing = calculate_total_cost(
            company_name=company["company_name"],
            target_npr=TARGET_NPR,
            rate=float(company["rate"]),
            deposit_method=DEPOSIT_METHOD
        )

        company["required_jpy"] = pricing["total_jpy"]
        company["remittance_amount"] = pricing["remittance_amount"]
        company["service_fee"] = pricing["service_fee"]
        company["deposit_fee"] = pricing["deposit_fee"]

        companies.append(company)

    companies = sorted(
        companies,
        key=lambda x: x["required_jpy"]
    )

    dashboard = {
        "last_updated": max(c["collected_at"] for c in companies),
        "target_npr": TARGET_NPR,
        "deposit_method": DEPOSIT_METHOD,
        "best_company": companies[0]["company_name"],
        "lowest_total_jpy": companies[0]["required_jpy"],
        "companies": companies
    }

    with open(DATA_DIR / "dashboard.json", "w", encoding="utf-8") as f:
        json.dump(
            dashboard,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("dashboard.json exported.")


if __name__ == "__main__":
    generate_dashboard()