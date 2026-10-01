from registrations import evaluate_registrations
from schemas import BusinessProfile


def _make_profile(industry: str, employees: int, operations: str, turnover: str):
    return BusinessProfile(
        businessType="Private Limited",
        industry=industry,
        state="Maharashtra",
        city="Pune",
        employees=employees,
        turnover=turnover,
        activity="Software and services business",
        operations=operations,
        gstin=None,
    )


def test_food_business_marks_fssai_applicable():
    profile = _make_profile("Food & Beverage", 5, "offline", "Under 20 Lakhs")
    results, _ = evaluate_registrations(profile)

    fssai = next(item for item in results if item.name == "FSSAI Registration/Licence")
    assert fssai.status == "Applicable"


def test_epfo_and_esic_based_on_employee_count():
    profile = _make_profile("Information Technology", 25, "both", "Above 1 Crore")
    results, _ = evaluate_registrations(profile)

    epfo = next(item for item in results if item.name == "EPFO Registration")
    esic = next(item for item in results if item.name == "ESIC Registration")

    assert epfo.status == "Applicable"
    assert esic.status == "Applicable"


def test_deterministic_output_for_same_input():
    profile = _make_profile("Retail", 8, "offline", "20-40 Lakhs")
    first, _ = evaluate_registrations(profile)
    second, _ = evaluate_registrations(profile)

    assert [item.model_dump() for item in first] == [item.model_dump() for item in second]


def test_professional_tax_state_logic():
    applicable_profile = _make_profile("Professional Services", 3, "offline", "Under 20 Lakhs")
    not_sure_profile = BusinessProfile(
        businessType="Private Limited",
        industry="Professional Services",
        state="Rajasthan",
        city="Jaipur",
        employees=3,
        turnover="Under 20 Lakhs",
        activity="Consulting services",
        operations="offline",
        gstin=None,
    )

    applicable_results, _ = evaluate_registrations(applicable_profile)
    uncertain_results, _ = evaluate_registrations(not_sure_profile)

    applicable = next(
        item for item in applicable_results if item.name == "Professional Tax Registration"
    )
    uncertain = next(
        item for item in uncertain_results if item.name == "Professional Tax Registration"
    )

    assert applicable.status == "Applicable"
    assert uncertain.status == "More Info Required"
