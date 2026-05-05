from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class RegimeLabel(str, Enum):
    EXPANSION = "expansion"
    OVERHEATING = "overheating"
    SLOWDOWN = "slowdown"
    CONTRACTION = "contraction"
    CRISIS = "crisis"
    TRANSITION = "transition"


class SignalVector(BaseModel):
    """Standardized input signals for regime classification."""
    date: str
    growth_z: float = Field(description="Growth composite z-score")
    inflation_z: float = Field(description="Inflation composite z-score")
    financial_conditions_z: float = Field(description="Financial conditions z-score (tighter = positive)")
    labor_z: float = Field(description="Labor market strength z-score")
    policy_sentiment: float = Field(
        default=0.0, ge=-1.0, le=1.0,
        description="Fed policy tone (-1=dovish, +1=hawkish)",
    )
    vol_z: float = Field(default=0.0, description="Market volatility z-score")
    yield_curve_z: float = Field(default=0.0, description="Yield curve slope z-score (inverted = negative)")


class RegimeState(BaseModel):
    """Current regime classification with uncertainty."""
    date: str
    label: RegimeLabel
    confidence: float = Field(ge=0, le=1)
    probabilities: dict[str, float] = Field(
        default_factory=dict,
        description="p(z_t = k | x_t) for each regime k",
    )
    drivers: list[dict[str, object]] = Field(
        default_factory=list,
        description="Signals most responsible for the classification",
    )
    previous_label: RegimeLabel | None = None
    transition_detected: bool = False


class TransitionRecord(BaseModel):
    date: str
    from_regime: RegimeLabel
    to_regime: RegimeLabel
    confidence: float
    key_signals: list[str] = Field(default_factory=list)
