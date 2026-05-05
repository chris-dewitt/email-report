from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


class ExerciseStyle(str, Enum):
    EUROPEAN = "european"
    AMERICAN = "american"


class OptionContract(BaseModel):
    spot: float = Field(gt=0, description="Current underlying price")
    strike: float = Field(gt=0, description="Strike price")
    expiry: float = Field(gt=0, description="Time to expiration in years")
    vol: float = Field(gt=0, description="Annualized volatility (decimal)")
    rate: float = Field(description="Risk-free rate (decimal)")
    dividend: float = Field(default=0.0, ge=0, description="Continuous dividend yield")
    option_type: OptionType = OptionType.CALL
    exercise: ExerciseStyle = ExerciseStyle.EUROPEAN
    notional: float = Field(default=1.0, gt=0)
