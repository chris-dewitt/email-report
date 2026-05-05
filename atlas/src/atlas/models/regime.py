"""Pydantic models for regime snapshot contracts."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class RegimeDriver(BaseModel):
    """A driver contributing to the current regime classification."""
    description: str
    value: float | None = None
    z_score: float | None = None


class RegimePoint(BaseModel):
    """A single point in regime history."""
    date: date
    regime: str
    confidence: float


class RegimeSnapshotResponse(BaseModel):
    """Response for regime-snapshot endpoint."""
    regime: str
    confidence: float
    as_of: date
    drivers: list[str]
    all_scores: dict[str, float]
    history: list[RegimePoint] = []
