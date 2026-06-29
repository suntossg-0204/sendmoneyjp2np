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


def export_latest():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM rate_history
        ORDER BY collected_at DESC
    """)

    rows = cur.fetchall()
    conn.close()

    latest = {}

    for row in rows:
        item = row_to_dict(row)
        company = item["company_name"]

        if company not in latest:
            latest[company] = item

    companies = list(latest.values())
    companies = rank_companies(DEFAULT_SEND_AMOUNT, companies)

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