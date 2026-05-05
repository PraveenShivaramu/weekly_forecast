import pandas as pd
import math


def weighted_average(values):
    """
    Gives more importance to recent values.
    Example with 4 values:
    oldest = 10%
    next = 20%
    next = 30%
    latest = 40%
    """
    values = list(values)

    if len(values) == 0:
        return 0

    weights = list(range(1, len(values) + 1))
    weighted_sum = sum(v * w for v, w in zip(values, weights))
    total_weight = sum(weights)

    return weighted_sum / total_weight


def forecast_one_wave(df_wave, target_date, history_weeks=4, buffer_pct=10):
    weekday = target_date.day_name()

    hist = df_wave[
        (df_wave["Date"] < target_date) &
        (df_wave["Day"] == weekday)
    ].sort_values("Date")

    hist = hist.tail(history_weeks)

    if hist.empty:
        return {
            "Expected Orders": 0,
            "Expected Productivity": 0,
            "Drivers Needed": 0,
            "History Used": 0,
        }

    expected_orders = weighted_average(hist["Orders Assigned"])

    productivity_series = hist["Orders Delivered"] / hist["Drivers Used"]
    productivity_series = (
        productivity_series
        .replace([float("inf"), -float("inf")], pd.NA)
        .dropna()
    )

    expected_productivity = weighted_average(productivity_series)

    if expected_productivity > 0:
        drivers_needed = math.ceil(
            (expected_orders / expected_productivity) * (1 + buffer_pct / 100)
        )
    else:
        drivers_needed = 0

    return {
        "Expected Orders": round(expected_orders),
        "Expected Productivity": round(expected_productivity, 1),
        "Drivers Needed": drivers_needed,
        "History Used": len(hist),
    }


def forecast_range(df, station, from_date, to_date, history_weeks=4, buffer_pct=10):
    date_range = pd.date_range(from_date, to_date, freq="D")

    station_df = df[df["Station"] == station].copy()

    results = []

    for target_date in date_range:
        for wave in ["Morning", "Afternoon"]:
            df_wave = station_df[station_df["Wave"] == wave].copy()

            result = forecast_one_wave(
                df_wave=df_wave,
                target_date=target_date,
                history_weeks=history_weeks,
                buffer_pct=buffer_pct,
            )

            results.append({
                "Date": target_date.date(),
                "Day": target_date.day_name(),
                "Wave": wave,
                **result
            })

    return pd.DataFrame(results)