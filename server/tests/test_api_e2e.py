import os

from fastapi.testclient import TestClient

from api import app


def test_form_to_plan_with_action_outputs():
    os.environ["VERIFICATION_MODE"] = "mock"
    client = TestClient(app)

    # Reset in-memory limiter for deterministic test behavior
    import api as api_module

    api_module._request_windows.clear()

    payload = {
        "businessType": "Private Limited",
        "industry": "Information Technology",
        "state": "Maharashtra",
        "city": "Pune",
        "employees": 12,
        "turnover": "40 Lakhs - 1 Crore",
        "activity": "Building and exporting software products",
        "operations": "both",
        "gstin": "27ABCDE1234F1Z5",
        "pan": "ABCDE1234F",
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert "potential_registrations" in body
    assert "action_results" in body
    assert isinstance(body["action_results"], list)
    assert any(item["name"] == "pdf_report" for item in body["action_results"])
    assert any(item["name"] == "google_sheet_tracker" for item in body["action_results"])
