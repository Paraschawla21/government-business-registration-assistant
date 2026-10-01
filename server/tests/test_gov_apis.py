from gov_apis import verify_gstin_with_setu, verify_pan_with_setu


def test_mock_mode_gstin(monkeypatch):
    monkeypatch.setenv("VERIFICATION_MODE", "mock")
    result = verify_gstin_with_setu("27ABCDE1234F1Z5")
    assert result["checked"] is True
    assert result["source_type"] == "mock_api"


def test_mock_mode_pan(monkeypatch):
    monkeypatch.setenv("VERIFICATION_MODE", "mock")
    result = verify_pan_with_setu("ABCDE1234F")
    assert result["checked"] is True
    assert result["source_type"] == "mock_api"


def test_sandbox_without_config_returns_not_configured(monkeypatch):
    monkeypatch.setenv("VERIFICATION_MODE", "sandbox")
    monkeypatch.delenv("SETU_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("SETU_GST_VERIFY_URL", raising=False)
    result = verify_gstin_with_setu("27ABCDE1234F1Z5")
    assert result["checked"] is False
    assert result["source_type"] == "not_configured"
