"""Series endpoints — list metadata, fetch history."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from atlas.models.series import (
    SeriesMeta,
    SeriesListResponse,
    SeriesHistoryResponse,
    SeriesPoint,
    SeriesStats,
)
from atlas.ingest.registry import SERIES_CATALOG, SERIES_MAP
from atlas.storage.parquet_store import read_bronze

router = APIRouter()


def _build_meta(series_id: str) -> SeriesMeta | None:
    """Build SeriesMeta from catalog + latest bronze data."""
    sd = SERIES_MAP.get(series_id)
    if sd is None:
        return None

    df = read_bronze(series_id, sd.source.value)
    latest_value = None
    last_updated = None
    if df is not None and not df.is_empty():
        last_row = df.sort("date").tail(1)
        latest_value = last_row["value"][0]
        last_updated = last_row["date"][0]

    return SeriesMeta(
        series_id=sd.series_id,
        name=sd.name,
        source=sd.source.value,
        frequency=sd.frequency.value,
        theme=sd.theme.value,
        unit=sd.unit,
        description=sd.description,
        last_updated=last_updated,
        latest_value=latest_value,
    )


@router.get("/series", response_model=SeriesListResponse)
async def list_series(
    theme: str | None = Query(None, description="Filter by theme"),
    source: str | None = Query(None, description="Filter by source"),
) -> SeriesListResponse:
    """List all tracked macro series with metadata."""
    metas: list[SeriesMeta] = []
    for sd in SERIES_CATALOG:
        if theme and sd.theme.value != theme:
            continue
        if source and sd.source.value != source:
            continue
        meta = _build_meta(sd.series_id)
        if meta:
            metas.append(meta)

    return SeriesListResponse(series=metas, count=len(metas))


@router.get("/series/{series_id}/history", response_model=SeriesHistoryResponse)
async def series_history(
    series_id: str,
    start: date | None = Query(None, description="Start date"),
    end: date | None = Query(None, description="End date"),
) -> SeriesHistoryResponse:
    """Fetch full history for a specific series."""
    sd = SERIES_MAP.get(series_id)
    if sd is None:
        raise HTTPException(status_code=404, detail=f"Series '{series_id}' not found")

    df = read_bronze(series_id, sd.source.value)
    if df is None or df.is_empty():
        raise HTTPException(status_code=404, detail=f"No data for '{series_id}'")

    # Apply date filters
    import polars as pl
    if start:
        df = df.filter(pl.col("date") >= start)
    if end:
        df = df.filter(pl.col("date") <= end)

    df = df.sort("date")

    meta = _build_meta(series_id)
    assert meta is not None

    data = [SeriesPoint(date=row["date"], value=row["value"]) for row in df.iter_rows(named=True)]

    # Compute stats
    values = df["value"]
    stats = SeriesStats(
        mean=round(values.mean(), 4) if len(values) > 0 else None,
        std=round(values.std(), 4) if len(values) > 1 else None,
        min=round(values.min(), 4) if len(values) > 0 else None,
        max=round(values.max(), 4) if len(values) > 0 else None,
        latest=round(values[-1], 4) if len(values) > 0 else None,
    )

    return SeriesHistoryResponse(
        series_id=series_id,
        meta=meta,
        data=data,
        stats=stats,
    )
