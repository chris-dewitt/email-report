from __future__ import annotations

from fastapi import APIRouter, HTTPException

from balancelab.models.scenarios import ScenarioDefinition
from balancelab.scenarios.catalog import ScenarioCatalog

router = APIRouter()
catalog = ScenarioCatalog()


@router.get("", response_model=list[ScenarioDefinition])
def list_scenarios() -> list[ScenarioDefinition]:
    return catalog.list_scenarios()


@router.get("/{scenario_id}", response_model=ScenarioDefinition)
def get_scenario(scenario_id: str) -> ScenarioDefinition:
    s = catalog.get(scenario_id)
    if s is None:
        raise HTTPException(404, f"Scenario '{scenario_id}' not found")
    return s


@router.post("", response_model=ScenarioDefinition)
def create_scenario(scenario: ScenarioDefinition) -> ScenarioDefinition:
    catalog.add(scenario)
    return scenario
