"""Pydantic models for feature group contracts."""

from __future__ import annotations

from pydantic import BaseModel


class FeatureMeta(BaseModel):
    """Metadata for a computed feature."""
    feature_id: str
    base_series: str
    transform: str
    latest_value: float | None = None
    latest_z: float | None = None
    change_1w: float | None = None


class FeatureGroup(BaseModel):
    """A themed group of features."""
    theme: str
    features: list[FeatureMeta]
    pca_factor_value: float | None = None


class FeatureGroupResponse(BaseModel):
    """Response for feature-groups endpoint."""
    groups: list[FeatureGroup]
