"""Pydantic models for health check contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DataQualityReport(BaseModel):
    """Summary of data quality metrics."""
    stale_series: list[str] = []
    missing_series: list[str] = []
    total_series: int = 0
    available_series: int = 0


class HealthResponse(BaseModel):
    """Response for /health endpoint."""
    status: Literal["ok", "degraded", "error"]
    last_pull: datetime | None = None
    series_count: int = 0
    feature_count: int = 0
    data_quality: DataQualityReport = DataQualityReport()
