"""Health check endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from atlas.models.health import HealthResponse, DataQualityReport
from atlas.ingest.registry import SERIES_CATALOG
from atlas.storage.paths import bronze_dir

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Check API health, data freshness, and series availability."""
    bronze_files = list(bronze_dir().rglob("*.parquet"))
    available_ids = {f.stem for f in bronze_files}
    catalog_ids = {s.series_id for s in SERIES_CATALOG}
    missing = catalog_ids - available_ids

    # Get most recent pull time from file modification
    last_pull = None
    if bronze_files:
        latest_file = max(bronze_files, key=lambda f: f.stat().st_mtime)
        last_pull = datetime.fromtimestamp(
            latest_file.stat().st_mtime, tz=timezone.utc
        )

    status = "ok" if not missing else ("degraded" if len(missing) < 10 else "error")

    return HealthResponse(
        status=status,
        last_pull=last_pull,
        series_count=len(available_ids),
        feature_count=0,  # TODO: count gold features
        data_quality=DataQualityReport(
            stale_series=[],
            missing_series=list(missing)[:10],
            total_series=len(catalog_ids),
            available_series=len(available_ids),
        ),
    )
