from dataclasses import dataclass

from schemas import ApplicabilityStatus, BusinessProfile, RegistrationAssessment


@dataclass(frozen=True)
class RegistrationRule:
    name: str
    required_documents: list[str]
    official_links: list[str]
    verification_notes: list[str]


REGISTRATION_CATALOG: list[RegistrationRule] = [
    RegistrationRule(
        name="PAN and TAN",
        required_documents=[
            "Business constitution details",
            "Identity and address proof of proprietor/partners/directors",
            "Business address proof",
        ],
        official_links=["https://www.incometax.gov.in/iec/foportal/"],
        verification_notes=[
            "Verify latest PAN/TAN process and latest document checklist on the Income Tax portal.",
        ],
    ),
    RegistrationRule(
        name="GST Registration",
        required_documents=[
            "PAN of business/entity",
            "Business address proof",
            "Promoter/authorized signatory identity proof",
            "Bank account details",
        ],
        official_links=["https://www.gst.gov.in/"],
        verification_notes=[
            "GST thresholds and compulsory registration categories should be verified from official GST guidance.",
        ],
    ),
    RegistrationRule(
        name="Udyam (MSME) Registration",
        required_documents=[
            "Aadhaar of proprietor/authorized signatory",
            "PAN",
            "Business activity details",
        ],
        official_links=["https://udyamregistration.gov.in/"],
        verification_notes=[
            "MSME classification should be checked against current investment and turnover criteria on Udyam portal.",
        ],
    ),
    RegistrationRule(
        name="Shops and Establishments Registration",
        required_documents=[
            "Business address proof",
            "Identity proof of owner/authorized person",
            "Employee details (if any)",
        ],
        official_links=["https://labour.gov.in/"],
        verification_notes=[
            "This is state-specific and often city-specific; verify exact process on the relevant state labour portal.",
        ],
    ),
    RegistrationRule(
        name="EPFO Registration",
        required_documents=[
            "PAN",
            "Incorporation/constitution documents",
            "Employee details",
            "Bank details",
        ],
        official_links=["https://www.epfindia.gov.in/"],
        verification_notes=[
            "Applicability thresholds can change; verify current criteria on EPFO portal.",
        ],
    ),
    RegistrationRule(
        name="ESIC Registration",
        required_documents=[
            "PAN",
            "Business registration proof",
            "Employee details and wage information",
            "Bank details",
        ],
        official_links=["https://www.esic.gov.in/"],
        verification_notes=[
            "Employee threshold and wage conditions must be verified on ESIC portal.",
        ],
    ),
    RegistrationRule(
        name="FSSAI Registration/Licence",
        required_documents=[
            "Business constitution proof",
            "Premises details",
            "Identity proof of applicant",
            "Food category/activity details",
        ],
        official_links=["https://foscos.fssai.gov.in/"],
        verification_notes=[
            "Registration vs state/central licence category depends on scale/type; verify on FoSCoS.",
        ],
    ),
]


