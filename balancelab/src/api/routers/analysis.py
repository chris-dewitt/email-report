from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from balancelab.core.engine import run_scenario, run_all_scenarios
from balancelab.core.gap import compute_liquidity_gap
from balancelab.models.results import ScenarioOutput, NIIResult, EVEResult, LiquidityGapResult
from balancelab.scenarios.catalog import ScenarioCatalog
from api.deps import get_balance_sheet

router = APIRouter()
catalog = ScenarioCatalog()


@router.get("/nii/{scenario_id}", response_model=NIIResult)
def compute_nii_endpoint(scenario_id: str) -> NIIResult:
    bs = get_balance_sheet()
    if bs is None:
        raise HTTPException(404, "No balance sheet loaded.")
    scenario = catalog.get(scenario_id)
    if scenario is None:
        raise HTTPException(404, f"Scenario '{scenario_id}' not found")
    result = run_scenario(bs, scenario)
    return result.nii


@router.get("/eve/{scenario_id}", response_model=EVEResult)
def compute_eve_endpoint(scenario_id: str) -> EVEResult:
    bs = get_balance_sheet()
    if bs is None:
        raise HTTPException(404, "No balance sheet loaded.")
    scenario = catalog.get(scenario_id)
    if scenario is None:
        raise HTTPException(404, f"Scenario '{scenario_id}' not found")
    result = run_scenario(bs, scenario)
    return result.eve


@router.get("/liquidity-gap", response_model=LiquidityGapResult)
def compute_gap_endpoint() -> LiquidityGapResult:
    bs = get_balance_sheet()
    if bs is None:
        raise HTTPException(404, "No balance sheet loaded.")
    return compute_liquidity_gap(bs)


@router.get("/shock/{scenario_id}", response_model=ScenarioOutput)
def run_shock(scenario_id: str) -> ScenarioOutput:
    bs = get_balance_sheet()
    if bs is None:
        raise HTTPException(404, "No balance sheet loaded.")
    scenario = catalog.get(scenario_id)
    if scenario is None:
        raise HTTPException(404, f"Scenario '{scenario_id}' not found")
    return run_scenario(bs, scenario)


@router.get("/shock-all", response_model=list[ScenarioOutput])
def run_all_shocks(
    scenario_ids: list[str] = Query(default=None),
) -> list[ScenarioOutput]:
    bs = get_balance_sheet()
    if bs is None:
        raise HTTPException(404, "No balance sheet loaded.")
    if scenario_ids:
        scenarios = [catalog.get(sid) for sid in scenario_ids]
        scenarios = [s for s in scenarios if s is not None]
    else:
        scenarios = catalog.list_scenarios()
    return run_all_scenarios(bs, scenarios)
