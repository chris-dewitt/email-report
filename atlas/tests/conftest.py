"""Shared test fixtures and configuration."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import polars as pl


@pytest.fixture(autouse=True)
def tmp_data_dir(monkeypatch, tmp_path):
    """Override ATLAS_DATA_DIR to use a temp directory for all tests."""
    monkeypatch.setenv("ATLAS_DATA_DIR", str(tmp_path / "data"))

    # Clear the cached settings so they reload with new env
    from atlas.config import get_settings
    get_settings.cache_clear()

    from atlas.storage.paths import ensure_dirs
    ensure_dirs()

    yield tmp_path / "data"

    # Clean up cache
    get_settings.cache_clear()


@pytest.fixture
def sample_daily_df() -> pl.DataFrame:
    """A small sample daily time series for testing."""
    import datetime
    start = datetime.date(2024, 1, 1)
    dates = []
    current = start
    while len(dates) < 60:
        if current.weekday() < 5:
            dates.append(current)
        current += datetime.timedelta(days=1)
    values = [100.0 + i * 0.1 + ((-1) ** i) * 0.05 for i in range(len(dates))]
    return pl.DataFrame({"date": dates, "value": values}).cast(
        {"date": pl.Date, "value": pl.Float64}
    )


@pytest.fixture
def sample_monthly_df() -> pl.DataFrame:
    """A small sample monthly time series for testing."""
    import datetime
    dates = [datetime.date(2022, m, 1) for m in range(1, 13)] + \
            [datetime.date(2023, m, 1) for m in range(1, 13)] + \
            [datetime.date(2024, m, 1) for m in range(1, 7)]
    values = [100.0 + i * 0.5 for i in range(len(dates))]
    return pl.DataFrame({"date": dates, "value": values}).cast(
        {"date": pl.Date, "value": pl.Float64}
    )
