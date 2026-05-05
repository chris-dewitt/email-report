"""Market data store for event studies — pulls from FRED + yfinance."""

from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

import polars as pl
import yfinance as yf
from rich.console import Console

from fedlens.config import get_settings
from fedlens.storage.paths import data_root

console = Console()

# Market series used for event studies
MARKET_SERIES = {
    "DGS2": {"source": "fred", "name": "2Y Treasury Yield"},
    "DGS10": {"source": "fred", "name": "10Y Treasury Yield"},
    "DGS30": {"source": "fred", "name": "30Y Treasury Yield"},
    "T10Y2Y": {"source": "fred", "name": "10Y-2Y Spread"},
    "VIXCLS": {"source": "fred", "name": "VIX"},
    "DFF": {"source": "fred", "name": "Fed Funds Effective"},
    "SPX": {"source": "yfinance", "name": "S&P 500", "ticker": "^GSPC"},
}


def _market_data_dir() -> Path:
    d = data_root() / "bronze" / "market"
    d.mkdir(parents=True, exist_ok=True)
    return d


def pull_market_data(start_date: str = "2010-01-01") -> None:
    """Pull all market series and save to bronze parquets.

    First tries to copy from Atlas's existing bronze data, then falls back
    to FRED/yfinance.
    """
    console.print("\n[cyan]Pulling market data...[/cyan]")

    # Try to copy from Atlas first
    atlas_bronze = Path("C:/Users/DELL/ClaudePlayground/atlas/data/bronze")
    atlas_fred = atlas_bronze / "fred"
    atlas_yf = atlas_bronze / "yfinance"

    for series_id, spec in MARKET_SERIES.items():
        dest = _market_data_dir() / f"{series_id}.parquet"
        if dest.exists():
            continue

        # Check Atlas
        copied = False
        if spec["source"] == "fred" and atlas_fred.exists():
            src = atlas_fred / f"{series_id}.parquet"
            if src.exists():
                df = pl.read_parquet(src).select(["date", "value"]).drop_nulls()
                df.write_parquet(dest)
                console.print(f"  {series_id}: [yellow]{len(df)}[/yellow] obs (from Atlas)")
                copied = True
        elif spec["source"] == "yfinance" and atlas_yf.exists():
            ticker = spec.get("ticker", series_id)
            # Atlas uses ticker as filename
            src = atlas_yf / f"{ticker}.parquet"
            if src.exists():
                df = pl.read_parquet(src).select(["date", "value"]).drop_nulls()
                df.write_parquet(dest)
                console.print(f"  {series_id}: [yellow]{len(df)}[/yellow] obs (from Atlas)")
                copied = True

        if not copied:
            if spec["source"] == "fred":
                _pull_fred(series_id, start_date)
            elif spec["source"] == "yfinance":
                _pull_yfinance(series_id, spec["ticker"], start_date)


def _pull_fred(series_id: str, start_date: str) -> None:
    """Pull a FRED series."""
    try:
        from fredapi import Fred

        api_key = os.environ.get("FRED_API_KEY")
        if not api_key:
            console.print(f"  [red]FRED_API_KEY not set, skipping {series_id}[/red]")
            return

        fred = Fred(api_key=api_key)
        data = fred.get_series(series_id, observation_start=start_date)

        if data is not None and len(data) > 0:
            df = pl.DataFrame({
                "date": data.index.date.tolist(),
                "value": data.values.tolist(),
            }).filter(pl.col("value").is_not_null()).filter(pl.col("value").is_not_nan())

            df.write_parquet(_market_data_dir() / f"{series_id}.parquet")
            console.print(f"  {series_id}: [yellow]{len(df)}[/yellow] observations")
    except Exception as e:
        console.print(f"  [red]{series_id} failed: {e}[/red]")


def _pull_yfinance(series_id: str, ticker: str, start_date: str) -> None:
    """Pull a yfinance series."""
    try:
        data = yf.download(ticker, start=start_date, progress=False)
        if data is not None and len(data) > 0:
            df = pl.DataFrame({
                "date": data.index.date.tolist(),
                "value": data["Close"].values.tolist(),
            }).filter(pl.col("value").is_not_null())

            df.write_parquet(_market_data_dir() / f"{series_id}.parquet")
            console.print(f"  {series_id}: [yellow]{len(df)}[/yellow] observations")
    except Exception as e:
        console.print(f"  [red]{series_id} failed: {e}[/red]")


def get_daily_returns(series_id: str) -> pl.DataFrame | None:
    """Load a market series and compute daily returns.

    Returns DataFrame: date, value, return (daily log return).
    """
    path = _market_data_dir() / f"{series_id}.parquet"
    if not path.exists():
        return None

    df = pl.read_parquet(path).sort("date")

    # For yields (DGS*, DFF, T10Y2Y, VIXCLS): use daily change in levels (bps)
    # For prices (SPX): use log returns
    is_yield = series_id.startswith("DGS") or series_id in ("DFF", "T10Y2Y", "VIXCLS")

    if is_yield:
        df = df.with_columns(
            (pl.col("value") - pl.col("value").shift(1)).alias("daily_return")
        )
    else:
        df = df.with_columns(
            (pl.col("value").log() - pl.col("value").log().shift(1)).alias("daily_return")
        )

    return df.drop_nulls("daily_return")
