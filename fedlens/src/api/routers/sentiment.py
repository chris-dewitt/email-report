"""Sentiment and drift endpoints for FedLens."""

from __future__ import annotations

from fastapi import APIRouter
import polars as pl

from fedlens.storage.paths import gold_dir

router = APIRouter()


@router.get("/sentiment")
async def get_sentiment(doc_type: str = "statement"):
    """Get sentiment time series for a document type."""
    path = gold_dir("sentiment") / f"{doc_type}.parquet"
    if not path.exists():
        return {"data": [], "total": 0}

    df = pl.read_parquet(path).sort("date")
    return {"data": df.to_dicts(), "total": len(df)}


@router.get("/drift")
async def get_drift(doc_type: str = "statement"):
    """Get semantic drift time series for a document type."""
    path = gold_dir("drift") / f"{doc_type}_drift.parquet"
    if not path.exists():
        return {"data": [], "total": 0}

    df = pl.read_parquet(path).sort("date")
    return {"data": df.to_dicts(), "total": len(df)}


@router.get("/uncertainty")
async def get_uncertainty(doc_type: str = "statement"):
    """Get uncertainty time series for a document type."""
    path = gold_dir("sentiment") / f"{doc_type}_uncertainty.parquet"
    if not path.exists():
        return {"data": [], "total": 0}

    df = pl.read_parquet(path).sort("date")
    return {"data": df.to_dicts(), "total": len(df)}
