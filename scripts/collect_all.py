from pathlib import Path
import importlib.util
import sys

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


def collect_all():
    init_db()

    collectors = discover_collectors()

    print(f"Found {len(collectors)} collectors.")

    for name, collector in collectors:
        try:
            print(f"Running collector: {name}")

            snapshot = collector()

            save_snapshot(snapshot)

            log_scrape(
                snapshot.company,
                "success",
                f"Saved rate {snapshot.rate}"
            )

        except Exception as e:
            log_scrape(
                name,
                "failed",
                str(e)
            )
            print(f"Collector failed: {name} - {e}")


if __name__ == "__main__":
    collect_all()