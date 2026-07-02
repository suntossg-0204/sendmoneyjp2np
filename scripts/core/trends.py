import json
import sqlite3
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = Path("database/rates.db")


def export_trends():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT company_name, rate, collected_at
        FROM rate_history
        ORDER BY company_name, collected_at
    """)

    rows = cur.fetchall()
    conn.close()

    grouped = {}

    for company, rate, collected_at in rows:
        grouped.setdefault(company, []).append({
            "rate": rate,
            "collected_at": collected_at
        })

    trends = {}

    for company, records in grouped.items():
        latest = records[-1]
        previous = records[-2] if len(records) >= 2 else None

        if previous:
            change = round(latest["rate"] - previous["rate"], 6)
        else:
            change = 0
            change_percent = 0

        trends[company] = {
            "latest_rate": latest["rate"],
            "previous_rate": previous["rate"] if previous else None,
            "change": change,
            "samples": len(records),
            "direction": "up" if change > 0 else "down" if change < 0 else "same"
        }

    DATA_DIR.mkdir(exist_ok=True)

    with open(DATA_DIR / "trends.json", "w", encoding="utf-8") as f:
        json.dump(trends, f, indent=4, ensure_ascii=False)

    print("trends.json exported.")


if __name__ == "__main__":
    export_trends()