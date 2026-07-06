from pathlib import Path
import importlib.util
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from database import init_db, save_snapshot, log_scrape


COLLECTORS_DIR = ROOT / "collectors"


def load_collector(file_path):
    module_name = file_path.stem

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "collect"):
        return module.collect

    return None


def discover_collectors():
    collectors = []

    for file_path in COLLECTORS_DIR.glob("*.py"):
        if file_path.name.startswith("_"):
            continue

        if file_path.name in ["base.py"]:
            continue

        collector = load_collector(file_path)

        if collector:
            collectors.append((file_path.stem, collector))

    return collectors


def print_health_report(results):
    print("-" * 60)
    print("Collector Health Report")
    print("-" * 60)

    success_count = 0

    for item in results:
        status = item["status"]

        if status == "success":
            success_count += 1
            icon = "✓"
        else:
            icon = "✗"

        print(f"{icon} {item['collector']:<20} {status.upper():<8} {item['message']}")

    print("-" * 60)
    print(f"{success_count} / {len(results)} collectors successful")


def collect_all():
    init_db()

    collectors = discover_collectors()
    results = []

    print(f"Found {len(collectors)} collectors.")

    for name, collector in collectors:
        try:
            print(f"Running collector: {name}")

            snapshot = collector()
            save_snapshot(snapshot)

            message = f"Saved {snapshot.company} = {snapshot.rate}"

            log_scrape(
                snapshot.company,
                "success",
                message
            )

            print(message)

            results.append({
                "collector": name,
                "company": snapshot.company,
                "status": "success",
                "rate": snapshot.rate,
                "message": message,
                "timestamp": datetime.now().isoformat(timespec="seconds")
            })

        except Exception as e:
            message = str(e)

            log_scrape(
                name,
                "failed",
                message
            )

            print(f"Collector failed: {name} - {message}")

            results.append({
                "collector": name,
                "company": name,
                "status": "failed",
                "rate": None,
                "message": message,
                "timestamp": datetime.now().isoformat(timespec="seconds")
            })

    print_health_report(results)

    return results


if __name__ == "__main__":
    collect_all()