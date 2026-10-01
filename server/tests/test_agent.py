from agent import run_business_setup_agent
from schemas import BusinessProfile


def _profile() -> BusinessProfile:
    return BusinessProfile(
        businessType="Private Limited",
        industry="Information Technology",
        state="Maharashtra",
        city="Pune",
        employees=12,
        turnover="40 Lakhs - 1 Crore",
        activity="Building SaaS tools for business users",
        operations="both",
        gstin=None,
        pan=None,
    )


def test_agent_returns_contract_with_fallback_safe_values():
    report = run_business_setup_agent(_profile())

    assert report.profile_summary
    assert isinstance(report.potential_registrations, list)
    assert isinstance(report.suggested_sequence, list)
    assert isinstance(report.data_sources, list)
    assert report.disclaimer


def test_agent_skips_pan_and_gst_when_not_provided():
    report = run_business_setup_agent(_profile())

    assert report.pan_verification is not None
    assert report.pan_verification.get("checked") is False
    gst_source = next((x for x in report.data_sources if x.source_name in {"GST verification", "Setu GST Verification API"}), None)
    assert gst_source is not None
