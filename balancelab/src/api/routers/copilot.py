from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from balancelab.core.engine import run_scenario
from balancelab.copilot.narrator import generate_narrative
from balancelab.scenarios.catalog import ScenarioCatalog
from api.deps import get_balance_sheet

router = APIRouter()
catalog = ScenarioCatalog()


class NarrativeRequest(BaseModel):
    scenario_id: str
    question: str | None = None


class NarrativeResponse(BaseModel):
    scenario: str
    narrative: str
    generated_at: str
    model: str


@router.post("", response_model=NarrativeResponse)
def generate_copilot_narrative(req: NarrativeRequest) -> NarrativeResponse:
    bs = get_balance_sheet()
    if bs is None:
        raise HTTPException(404, "No balance sheet loaded.")
    scenario = catalog.get(req.scenario_id)
    if scenario is None:
        raise HTTPException(404, f"Scenario '{req.scenario_id}' not found")
    output = run_scenario(bs, scenario)
    result = generate_narrative(output, req.question)
    return NarrativeResponse(**result)
