import sqlite3
import json
from pathlib import Path

DATABASE = Path("database/rates.db")
EXPORT_DIR = Path("exports")
DATA_DIR = Path("data")

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
    latest = {}

    for row in rows:
        item = row_to_dict(row)
        company = item["company_name"]

        if company not in latest:
            latest[company] = item

    conn.close()

    for folder in [EXPORT_DIR, DATA_DIR]:
        with open(folder / "latest.json", "w", encoding="utf-8") as f:
            json.dump(latest, f, indent=4, ensure_ascii=False)

    print("latest.json exported.")


if __name__ == "__main__":
    export_latest()