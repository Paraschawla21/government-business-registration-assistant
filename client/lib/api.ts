import type { BusinessSetupReport, FormState } from "@/lib/business";

export async function submitBusinessProfile(
  form: FormState,
): Promise<BusinessSetupReport> {
  const res = await fetch("/api/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      businessType: form.businessType,
      industry: form.industry,
      state: form.state,
      city: form.city,
      employees: Number(form.employees),
      turnover: form.turnover,
      activity: form.activity,
      operations: form.operations,
      gstin: form.gstin,
      pan: form.pan,
    }),
  });

  if (!res.ok) {
    throw new Error(`Request failed with status ${res.status}`);
  }

  return (await res.json()) as BusinessSetupReport;
}
