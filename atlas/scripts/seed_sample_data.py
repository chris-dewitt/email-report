"""Generate synthetic but realistic sample data for offline development and testing.

Run: python scripts/seed_sample_data.py
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
import math
import random

# Add src to path so we can import atlas modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import polars as pl
from atlas.ingest.registry import SERIES_CATALOG, Frequency
from atlas.storage.paths import ensure_dirs, bronze_dir


def _generate_business_days(start: date, end: date) -> list[date]:
    """Generate business days between start and end."""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:  # Mon-Fri
            days.append(current)
        current += timedelta(days=1)
    return days


def _generate_series(
    dates: list[date],
    base: float,
    volatility: float,
    trend: float = 0.0,
    mean_revert: float = 0.0,
) -> list[float]:
    """Generate a synthetic time series with drift, volatility, and mean-reversion."""
    values = [base]
    for i in range(1, len(dates)):
        prev = values[-1]
        mr = mean_revert * (base - prev)  # pull toward base
        drift = trend / 252  # daily drift
        shock = random.gauss(0, volatility / math.sqrt(252))
        new_val = prev + mr + drift + shock
        values.append(round(new_val, 4))
    return values


# Realistic parameters for each series
SERIES_PARAMS: dict[str, dict] = {
    # Inflation
    "CPIAUCSL": {"base": 300, "vol": 0.5, "trend": 3.0},
    "CPILFESL": {"base": 310, "vol": 0.3, "trend": 2.5},
    "PCEPI": {"base": 120, "vol": 0.3, "trend": 2.5},
    "PCEPILFE": {"base": 122, "vol": 0.2, "trend": 2.0},
    "T5YIE": {"base": 2.3, "vol": 0.4, "trend": 0.0, "mr": 0.02},
    "T10YIE": {"base": 2.3, "vol": 0.3, "trend": 0.0, "mr": 0.02},
    "MICH": {"base": 3.0, "vol": 0.5, "trend": 0.0, "mr": 0.05},
    # Labor
    "PAYEMS": {"base": 155000, "vol": 100, "trend": 200},
    "UNRATE": {"base": 4.0, "vol": 0.3, "trend": 0.0, "mr": 0.02},
    "ICSA": {"base": 220, "vol": 15, "trend": 0.0, "mr": 0.05},
    "CCSA": {"base": 1700, "vol": 50, "trend": 0.0, "mr": 0.03},
    "CES0500000003": {"base": 30.0, "vol": 0.1, "trend": 0.5},
    "JTSJOL": {"base": 8000, "vol": 200, "trend": 0.0, "mr": 0.02},
    "JTSQUR": {"base": 2.5, "vol": 0.2, "trend": 0.0, "mr": 0.03},
    # Rates
    "DFF": {"base": 5.0, "vol": 0.3, "trend": 0.0, "mr": 0.01},
    "DGS2": {"base": 4.5, "vol": 0.5, "trend": 0.0, "mr": 0.01},
    "DGS10": {"base": 4.2, "vol": 0.4, "trend": 0.0, "mr": 0.01},
    "DGS30": {"base": 4.5, "vol": 0.3, "trend": 0.0, "mr": 0.01},
    "T10Y2Y": {"base": 0.2, "vol": 0.3, "trend": 0.0, "mr": 0.03},
    "T10Y3M": {"base": 0.5, "vol": 0.4, "trend": 0.0, "mr": 0.03},
    "DFII10": {"base": 2.0, "vol": 0.3, "trend": 0.0, "mr": 0.01},
    # Financial Conditions
    "BAMLH0A0HYM2": {"base": 3.5, "vol": 0.5, "trend": 0.0, "mr": 0.03},
    "BAMLC0A4CBBB": {"base": 1.5, "vol": 0.2, "trend": 0.0, "mr": 0.03},
    "NFCI": {"base": -0.3, "vol": 0.2, "trend": 0.0, "mr": 0.05},
    "STLFSI2": {"base": -0.5, "vol": 0.3, "trend": 0.0, "mr": 0.05},
    "VIXCLS": {"base": 18.0, "vol": 5.0, "trend": 0.0, "mr": 0.05},
    "TEDRATE": {"base": 0.3, "vol": 0.1, "trend": 0.0, "mr": 0.05},
    # Growth
    "GDP": {"base": 28000, "vol": 200, "trend": 500},
    "GDPC1": {"base": 22000, "vol": 150, "trend": 300},
    "INDPRO": {"base": 104, "vol": 0.5, "trend": 1.0},
    "RSAFS": {"base": 700000, "vol": 5000, "trend": 10000},
    "NAPM": {"base": 50, "vol": 2.0, "trend": 0.0, "mr": 0.05},
    # FX / Market
    "DX-Y.NYB": {"base": 104, "vol": 3.0, "trend": 0.0, "mr": 0.01},
    "EURUSD=X": {"base": 1.08, "vol": 0.03, "trend": 0.0, "mr": 0.01},
    "JPY=X": {"base": 150, "vol": 5.0, "trend": 0.0, "mr": 0.005},
    "^GSPC": {"base": 5000, "vol": 200, "trend": 300},
}


def main() -> None:
    random.seed(42)

    ensure_dirs()

    start = date(2020, 1, 2)
    end = date(2026, 3, 28)
    business_days = _generate_business_days(start, end)

    # Sample frequencies
    monthly_dates = [d for d in business_days if d.day <= 7 and d.weekday() == 0][:75]
    weekly_dates = business_days[::5][:325]
    quarterly_dates = monthly_dates[::3][:25]

    generated = 0
    for sd in SERIES_CATALOG:
        params = SERIES_PARAMS.get(sd.series_id, {"base": 100, "vol": 1.0, "trend": 0.0})

        # Pick dates based on frequency
        if sd.frequency == Frequency.QUARTERLY:
            dates = quarterly_dates
        elif sd.frequency == Frequency.MONTHLY:
            dates = monthly_dates
        elif sd.frequency == Frequency.WEEKLY:
            dates = weekly_dates
        else:
            dates = business_days

        values = _generate_series(
            dates,
            base=params["base"],
            volatility=params["vol"],
            trend=params.get("trend", 0.0),
            mean_revert=params.get("mr", 0.0),
        )

        df = pl.DataFrame({
            "date": dates,
            "value": [float(v) for v in values[:len(dates)]],
        }, schema={"date": pl.Date, "value": pl.Float64})

        # Write to bronze
        source = sd.source.value
        path = bronze_dir(source) / f"{sd.series_id}.parquet"
        enriched = df.with_columns(
            pl.lit(source).alias("source"),
            pl.lit(sd.series_id).alias("series_id"),
            pl.lit("2026-03-28T00:00:00").str.to_datetime().alias("pulled_at"),
        )
        enriched.write_parquet(path)
        generated += 1

    print(f"[OK] Generated {generated} synthetic series in data/bronze/")


if __name__ == "__main__":
    main()
