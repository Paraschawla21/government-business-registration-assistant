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
        pan=None,
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
        pan=None,
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


def test_all_catalog_registrations_are_returned():
    profile = _make_profile("Information Technology", 5, "both", "20-40 Lakhs")
    results, _ = evaluate_registrations(profile)

    names = {item.name for item in results}
    expected = {
        "PAN and TAN",
        "GST Registration",
        "Udyam (MSME) Registration",
        "Shops and Establishments Registration",
        "EPFO Registration",
        "ESIC Registration",
        "FSSAI Registration/Licence",
        "Professional Tax Registration",
        "Trade Licence",
        "Import Export Code (IEC)",
    }
    assert names == expected


def test_iec_activity_keyword_matching():
    profile = BusinessProfile(
        businessType="Private Limited",
        industry="Logistics & Transportation",
        state="Maharashtra",
        city="Mumbai",
        employees=12,
        turnover="40 Lakhs - 1 Crore",
        activity="We import components and export finished kits globally",
        operations="both",
        gstin=None,
        pan=None,
    )
    results, _ = evaluate_registrations(profile)
    iec = next(item for item in results if item.name == "Import Export Code (IEC)")
    assert iec.status == "Applicable"


def test_trade_license_for_online_only_is_more_info():
    profile = _make_profile("Information Technology", 4, "online", "Under 20 Lakhs")
    results, _ = evaluate_registrations(profile)
    trade = next(item for item in results if item.name == "Trade Licence")
    assert trade.status == "More Info Required"


def test_state_portal_routing_for_maharashtra_links():
    profile = _make_profile("Professional Services", 8, "offline", "20-40 Lakhs")
    results, _ = evaluate_registrations(profile)

    shops = next(item for item in results if item.name == "Shops and Establishments Registration")
    pt = next(item for item in results if item.name == "Professional Tax Registration")
    trade = next(item for item in results if item.name == "Trade Licence")

    assert shops.official_links[0] == "https://aaplesarkar.mahaonline.gov.in/"
    assert pt.official_links[0] == "https://www.mahagst.gov.in/"
    assert trade.official_links[0] == "https://portal.mcgm.gov.in/"
