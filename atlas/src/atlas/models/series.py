"""Pydantic models for series data contracts."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class SeriesMeta(BaseModel):
    """Metadata for a tracked macro series."""
    series_id: str
    name: str
    source: str
    frequency: str
    theme: str
    unit: str = ""
    description: str = ""
    last_updated: date | None = None
    latest_value: float | None = None


class SeriesPoint(BaseModel):
    """A single data point in a time series."""
    date: date
    value: float


class SeriesStats(BaseModel):
    """Summary statistics for a series."""
    mean: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    latest: float | None = None
    latest_z: float | None = None
    change_1w: float | None = None
    change_1m: float | None = None
    pct_rank: float | None = None


class SeriesHistoryResponse(BaseModel):
    """Full history response for a single series."""
    series_id: str
    meta: SeriesMeta
    data: list[SeriesPoint]
    stats: SeriesStats


class SeriesListResponse(BaseModel):
    """Response for series listing endpoint."""
    series: list[SeriesMeta]
    count: int
