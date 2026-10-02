from fastapi.testclient import TestClient

from api import app
import api as api_module


def test_integrations_health_endpoint_returns_checks():
    api_module._request_windows.clear()
    client = TestClient(app)
    response = client.get("/api/health/integrations")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "checks" in body
    assert isinstance(body["checks"], list)
    names = {item.get("name") for item in body["checks"]}
    assert {"ollama", "google_sheets", "smtp_email"}.issubset(names)
