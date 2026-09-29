import { Field } from "@/components/Field";
import { SparkleIcon, Spinner } from "@/components/Icons";
import type { FormEvent } from "react";
import {
  BUSINESS_TYPES,
  INDUSTRIES,
  OPERATIONS_OPTIONS,
  TURNOVER_BRACKETS,
  type FormErrors,
  type FormState,
  inputClasses,
  selectClasses,
} from "@/lib/business";

export function BusinessProfileForm({
  form,
  errors,
  status,
  errorMessage,
  onFieldChange,
  onSubmit,
}: {
  form: FormState;
  errors: FormErrors;
  status: "idle" | "submitting" | "error";
  errorMessage: string;
  onFieldChange: (field: keyof FormState, value: string) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form onSubmit={onSubmit} noValidate className="p-6 sm:p-8">
      <div className="mb-6 border-b border-slate-100 pb-4">
        <h2 className="text-lg font-semibold text-slate-900">Business Profile Details</h2>
        <p className="text-sm text-slate-500">
          Fields marked <span className="text-red-500">*</span> are required.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <Field label="Business Type" required error={errors.businessType}>
          <select
            value={form.businessType}
            onChange={(e) => onFieldChange("businessType", e.target.value)}
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

        <Field label="Industry" required error={errors.industry}>
          <select
            value={form.industry}
            onChange={(e) => onFieldChange("industry", e.target.value)}
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

        <Field label="State" required error={errors.state}>
          <input
            type="text"
            placeholder="e.g. Maharashtra"
            value={form.state}
            onChange={(e) => onFieldChange("state", e.target.value)}
            className={inputClasses(!!errors.state)}
          />
        </Field>

        <Field label="City" required error={errors.city}>
          <input
            type="text"
            placeholder="e.g. Pune"
            value={form.city}
            onChange={(e) => onFieldChange("city", e.target.value)}
            className={inputClasses(!!errors.city)}
          />
        </Field>

        <Field label="Number of Employees" required error={errors.employees}>
          <input
            type="number"
            min={0}
            placeholder="e.g. 5"
            value={form.employees}
            onChange={(e) => onFieldChange("employees", e.target.value)}
            className={inputClasses(!!errors.employees)}
          />
        </Field>

        <Field label="Expected Turnover (INR)" required error={errors.turnover}>
          <select
            value={form.turnover}
            onChange={(e) => onFieldChange("turnover", e.target.value)}
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

        <div className="sm:col-span-2">
          <Field label="Core Business Activity" required error={errors.activity}>
            <textarea
              rows={3}
              placeholder="Briefly describe what your business does..."
              value={form.activity}
              onChange={(e) => onFieldChange("activity", e.target.value)}
              className={inputClasses(!!errors.activity) + " resize-none"}
            />
          </Field>
        </div>

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
                    onChange={(e) => onFieldChange("operations", e.target.value)}
                    className="h-4 w-4 accent-blue-600"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </Field>
        </div>

        <div className="sm:col-span-2">
          <Field label="GSTIN" error={errors.gstin} optionalHint>
            <input
              type="text"
              placeholder="e.g. 27ABCDE1234F1Z5"
              maxLength={15}
              value={form.gstin}
              onChange={(e) => onFieldChange("gstin", e.target.value)}
              className={inputClasses(!!errors.gstin) + " uppercase tracking-wide"}
            />
            <p className="mt-1.5 flex items-start gap-1.5 text-xs text-slate-400">
              <SparkleIcon />
              If you already have a GSTIN, our AI agent will fetch and verify your live official GST data automatically.
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
        Your information is used solely to generate a personalized registration guide and is not shared with third parties.
      </p>
    </form>
  );
}
