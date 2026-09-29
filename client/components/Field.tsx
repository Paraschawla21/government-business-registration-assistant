import type { ReactNode } from "react";

export function Field({
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
  children: ReactNode;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-slate-700">
        {label}
        {required && <span className="ml-0.5 text-red-500">*</span>}
        {optionalHint && (
          <span className="ml-1.5 text-xs font-normal text-slate-400">(Optional)</span>
        )}
      </label>
      {children}
      {error && <p className="mt-1 text-xs font-medium text-red-500">{error}</p>}
    </div>
  );
}
