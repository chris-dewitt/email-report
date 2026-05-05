from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert len(data["regime_labels"]) == 6


def test_signals_list():
    resp = client.get("/signals")
    assert resp.status_code == 200
    assert len(resp.json()) > 0


def test_signals_latest():
    resp = client.get("/signals/latest")
    assert resp.status_code == 200
    assert "growth_z" in resp.json()


def test_state_current():
    resp = client.get("/state")
    assert resp.status_code == 200
    data = resp.json()
    assert "label" in data
    assert "confidence" in data
    assert data["confidence"] > 0


def test_state_history():
    resp = client.get("/state/history")
    assert resp.status_code == 200
    assert len(resp.json()) > 5


def test_state_uncertainty():
    resp = client.get("/state/uncertainty")
    assert resp.status_code == 200
    probs = resp.json()
    assert abs(sum(probs.values()) - 1.0) < 1e-6


def test_state_classify():
    signal = {"date": "2024-01-01", "growth_z": 0.8, "inflation_z": 0.1,
              "financial_conditions_z": -0.5, "labor_z": 0.9}
    resp = client.post("/state/classify", json=signal)
    assert resp.status_code == 200
    assert resp.json()["label"] == "expansion"


def test_recommendations():
    resp = client.get("/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert "regime" in data
    assert "actions" in data
    assert len(data["actions"]) > 0


def test_explain():
    resp = client.get("/recommendations/explain")
    assert resp.status_code == 200
    assert "briefing" in resp.json()


def test_approval_queue_empty_initially():
    resp = client.get("/approval-queue")
    assert resp.status_code == 200
