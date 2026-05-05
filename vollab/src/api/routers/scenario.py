from __future__ import annotations

from fastapi import APIRouter

from vollab.models.option import OptionContract
from vollab.models.results import ScenarioPnL
from vollab.simulation.scenario import compute_scenario_pnl

router = APIRouter()


@router.post("", response_model=list[ScenarioPnL])
def scenario_pnl(contract: OptionContract) -> list[ScenarioPnL]:
    return compute_scenario_pnl(contract)
