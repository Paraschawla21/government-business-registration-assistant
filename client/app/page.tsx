"use client";

import { useState, type FormEvent } from "react";

import { BusinessProfileForm } from "@/components/BusinessProfileForm";
import { SuccessState } from "@/components/SuccessState";
import { submitBusinessProfile } from "@/lib/api";
import {
  INITIAL_STATE,
  type BusinessSetupReport,
  type FormErrors,
  type FormState,
  type Status,
  validateForm,
} from "@/lib/business";

export default function Home() {
  const [form, setForm] = useState<FormState>(INITIAL_STATE);
  const [errors, setErrors] = useState<FormErrors>({});
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [report, setReport] = useState<BusinessSetupReport | null>(null);

  const updateField = (field: keyof FormState, value: string) => {
    setForm((prev) => ({
      ...prev,
      [field]: field === "gstin" || field === "pan" ? value.toUpperCase() : value,
    }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const nextErrors = validateForm(form);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setStatus("submitting");
    setErrorMessage("");

    try {
      const response = await submitBusinessProfile(form);
      setReport(response);
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
    setReport(null);
  };

  return (
    <div className="relative isolate min-h-screen overflow-hidden bg-slate-100">
      <div className="pointer-events-none absolute -left-20 top-0 h-80 w-80 rounded-full bg-cyan-200/45 blur-3xl" />
      <div className="pointer-events-none absolute right-0 top-28 h-96 w-96 rounded-full bg-indigo-200/55 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-emerald-200/35 blur-3xl" />

      <div className="relative mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-12 lg:py-16">
        <div className="grid gap-6 lg:grid-cols-[1.05fr_1fr] lg:items-start">
          <section className="rounded-3xl border border-slate-200/80 bg-white/80 p-6 shadow-lg shadow-slate-200/60 backdrop-blur sm:p-8">
            <div className="inline-flex items-center gap-2 rounded-full bg-sky-50 px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-sky-700 ring-1 ring-inset ring-sky-200">
              <span className="h-2 w-2 rounded-full bg-sky-500" />
              Government Business Registration Assistant
            </div>
            <h1 className="mt-5 text-3xl font-bold leading-tight text-slate-900 sm:text-4xl">
              Build your registration roadmap with an AI agent that stays grounded
            </h1>
            <p className="mt-4 text-base leading-relaxed text-slate-600 sm:text-lg">
              Share your business profile once. We evaluate potentially relevant registrations, show what is missing,
              and generate actionable outputs you can use instantly.
            </p>

            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <p className="text-sm font-semibold text-slate-800">Deterministic core</p>
                <p className="mt-1 text-xs text-slate-500">Rule engine + verified links + source-traceable decisions.</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <p className="text-sm font-semibold text-slate-800">Action-ready outputs</p>
                <p className="mt-1 text-xs text-slate-500">Generate markdown, CSV, PDF, and connected trackers.</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 sm:col-span-2">
                <p className="text-sm font-semibold text-slate-800">Built for founders, audited for clarity</p>
                <p className="mt-1 text-xs text-slate-500">Statuses: Applicable, More Info Required, Not Relevant.</p>
              </div>
            </div>
          </section>

          <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl shadow-slate-300/50">
            {status === "success" ? (
              <SuccessState onReset={handleReset} report={report} />
            ) : status === "submitting" ? (
              <AnalyzingState form={form} />
            ) : (
              <BusinessProfileForm
                form={form}
                errors={errors}
                status={status === "error" ? "error" : "idle"}
                errorMessage={errorMessage}
                onFieldChange={updateField}
                onSubmit={handleSubmit}
              />
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

function AnalyzingState({ form }: { form: FormState }) {
  return (
    <div className="flex min-h-[620px] flex-col items-center justify-center px-6 py-12 text-center sm:px-10">
      <div className="relative mb-6">
        <span className="absolute inset-0 animate-ping rounded-full bg-blue-300/50" />
        <span className="relative flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg shadow-blue-400/40">
          <svg className="h-6 w-6 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeOpacity="0.25" strokeWidth="4" />
            <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
          </svg>
        </span>
      </div>

      <h2 className="text-xl font-bold text-slate-900 sm:text-2xl">AI agent is analyzing your business profile</h2>
      <p className="mt-2 max-w-md text-sm leading-relaxed text-slate-600 sm:text-base">
        We are checking deterministic registration rules, source links, and verification readiness before generating your
        setup plan.
      </p>

      <div className="mt-6 w-full max-w-md rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-left">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Current profile</p>
        <p className="mt-1 text-sm text-slate-700">
          {form.businessType || "Business type"} in {form.city || "city"}, {form.state || "state"} •
          {" "}{form.industry || "industry"} • {form.turnover || "turnover"}
        </p>
      </div>

      <p className="mt-4 text-xs font-medium text-blue-700">Preparing checklist, sources, and downloadable outputs...</p>
    </div>
  );
}
