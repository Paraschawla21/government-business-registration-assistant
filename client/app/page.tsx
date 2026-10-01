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
    <div className="flex flex-1 flex-col items-center bg-slate-50 px-4 py-10 sm:py-16">
      <div className="w-full max-w-2xl">
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

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-200/50">
          {status === "success" ? (
            <SuccessState onReset={handleReset} report={report} />
          ) : (
            <BusinessProfileForm
              form={form}
              errors={errors}
              status={status === "submitting" ? "submitting" : status === "error" ? "error" : "idle"}
              errorMessage={errorMessage}
              onFieldChange={updateField}
              onSubmit={handleSubmit}
            />
          )}
        </div>
      </div>
    </div>
  );
}
