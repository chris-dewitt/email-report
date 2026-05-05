"""Load balance sheets and scenarios from JSON files."""

from __future__ import annotations

import json
from pathlib import Path

from balancelab.models.positions import BalanceSheet
from balancelab.models.scenarios import ScenarioDefinition


def load_balance_sheet(path: Path) -> BalanceSheet:
    data = json.loads(path.read_text(encoding="utf-8"))
    return BalanceSheet.model_validate(data)


def load_scenario(path: Path) -> ScenarioDefinition:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ScenarioDefinition.model_validate(data)


def save_balance_sheet(bs: BalanceSheet, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(bs.model_dump_json(indent=2), encoding="utf-8")


def save_scenario(scenario: ScenarioDefinition, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scenario.model_dump_json(indent=2), encoding="utf-8")
