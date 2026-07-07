import sqlite3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from core.calculator import rank_companies

DATABASE = Path("database/rates.db")
EXPORT_DIR = Path("exports")
DATA_DIR = Path("data")

DEFAULT_SEND_AMOUNT = 100000

EXPORT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


def row_to_dict(row):
    item = dict(row)

    if item.get("metadata"):
        try:
            item["metadata"] = json.loads(item["metadata"])
        except Exception:
            item["metadata"] = {}

    return item


def calculate_rate_last_changed(rows_by_company):
    result = {}

    for company, rows in rows_by_company.items():
        if not rows:
            continue

        latest_rate = float(rows[0]["rate"])
        last_changed = rows[0]["collected_at"]

        for row in rows[1:]:
            previous_rate = float(row["rate"])

            if previous_rate == latest_rate:
                last_changed = row["collected_at"]
            else:
                break

        result[company] = last_changed

    return result


def load_collector_health():
    health_path = DATA_DIR / "collector_health.json"

    if not health_path.exists():
        return {}

    try:
        health = json.loads(health_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    by_company = {}

    for item in health.get("collectors", []):
        company = item.get("company")
        if company:
            by_company[company] = item

    return by_company


def apply_health_status(companies):
    health_by_company = load_collector_health()

    for company in companies:
        name = company["company_name"]
        health = health_by_company.get(name)

        if not health:
            company["health_status"] = "unknown"
            company["rate_status"] = "unknown"
            company["collector_message"] = None
            company["collector_duration_ms"] = None
            continue

        company["health_status"] = health["status"]
        company["collector_message"] = health["message"]
        company["collector_duration_ms"] = health["duration_ms"]

        if health["status"] == "success":
            company["rate_status"] = "fresh"
        else:
            company["rate_status"] = "stale"

    return companies


def export_latest():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM rate_history
        ORDER BY company_name, collected_at DESC
    """)

    rows = cur.fetchall()
    conn.close()

    latest = {}
    rows_by_company = {}

    for row in rows:
        item = row_to_dict(row)
        company = item["company_name"]

        rows_by_company.setdefault(company, []).append(item)

        if company not in latest:
            latest[company] = item

    rate_last_changed_by_company = calculate_rate_last_changed(rows_by_company)

    for company, item in latest.items():
        item["rate_last_changed"] = rate_last_changed_by_company.get(
            company,
            item["collected_at"]
        )

    companies = list(latest.values())
    companies = rank_companies(DEFAULT_SEND_AMOUNT, companies)
    companies = apply_health_status(companies)

    latest = {
        company["company_name"]: company
        for company in companies
    }

    for folder in [EXPORT_DIR, DATA_DIR]:
        with open(folder / "latest.json", "w", encoding="utf-8") as f:
            json.dump(latest, f, indent=4, ensure_ascii=False)

    print("latest.json exported.")


if __name__ == "__main__":
    export_latest()