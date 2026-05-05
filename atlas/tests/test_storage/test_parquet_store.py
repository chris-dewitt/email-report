"""Tests for parquet read/write helpers."""

import polars as pl

from atlas.storage.parquet_store import (
    write_bronze,
    read_bronze,
    write_silver,
    read_silver,
    write_gold,
    read_gold,
)


def test_bronze_write_read(sample_daily_df, tmp_data_dir):
    """Write and read back a bronze parquet."""
    path = write_bronze(sample_daily_df, "TEST_SERIES", "fred")
    assert path.exists()

    df = read_bronze("TEST_SERIES", "fred")
    assert df is not None
    assert "date" in df.columns
    assert "value" in df.columns
    assert "source" in df.columns
    assert "series_id" in df.columns
    assert len(df) == len(sample_daily_df)


def test_bronze_read_missing(tmp_data_dir):
    """Reading a missing bronze file returns None."""
    assert read_bronze("NONEXISTENT", "fred") is None


def test_silver_write_read(sample_daily_df, tmp_data_dir):
    """Write and read back a silver parquet."""
    write_silver(sample_daily_df, "test_aligned", sub="aligned")
    df = read_silver("test_aligned", sub="aligned")
    assert df is not None
    assert len(df) == len(sample_daily_df)


def test_gold_write_read(sample_daily_df, tmp_data_dir):
    """Write and read back a gold parquet."""
    write_gold(sample_daily_df, "test_features", sub="features")
    df = read_gold("test_features", sub="features")
    assert df is not None
    assert len(df) == len(sample_daily_df)
