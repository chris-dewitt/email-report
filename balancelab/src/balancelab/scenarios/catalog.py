"""Scenario catalog: manage and retrieve scenario definitions."""

from __future__ import annotations

from balancelab.models.scenarios import ScenarioDefinition, STANDARD_SCENARIOS


class ScenarioCatalog:
    def __init__(self) -> None:
        self._scenarios: dict[str, ScenarioDefinition] = {
            s.id: s for s in STANDARD_SCENARIOS
        }

    def list_scenarios(self) -> list[ScenarioDefinition]:
        return list(self._scenarios.values())

    def get(self, scenario_id: str) -> ScenarioDefinition | None:
        return self._scenarios.get(scenario_id)

    def add(self, scenario: ScenarioDefinition) -> None:
        self._scenarios[scenario.id] = scenario

    def remove(self, scenario_id: str) -> bool:
        return self._scenarios.pop(scenario_id, None) is not None

    @property
    def ids(self) -> list[str]:
        return list(self._scenarios.keys())
