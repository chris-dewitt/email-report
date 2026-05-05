"""Read/write helpers for the bronze/silver/gold parquet lake."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from atlas.storage.paths import bronze_dir, silver_dir, gold_dir


# ── Bronze ──────────────────────────────────────────────────────────────────

def write_bronze(
    df: pl.DataFrame,
    series_id: str,
    source: str,
) -> Path:
    """Write a raw series to the bronze layer.

    Expects columns: date (Date), value (Float64).
    Adds: source, series_id, pulled_at.
    """
    enriched = df.with_columns(
        pl.lit(source).alias("source"),
        pl.lit(series_id).alias("series_id"),
        pl.lit(datetime.now(timezone.utc)).alias("pulled_at"),
    )
    path = bronze_dir(source) / f"{series_id}.parquet"
    enriched.write_parquet(path)
    return path


def read_bronze(series_id: str, source: str) -> pl.DataFrame | None:
    """Read a bronze parquet for a given series. Returns None if missing."""
    path = bronze_dir(source) / f"{series_id}.parquet"
    if not path.exists():
        return None
    return pl.read_parquet(path)


def read_all_bronze(source: str | None = None) -> pl.DataFrame:
    """Read all bronze parquets, optionally filtered by source."""
    base = bronze_dir(source) if source else bronze_dir()
    files = list(base.rglob("*.parquet"))
    if not files:
        return pl.DataFrame()
    return pl.concat([pl.read_parquet(f) for f in files], how="diagonal_relaxed")


# ── Silver ──────────────────────────────────────────────────────────────────

def write_silver(df: pl.DataFrame, name: str, sub: str = "aligned") -> Path:
    """Write a processed DataFrame to the silver layer."""
    path = silver_dir(sub) / f"{name}.parquet"
    df.write_parquet(path)
    return path


def read_silver(name: str, sub: str = "aligned") -> pl.DataFrame | None:
    path = silver_dir(sub) / f"{name}.parquet"
    if not path.exists():
        return None
    return pl.read_parquet(path)


# ── Gold ────────────────────────────────────────────────────────────────────

def write_gold(df: pl.DataFrame, name: str, sub: str = "features") -> Path:
    """Write a feature or regime DataFrame to the gold layer."""
    path = gold_dir(sub) / f"{name}.parquet"
    df.write_parquet(path)
    return path


def read_gold(name: str, sub: str = "features") -> pl.DataFrame | None:
    path = gold_dir(sub) / f"{name}.parquet"
    if not path.exists():
        return None
    return pl.read_parquet(path)
