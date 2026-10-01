from actions import generate_csv_tracker, generate_markdown_report
from schemas import (
    ActionItem,
    ApplicabilityStatus,
    BusinessSetupReport,
    RegistrationAssessment,
)

from actions import generate_pdf_report
from actions import create_google_sheet_tracker, send_email_report


def _sample_report() -> BusinessSetupReport:
    return BusinessSetupReport(
        profile_summary="Sample business in Pune",
        potential_registrations=[
            RegistrationAssessment(
                name="GST Registration",
                issuing_authority="GSTN",
                status=ApplicabilityStatus.MORE_INFO_REQUIRED,
                why_relevant="Needs turnover details",
                required_documents=["PAN"],
                information_still_required=["Exact turnover in INR"],
                official_links=["https://www.gst.gov.in/"],
                source_reference_url="https://www.gst.gov.in/",
                source_reference_date="2026-10-01",
                verification_notes=["Verify threshold"],
            )
        ],
        information_still_required=["Exact turnover in INR"],
        suggested_sequence=[
            ActionItem(step=1, title="Collect data", detail="Collect missing turnover")
        ],
        disclaimer="Guidance only",
    )


def test_markdown_action_generates_text_artifact():
    artifact = generate_markdown_report(_sample_report())
    assert artifact.status == "generated"
    assert artifact.artifact_filename == "business_setup_report.md"
    assert artifact.artifact_content is not None
    assert "Government Business Setup Report" in artifact.artifact_content


def test_csv_action_generates_text_artifact():
    artifact = generate_csv_tracker(_sample_report())
    assert artifact.status == "generated"
    assert artifact.artifact_filename == "business_setup_tracker.csv"
    assert artifact.artifact_content is not None
    assert "Registration,Status,Why Relevant" in artifact.artifact_content


def test_pdf_action_generates_base64_artifact():
    artifact = generate_pdf_report(_sample_report())
    assert artifact.status == "generated"
    assert artifact.artifact_filename == "business_setup_report.pdf"
    assert artifact.artifact_base64 is not None


def test_google_sheet_tracker_skips_without_config(monkeypatch):
    monkeypatch.delenv("GOOGLE_SHEETS_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SHEETS_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    artifact = create_google_sheet_tracker(_sample_report())
    assert artifact.status == "skipped"


def test_email_report_skips_without_config(monkeypatch):
    for key in [
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "REPORT_FROM_EMAIL",
        "REPORT_TO_EMAIL",
    ]:
        monkeypatch.delenv(key, raising=False)
    artifact = send_email_report(_sample_report(), None)
    assert artifact.status == "skipped"
