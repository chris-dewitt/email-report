"""Net Interest Income (NII) sensitivity engine.

Core formula:  Delta_NII ≈ Σ_i (RSA_i - RSL_i) * Δr_i * (horizon / 12)
with deposit-beta adjustments on liability repricing.
"""

from __future__ import annotations

from balancelab.models.positions import (
    BalanceSheet,
    Position,
    RepricingBucket,
    BUCKET_HORIZON_YEARS,
)
from balancelab.models.scenarios import ScenarioDefinition
from balancelab.models.results import NIIResult


def _position_nii(pos: Position, horizon_years: float) -> float:
    """Annualized interest income/expense for one position, pro-rated to horizon."""
    return pos.balance * pos.rate * min(horizon_years, 1.0)


def _reprices_within_horizon(bucket: RepricingBucket, horizon_years: float) -> bool:
    return BUCKET_HORIZON_YEARS.get(bucket, 0.0) <= horizon_years


def _shocked_rate(
    pos: Position,
    scenario: ScenarioDefinition,
    horizon_years: float,
) -> float:
    """Compute the new effective rate for a position after applying the shock."""
    if not _reprices_within_horizon(pos.repricing_bucket, horizon_years):
        return pos.rate

    shock = scenario.rate_shock.shock_for_bucket(pos.repricing_bucket)

    if not pos.is_asset:
        beta = scenario.get_beta(pos.asset_class.value)
        shock *= beta

    return max(pos.rate + shock, 0.0)


def compute_nii(bs: BalanceSheet, scenario: ScenarioDefinition) -> NIIResult:
    horizon_years = scenario.horizon_months / 12.0

    base_nii = 0.0
    shocked_nii = 0.0
    drivers: list[dict[str, object]] = []

    for pos in bs.positions:
        base_income = _position_nii(pos, horizon_years)
        sign = 1.0 if pos.is_asset else -1.0
        base_nii += sign * base_income

        new_rate = _shocked_rate(pos, scenario, horizon_years)
        shocked_income = pos.balance * new_rate * min(horizon_years, 1.0)
        shocked_nii += sign * shocked_income

        delta = sign * (shocked_income - base_income)
        if abs(delta) > 0:
            drivers.append({
                "position_id": pos.id,
                "name": pos.name,
                "side": "asset" if pos.is_asset else "liability",
                "balance": pos.balance,
                "base_rate": pos.rate,
                "shocked_rate": new_rate,
                "delta_income": round(delta, 2),
            })

    drivers.sort(key=lambda d: abs(d["delta_income"]), reverse=True)  # type: ignore[arg-type]

    delta_nii = shocked_nii - base_nii
    delta_pct = (delta_nii / base_nii * 100) if base_nii != 0 else 0.0

    return NIIResult(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        base_nii=round(base_nii, 2),
        shocked_nii=round(shocked_nii, 2),
        delta_nii=round(delta_nii, 2),
        delta_nii_pct=round(delta_pct, 2),
        horizon_months=scenario.horizon_months,
        top_drivers=drivers[:10],
    )
