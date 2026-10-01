export const BUSINESS_TYPES = [
  "Sole Proprietorship",
  "Partnership",
  "LLP",
  "Private Limited",
  "Other",
];

export const INDUSTRIES = [
  "Food & Beverage",
  "Information Technology",
  "Manufacturing",
  "Retail",
  "Healthcare",
  "Education",
  "Professional Services",
  "Construction & Real Estate",
  "Logistics & Transportation",
  "Other",
];

export const TURNOVER_BRACKETS = [
  "Under 20 Lakhs",
  "20-40 Lakhs",
  "40 Lakhs - 1 Crore",
  "Above 1 Crore",
];

export const OPERATIONS_OPTIONS = [
  { value: "online", label: "Entirely Online" },
  { value: "offline", label: "Entirely Offline" },
  { value: "both", label: "Both Online & Offline" },
];

export const GSTIN_PATTERN =
  /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;

export const PAN_PATTERN = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

export type FormState = {
  businessType: string;
  industry: string;
  state: string;
  city: string;
  employees: string;
  turnover: string;
  activity: string;
  operations: string;
  gstin: string;
  pan: string;
};

export const INITIAL_STATE: FormState = {
  businessType: "",
  industry: "",
  state: "",
  city: "",
  employees: "",
  turnover: "",
  activity: "",
  operations: "",
  gstin: "",
  pan: "",
};

export type Status = "idle" | "submitting" | "success" | "error";

export type ApplicabilityStatus =
  | "Applicable"
  | "More Info Required"
  | "Not Relevant";

export type RegistrationAssessment = {
  name: string;
  status: ApplicabilityStatus;
  why_relevant: string;
  required_documents: string[];
  information_still_required: string[];
  official_links: string[];
  verification_notes: string[];
};

export type ActionItem = {
  step: number;
  title: string;
  detail: string;
};

export type BusinessSetupReport = {
  profile_summary: string;
  potential_registrations: RegistrationAssessment[];
  information_still_required: string[];
  suggested_sequence: ActionItem[];
  gst_verification?: {
    checked?: boolean;
    provider?: string;
    gstin?: string;
    legal_name?: string | null;
    trade_name?: string | null;
    status?: string | null;
    message?: string;
  } | null;
  pan_verification?: {
    checked?: boolean;
    provider?: string;
    pan?: string;
    name?: string | null;
    status?: string | null;
    message?: string;
  } | null;
  data_sources?: {
    source_type: string;
    source_name: string;
    status: string;
    message: string;
  }[];
  action_results?: {
    name: string;
    status: string;
    message: string;
    artifact_url?: string | null;
    artifact_content?: string | null;
    artifact_filename?: string | null;
  }[];
  disclaimer: string;
};

export type FormErrors = Partial<Record<keyof FormState, string>>;

export function validateForm(form: FormState): FormErrors {
  const nextErrors: FormErrors = {};

  if (!form.businessType) nextErrors.businessType = "Please select a business type.";
  if (!form.industry) nextErrors.industry = "Please select an industry.";
  if (!form.state.trim()) nextErrors.state = "State is required.";
  if (!form.city.trim()) nextErrors.city = "City is required.";
  if (!form.employees || Number(form.employees) < 0) {
    nextErrors.employees = "Enter a valid number of employees.";
  }
  if (!form.turnover) {
    nextErrors.turnover = "Please select an expected turnover bracket.";
  }
  if (!form.activity.trim() || form.activity.trim().length < 10) {
    nextErrors.activity =
      "Please describe your core business activity (min 10 characters).";
  }
  if (!form.operations) {
    nextErrors.operations = "Please select an operations mode.";
  }
  if (form.gstin.trim() && !GSTIN_PATTERN.test(form.gstin.trim())) {
    nextErrors.gstin = "Enter a valid 15-character GSTIN (e.g. 27ABCDE1234F1Z5).";
  }
  if (form.pan.trim() && !PAN_PATTERN.test(form.pan.trim().toUpperCase())) {
    nextErrors.pan = "Enter a valid PAN (e.g. ABCDE1234F).";
  }

  return nextErrors;
}

export function inputClasses(hasError: boolean) {
  return `w-full rounded-lg border bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-colors focus:ring-2 focus:ring-blue-500/30 ${
    hasError ? "border-red-400 focus:border-red-500" : "border-slate-200 focus:border-blue-500"
  }`;
}

export function selectClasses(hasError: boolean) {
  return `w-full rounded-lg border bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition-colors focus:ring-2 focus:ring-blue-500/30 ${
    hasError ? "border-red-400 focus:border-red-500" : "border-slate-200 focus:border-blue-500"
  }`;
}
