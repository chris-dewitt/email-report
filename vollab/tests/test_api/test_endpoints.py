from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

SAMPLE_CONTRACT = {
    "spot": 100, "strike": 100, "expiry": 1.0,
    "vol": 0.20, "rate": 0.05, "option_type": "call",
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_price_bs():
    resp = client.post("/price/bs", json=SAMPLE_CONTRACT)
    assert resp.status_code == 200
    assert resp.json()["method"] == "black_scholes"
    assert resp.json()["price"] > 0


def test_price_mc():
    resp = client.post("/price/mc", json=SAMPLE_CONTRACT, params={"n_paths": 10000})
    assert resp.status_code == 200
    assert resp.json()["method"] == "monte_carlo"


def test_greeks_analytical():
    resp = client.post("/greeks/analytical", json=SAMPLE_CONTRACT)
    assert resp.status_code == 200
    data = resp.json()
    assert 0 < data["delta"] < 1
    assert data["gamma"] > 0


def test_surface_sample():
    resp = client.get("/surface/sample")
    assert resp.status_code == 200
    assert len(resp.json()) > 0


def test_scenario_pnl():
    resp = client.post("/scenario-pnl", json=SAMPLE_CONTRACT)
    assert resp.status_code == 200
    assert len(resp.json()) > 0


def test_compare_methods():
    resp = client.post("/price/compare", json=SAMPLE_CONTRACT)
    assert resp.status_code == 200
    assert len(resp.json()) == 2
