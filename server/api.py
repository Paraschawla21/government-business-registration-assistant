from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from gov_apis import verify_gstin_with_setu, verify_pan_with_setu
from registrations import evaluate_registrations
from schemas import (
    ActionItem,
    BusinessProfile,
    BusinessSetupReport,
    DataSourceLog,
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


def build_business_setup_report(profile: BusinessProfile) -> BusinessSetupReport:
    profile_summary = (
        f"{profile.business_type} in {profile.city}, {profile.state} operating in "
        f"{profile.industry} with {profile.employees} employees, expected turnover "
        f"'{profile.turnover}', operations '{profile.operations}'."
    )

    items, kb_source_log = evaluate_registrations(profile)

    gst_verification = None
    data_sources: list[DataSourceLog] = [kb_source_log]

    if profile.gstin:
        gst_verification = verify_gstin_with_setu(profile.gstin)
        data_sources.append(
            DataSourceLog(
                source_type=gst_verification.get("source_type", "live_api"),
                source_name="Setu GST Verification API",
                status="used" if gst_verification.get("checked") else "fallback",
                message=gst_verification.get("message", "GST verification attempted."),
            )
        )
    else:
        data_sources.append(
            DataSourceLog(
                source_type="input",
                source_name="GST verification",
                status="skipped",
                message="GSTIN not provided by user; live GST verification skipped.",
            )
        )

    if profile.pan:
        pan_verification = verify_pan_with_setu(profile.pan)
        data_sources.append(
            DataSourceLog(
                source_type=pan_verification.get("source_type", "live_api"),
                source_name="Setu PAN Verification API",
                status="used" if pan_verification.get("checked") else "fallback",
                message=pan_verification.get("message", "PAN verification attempted."),
            )
        )
    else:
        pan_verification = {
            "checked": False,
            "provider": "setu",
            "message": "PAN was not provided in input; live PAN verification skipped.",
            "source_type": "input",
        }
        data_sources.append(
            DataSourceLog(
                source_type="input",
                source_name="PAN verification",
                status="skipped",
                message="PAN not provided by user; live PAN verification skipped.",
            )
        )

    action_steps = [
        ActionItem(
            step=1,
            title="Confirm missing business details",
            detail="Provide precise turnover, interstate supply status, and investment details to finalize GST and MSME applicability.",
        ),
        ActionItem(
            step=2,
            title="Complete base registrations in sequence",
            detail="Start with PAN/TAN foundation, then GST/Udyam and sector-specific registrations.",
        ),
        ActionItem(
            step=3,
            title="Use official portals and maintain proof pack",
            detail="Submit through official links and retain acknowledgment/reference IDs for each filing.",
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
        gst_verification=gst_verification,
        pan_verification=pan_verification,
        data_sources=data_sources,
        disclaimer=(
            "This output is guidance only and not legal advice. Always verify "
            "latest rules, fees, and procedures on official government sources "
            "before filing."
        ),
    )


@app.post("/api/evaluate", response_model=BusinessSetupReport)
async def evaluate_business_profile(payload: BusinessProfile):
    try:
        return build_business_setup_report(payload)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
