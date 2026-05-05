from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["scenarios_available"] >= 7


def test_positions_returns_response():
    resp = client.get("/positions")
    assert resp.status_code in (200, 404)
