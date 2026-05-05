import json
from pathlib import Path

from balancelab.models.positions import BalanceSheet
from balancelab.models.scenarios import STANDARD_SCENARIOS
from balancelab.core.engine import run_scenario
from balancelab.copilot.narrator import _fallback_narrative

SAMPLE = Path(__file__).parent.parent.parent / "sample_data" / "sample_balance_sheet.json"


def test_fallback_narrative_has_content():
    bs = BalanceSheet.model_validate(json.loads(SAMPLE.read_text(encoding="utf-8")))
    result = run_scenario(bs, STANDARD_SCENARIOS[1])
    narrative = _fallback_narrative(result)
    assert len(narrative) > 100
    assert "$" in narrative
    assert result.scenario_name in narrative


def test_fallback_mentions_top_driver():
    bs = BalanceSheet.model_validate(json.loads(SAMPLE.read_text(encoding="utf-8")))
    result = run_scenario(bs, STANDARD_SCENARIOS[2])
    narrative = _fallback_narrative(result)
    if result.nii.top_drivers:
        assert result.nii.top_drivers[0]["name"] in narrative
