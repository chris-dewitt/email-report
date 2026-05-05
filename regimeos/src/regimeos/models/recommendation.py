from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class RiskAction(str, Enum):
    REDUCE_DURATION = "reduce_duration"
    EXTEND_DURATION = "extend_duration"
    INCREASE_HEDGES = "increase_hedges"
    REDUCE_HEDGES = "reduce_hedges"
    TIGHTEN_CREDIT = "tighten_credit"
    ADD_LIQUIDITY_BUFFER = "add_liquidity_buffer"
    INCREASE_EQUITY_EXPOSURE = "increase_equity_exposure"
    REDUCE_EQUITY_EXPOSURE = "reduce_equity_exposure"
    HOLD_STEADY = "hold_steady"
    REVIEW_ASSUMPTIONS = "review_assumptions"


class Recommendation(BaseModel):
    regime: str
    confidence: float
    actions: list[RiskAction]
    rationale: str
    watchlist: list[str] = Field(default_factory=list)
    scenario_priorities: list[str] = Field(default_factory=list)
    generated_at: str = ""
    approval_status: str = "pending"
