from pathlib import Path
import importlib.util
import sys
import json
import shutil
import time
from datetime import datetime

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from database import init_db, save_snapshot, log_scrape


COLLECTORS_DIR = ROOT / "collectors"
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = PROJECT_ROOT / "exports"


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

        duration = f"{item['duration_ms']}ms"
        print(f"{icon} {item['collector']:<20} {status.upper():<8} {duration:<8} {item['message']}")

    print("-" * 60)
    print(f"{success_count} / {len(results)} collectors successful")


def export_collector_health(results, pipeline_duration_ms):
    generated_at = datetime.now().isoformat(timespec="seconds")

    success_count = sum(1 for item in results if item["status"] == "success")
    failed_count = sum(1 for item in results if item["status"] == "failed")

    payload = {
        "generated_at": generated_at,
        "pipeline_duration_ms": pipeline_duration_ms,
        "summary": {
            "total": len(results),
            "success": success_count,
            "failed": failed_count,
        },
        "collectors": results,
    }

    DATA_DIR.mkdir(exist_ok=True)
    EXPORTS_DIR.mkdir(exist_ok=True)

    data_path = DATA_DIR / "collector_health.json"
    export_path = EXPORTS_DIR / "collector_health.json"

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    shutil.copyfile(data_path, export_path)

    print("collector_health.json exported.")


def collect_all():
    pipeline_start = time.perf_counter()

    init_db()

    collectors = discover_collectors()
    results = []

    print(f"Found {len(collectors)} collectors.")

    for name, collector in collectors:
        collector_start = time.perf_counter()

        try:
            print(f"Running collector: {name}")

            snapshot = collector()
            save_snapshot(snapshot)

            duration_ms = round((time.perf_counter() - collector_start) * 1000)

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
                "duration_ms": duration_ms,
                "message": message,
                "timestamp": datetime.now().isoformat(timespec="seconds")
            })

        except Exception as e:
            duration_ms = round((time.perf_counter() - collector_start) * 1000)
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
                "duration_ms": duration_ms,
                "message": message,
                "timestamp": datetime.now().isoformat(timespec="seconds")
            })

    pipeline_duration_ms = round((time.perf_counter() - pipeline_start) * 1000)

    print_health_report(results)
    export_collector_health(results, pipeline_duration_ms)

    return results


if __name__ == "__main__":
    collect_all()