import os
from typing import Any

import ollama
from pydantic import BaseModel, Field

from actions import run_actions
from gov_apis import verify_gstin_with_setu, verify_pan_with_setu
from registrations import evaluate_registrations
from schemas import (
    ActionItem,
    ApplicabilityStatus,
    BusinessProfile,
    BusinessSetupReport,
    DataSourceLog,
    RegistrationAssessment,
)


class LLMSequenceItem(BaseModel):
    step: int = Field(ge=1)
    title: str
    detail: str


class LLMOrchestrationOutput(BaseModel):
    profile_summary: str
    suggested_sequence: list[LLMSequenceItem]


def _base_profile_summary(profile: BusinessProfile) -> str:
    return (
        f"{profile.business_type} in {profile.city}, {profile.state} operating in "
        f"{profile.industry} with {profile.employees} employees, expected turnover "
        f"'{profile.turnover}', operations '{profile.operations}'."
    )


def _deterministic_sequence() -> list[ActionItem]:
    return [
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


def _fallback_report(profile: BusinessProfile, message: str) -> BusinessSetupReport:
    return BusinessSetupReport(
        profile_summary=_base_profile_summary(profile),
        potential_registrations=[
            RegistrationAssessment(
                name="Manual Verification Required",
                issuing_authority="Multiple authorities",
                status=ApplicabilityStatus.MORE_INFO_REQUIRED,
                why_relevant="The orchestration pipeline encountered an error and requires manual verification.",
                required_documents=[],
                information_still_required=["Re-run analysis after resolving backend error"],
                official_links=["https://www.india.gov.in/"],
                source_reference_url="https://www.india.gov.in/",
                source_reference_date="2026-10-01",
                verification_notes=["Perform manual verification with official portals before filing."],
            )
        ],
        information_still_required=["Manual review required"],
        suggested_sequence=_deterministic_sequence(),
        gst_verification=None,
        pan_verification=None,
        data_sources=[
            DataSourceLog(
                source_type="system",
                source_name="agent_orchestrator",
                status="fallback",
                message=message,
            )
        ],
        disclaimer=(
            "This output is guidance only and not legal advice. Always verify latest rules, "
            "fees, and procedures on official government sources before filing."
        ),
    )


def _maybe_llm_enrich(
    profile: BusinessProfile,
    assessments: list[RegistrationAssessment],
    default_summary: str,
    default_sequence: list[ActionItem],
    data_sources: list[DataSourceLog],
) -> tuple[str, list[ActionItem]]:
    llm_enabled = os.getenv("AGENT_ENABLE_LLM", "false").strip().lower() == "true"
    if not llm_enabled:
        data_sources.append(
            DataSourceLog(
                source_type="llm",
                source_name="ollama",
                status="skipped",
                message="LLM orchestration disabled (set AGENT_ENABLE_LLM=true to enable).",
            )
        )
        return default_summary, default_sequence

    try:
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a compliance workflow assistant. Use only provided tool outputs. "
                        "Do not introduce new registrations, documents, fees, or deadlines. "
                        "Return only the requested JSON schema."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Business profile:\n"
                        f"- businessType: {profile.business_type}\n"
                        f"- industry: {profile.industry}\n"
                        f"- state: {profile.state}\n"
                        f"- city: {profile.city}\n"
                        f"- employees: {profile.employees}\n"
                        f"- turnover: {profile.turnover}\n"
                        f"- operations: {profile.operations}\n"
                        f"- activity: {profile.activity}\n"
                        "\n"
                        "Registration assessments (authoritative; do not alter statuses or names):\n"
                        f"{[item.model_dump() for item in assessments]}\n\n"
                        "Provide concise profile summary and a practical 3-step sequence."
                    ),
                },
            ],
            format=LLMOrchestrationOutput.model_json_schema(),
        )

        parsed = LLMOrchestrationOutput.model_validate_json(response["message"]["content"])
        sequence = [
            ActionItem(step=item.step, title=item.title, detail=item.detail)
            for item in sorted(parsed.suggested_sequence, key=lambda item: item.step)
        ]

        data_sources.append(
            DataSourceLog(
                source_type="llm",
                source_name=f"ollama:{model_name}",
                status="used",
                message="LLM used for wording/prioritization only.",
            )
        )
        return parsed.profile_summary, sequence or default_sequence
    except Exception:
        data_sources.append(
            DataSourceLog(
                source_type="llm",
                source_name="ollama",
                status="fallback",
                message="LLM enrichment failed; deterministic wording used.",
            )
        )
        return default_summary, default_sequence


def run_business_setup_agent(profile: BusinessProfile) -> BusinessSetupReport:
    try:
        items, kb_source_log = evaluate_registrations(profile)
        data_sources: list[DataSourceLog] = [kb_source_log]

        gst_verification: dict[str, Any] | None = None
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
                "message": "PAN not provided by user; live PAN verification skipped.",
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

        default_summary = _base_profile_summary(profile)
        default_sequence = _deterministic_sequence()
        profile_summary, suggested_sequence = _maybe_llm_enrich(
            profile=profile,
            assessments=items,
            default_summary=default_summary,
            default_sequence=default_sequence,
            data_sources=data_sources,
        )

        report = BusinessSetupReport(
            profile_summary=profile_summary,
            potential_registrations=items,
            information_still_required=sorted(
                {
                    info
                    for entry in items
                    for info in entry.information_still_required
                }
            ),
            suggested_sequence=suggested_sequence,
            gst_verification=gst_verification,
            pan_verification=pan_verification,
            data_sources=data_sources,
            disclaimer=(
                "This output is guidance only and not legal advice. Always verify "
                "latest rules, fees, and procedures on official government sources "
                "before filing."
            ),
        )
        report.action_results = run_actions(report)
        return report
    except Exception as exc:
        return _fallback_report(profile, f"Agent fallback due to error: {type(exc).__name__}")
