import json
from pathlib import Path
from database import get_connection


def export_trend_summary(days=7):
    output = Path(f"data/trends_{days}d_summary.json")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT company_name, rate, collected_at
        FROM rate_history
        WHERE collected_at >= datetime('now', ?)
        ORDER BY company_name, collected_at
    """, (f"-{days} days",))

    rows = cur.fetchall()
    conn.close()

    grouped = {}

    for company_name, rate, collected_at in rows:
        grouped.setdefault(company_name, []).append({
            "rate": float(rate),
            "collected_at": collected_at
        })

    summary = {}

    for company_name, records in grouped.items():
        rates = [record["rate"] for record in records]

        opening = rates[0]
        current = rates[-1]
        highest = max(rates)
        lowest = min(rates)
        average = sum(rates) / len(rates)
        change = current - opening
        change_percent = (change / opening) * 100 if opening else 0

        summary[company_name] = {
            "opening_rate": round(opening, 6),
            "current_rate": round(current, 6),
            "change": round(change, 6),
            "change_percent": round(change_percent, 2),
            "highest": round(highest, 6),
            "lowest": round(lowest, 6),
            "average": round(average, 6),
            "volatility": round(highest - lowest, 6),
            "samples": len(records),
            "first_collected_at": records[0]["collected_at"],
            "last_collected_at": records[-1]["collected_at"]
        }

    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    print(f"trends_{days}d_summary.json exported.")