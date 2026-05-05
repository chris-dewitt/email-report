"""FRED API connector — pulls macro series via fredapi."""

from __future__ import annotations

from datetime import date

import polars as pl
from fredapi import Fred

from atlas.config import get_settings
from atlas.ingest.base import BaseConnector
from atlas.ingest.registry import SeriesDef, Source


class FredConnector(BaseConnector):
    """Connector for FRED (Federal Reserve Economic Data)."""

    def __init__(self, api_key: str | None = None):
        key = api_key or get_settings().fred_api_key
        if not key:
            raise ValueError(
                "FRED_API_KEY not set. Add it to .env or pass it directly."
            )
        self._fred = Fred(api_key=key)

    def supports(self, series_def: SeriesDef) -> bool:
        return series_def.source == Source.FRED

    def pull(self, series_def: SeriesDef, start: date | None = None) -> pl.DataFrame:
        """Pull a FRED series and return as polars DataFrame.

        Returns DataFrame with columns: date (Date), value (Float64).
        """
        start_str = (start or date(2015, 1, 1)).isoformat()

        # fredapi returns a pandas Series with DatetimeIndex
        pd_series = self._fred.get_series(
            series_def.series_id,
            observation_start=start_str,
        )

        if pd_series is None or pd_series.empty:
            return pl.DataFrame({"date": [], "value": []}).cast(
                {"date": pl.Date, "value": pl.Float64}
            )

        # Convert pandas Series → polars DataFrame
        pdf = pd_series.reset_index()
        pdf.columns = ["date", "value"]

        df = pl.from_pandas(pdf).with_columns(
            pl.col("date").cast(pl.Date),
            pl.col("value").cast(pl.Float64),
        ).drop_nulls(subset=["value"])

        return df.sort("date")
