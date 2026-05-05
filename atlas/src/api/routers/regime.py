"""Regime snapshot endpoint."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException

from atlas.models.regime import RegimeSnapshotResponse
from atlas.features.regime import compute_regime_snapshot

router = APIRouter()


@router.get("/regime-snapshot", response_model=RegimeSnapshotResponse)
async def regime_snapshot() -> RegimeSnapshotResponse:
    """Compute and return the current macro regime classification."""
    result = compute_regime_snapshot()

    if result is None:
        raise HTTPException(
            status_code=503,
            detail="Not enough feature data to classify regime. Run 'atlas build-features' first.",
        )

    return RegimeSnapshotResponse(
        regime=result["regime"],
        confidence=result["confidence"],
        as_of=date.fromisoformat(result["as_of"]),
        drivers=result["drivers"],
        all_scores=result["all_scores"],
    )
