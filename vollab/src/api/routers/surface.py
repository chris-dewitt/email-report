from __future__ import annotations

from fastapi import APIRouter, Query

from vollab.models.results import SurfacePoint
from vollab.surface.builder import build_surface, interpolate_vol, sample_skew_surface

router = APIRouter()


@router.get("/sample", response_model=list[SurfacePoint])
def get_sample_surface(spot: float = Query(default=100.0, gt=0)) -> list[SurfacePoint]:
    strikes, expiries, vols = sample_skew_surface(spot)
    return build_surface(strikes, expiries, vols, spot)


@router.get("/interpolate")
def interpolate(
    strike: float = Query(gt=0),
    expiry: float = Query(gt=0),
    spot: float = Query(default=100.0, gt=0),
) -> dict[str, float]:
    strikes, expiries, vols = sample_skew_surface(spot)
    vol = interpolate_vol(strikes, expiries, vols, strike, expiry)
    return {"strike": strike, "expiry": expiry, "interpolated_vol": round(vol, 6)}
