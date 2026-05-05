"""Event study endpoints for FedLens."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
import polars as pl

from fedlens.storage.paths import gold_dir

router = APIRouter()


@router.get("/event-study")
async def list_event_studies(doc_type: str | None = None, series_id: str | None = None):
    """List event study results with optional filters."""
    path = gold_dir("event_study") / "results.parquet"
    if not path.exists():
        return {"results": [], "total": 0}

    df = pl.read_parquet(path)

    if doc_type:
        df = df.filter(pl.col("doc_id").str.starts_with(doc_type))
    if series_id:
        df = df.filter(pl.col("series_id") == series_id)

    df = df.sort("event_date", descending=True)
    results = df.to_dicts()

    return {"results": results, "total": len(results)}


@router.get("/event-study/{doc_id}")
async def get_event_study(doc_id: str):
    """Get event study results for a specific document."""
    path = gold_dir("event_study") / "results.parquet"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Event study results not found")

    df = pl.read_parquet(path).filter(pl.col("doc_id") == doc_id)
    if df.is_empty():
        raise HTTPException(status_code=404, detail=f"No results for {doc_id}")

    return {"doc_id": doc_id, "results": df.to_dicts()}
