"""Scenario execution engine — runs NII, EVE, and gap analysis for a given scenario."""

from __future__ import annotations

from balancelab.models.positions import BalanceSheet
from balancelab.models.scenarios import ScenarioDefinition
from balancelab.models.results import ScenarioOutput
from balancelab.core.nii import compute_nii
from balancelab.core.eve import compute_eve
from balancelab.core.gap import compute_liquidity_gap


def run_scenario(bs: BalanceSheet, scenario: ScenarioDefinition) -> ScenarioOutput:
    nii = compute_nii(bs, scenario)
    eve = compute_eve(bs, scenario)
    liquidity = compute_liquidity_gap(bs)

    assumptions = {
        "horizon_months": scenario.horizon_months,
        "rate_shock": scenario.rate_shock.model_dump(),
        "deposit_betas": [db.model_dump() for db in scenario.deposit_betas],
        "balance_growth_pct": scenario.balance_growth_pct,
        "total_assets": bs.total_assets,
        "total_liabilities": bs.total_liabilities,
        "equity": bs.equity,
        "position_count": len(bs.positions),
    }

    return ScenarioOutput(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        nii=nii,
        eve=eve,
        liquidity=liquidity,
        assumptions_summary=assumptions,
    )


def run_all_scenarios(
    bs: BalanceSheet,
    scenarios: list[ScenarioDefinition],
) -> list[ScenarioOutput]:
    return [run_scenario(bs, s) for s in scenarios]
