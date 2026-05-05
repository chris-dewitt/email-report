"""yfinance connector — pulls FX, VIX, and equity market data."""

from __future__ import annotations

from datetime import date

import polars as pl
import yfinance as yf

from atlas.ingest.base import BaseConnector
from atlas.ingest.registry import SeriesDef, Source


class YFinanceConnector(BaseConnector):
    """Connector for Yahoo Finance market data."""

    def supports(self, series_def: SeriesDef) -> bool:
        return series_def.source == Source.YFINANCE

    def pull(self, series_def: SeriesDef, start: date | None = None) -> pl.DataFrame:
        """Pull a yfinance ticker and return closing prices as polars DataFrame.

        Returns DataFrame with columns: date (Date), value (Float64).
        """
        start_str = (start or date(2015, 1, 1)).isoformat()

        ticker = yf.Ticker(series_def.series_id)
        hist = ticker.history(start=start_str, auto_adjust=True)

        if hist is None or hist.empty:
            return pl.DataFrame({"date": [], "value": []}).cast(
                {"date": pl.Date, "value": pl.Float64}
            )

        # Use closing price as the value
        pdf = hist[["Close"]].reset_index()
        pdf.columns = ["date", "value"]

        # yfinance returns timezone-aware datetimes; strip tz for Date cast
        df = pl.from_pandas(pdf).with_columns(
            pl.col("date").cast(pl.Datetime("us")).dt.date().alias("date"),
            pl.col("value").cast(pl.Float64),
        ).drop_nulls(subset=["value"])

        return df.sort("date")
