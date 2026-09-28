"use client";

import { useState, type FormEvent } from "react";

const BUSINESS_TYPES = [
  "Sole Proprietorship",
  "Partnership",
  "LLP",
  "Private Limited",
  "Other",
];

const INDUSTRIES = [
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

const TURNOVER_BRACKETS = [
  "Under 20 Lakhs",
  "20-40 Lakhs",
  "40 Lakhs - 1 Crore",
  "Above 1 Crore",
];

const OPERATIONS_OPTIONS = [
  { value: "online", label: "Entirely Online" },
  { value: "offline", label: "Entirely Offline" },
  { value: "both", label: "Both Online & Offline" },
];

// Standard 15-character GSTIN format, e.g. 27ABCDE1234F1Z5
const GSTIN_PATTERN =
  /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;

type FormState = {
  businessType: string;
  industry: string;
  state: string;
  city: string;
  employees: string;
  turnover: string;
  activity: string;
  operations: string;
  gstin: string;
};

const INITIAL_STATE: FormState = {
  businessType: "",
  industry: "",
  state: "",
  city: "",
  employees: "",
  turnover: "",
  activity: "",
  operations: "",
  gstin: "",
};

type Status = "idle" | "submitting" | "success" | "error";

type ToolReview = {
  tool_name: string;
  pros: string[];
  cons: string[];
  rating_out_of_10: number;
};

export default function Home() {
  const [form, setForm] = useState<FormState>(INITIAL_STATE);
  const [errors, setErrors] = useState<
    Partial<Record<keyof FormState, string>>
  >({});
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [review, setReview] = useState<ToolReview | null>(null);

  const updateField = (field: keyof FormState, value: string) => {
    setForm((prev) => ({
      ...prev,
      [field]: field === "gstin" ? value.toUpperCase() : value,
    }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const nextErrors: Partial<Record<keyof FormState, string>> = {};

    if (!form.businessType)
      nextErrors.businessType = "Please select a business type.";
    if (!form.industry) nextErrors.industry = "Please select an industry.";
    if (!form.state.trim()) nextErrors.state = "State is required.";
    if (!form.city.trim()) nextErrors.city = "City is required.";
    if (!form.employees || Number(form.employees) < 0)
      nextErrors.employees = "Enter a valid number of employees.";
    if (!form.turnover)
      nextErrors.turnover = "Please select an expected turnover bracket.";
    if (!form.activity.trim() || form.activity.trim().length < 10)
      nextErrors.activity =
        "Please describe your core business activity (min 10 characters).";
    if (!form.operations)
      nextErrors.operations = "Please select an operations mode.";

    // GSTIN is optional, but if provided it must match the standard 15-character format
    if (form.gstin.trim() && !GSTIN_PATTERN.test(form.gstin.trim())) {
      nextErrors.gstin =
        "Enter a valid 15-character GSTIN (e.g. 27ABCDE1234F1Z5).";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validate()) return;

    setStatus("submitting");
    setErrorMessage("");

    try {
      const res = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool_name: form.activity.trim() }),
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      setReview((await res.json()) as ToolReview);
      setStatus("success");
    } catch (err) {
      setStatus("error");
      setErrorMessage(
        err instanceof Error
          ? err.message
          : "Something went wrong while submitting your profile. Please try again.",
      );
    }
  };

  const handleReset = () => {
    setForm(INITIAL_STATE);
    setErrors({});
    setStatus("idle");
    setErrorMessage("");
    setReview(null);
  };

  return (
    <div className="flex flex-1 flex-col items-center bg-slate-50 px-4 py-10 sm:py-16">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-700 ring-1 ring-inset ring-blue-200">
            <span className="h-2 w-2 rounded-full bg-blue-600" />
            Government Business Registration Assistant
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Let&apos;s build your registration roadmap
          </h1>
          <p className="mt-2 text-sm text-slate-500 sm:text-base">
            Answer a few questions about your business and we&apos;ll generate a
            personalized government registration checklist for you.
          </p>
        </div>

        {/* Card */}
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-200/50">
          {status === "success" ? (
            <SuccessState onReset={handleReset} review={review} />
          ) : (
            <form onSubmit={handleSubmit} noValidate className="p-6 sm:p-8">
              <div className="mb-6 border-b border-slate-100 pb-4">
                <h2 className="text-lg font-semibold text-slate-900">
                  Business Profile Details
                </h2>
                <p className="text-sm text-slate-500">
                  Fields marked <span className="text-red-500">*</span> are
                  required.
                </p>
              </div>

              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                {/* Business Type */}
                <Field
                  label="Business Type"
                  required
                  error={errors.businessType}
                >
                  <select
                    value={form.businessType}
                    onChange={(e) =>
                      updateField("businessType", e.target.value)
                    }
                    className={selectClasses(!!errors.businessType)}
                  >
                    <option value="">Select business type</option>
                    {BUSINESS_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </Field>

                {/* Industry */}
                <Field label="Industry" required error={errors.industry}>
                  <select
                    value={form.industry}
                    onChange={(e) => updateField("industry", e.target.value)}
                    className={selectClasses(!!errors.industry)}
                  >
                    <option value="">Select industry</option>
                    {INDUSTRIES.map((industry) => (
                      <option key={industry} value={industry}>
                        {industry}
                      </option>
                    ))}
                  </select>
                </Field>

                {/* State */}
                <Field label="State" required error={errors.state}>
                  <input
                    type="text"
                    placeholder="e.g. Maharashtra"
                    value={form.state}
                    onChange={(e) => updateField("state", e.target.value)}
                    className={inputClasses(!!errors.state)}
                  />
                </Field>

                {/* City */}
                <Field label="City" required error={errors.city}>
                  <input
                    type="text"
                    placeholder="e.g. Pune"
                    value={form.city}
                    onChange={(e) => updateField("city", e.target.value)}
                    className={inputClasses(!!errors.city)}
                  />
                </Field>

                {/* Employees */}
                <Field
                  label="Number of Employees"
                  required
                  error={errors.employees}
                >
                  <input
                    type="number"
                    min={0}
                    placeholder="e.g. 5"
                    value={form.employees}
                    onChange={(e) => updateField("employees", e.target.value)}
                    className={inputClasses(!!errors.employees)}
                  />
                </Field>

                {/* Turnover */}
                <Field
                  label="Expected Turnover (INR)"
                  required
                  error={errors.turnover}
                >
                  <select
                    value={form.turnover}
                    onChange={(e) => updateField("turnover", e.target.value)}
                    className={selectClasses(!!errors.turnover)}
                  >
                    <option value="">Select turnover bracket</option>
                    {TURNOVER_BRACKETS.map((bracket) => (
                      <option key={bracket} value={bracket}>
                        {bracket}
                      </option>
                    ))}
                  </select>
                </Field>

                {/* Core Business Activity */}
                <div className="sm:col-span-2">
                  <Field
                    label="Core Business Activity"
                    required
                    error={errors.activity}
                  >
                    <textarea
                      rows={3}
                      placeholder="Briefly describe what your business does..."
                      value={form.activity}
                      onChange={(e) => updateField("activity", e.target.value)}
                      className={
                        inputClasses(!!errors.activity) + " resize-none"
                      }
                    />
                  </Field>
                </div>

                {/* Operations */}
                <div className="sm:col-span-2">
                  <Field label="Operations" required error={errors.operations}>
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                      {OPERATIONS_OPTIONS.map((opt) => (
                        <label
                          key={opt.value}
                          className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2.5 text-sm transition-colors ${
                            form.operations === opt.value
                              ? "border-blue-600 bg-blue-50 text-blue-700"
                              : "border-slate-200 text-slate-600 hover:border-slate-300"
                          }`}
                        >
                          <input
                            type="radio"
                            name="operations"
                            value={opt.value}
                            checked={form.operations === opt.value}
                            onChange={(e) =>
                              updateField("operations", e.target.value)
                            }
                            className="h-4 w-4 accent-blue-600"
                          />
                          {opt.label}
                        </label>
                      ))}
                    </div>
                  </Field>
                </div>

                {/* GSTIN */}
                <div className="sm:col-span-2">
                  <Field label="GSTIN" error={errors.gstin} optionalHint>
                    <input
                      type="text"
                      placeholder="e.g. 27ABCDE1234F1Z5"
                      maxLength={15}
                      value={form.gstin}
                      onChange={(e) => updateField("gstin", e.target.value)}
                      className={
                        inputClasses(!!errors.gstin) +
                        " uppercase tracking-wide"
                      }
                    />
                    <p className="mt-1.5 flex items-start gap-1.5 text-xs text-slate-400">
                      <SparkleIcon />
                      If you already have a GSTIN, our AI agent will fetch and
                      verify your live official GST data automatically.
                    </p>
                  </Field>
                </div>
              </div>

              {status === "error" && (
                <div className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  <span className="font-medium">Submission failed: </span>
                  {errorMessage}
                </div>
              )}

              <button
                type="submit"
                disabled={status === "submitting"}
                className="mt-8 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm shadow-blue-600/30 transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              >
                {status === "submitting" ? (
                  <>
                    <Spinner />
                    Analyzing Requirements...
                  </>
                ) : (
                  "Generate My Registration Checklist"
                )}
              </button>

              <p className="mt-4 text-center text-xs text-slate-400">
                Your information is used solely to generate a personalized
                registration guide and is not shared with third parties.
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  required,
  optionalHint,
  error,
  children,
}: {
  label: string;
  required?: boolean;
  optionalHint?: boolean;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-slate-700">
        {label}
        {required && <span className="ml-0.5 text-red-500">*</span>}
        {optionalHint && (
          <span className="ml-1.5 text-xs font-normal text-slate-400">
            (Optional)
          </span>
        )}
      </label>
      {children}
      {error && (
        <p className="mt-1 text-xs font-medium text-red-500">{error}</p>
      )}
    </div>
  );
}

function inputClasses(hasError: boolean) {
  return `w-full rounded-lg border bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-colors focus:ring-2 focus:ring-blue-500/30 ${
    hasError
      ? "border-red-400 focus:border-red-500"
      : "border-slate-200 focus:border-blue-500"
  }`;
}

function selectClasses(hasError: boolean) {
  return `w-full rounded-lg border bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition-colors focus:ring-2 focus:ring-blue-500/30 ${
    hasError
      ? "border-red-400 focus:border-red-500"
      : "border-slate-200 focus:border-blue-500"
  }`;
}

function SparkleIcon() {
  return (
    <svg
      className="mt-0.5 h-3.5 w-3.5 shrink-0 text-blue-500"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M12 2l1.6 5.4L19 9l-5.4 1.6L12 16l-1.6-5.4L5 9l5.4-1.6L12 2zM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15z" />
    </svg>
  );
}

function Spinner() {
  return (
    <svg
      className="h-4 w-4 animate-spin text-white"
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
  );
}

function SuccessState({
  onReset,
  review,
}: {
  onReset: () => void;
  review: ToolReview | null;
}) {
  return (
    <div className="flex flex-col items-center px-6 py-14 text-center sm:px-10">
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
        <svg
          className="h-9 w-9 text-green-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>
      <h2 className="text-xl font-bold text-slate-900">
        Your Profile Is Analyzed
      </h2>
      {review ? (
        <div className="mt-5 w-full max-w-md text-left">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <span className="text-sm font-medium text-slate-700">
              Backend rating
            </span>
            <span className="text-lg font-bold text-blue-600">
              {review.rating_out_of_10}/10
            </span>
          </div>
          <p className="mt-4 text-sm font-semibold text-slate-700">Strengths</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-500">
            {review.pros.map((pro) => (
              <li key={pro}>{pro}</li>
            ))}
          </ul>
          <p className="mt-4 text-sm font-semibold text-slate-700">
            Considerations
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-500">
            {review.cons.map((con) => (
              <li key={con}>{con}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="mt-3 max-w-md text-sm leading-relaxed text-slate-500">
          The Python backend returned no review data.
        </p>
      )}
      <button
        onClick={onReset}
        className="mt-8 rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50"
      >
        Submit another business profile
      </button>
    </div>
  );
}
