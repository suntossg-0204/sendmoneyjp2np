import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


DATA_DIR = Path("data")
DB_PATH = Path("database/rates.db")

HISTORY_RETENTION_DAYS = 35


def export_history(retention_days=HISTORY_RETENTION_DAYS):
    """
    Export provider rate history for the most recent retention window.

    History is retained by time instead of by record count so the
    dashboard can reliably support Today, 7D, and 30D trend views.
    """

    cutoff = datetime.now() - timedelta(days=retention_days)
    cutoff_text = cutoff.strftime("%Y-%m-%dT%H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT company_name, rate, collected_at
        FROM rate_history
        WHERE collected_at >= ?
        ORDER BY company_name, collected_at ASC
        """,
        (cutoff_text,),
    )

    rows = cur.fetchall()
    conn.close()

    grouped = {}

    for company, rate, collected_at in rows:
        grouped.setdefault(company, [])

        grouped[company].append(
            {
                "rate": rate,
                "collected_at": collected_at,
            }
        )

    DATA_DIR.mkdir(exist_ok=True)

    history_path = DATA_DIR / "history.json"

    with history_path.open("w", encoding="utf-8") as f:
        json.dump(
            grouped,
            f,
            indent=4,
            ensure_ascii=False,
        )

    total_records = sum(
        len(records)
        for records in grouped.values()
    )

    print(
        f"history.json exported. "
        f"{total_records} records across "
        f"{len(grouped)} providers "
        f"(last {retention_days} days)."
    )


if __name__ == "__main__":
    export_history()