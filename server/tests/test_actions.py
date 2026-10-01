from actions import generate_csv_tracker, generate_markdown_report
from schemas import (
    ActionItem,
    ApplicabilityStatus,
    BusinessSetupReport,
    RegistrationAssessment,
)


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
