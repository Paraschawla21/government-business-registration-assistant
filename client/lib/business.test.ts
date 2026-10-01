import { describe, expect, it } from "vitest";

import { INITIAL_STATE, validateForm } from "@/lib/business";

describe("validateForm", () => {
  it("returns validation errors for empty fields", () => {
    const errors = validateForm(INITIAL_STATE);

    expect(errors.businessType).toBeTruthy();
    expect(errors.industry).toBeTruthy();
    expect(errors.state).toBeTruthy();
    expect(errors.city).toBeTruthy();
    expect(errors.employees).toBeTruthy();
    expect(errors.turnover).toBeTruthy();
    expect(errors.activity).toBeTruthy();
    expect(errors.operations).toBeTruthy();
  });

  it("accepts a valid profile", () => {
    const errors = validateForm({
      businessType: "Private Limited",
      industry: "Information Technology",
      state: "Maharashtra",
      city: "Pune",
      employees: "12",
      turnover: "40 Lakhs - 1 Crore",
      activity: "Custom software product development",
      operations: "both",
      gstin: "27ABCDE1234F1Z5",
      pan: "ABCDE1234F",
    });

    expect(Object.keys(errors)).toHaveLength(0);
  });

  it("validates PAN format when provided", () => {
    const errors = validateForm({
      ...INITIAL_STATE,
      businessType: "Private Limited",
      industry: "Information Technology",
      state: "Maharashtra",
      city: "Pune",
      employees: "5",
      turnover: "20-40 Lakhs",
      activity: "Building software products",
      operations: "online",
      pan: "123INVALID",
    });

    expect(errors.pan).toBeTruthy();
  });
});
