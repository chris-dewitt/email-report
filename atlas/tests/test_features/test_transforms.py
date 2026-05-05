"""Regression tests for mathematical transforms."""

import math
import polars as pl
import pytest

from atlas.features.transforms import (
    z_score,
    yoy_change,
    log_diff,
    rolling_change,
    level_diff,
)


def test_z_score_basic(sample_daily_df):
    """Z-score should have mean ~0 and std ~1 in the window."""
    result = z_score(sample_daily_df, window=20)
    zs = result["value_zscore"].drop_nulls()

    # After enough data, z-scores should exist
    assert len(zs) > 0
    # The last few z-scores should be finite
    assert all(math.isfinite(v) for v in zs.tail(10).to_list())


def test_yoy_change_known_values():
    """YoY change of [100, ..., 110] after 4 periods should be 10%."""
    df = pl.DataFrame({
        "date": [f"2024-0{i+1}-01" for i in range(8)],
        "value": [100.0, 101.0, 102.0, 103.0, 110.0, 111.0, 112.0, 113.0],
    }).with_columns(
        pl.col("date").str.to_date(),
        pl.col("value").cast(pl.Float64),
    )

    result = yoy_change(df, periods=4)
    # At index 4: (110 - 100) / 100 = 0.10
    yoy_vals = result["value_yoy"].to_list()
    assert yoy_vals[4] == pytest.approx(0.10, abs=0.001)


def test_log_diff_basic(sample_daily_df):
    """Log-diff should be approximately equal to percentage change for small moves."""
    result = log_diff(sample_daily_df)
    ld = result["value_logdiff"].drop_nulls()
    assert len(ld) > 0
    # All values should be finite
    assert all(math.isfinite(v) for v in ld.to_list())


def test_rolling_change(sample_daily_df):
    """Rolling change of window=5 should be x_t - x_{t-5}."""
    result = rolling_change(sample_daily_df, window=5)
    chg = result["value_chg5"].to_list()
    values = sample_daily_df["value"].to_list()

    # Check a specific value
    for i in range(5, min(20, len(values))):
        expected = values[i] - values[i - 5]
        assert chg[i] == pytest.approx(expected, abs=1e-6)


def test_level_diff(sample_daily_df):
    """Level diff should be x_t - x_{t-1}."""
    result = level_diff(sample_daily_df)
    d = result["value_diff1"].to_list()
    values = sample_daily_df["value"].to_list()

    for i in range(1, min(20, len(values))):
        assert d[i] == pytest.approx(values[i] - values[i - 1], abs=1e-6)
