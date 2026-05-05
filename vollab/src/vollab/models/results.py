from __future__ import annotations

from pydantic import BaseModel, Field


class PricingResult(BaseModel):
    price: float
    method: str
    option_type: str
    spot: float
    strike: float
    expiry: float
    vol: float
    rate: float
    intrinsic: float = 0.0
    time_value: float = 0.0
    mc_std_error: float | None = None
    mc_paths: int | None = None


class GreeksResult(BaseModel):
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    method: str = "analytical"


class SurfacePoint(BaseModel):
    strike: float
    expiry: float
    vol: float
    moneyness: float = Field(description="K/S ratio")


class ScenarioPnL(BaseModel):
    spot_shift: float
    vol_shift: float
    base_price: float
    new_price: float
    pnl: float
    pnl_pct: float