def evaluate_registrations(profile: BusinessProfile) -> list[RegistrationAssessment]:
    results: list[RegistrationAssessment] = []
    turnover = profile.turnover.lower()
    industry = profile.industry.lower()
    operations = profile.operations.lower()

    for entry in REGISTRATION_CATALOG:
        if entry.name == "PAN and TAN":
            results.append(
                RegistrationAssessment(
                    name=entry.name,
                    status=ApplicabilityStatus.APPLICABLE,
                    why_relevant="PAN is foundational for tax identity and TAN may be required for TDS compliance.",
                    required_documents=entry.required_documents,
                    information_still_required=[],
                    official_links=entry.official_links,
                    verification_notes=entry.verification_notes,
                )
            )
            continue

        if entry.name == "GST Registration":
            missing = [
                "Exact annual turnover estimate in INR",
                "Whether interstate taxable supplies are made",
            ]
            status = ApplicabilityStatus.MORE_INFO_REQUIRED
            reason = "GST applicability depends on turnover threshold and nature/place of supply."
            if turnover == "above 1 crore":
                status = ApplicabilityStatus.APPLICABLE
                missing = []
                reason = "High expected turnover indicates GST registration is likely applicable."
            elif operations in {"online", "both"} and turnover in {
                "40 lakhs - 1 crore",
                "above 1 crore",
            }:
                status = ApplicabilityStatus.APPLICABLE
                missing = []
                reason = "Online or mixed operations with higher turnover may trigger GST obligations."

            results.append(
                RegistrationAssessment(
                    name=entry.name,
                    status=status,
                    why_relevant=reason,
                    required_documents=entry.required_documents,
                    information_still_required=missing,
                    official_links=entry.official_links,
                    verification_notes=entry.verification_notes,
                )
            )
            continue

        if entry.name == "Udyam (MSME) Registration":
            results.append(
                RegistrationAssessment(
                    name=entry.name,
                    status=ApplicabilityStatus.MORE_INFO_REQUIRED,
                    why_relevant="MSME registration may be beneficial, but classification depends on investment and turnover details.",
                    required_documents=entry.required_documents,
                    information_still_required=[
                        "Plant/equipment investment details",
                        "Final turnover estimate in INR",
                    ],
                    official_links=entry.official_links,
                    verification_notes=entry.verification_notes,
                )
            )
            continue

        if entry.name == "Shops and Establishments Registration":
            status = (
                ApplicabilityStatus.APPLICABLE
                if operations in {"offline", "both"}
                else ApplicabilityStatus.NOT_RELEVANT
            )
            reason = (
                "Physical establishment operations commonly require local Shops and Establishments registration."
                if status == ApplicabilityStatus.APPLICABLE
                else "Purely online setup may not need this, subject to state rules."
            )
            notes = list(entry.verification_notes)
            results.append(
                RegistrationAssessment(
                    name=entry.name,
                    status=status,
                    why_relevant=reason,
                    required_documents=entry.required_documents,
                    information_still_required=[]
                    if status == ApplicabilityStatus.NOT_RELEVANT
                    else ["Exact office/shop location and local municipal jurisdiction"],
                    official_links=entry.official_links,
                    verification_notes=notes,
                )
            )
            continue

        if entry.name == "EPFO Registration":
            status = (
                ApplicabilityStatus.APPLICABLE
                if profile.employees >= 20
                else ApplicabilityStatus.NOT_RELEVANT
            )
            reason = (
                "Employee count is at/above commonly referenced EPFO threshold."
                if status == ApplicabilityStatus.APPLICABLE
                else "Current employee count is below commonly referenced EPFO threshold."
            )
            results.append(
                RegistrationAssessment(
                    name=entry.name,
                    status=status,
                    why_relevant=reason,
                    required_documents=entry.required_documents,
                    information_still_required=[] if status == ApplicabilityStatus.NOT_RELEVANT else ["Employee joining dates and payroll setup details"],
                    official_links=entry.official_links,
                    verification_notes=entry.verification_notes,
                )
            )
            continue

        if entry.name == "ESIC Registration":
            status = (
                ApplicabilityStatus.APPLICABLE
                if profile.employees >= 10
                else ApplicabilityStatus.NOT_RELEVANT
            )
            reason = (
                "Employee count suggests ESIC applicability may arise."
                if status == ApplicabilityStatus.APPLICABLE
                else "Current employee count is below commonly referenced ESIC threshold."
            )
            missing_info = (
                ["Employee wage details for ESIC wage-threshold check"]
                if status == ApplicabilityStatus.APPLICABLE
                else []
            )
            results.append(
                RegistrationAssessment(
                    name=entry.name,
                    status=status,
                    why_relevant=reason,
                    required_documents=entry.required_documents,
                    information_still_required=missing_info,
                    official_links=entry.official_links,
                    verification_notes=entry.verification_notes,
                )
            )
            continue

        if entry.name == "FSSAI Registration/Licence":
            is_food = "food" in industry or "beverage" in industry
            status = (
                ApplicabilityStatus.APPLICABLE
                if is_food
                else ApplicabilityStatus.NOT_RELEVANT
            )
            reason = (
                "Food and beverage activities usually require FSSAI registration or licence."
                if is_food
                else "No clear food handling/manufacturing activity indicated in profile."
            )
            results.append(
                RegistrationAssessment(
                    name=entry.name,
                    status=status,
                    why_relevant=reason,
                    required_documents=entry.required_documents,
                    information_still_required=[] if not is_food else ["Exact food activity category and scale of operations"],
                    official_links=entry.official_links,
                    verification_notes=entry.verification_notes,
                )
            )

    return results
