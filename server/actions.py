import base64
import csv
import json
import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from io import BytesIO, StringIO
from typing import Optional
from urllib import error, request

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from schemas import ActionResult, BusinessSetupReport


def _clean_line(text: str, max_len: int = 110) -> str:
    if not text:
        return ""
    compact = " ".join(text.split())
    return compact[:max_len]


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
        artifact_mime_type="text/markdown",
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

    content = buffer.getvalue()
    return ActionResult(
        name="csv_tracker",
        status="generated",
        message="Checklist tracker CSV generated in-memory.",
        artifact_filename="business_setup_tracker.csv",
        artifact_mime_type="text/csv",
        artifact_content=content,
    )


def generate_pdf_report(report: BusinessSetupReport) -> ActionResult:
    packet = BytesIO()
    pdf = canvas.Canvas(packet, pagesize=A4)
    width, height = A4

    y = height - 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Government Business Setup Report")
    y -= 20

    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, f"Generated At: {datetime.utcnow().isoformat()}Z")
    y -= 20

    def write_line(text: str, bold: bool = False):
        nonlocal y
        if y < 60:
            pdf.showPage()
            y = height - 40
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", 10 if bold else 9)
        pdf.drawString(40, y, _clean_line(text, 120))
        y -= 14

    write_line("Profile Summary", bold=True)
    write_line(report.profile_summary)
    y -= 6

    write_line("Potential Registrations", bold=True)
    for item in report.potential_registrations:
        write_line(f"- {item.name} [{item.status}]", bold=True)
        write_line(f"  Why: {item.why_relevant}")
        if item.official_links:
            write_line(f"  Link: {item.official_links[0]}")

    y -= 6
    write_line("Suggested Sequence", bold=True)
    for step in report.suggested_sequence:
        write_line(f"{step.step}. {step.title}: {step.detail}")

    y -= 6
    write_line("Disclaimer", bold=True)
    write_line(report.disclaimer)

    pdf.save()
    pdf_bytes = packet.getvalue()
    encoded = base64.b64encode(pdf_bytes).decode("ascii")

    return ActionResult(
        name="pdf_report",
        status="generated",
        message="PDF report generated in-memory.",
        artifact_filename="business_setup_report.pdf",
        artifact_mime_type="application/pdf",
        artifact_base64=encoded,
    )


def create_google_sheet_tracker(report: BusinessSetupReport) -> ActionResult:
    sheets_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
    api_key = os.getenv("GOOGLE_SHEETS_API_KEY", "").strip()

    if not sheets_id or not api_key:
        return ActionResult(
            name="google_sheet_tracker",
            status="skipped",
            message="Google Sheets integration not configured (requires GOOGLE_SHEETS_ID and GOOGLE_SHEETS_API_KEY).",
        )

    rows = [
        [
            "Registration",
            "Status",
            "Why Relevant",
            "Required Documents",
            "Information Still Required",
            "Official Link",
        ]
    ]
    for item in report.potential_registrations:
        rows.append(
            [
                item.name,
                str(item.status),
                item.why_relevant,
                " | ".join(item.required_documents),
                " | ".join(item.information_still_required),
                item.official_links[0] if item.official_links else "",
            ]
        )

    endpoint = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheets_id}/values/Sheet1!A1:append"
        f"?valueInputOption=RAW&key={api_key}"
    )

    payload = json.dumps({"values": rows}).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            if response.status < 200 or response.status >= 300:
                return ActionResult(
                    name="google_sheet_tracker",
                    status="fallback",
                    message=f"Google Sheets append failed with status {response.status}.",
                )

        return ActionResult(
            name="google_sheet_tracker",
            status="generated",
            message="Checklist appended to configured Google Sheet.",
            artifact_url=f"https://docs.google.com/spreadsheets/d/{sheets_id}",
        )
    except error.HTTPError as exc:
        return ActionResult(
            name="google_sheet_tracker",
            status="fallback",
            message=f"Google Sheets API HTTP error: {exc.code}",
        )
    except Exception:
        return ActionResult(
            name="google_sheet_tracker",
            status="fallback",
            message="Google Sheets tracker creation failed.",
        )


def send_email_report(report: BusinessSetupReport, markdown_report: Optional[ActionResult]) -> ActionResult:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "0") or "0")
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    sender = os.getenv("REPORT_FROM_EMAIL", "").strip()
    recipient = os.getenv("REPORT_TO_EMAIL", "").strip()

    if not all([host, port, username, password, sender, recipient]):
        return ActionResult(
            name="email_delivery",
            status="skipped",
            message="Email integration not configured (SMTP/recipient env vars missing).",
        )

    msg = EmailMessage()
    msg["Subject"] = "Business Setup Report"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(
        "Your business setup report has been generated. "
        "Please find the summary attached as markdown."
    )

    if markdown_report and markdown_report.artifact_content:
        msg.add_attachment(
            markdown_report.artifact_content.encode("utf-8"),
            maintype="text",
            subtype="markdown",
            filename=markdown_report.artifact_filename or "business_setup_report.md",
        )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls(context=context)
            server.login(username, password)
            server.send_message(msg)
        return ActionResult(
            name="email_delivery",
            status="sent",
            message=f"Report email sent to {recipient}.",
        )
    except Exception:
        return ActionResult(
            name="email_delivery",
            status="fallback",
            message="Email delivery failed.",
        )


def run_actions(report: BusinessSetupReport) -> list[ActionResult]:
    markdown = generate_markdown_report(report)
    csv_tracker = generate_csv_tracker(report)
    pdf_report = generate_pdf_report(report)
    sheet_tracker = create_google_sheet_tracker(report)
    email_delivery = send_email_report(report, markdown)
    return [markdown, csv_tracker, pdf_report, sheet_tracker, email_delivery]
