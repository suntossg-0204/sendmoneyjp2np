import json
import sqlite3
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = Path("database/rates.db")


def export_history(limit_per_company=50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT company_name, rate, collected_at
        FROM rate_history
        ORDER BY company_name, collected_at DESC
    """)

    rows = cur.fetchall()
    conn.close()

    grouped = {}

    for company, rate, collected_at in rows:
        grouped.setdefault(company, [])

        if len(grouped[company]) < limit_per_company:
            grouped[company].append({
                "rate": rate,
                "collected_at": collected_at
            })

    # reverse so chart goes old → new
    for company in grouped:
        grouped[company] = list(reversed(grouped[company]))

    DATA_DIR.mkdir(exist_ok=True)

    with open(DATA_DIR / "history.json", "w", encoding="utf-8") as f:
        json.dump(grouped, f, indent=4, ensure_ascii=False)

    print("history.json exported.")


if __name__ == "__main__":
    export_history()