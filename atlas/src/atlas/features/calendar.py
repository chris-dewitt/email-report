"""Frequency alignment and business-day resampling.

Converts all series to a common business-day calendar without look-ahead bias.
"""

from __future__ import annotations

from datetime import date, timedelta

import polars as pl

from atlas.ingest.registry import Frequency


def generate_business_days(start: date, end: date) -> pl.DataFrame:
    """Generate a DataFrame of business days between start and end."""
    all_dates = pl.date_range(start, end, interval="1d", eager=True)
    # Filter to weekdays (Mon=1 ... Fri=5 in polars)
    bdays = all_dates.filter(all_dates.dt.weekday() < 6)  # polars: Mon=1, Sun=7
    return pl.DataFrame({"date": bdays})


def align_to_business_days(
    df: pl.DataFrame,
    frequency: Frequency,
    calendar: pl.DataFrame,
) -> pl.DataFrame:
    """Align a series to the business-day calendar.

    Strategy by original frequency:
        - Daily: join directly, forward-fill gaps (weekends/holidays already absent)
        - Weekly: join, forward-fill across the week
        - Monthly/Quarterly: point-in-time join — value appears on publication date,
          forward-filled until next publication. No look-ahead.

    Args:
        df: DataFrame with columns [date, value].
        frequency: Original frequency of the series.
        calendar: Business-day calendar DataFrame with column [date].

    Returns:
        DataFrame aligned to calendar with columns [date, value, is_filled].
    """
    # Sort both
    df = df.sort("date")
    calendar = calendar.sort("date")

    # Left join calendar to data
    aligned = calendar.join(df.select("date", "value"), on="date", how="left")

    # Mark filled rows
    aligned = aligned.with_columns(
        pl.col("value").is_null().alias("is_filled")
    )

    # Forward-fill
    aligned = aligned.with_columns(
        pl.col("value").forward_fill()
    )

    # Add metadata
    aligned = aligned.with_columns(
        pl.lit(frequency.value).alias("frequency_original"),
    )

    return aligned


def align_all_series(
    series_dict: dict[str, tuple[pl.DataFrame, Frequency]],
    start: date | None = None,
    end: date | None = None,
) -> dict[str, pl.DataFrame]:
    """Align all series to a common business-day calendar.

    Args:
        series_dict: Mapping of series_id -> (DataFrame, Frequency).
        start: Calendar start (default: earliest date in data).
        end: Calendar end (default: latest date in data).

    Returns:
        Dict mapping series_id -> aligned DataFrame.
    """
    if not series_dict:
        return {}

    # Determine calendar range
    all_dates: list[date] = []
    for df, _ in series_dict.values():
        if not df.is_empty():
            dates = df["date"].to_list()
            all_dates.extend(dates)

    if not all_dates:
        return {}

    cal_start = start or min(all_dates)
    cal_end = end or max(all_dates)
    calendar = generate_business_days(cal_start, cal_end)

    result: dict[str, pl.DataFrame] = {}
    for sid, (df, freq) in series_dict.items():
        if df.is_empty():
            continue
        result[sid] = align_to_business_days(df, freq, calendar)

    return result
