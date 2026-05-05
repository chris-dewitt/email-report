"""Feature metadata catalog — describes all available computed features."""

from __future__ import annotations

from dataclasses import dataclass
from atlas.ingest.registry import Theme


@dataclass(frozen=True)
class FeatureDef:
    """Metadata for a computed feature."""
    feature_id: str          # e.g., "CPIAUCSL_yoy"
    base_series: str         # e.g., "CPIAUCSL"
    transform: str           # e.g., "yoy", "zscore", "logdiff"
    theme: Theme
    description: str = ""


def build_feature_catalog() -> list[FeatureDef]:
    """Generate the full feature catalog from the series catalog and transforms."""
    from atlas.ingest.registry import SERIES_CATALOG, Frequency

    features: list[FeatureDef] = []

    for sd in SERIES_CATALOG:
        # Every series gets a z-score
        features.append(FeatureDef(
            feature_id=f"{sd.series_id}_zscore",
            base_series=sd.series_id,
            transform="zscore",
            theme=sd.theme,
            description=f"Rolling z-score of {sd.name}",
        ))

        if sd.frequency == Frequency.DAILY:
            features.append(FeatureDef(
                feature_id=f"{sd.series_id}_chg5",
                base_series=sd.series_id,
                transform="rolling_change_5",
                theme=sd.theme,
                description=f"1-week change of {sd.name}",
            ))
            features.append(FeatureDef(
                feature_id=f"{sd.series_id}_chg21",
                base_series=sd.series_id,
                transform="rolling_change_21",
                theme=sd.theme,
                description=f"1-month change of {sd.name}",
            ))
            features.append(FeatureDef(
                feature_id=f"{sd.series_id}_logdiff",
                base_series=sd.series_id,
                transform="log_diff",
                theme=sd.theme,
                description=f"Log-difference of {sd.name}",
            ))

        if sd.frequency in (Frequency.MONTHLY, Frequency.QUARTERLY):
            features.append(FeatureDef(
                feature_id=f"{sd.series_id}_yoy",
                base_series=sd.series_id,
                transform="yoy",
                theme=sd.theme,
                description=f"Year-over-year change of {sd.name}",
            ))

    return features
