import json
import shutil
from pathlib import Path

DATA_DIR = Path("data")
EXPORT_DIR = Path("exports")


def export_analytics():
    latest_path = DATA_DIR / "latest.json"
    dashboard_path = DATA_DIR / "dashboard.json"
    health_path = DATA_DIR / "collector_health.json"

    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))

    health = None
    if health_path.exists():
        health = json.loads(health_path.read_text(encoding="utf-8"))

    companies = list(latest.values())

    if not companies:
        raise Exception("No latest rate data found for analytics.")

    rates = [float(c["rate"]) for c in companies]

    best_rate_company = max(companies, key=lambda c: float(c["rate"]))
    lowest_rate_company = min(companies, key=lambda c: float(c["rate"]))

    best_total_company = dashboard["companies"][0]

    average_rate = round(sum(rates) / len(rates), 6)
    highest_rate = float(best_rate_company["rate"])
    lowest_rate = float(lowest_rate_company["rate"])
    rate_spread = round(highest_rate - lowest_rate, 6)

    analytics = {
        "last_updated": dashboard["last_updated"],
        "target_npr": dashboard["target_npr"],
        "deposit_method": dashboard["deposit_method"],
        "best_by_total_cost": {
            "company": best_total_company["company_name"],
            "required_jpy": best_total_company["required_jpy"],
            "rate": float(best_total_company["rate"]),
            "service_fee": best_total_company["service_fee"],
            "deposit_fee": best_total_company["deposit_fee"],
        },
        "best_by_rate": {
            "company": best_rate_company["company_name"],
            "rate": highest_rate,
        },
        "lowest_by_rate": {
            "company": lowest_rate_company["company_name"],
            "rate": lowest_rate,
        },
        "market": {
            "average_rate": average_rate,
            "highest_rate": highest_rate,
            "lowest_rate": lowest_rate,
            "rate_spread": rate_spread,
            "provider_count": len(companies),
        },
        "collector_health": health["summary"] if health else None,
    }

    DATA_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)

    data_path = DATA_DIR / "analytics.json"
    export_path = EXPORT_DIR / "analytics.json"

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(analytics, f, ensure_ascii=False, indent=4)

    shutil.copyfile(data_path, export_path)

    print("analytics.json exported.")


if __name__ == "__main__":
    export_analytics()