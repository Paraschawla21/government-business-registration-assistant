import ollama
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    ActionItem,
    ApplicabilityStatus,
    BusinessProfile,
    BusinessSetupReport,
    RegistrationAssessment,
)

app = FastAPI(title="AI Tool Evaluator API")

# Configure CORS to allow requests from your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_mvp_stub_report(profile: BusinessProfile) -> BusinessSetupReport:
    profile_summary = (
        f"{profile.business_type} in {profile.city}, {profile.state} operating in "
        f"{profile.industry} with {profile.employees} employees, expected turnover "
        f"'{profile.turnover}', operations '{profile.operations}'."
    )

    items = [
        RegistrationAssessment(
            name="PAN and TAN",
            status=ApplicabilityStatus.APPLICABLE,
            why_relevant="PAN is required for tax identity; TAN is generally required for TDS-related compliance.",
            required_documents=[
                "Business constitution details",
                "Identity and address proof of proprietor/partners/directors",
                "Business address proof",
            ],
            information_still_required=[],
            official_links=[
                "https://www.incometax.gov.in/iec/foportal/",
            ],
            verification_notes=[
                "Verify latest PAN/TAN filing process and document checklist on the Income Tax portal.",
            ],
        ),
        RegistrationAssessment(
            name="GST Registration",
            status=ApplicabilityStatus.MORE_INFO_REQUIRED,
            why_relevant="GST applicability depends on turnover threshold, state category, and nature of supply.",
            required_documents=[
                "PAN of business/entity",
                "Address proof of principal place of business",
                "Promoter/authorized signatory identity proof",
                "Bank account details",
            ],
            information_still_required=[
                "Exact annual turnover estimate in INR",
                "Whether interstate taxable supplies are made",
                "Whether business falls under compulsory GST registration categories",
            ],
            official_links=[
                "https://www.gst.gov.in/",
            ],
            verification_notes=[
                "Thresholds and compulsory registration conditions must be verified on GST official guidance.",
            ],
        ),
        RegistrationAssessment(
            name="Udyam (MSME) Registration",
            status=ApplicabilityStatus.MORE_INFO_REQUIRED,
            why_relevant="MSME classification depends on investment and turnover criteria.",
            required_documents=[
                "Aadhaar of proprietor/authorized signatory",
                "PAN",
                "Business details and activity",
            ],
            information_still_required=[
                "Plant/equipment investment details",
                "Turnover confirmation for MSME classification",
            ],
            official_links=[
                "https://udyamregistration.gov.in/",
            ],
            verification_notes=[
                "Confirm current MSME classification criteria from Udyam portal.",
            ],
        ),
    ]

    action_steps = [
        ActionItem(
            step=1,
            title="Confirm missing business details",
            detail="Provide precise turnover, interstate supply status, and investment details to finalize GST and MSME applicability.",
        ),
        ActionItem(
            step=2,
            title="Complete foundational tax identity setup",
            detail="Apply for or verify PAN/TAN details before downstream registrations.",
        ),
        ActionItem(
            step=3,
            title="File GST/Udyam if eligibility is confirmed",
            detail="Use official portals and keep document scans ready to avoid rework.",
        ),
    ]

    return BusinessSetupReport(
        profile_summary=profile_summary,
        potential_registrations=items,
        information_still_required=sorted(
            {
                info
                for entry in items
                for info in entry.information_still_required
            }
        ),
        suggested_sequence=action_steps,
        disclaimer=(
            "This output is guidance only and not legal advice. Always verify "
            "latest rules, fees, and procedures on official government sources "
            "before filing."
        ),
    )


@app.post("/api/evaluate", response_model=BusinessSetupReport)
async def evaluate_business_profile(payload: BusinessProfile):
    try:
        # Current MVP scope freeze implementation:
        # - Uses validated profile schema and fixed output schema
        # - Returns deterministic placeholder assessments while rule engine/API
        #   integrations are being implemented in next steps.
        _ = ollama  # Kept imported for upcoming LLM reasoning phase.
        return build_mvp_stub_report(payload)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
