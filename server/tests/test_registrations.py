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
    results = evaluate_registrations(profile)

    fssai = next(item for item in results if item.name == "FSSAI Registration/Licence")
    assert fssai.status == "Applicable"


def test_epfo_and_esic_based_on_employee_count():
    profile = _make_profile("Information Technology", 25, "both", "Above 1 Crore")
    results = evaluate_registrations(profile)

    epfo = next(item for item in results if item.name == "EPFO Registration")
    esic = next(item for item in results if item.name == "ESIC Registration")

    assert epfo.status == "Applicable"
    assert esic.status == "Applicable"
