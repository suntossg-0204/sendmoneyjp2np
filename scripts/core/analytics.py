import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


DATA_DIR = Path("data")
EXPORT_DIR = Path("exports")


def load_json(path: Path) -> Any:
    """Load and return JSON data from a file."""
    return json.loads(path.read_text(encoding="utf-8"))


def build_daily_best_rates(
    history: dict[str, list[dict[str, Any]]],
) -> dict[str, float]:
    """
    Build one best available market rate for each calendar day.

    Each provider may have many hourly records. Using one daily best rate
    prevents providers with more frequent collection records from receiving
    extra weight in historical calculations.
    """
    daily_best: dict[str, float] = {}

    for records in history.values():
        for record in records:
            try:
                rate = float(record["rate"])
                collected_at = datetime.fromisoformat(record["collected_at"])
            except (KeyError, TypeError, ValueError):
                continue

            day_key = collected_at.date().isoformat()

            if day_key not in daily_best or rate > daily_best[day_key]:
                daily_best[day_key] = rate

    return daily_best


def calculate_window_stats(
    daily_best: dict[str, float],
    current_rate: float,
    days: int,
) -> dict[str, Any] | None:
    """Calculate historical market statistics for a rolling day window."""
    if not daily_best:
        return None

    latest_day = max(
        datetime.fromisoformat(day).date()
        for day in daily_best
    )

    start_day = latest_day - timedelta(days=days - 1)

    window_values = [
        rate
        for day, rate in daily_best.items()
        if datetime.fromisoformat(day).date() >= start_day
    ]

    if not window_values:
        return None

    average_rate = sum(window_values) / len(window_values)
    highest_rate = max(window_values)
    lowest_rate = min(window_values)

    if average_rate:
        current_vs_average_pct = (
            (current_rate - average_rate) / average_rate
        ) * 100
    else:
        current_vs_average_pct = 0.0

    return {
        "calendar_days": days,
        "sample_days": len(window_values),
        "average_best_rate": round(average_rate, 6),
        "highest_best_rate": round(highest_rate, 6),
        "lowest_best_rate": round(lowest_rate, 6),
        "current_vs_average_pct": round(
            current_vs_average_pct,
            3,
        ),
        "is_current_period_high": current_rate >= highest_rate,
        "is_current_period_low": current_rate <= lowest_rate,
    }


