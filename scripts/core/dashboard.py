import json
from pathlib import Path

DATA_DIR = Path("data")


def generate_dashboard():
    latest = json.loads((DATA_DIR / "latest.json").read_text(encoding="utf-8"))

    companies = sorted(
        latest.values(),
        key=lambda x: x["received_npr"],
        reverse=True
    )

    dashboard = {
        "last_updated": max(c["collected_at"] for c in companies),
        "send_amount": 100000,
        "best_company": companies[0]["company_name"],
        "best_received": companies[0]["received_npr"],
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