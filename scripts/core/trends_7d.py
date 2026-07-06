import json
from pathlib import Path
from database import get_connection

OUTPUT = Path("data/trends_7d.json")


def export_trends_7d():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT company_name, rate, collected_at
        FROM rate_history
        WHERE collected_at >= datetime('now', '-7 days', 'localtime')
        ORDER BY company_name, collected_at
    """)

    rows = cur.fetchall()
    conn.close()

    data = {}

    for company_name, rate, collected_at in rows:
        data.setdefault(company_name, []).append({
            "rate": rate,
            "collected_at": collected_at
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("trends_7d.json exported.")