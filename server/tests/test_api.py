from fastapi.testclient import TestClient

from api import app


def test_evaluate_endpoint_returns_report_shape():
    client = TestClient(app)
    payload = {
        "businessType": "Private Limited",
        "industry": "Information Technology",
        "state": "Maharashtra",
        "city": "Pune",
        "employees": 15,
        "turnover": "40 Lakhs - 1 Crore",
        "activity": "Building SaaS products for enterprises",
        "operations": "both",
        "gstin": None,
        "pan": None,
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert "profile_summary" in body
    assert "potential_registrations" in body
    assert "suggested_sequence" in body
    assert "data_sources" in body
    assert "disclaimer" in body
    assert isinstance(body["potential_registrations"], list)
    assert isinstance(body["data_sources"], list)


def test_rate_limit_rejection(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "1")
    from importlib import reload
    import api as api_module

    reload(api_module)
    client = TestClient(api_module.app)
    payload = {
        "businessType": "Private Limited",
        "industry": "Information Technology",
        "state": "Maharashtra",
        "city": "Pune",
        "employees": 15,
        "turnover": "40 Lakhs - 1 Crore",
        "activity": "Building SaaS products for enterprises",
        "operations": "both",
        "gstin": None,
        "pan": None,
    }

    first = client.post("/api/evaluate", json=payload)
    second = client.post("/api/evaluate", json=payload)
    assert first.status_code == 200
    assert second.status_code == 429
