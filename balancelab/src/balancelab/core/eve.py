"""Economic Value of Equity (EVE) sensitivity engine.

Core formula:  Delta_EVE ≈ -D_A * A * Δy + D_L * L * Δy
where D_A, D_L are weighted-average durations of assets and liabilities.
"""

from __future__ import annotations

from balancelab.models.positions import (
    BalanceSheet,
    Position,
    BUCKET_MIDPOINTS_YEARS,
)
from balancelab.models.scenarios import ScenarioDefinition
from balancelab.models.results import EVEResult


def _present_value(pos: Position, rate_shift: float = 0.0) -> float:
    """Approximate PV as balance discounted at the position's rate +/- shift."""
    discount_rate = max(pos.rate + rate_shift, 0.001)
    t = BUCKET_MIDPOINTS_YEARS.get(pos.repricing_bucket, pos.maturity_years)
    if t <= 0:
        return pos.balance
    return pos.balance / (1 + discount_rate) ** t


def _weighted_duration(positions: list[Position]) -> float:
    total_balance = sum(p.balance for p in positions)
    if total_balance == 0:
        return 0.0
    return sum(p.duration_approx * p.balance for p in positions) / total_balance


def compute_eve(bs: BalanceSheet, scenario: ScenarioDefinition) -> EVEResult:
    assets = bs.assets()
    liabs = bs.liabilities()

    base_pv_assets = sum(_present_value(p) for p in assets)
    base_pv_liabs = sum(_present_value(p) for p in liabs)
    base_eve = base_pv_assets - base_pv_liabs

    shocked_pv_assets = 0.0
    for p in assets:
        shift = scenario.rate_shock.shock_for_bucket(p.repricing_bucket)
        shocked_pv_assets += _present_value(p, shift)

    shocked_pv_liabs = 0.0
    for p in liabs:
        shift = scenario.rate_shock.shock_for_bucket(p.repricing_bucket)
        beta = scenario.get_beta(p.asset_class.value)
        shocked_pv_liabs += _present_value(p, shift * beta)

    shocked_eve = shocked_pv_assets - shocked_pv_liabs
    delta_eve = shocked_eve - base_eve
    delta_pct = (delta_eve / base_eve * 100) if base_eve != 0 else 0.0

    asset_dur = _weighted_duration(assets)
    liab_dur = _weighted_duration(liabs)

    return EVEResult(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        base_eve=round(base_eve, 2),
        shocked_eve=round(shocked_eve, 2),
        delta_eve=round(delta_eve, 2),
        delta_eve_pct=round(delta_pct, 2),
        asset_duration=round(asset_dur, 4),
        liability_duration=round(liab_dur, 4),
        duration_gap=round(asset_dur - liab_dur, 4),
    )
