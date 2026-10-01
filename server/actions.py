import csv
from datetime import datetime
from io import StringIO

from schemas import ActionResult, BusinessSetupReport


def generate_markdown_report(report: BusinessSetupReport) -> ActionResult:
    lines: list[str] = []
    lines.append("# Government Business Setup Report")
    lines.append("")
    lines.append(f"Generated At: {datetime.utcnow().isoformat()}Z")
    lines.append("")
    lines.append("## Profile Summary")
    lines.append(report.profile_summary)
    lines.append("")
    lines.append("## Potential Registrations")
    for item in report.potential_registrations:
        lines.append(f"### {item.name}")
        lines.append(f"- Status: {item.status}")
        if item.issuing_authority:
            lines.append(f"- Issuing Authority: {item.issuing_authority}")
        lines.append(f"- Why Relevant: {item.why_relevant}")
        if item.required_documents:
            lines.append("- Required Documents:")
            for doc in item.required_documents:
                lines.append(f"  - {doc}")
        if item.information_still_required:
            lines.append("- Information Still Required:")
            for detail in item.information_still_required:
                lines.append(f"  - {detail}")
        if item.official_links:
            lines.append(f"- Official Link: {item.official_links[0]}")
        if item.source_reference_url:
            lines.append(f"- Source Reference: {item.source_reference_url}")
        if item.source_reference_date:
            lines.append(f"- Source Date: {item.source_reference_date}")
        lines.append("")

    lines.append("## Suggested Sequence")
    for step in report.suggested_sequence:
        lines.append(f"{step.step}. {step.title} - {step.detail}")
    lines.append("")
    lines.append("## Data Sources")
    for src in report.data_sources:
        lines.append(f"- {src.source_name} ({src.source_type}) [{src.status}] - {src.message}")
    lines.append("")
    lines.append("## Disclaimer")
    lines.append(report.disclaimer)

    content = "\n".join(lines)
    return ActionResult(
        name="markdown_report",
        status="generated",
        message="Markdown business setup report generated in-memory.",
        artifact_filename="business_setup_report.md",
        artifact_content=content,
    )


def generate_csv_tracker(report: BusinessSetupReport) -> ActionResult:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Registration",
            "Status",
            "Why Relevant",
            "Required Documents",
            "Information Still Required",
            "Official Link",
        ]
    )

    for item in report.potential_registrations:
        writer.writerow(
            [
                item.name,
                item.status,
                item.why_relevant,
                " | ".join(item.required_documents),
                " | ".join(item.information_still_required),
                item.official_links[0] if item.official_links else "",
            ]
        )

    return ActionResult(
        name="csv_tracker",
        status="generated",
        message="Checklist tracker CSV generated in-memory.",
        artifact_filename="business_setup_tracker.csv",
        artifact_content=buffer.getvalue(),
    )


def run_actions(report: BusinessSetupReport) -> list[ActionResult]:
    return [generate_markdown_report(report), generate_csv_tracker(report)]
