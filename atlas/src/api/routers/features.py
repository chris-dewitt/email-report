"""Feature group endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from atlas.models.features import FeatureGroupResponse, FeatureGroup, FeatureMeta
from atlas.ingest.registry import Theme
from atlas.storage.parquet_store import read_gold

router = APIRouter()


@router.get("/feature-groups", response_model=FeatureGroupResponse)
async def list_feature_groups() -> FeatureGroupResponse:
    """List all themed feature groups with latest values and z-scores."""
    groups: list[FeatureGroup] = []

    for theme in Theme:
        df = read_gold(theme.value, sub="features")
        if df is None or df.is_empty():
            continue

        features: list[FeatureMeta] = []
        series_ids = df["series_id"].unique().to_list()

        for sid in series_ids:
            subset = df.filter(df["series_id"] == sid).sort("date")
            if subset.is_empty():
                continue

            last_row = subset.tail(1)
            latest_val = last_row["value"][0] if "value" in last_row.columns else None
            latest_z = last_row["value_zscore"][0] if "value_zscore" in last_row.columns else None

            features.append(FeatureMeta(
                feature_id=f"{sid}_level",
                base_series=sid,
                transform="level",
                latest_value=round(latest_val, 4) if latest_val is not None else None,
                latest_z=round(latest_z, 4) if latest_z is not None else None,
            ))

        groups.append(FeatureGroup(
            theme=theme.value,
            features=features,
        ))

    return FeatureGroupResponse(groups=groups)
