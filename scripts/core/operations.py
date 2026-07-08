import json
import shutil
from pathlib import Path

DATA_DIR = Path("data")
EXPORT_DIR = Path("exports")


def ms_to_seconds(ms):
    return round((ms or 0) / 1000, 1)


def export_operations():
    health_path = DATA_DIR / "collector_health.json"
    dashboard_path = DATA_DIR / "dashboard.json"

    if not health_path.exists():
        raise Exception("collector_health.json not found.")

    health = json.loads(health_path.read_text(encoding="utf-8"))
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))

    summary = health.get("summary", {})
    total = summary.get("total", 0)
    success = summary.get("success", 0)
    failed = summary.get("failed", 0)

    operations = {
        "generated_at": health.get("generated_at"),
        "status": "healthy" if failed == 0 else "warning",
        "last_dashboard_update": dashboard.get("last_updated"),
        "automation": {
            "primary": "cron-job.org",
            "backup": "GitHub Schedule",
            "frequency": "hourly"
        },
        "pipeline": {
            "duration_ms": health.get("pipeline_duration_ms"),
            "duration_seconds": ms_to_seconds(health.get("pipeline_duration_ms"))
        },
        "collectors": {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round((success / total) * 100, 1) if total else 0
        }
    }

    DATA_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)

    data_path = DATA_DIR / "operations.json"
    export_path = EXPORT_DIR / "operations.json"

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(operations, f, ensure_ascii=False, indent=4)

    shutil.copyfile(data_path, export_path)

    print("operations.json exported.")


if __name__ == "__main__":
    export_operations()