from database import init_db, save_snapshot, log_scrape
from collectors.wise import collect as collect_wise


def collect_all():
    init_db()

    collectors = [
        collect_wise
    ]

    for collector in collectors:
        try:
            snapshot = collector()
            save_snapshot(snapshot)
            log_scrape(snapshot.company, "success", f"Saved rate {snapshot.rate}")
        except Exception as e:
            log_scrape("Unknown", "failed", str(e))
            print("Collector failed:", e)


if __name__ == "__main__":
    collect_all()