def build_market_intelligence(
    seven_day: dict[str, Any] | None,
    thirty_day: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Convert historical statistics into a simple market position
    and remittance recommendation.
    """
    reference_window = "30_day" if thirty_day else "7_day"
    reference = thirty_day or seven_day

    if not reference:
        return {
            "position": "insufficient_data",
            "recommendation": "neutral",
            "headline": "Not enough historical data",
            "message": (
                "More rate history is needed before making a reliable "
                "market comparison."
            ),
            "reference_window": None,
            "sample_days": 0,
        }

    vs_average = float(reference["current_vs_average_pct"])
    is_period_high = bool(reference["is_current_period_high"])
    is_period_low = bool(reference["is_current_period_low"])
    sample_days = int(reference["sample_days"])

    common_fields = {
        "reference_window": reference_window,
        "sample_days": sample_days,
    }

    if sample_days < 5:
        direction = "above" if vs_average >= 0 else "below"

        return {
            "position": "limited_history",
            "recommendation": "neutral",
            "headline": "Early market signal",
            "message": (
                f"The current best rate is {abs(vs_average):.2f}% "
                f"{direction} the recent average, but more historical "
                "data is needed."
            ),
            **common_fields,
        }

    if is_period_high or vs_average >= 0.75:
        return {
            "position": "strong",
            "recommendation": "good_time",
            "headline": "Good time to remit",
            "message": (
                f"The current best rate is {vs_average:.2f}% above "
                "the recent average."
            ),
            **common_fields,
        }

    if vs_average >= 0.20:
        return {
            "position": "above_average",
            "recommendation": "favorable",
            "headline": "Rates are above average",
            "message": (
                f"The current best rate is {vs_average:.2f}% above "
                "the recent average."
            ),
            **common_fields,
        }

    if is_period_low or vs_average <= -0.75:
        return {
            "position": "weak",
            "recommendation": "consider_waiting",
            "headline": "Rates are relatively weak",
            "message": (
                f"The current best rate is {abs(vs_average):.2f}% below "
                "the recent average."
            ),
            **common_fields,
        }

    if vs_average <= -0.20:
        return {
            "position": "below_average",
            "recommendation": "cautious",
            "headline": "Rates are below average",
            "message": (
                f"The current best rate is {abs(vs_average):.2f}% below "
                "the recent average."
            ),
            **common_fields,
        }

    return {
        "position": "average",
        "recommendation": "neutral",
        "headline": "Market conditions are stable",
        "message": (
            "The current best rate is close to the recent average."
        ),
        **common_fields,
    }


def export_analytics() -> None:
    latest_path = DATA_DIR / "latest.json"
    dashboard_path = DATA_DIR / "dashboard.json"
    health_path = DATA_DIR / "collector_health.json"
    history_path = DATA_DIR / "history.json"

    latest = load_json(latest_path)
    dashboard = load_json(dashboard_path)

    health = load_json(health_path) if health_path.exists() else None
    history = load_json(history_path) if history_path.exists() else {}

    companies = list(latest.values())

    if not companies:
        raise Exception("No latest rate data found for analytics.")

    rates = [
        float(company["rate"])
        for company in companies
    ]

    best_rate_company = max(
        companies,
        key=lambda company: float(company["rate"]),
    )

    lowest_rate_company = min(
        companies,
        key=lambda company: float(company["rate"]),
    )

    best_total_company = dashboard["companies"][0]

    average_rate = round(sum(rates) / len(rates), 6)
    highest_rate = float(best_rate_company["rate"])
    lowest_rate = float(lowest_rate_company["rate"])
    rate_spread = round(highest_rate - lowest_rate, 6)

    daily_best_rates = build_daily_best_rates(history)

    seven_day_stats = calculate_window_stats(
        daily_best_rates,
        highest_rate,
        7,
    )

    thirty_day_stats = calculate_window_stats(
        daily_best_rates,
        highest_rate,
        30,
    )

    historical_market = {
        "daily_sample_count": len(daily_best_rates),
        "7_day": seven_day_stats,
        "30_day": thirty_day_stats,
    }

    market_intelligence = build_market_intelligence(
        seven_day_stats,
        thirty_day_stats,
    )

    analytics = {
        "last_updated": dashboard["last_updated"],
        "target_npr": dashboard["target_npr"],
        "deposit_method": dashboard["deposit_method"],
        "best_by_total_cost": {
            "company": best_total_company["company_name"],
            "required_jpy": best_total_company["required_jpy"],
            "rate": float(best_total_company["rate"]),
            "service_fee": best_total_company["service_fee"],
            "deposit_fee": best_total_company["deposit_fee"],
        },
        "best_by_rate": {
            "company": best_rate_company["company_name"],
            "rate": highest_rate,
        },
        "lowest_by_rate": {
            "company": lowest_rate_company["company_name"],
            "rate": lowest_rate,
        },
        "market": {
            "average_rate": average_rate,
            "highest_rate": highest_rate,
            "lowest_rate": lowest_rate,
            "rate_spread": rate_spread,
            "provider_count": len(companies),
        },
        "historical_market": historical_market,
        "market_intelligence": market_intelligence,
        "collector_health": (
            health["summary"]
            if health
            else None
        ),
    }

    DATA_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)

    data_path = DATA_DIR / "analytics.json"
    export_path = EXPORT_DIR / "analytics.json"

    with data_path.open("w", encoding="utf-8") as file:
        json.dump(
            analytics,
            file,
            ensure_ascii=False,
            indent=4,
        )

    shutil.copyfile(data_path, export_path)

    print("analytics.json exported.")


if __name__ == "__main__":
    export_analytics()