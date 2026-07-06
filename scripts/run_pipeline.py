from collect_all import collect_all
from core.exporter import export_latest
from core.statistics import export_daily_summary
from database import cleanup_old_data
from core.dashboard import generate_dashboard
from core.trends import export_trends
from core.history import export_history
from core.trends_7d import export_trends_7d
from core.trends_summary import export_trend_summary

def run_pipeline():
    print("=" * 60)
    print("RemitTracker JP Pipeline Started")
    print("=" * 60)

    collect_all()
    cleanup_old_data(days=31)

    print("-" * 60)

    export_latest()
    export_daily_summary()
    export_trends()
    export_history()
    export_trends_7d()
    export_trend_summary(7)
    export_trend_summary(30)
    generate_dashboard()
   

    print("=" * 60)
    print("Pipeline completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()