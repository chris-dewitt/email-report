from __future__ import annotations

from pydantic import BaseModel, Field
from balancelab.models.positions import RepricingBucket


class RateShock(BaseModel):
    name: str
    parallel_bps: int = Field(default=0, description="Parallel shift in basis points")
    short_end_bps: int = Field(default=0, description="Short-end twist (<= 1Y)")
    long_end_bps: int = Field(default=0, description="Long-end twist (> 5Y)")
    description: str = ""

    def shock_for_bucket(self, bucket: RepricingBucket) -> float:
        """Return rate shock in decimal for a given repricing bucket."""
        if bucket == RepricingBucket.NON_REPRICING:
            return 0.0
        bps = self.parallel_bps
        short_buckets = {
            RepricingBucket.OVERNIGHT,
            RepricingBucket.M1,
            RepricingBucket.M3,
            RepricingBucket.M6,
            RepricingBucket.Y1,
        }
        long_buckets = {
            RepricingBucket.Y5,
            RepricingBucket.Y10,
            RepricingBucket.Y10_PLUS,
        }
        if bucket in short_buckets:
            bps += self.short_end_bps
        elif bucket in long_buckets:
            bps += self.long_end_bps
        return bps / 10_000


class DepositBetaAssumption(BaseModel):
    asset_class_name: str
    beta: float = Field(ge=0.0, le=1.0, description="Pass-through rate (0=sticky, 1=full)")
    lag_months: int = Field(default=0, ge=0, description="Repricing lag in months")


class ScenarioDefinition(BaseModel):
    id: str
    name: str
    description: str = ""
    rate_shock: RateShock
    deposit_betas: list[DepositBetaAssumption] = Field(default_factory=list)
    horizon_months: int = Field(default=12, description="NII projection horizon")
    balance_growth_pct: float = Field(default=0.0, description="Annualized balance growth assumption")

    def get_beta(self, asset_class_name: str) -> float:
        for db in self.deposit_betas:
            if db.asset_class_name == asset_class_name:
                return db.beta
        return 1.0


STANDARD_SCENARIOS: list[ScenarioDefinition] = [
    ScenarioDefinition(
        id="base",
        name="Base Case",
        description="No rate change — current rates held flat",
        rate_shock=RateShock(name="flat", parallel_bps=0),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.2),
            DepositBetaAssumption(asset_class_name="savings", beta=0.4),
            DepositBetaAssumption(asset_class_name="term_deposit", beta=0.8),
        ],
    ),
    ScenarioDefinition(
        id="up_100",
        name="+100 bps Parallel",
        description="Parallel upward shift of 100 basis points",
        rate_shock=RateShock(name="up_100", parallel_bps=100),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.2),
            DepositBetaAssumption(asset_class_name="savings", beta=0.4),
            DepositBetaAssumption(asset_class_name="term_deposit", beta=0.8),
        ],
    ),
    ScenarioDefinition(
        id="up_200",
        name="+200 bps Parallel",
        description="Parallel upward shift of 200 basis points",
        rate_shock=RateShock(name="up_200", parallel_bps=200),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.2),
            DepositBetaAssumption(asset_class_name="savings", beta=0.4),
            DepositBetaAssumption(asset_class_name="term_deposit", beta=0.8),
        ],
    ),
    ScenarioDefinition(
        id="down_100",
        name="-100 bps Parallel",
        description="Parallel downward shift of 100 basis points",
        rate_shock=RateShock(name="down_100", parallel_bps=-100),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.15),
            DepositBetaAssumption(asset_class_name="savings", beta=0.3),
            DepositBetaAssumption(asset_class_name="term_deposit", beta=0.7),
        ],
    ),
    ScenarioDefinition(
        id="down_200",
        name="-200 bps Parallel",
        description="Parallel downward shift of 200 basis points",
        rate_shock=RateShock(name="down_200", parallel_bps=-200),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.15),
            DepositBetaAssumption(asset_class_name="savings", beta=0.3),
            DepositBetaAssumption(asset_class_name="term_deposit", beta=0.7),
        ],
    ),
    ScenarioDefinition(
        id="steepener",
        name="Curve Steepener",
        description="Short end -50 bps, long end +50 bps",
        rate_shock=RateShock(name="steepener", parallel_bps=0, short_end_bps=-50, long_end_bps=50),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.2),
            DepositBetaAssumption(asset_class_name="savings", beta=0.4),
            DepositBetaAssumption(asset_class_name="term_deposit", beta=0.8),
        ],
    ),
    ScenarioDefinition(
        id="flattener",
        name="Curve Flattener",
        description="Short end +75 bps, long end -25 bps",
        rate_shock=RateShock(name="flattener", parallel_bps=0, short_end_bps=75, long_end_bps=-25),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.2),
            DepositBetaAssumption(asset_class_name="savings", beta=0.4),
            DepositBetaAssumption(asset_class_name="term_deposit", beta=0.8),
        ],
    ),
]
