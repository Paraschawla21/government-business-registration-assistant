import json
from pathlib import Path
from typing import Any

from schemas import ApplicabilityStatus, BusinessProfile, DataSourceLog, RegistrationAssessment


CATALOG_PATH = Path(__file__).resolve().parent / "data" / "registrations.json"
STATE_PORTALS_PATH = Path(__file__).resolve().parent / "data" / "india_registration_portals.json"


def _load_catalog() -> list[dict[str, Any]]:
    with CATALOG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _load_state_portal_map() -> dict[str, dict[str, str]]:
    with STATE_PORTALS_PATH.open("r", encoding="utf-8") as file:
        rows = json.load(file)

    mapping: dict[str, dict[str, str]] = {}
    for row in rows:
        state_name = row.get("State / Union Territory", "").strip()
        if not state_name:
            continue
        mapping[state_name] = {
            "sne_url": row.get("S&E URL", "").strip(),
            "pt_url": row.get("PT URL", "").strip(),
            "trade_url": row.get("Trade Licence URL", "").strip(),
        }
    return mapping


def _resolve_state_portals(profile_state: str, state_map: dict[str, dict[str, str]]) -> dict[str, str]:
    normalized = profile_state.strip().lower()
    for key, value in state_map.items():
        key_norm = key.lower()
        if normalized == key_norm:
            return value
        if normalized in key_norm or key_norm in normalized:
            return value
    return {}


def _turnover_rank(turnover: str) -> int:
    order = {
        "Under 20 Lakhs": 0,
        "20-40 Lakhs": 1,
        "40 Lakhs - 1 Crore": 2,
        "Above 1 Crore": 3,
    }
    return order.get(turnover, -1)


def _has_any_keyword(text: str, keywords: list[str]) -> bool:
    normalized = text.lower()
    return any(keyword.lower() in normalized for keyword in keywords)


def _build_assessment(
    entry: dict[str, Any],
    status: ApplicabilityStatus,
    reason: str,
    missing_info: list[str],
) -> RegistrationAssessment:
    return RegistrationAssessment(
        name=entry["name"],
        issuing_authority=entry.get("issuing_authority"),
        status=status,
        why_relevant=reason,
        required_documents=entry.get("required_documents", []),
        information_still_required=missing_info,
        official_links=[entry.get("official_url", "")],
        source_reference_url=entry.get("source_reference_url"),
        source_reference_date=entry.get("source_reference_date"),
        verification_notes=entry.get("verification_notes", []),
    )


def evaluate_registrations(profile: BusinessProfile) -> tuple[list[RegistrationAssessment], DataSourceLog]:
    catalog = _load_catalog()
    state_portals = _load_state_portal_map()
    resolved_portals = _resolve_state_portals(profile.state, state_portals)
    results: list[RegistrationAssessment] = []

    for entry in catalog:
        conditions = entry.get("conditions", {})
        name = entry.get("name", "Unknown")

        if conditions.get("always_applicable"):
            results.append(
                _build_assessment(
                    entry,
                    ApplicabilityStatus.APPLICABLE,
                    "Foundational registration generally required for tax and compliance identity.",
                    [],
                )
            )
            continue

        if name == "GST Registration":
            high_turnover = _turnover_rank(profile.turnover) >= 2
            higher_risk_ops = profile.operations in conditions.get("operations_likely_applicable", [])
            if high_turnover or higher_risk_ops:
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.APPLICABLE,
                        "Turnover and/or operations profile suggests GST registration may be applicable.",
                        [],
                    )
                )
            else:
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.MORE_INFO_REQUIRED,
                        "GST applicability depends on turnover details and supply nature; more details are required.",
                        conditions.get("requires_additional_info", []),
                    )
                )
            continue

        if conditions.get("always_more_info_required"):
            results.append(
                _build_assessment(
                    entry,
                    ApplicabilityStatus.MORE_INFO_REQUIRED,
                    "More details are required to determine final applicability.",
                    conditions.get("requires_additional_info", []),
                )
            )
            continue

        if "operations_applicable" in conditions:
            official_links = [entry.get("official_url", "")]
            if name == "Shops and Establishments Registration" and resolved_portals.get("sne_url"):
                official_links = [resolved_portals["sne_url"]]
            if name == "Trade Licence" and resolved_portals.get("trade_url"):
                official_links = [resolved_portals["trade_url"]]

            if profile.operations in conditions.get("operations_applicable", []):
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.APPLICABLE,
                        "Operational mode indicates this registration is likely relevant.",
                        conditions.get("requires_additional_info", []),
                    )
                )
                results[-1].official_links = official_links
            elif profile.operations in conditions.get("operations_not_relevant", []):
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.NOT_RELEVANT,
                        "Current operational mode does not strongly indicate applicability.",
                        [],
                    )
                )
                results[-1].official_links = official_links
            else:
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.MORE_INFO_REQUIRED,
                        "Unable to determine applicability from operations alone.",
                        conditions.get("requires_additional_info", []),
                    )
                )
                results[-1].official_links = official_links
            continue

        if "employees_min_applicable" in conditions:
            threshold = int(conditions["employees_min_applicable"])
            if profile.employees >= threshold:
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.APPLICABLE,
                        f"Employee count meets or exceeds a commonly used threshold ({threshold}).",
                        conditions.get("requires_additional_info", []),
                    )
                )
            else:
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.NOT_RELEVANT,
                        f"Employee count is currently below the commonly used threshold ({threshold}).",
                        [],
                    )
                )
            continue

        if "industry_keywords" in conditions:
            if _has_any_keyword(profile.industry, conditions.get("industry_keywords", [])):
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.APPLICABLE,
                        "Industry profile suggests this registration/licence may be required.",
                        conditions.get("requires_additional_info", []),
                    )
                )
            else:
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.NOT_RELEVANT,
                        "Industry profile does not strongly indicate this registration.",
                        [],
                    )
                )
            continue

        if conditions.get("state_specific"):
            official_links = [entry.get("official_url", "")]
            if name == "Professional Tax Registration" and resolved_portals.get("pt_url"):
                official_links = [resolved_portals["pt_url"]]

            if profile.state in conditions.get("states_likely_applicable", []):
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.APPLICABLE,
                        "State appears to have this registration category; verify exact state process.",
                        conditions.get("requires_additional_info", []),
                    )
                )
                results[-1].official_links = official_links
            else:
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.MORE_INFO_REQUIRED,
                        "State-specific applicability is uncertain for this location.",
                        conditions.get("requires_additional_info", []),
                    )
                )
                results[-1].official_links = official_links
            continue

        if "activity_keywords" in conditions:
            if _has_any_keyword(profile.activity, conditions.get("activity_keywords", [])):
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.APPLICABLE,
                        "Business activity indicates this registration may be relevant.",
                        conditions.get("requires_additional_info", []),
                    )
                )
            else:
                results.append(
                    _build_assessment(
                        entry,
                        ApplicabilityStatus.MORE_INFO_REQUIRED,
                        "International trade intent is not explicit from current activity description.",
                        conditions.get("requires_additional_info", []),
                    )
                )
            continue

        results.append(
            _build_assessment(
                entry,
                ApplicabilityStatus.MORE_INFO_REQUIRED,
                "Insufficient structured conditions; manual review required.",
                conditions.get("requires_additional_info", []),
            )
        )

    source_log = DataSourceLog(
        source_type="knowledge_base",
        source_name="server/data/registrations.json",
        status="used",
        message="Deterministic registration catalog was used for applicability evaluation.",
    )

    return results, source_log
