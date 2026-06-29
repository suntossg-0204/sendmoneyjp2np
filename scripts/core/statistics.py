import sqlite3
import json
from pathlib import Path

DATABASE = Path("database/rates.db")
EXPORT_DIR = Path("exports")
DATA_DIR = Path("data")


def export_daily_summary():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            company_name,
            MAX(rate) AS high_rate,
            MIN(rate) AS low_rate,
            ROUND(AVG(rate),6) AS average_rate,
            COUNT(*) AS samples,
            MAX(collected_at) AS last_update
        FROM rate_history
        WHERE date(collected_at)=date('now','localtime')
        GROUP BY company_name
    """)

    rows = [dict(r) for r in cur.fetchall()]

    conn.close()

    for folder in [EXPORT_DIR, DATA_DIR]:

        with open(
            folder / "daily_summary.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                rows,
                f,
                indent=4,
                ensure_ascii=False
            )

    print("daily_summary.json exported.")