from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    FIXED_RATE_LOAN = "fixed_rate_loan"
    FLOATING_RATE_LOAN = "floating_rate_loan"
    MORTGAGE = "mortgage"
    INVESTMENT_SECURITY = "investment_security"
    DEMAND_DEPOSIT = "demand_deposit"
    TERM_DEPOSIT = "term_deposit"
    SAVINGS = "savings"
    BORROWING = "borrowing"
    FIXED_RATE_BOND = "fixed_rate_bond"
    FLOATING_RATE_BOND = "floating_rate_bond"
    EQUITY = "equity"
    OTHER_ASSET = "other_asset"
    OTHER_LIABILITY = "other_liability"


ASSET_CLASSES = {
    AssetClass.FIXED_RATE_LOAN,
    AssetClass.FLOATING_RATE_LOAN,
    AssetClass.MORTGAGE,
    AssetClass.INVESTMENT_SECURITY,
    AssetClass.OTHER_ASSET,
}

LIABILITY_CLASSES = {
    AssetClass.DEMAND_DEPOSIT,
    AssetClass.TERM_DEPOSIT,
    AssetClass.SAVINGS,
    AssetClass.BORROWING,
    AssetClass.FIXED_RATE_BOND,
    AssetClass.FLOATING_RATE_BOND,
    AssetClass.OTHER_LIABILITY,
}


class RepricingBucket(str, Enum):
    OVERNIGHT = "overnight"
    M1 = "1m"
    M3 = "3m"
    M6 = "6m"
    Y1 = "1y"
    Y2 = "2y"
    Y3 = "3y"
    Y5 = "5y"
    Y10 = "10y"
    Y10_PLUS = "10y+"
    NON_REPRICING = "non_repricing"


BUCKET_MIDPOINTS_YEARS: dict[RepricingBucket, float] = {
    RepricingBucket.OVERNIGHT: 1 / 365,
    RepricingBucket.M1: 1 / 12,
    RepricingBucket.M3: 3 / 12,
    RepricingBucket.M6: 6 / 12,
    RepricingBucket.Y1: 1.0,
    RepricingBucket.Y2: 2.0,
    RepricingBucket.Y3: 3.0,
    RepricingBucket.Y5: 5.0,
    RepricingBucket.Y10: 10.0,
    RepricingBucket.Y10_PLUS: 15.0,
    RepricingBucket.NON_REPRICING: 0.0,
}

BUCKET_HORIZON_YEARS: dict[RepricingBucket, float] = {
    RepricingBucket.OVERNIGHT: 1 / 365,
    RepricingBucket.M1: 1 / 12,
    RepricingBucket.M3: 3 / 12,
    RepricingBucket.M6: 6 / 12,
    RepricingBucket.Y1: 1.0,
    RepricingBucket.Y2: 2.0,
    RepricingBucket.Y3: 3.0,
    RepricingBucket.Y5: 5.0,
    RepricingBucket.Y10: 10.0,
    RepricingBucket.Y10_PLUS: 20.0,
    RepricingBucket.NON_REPRICING: 0.0,
}


class Position(BaseModel):
    id: str
    name: str
    asset_class: AssetClass
    balance: float = Field(ge=0, description="Outstanding balance in USD")
    rate: float = Field(description="Current contracted rate (annualized, decimal)")
    repricing_bucket: RepricingBucket
    maturity_years: float = Field(ge=0, description="Remaining maturity in years")
    is_asset: bool = True

    @property
    def is_rate_sensitive(self) -> bool:
        return self.repricing_bucket != RepricingBucket.NON_REPRICING

    @property
    def duration_approx(self) -> float:
        if self.rate == 0:
            return self.maturity_years
        y = self.rate
        n = self.maturity_years
        return (1 - (1 + y) ** (-n)) / y if n > 0 else 0.0


class BalanceSheet(BaseModel):
    name: str = "Sample Institution"
    as_of_date: str = "2024-12-31"
    positions: list[Position] = Field(default_factory=list)

    @property
    def total_assets(self) -> float:
        return sum(p.balance for p in self.positions if p.is_asset)

    @property
    def total_liabilities(self) -> float:
        return sum(p.balance for p in self.positions if not p.is_asset)

    @property
    def equity(self) -> float:
        return self.total_assets - self.total_liabilities

    def assets(self) -> list[Position]:
        return [p for p in self.positions if p.is_asset]

    def liabilities(self) -> list[Position]:
        return [p for p in self.positions if not p.is_asset]

    def by_bucket(self, bucket: RepricingBucket) -> list[Position]:
        return [p for p in self.positions if p.repricing_bucket == bucket]
