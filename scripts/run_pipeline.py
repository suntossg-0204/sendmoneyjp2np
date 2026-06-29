from collect_all import collect_all
from core.exporter import export_latest
from core.statistics import export_daily_summary


def run_pipeline():
    print("=" * 60)
    print("RemitTracker JP Pipeline Started")
    print("=" * 60)

    collect_all()

    print("-" * 60)

    export_latest()
    export_daily_summary()

    print("=" * 60)
    print("Pipeline completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()