import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SuccessState } from "@/components/SuccessState";

describe("SuccessState", () => {
  it("renders report details", () => {
    render(
      <SuccessState
        onReset={vi.fn()}
        report={{
          profile_summary: "Profile summary",
          potential_registrations: [
            {
              name: "GST Registration",
              status: "Applicable",
              why_relevant: "Reason",
              required_documents: ["PAN"],
              information_still_required: [],
              official_links: ["https://www.gst.gov.in/"],
              verification_notes: ["Verify on portal"],
            },
          ],
          information_still_required: ["Exact turnover in INR"],
          suggested_sequence: [
            {
              step: 1,
              title: "Collect missing info",
              detail: "Add turnover details",
            },
          ],
          pan_verification: {
            checked: false,
            provider: "setu",
            message: "PAN not provided",
          },
          data_sources: [
            {
              source_type: "knowledge_base",
              source_name: "server/data/registrations.json",
              status: "used",
              message: "Used deterministic KB",
            },
          ],
          action_results: [
            {
              name: "markdown_report",
              status: "generated",
              message: "Markdown generated",
              artifact_filename: "report.md",
              artifact_content: "# report",
            },
            {
              name: "pdf_report",
              status: "generated",
              message: "PDF generated",
              artifact_filename: "report.pdf",
              artifact_base64: "UERG",
            },
            {
              name: "google_sheet_tracker",
              status: "generated",
              message: "Sheet updated",
              artifact_url: "https://docs.google.com/spreadsheets/d/123",
            },
          ],
          disclaimer: "Guidance only",
        }}
      />,
    );

    expect(screen.getByText("Your Profile Is Analyzed")).toBeInTheDocument();
    expect(screen.getByText("GST Registration")).toBeInTheDocument();
    expect(screen.getByText("Applicable")).toBeInTheDocument();
    expect(screen.getByText("Guidance only")).toBeInTheDocument();
    expect(screen.getByText("Generated outputs")).toBeInTheDocument();
  });
});
