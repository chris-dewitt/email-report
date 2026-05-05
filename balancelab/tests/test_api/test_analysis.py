import json
from pathlib import Path

from fastapi.testclient import TestClient
from api.main import app
from api.deps import set_balance_sheet
from balancelab.models.positions import BalanceSheet

client = TestClient(app)
SAMPLE = Path(__file__).parent.parent.parent / "sample_data" / "sample_balance_sheet.json"


def _load_sample() -> None:
    bs = BalanceSheet.model_validate(json.loads(SAMPLE.read_text(encoding="utf-8")))
    set_balance_sheet(bs)


def test_shock_endpoint():
    _load_sample()
    resp = client.get("/shock/up_200")
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_id"] == "up_200"
    assert "nii" in data
    assert "eve" in data
    assert "liquidity" in data


def test_nii_endpoint():
    _load_sample()
    resp = client.get("/nii/up_100")
    assert resp.status_code == 200
    data = resp.json()
    assert data["delta_nii"] != 0


def test_liquidity_gap_endpoint():
    _load_sample()
    resp = client.get("/liquidity-gap")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["gap_table"]) == 11


def test_unknown_scenario_404():
    _load_sample()
    resp = client.get("/shock/nonexistent")
    assert resp.status_code == 404
