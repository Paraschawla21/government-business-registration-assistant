import type { BusinessSetupReport } from "@/lib/business";

function downloadTextArtifact(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function downloadPdfArtifact(filename: string, base64Content: string) {
  const binary = atob(base64Content);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  const blob = new Blob([bytes], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function SuccessState({
  onReset,
  report,
}: {
  onReset: () => void;
  report: BusinessSetupReport | null;
}) {
  return (
    <div className="flex flex-col items-center px-6 py-14 text-center sm:px-10">
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
        <svg className="h-9 w-9 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h2 className="text-xl font-bold text-slate-900">Your Profile Is Analyzed</h2>
      {report ? (
        <div className="mt-5 w-full max-w-xl text-left">
          <p className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-600">{report.profile_summary}</p>

          <p className="mt-4 text-sm font-semibold text-slate-700">Potential registrations</p>
          <div className="mt-2 space-y-3">
            {report.potential_registrations.map((item) => (
              <div key={item.name} className="rounded-lg border border-slate-200 px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-slate-800">{item.name}</p>
                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">{item.status}</span>
                </div>
                <p className="mt-1.5 text-sm text-slate-600">{item.why_relevant}</p>

                {item.required_documents.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Documents</p>
                    <ul className="mt-1 list-disc space-y-0.5 pl-5 text-xs text-slate-600">
                      {item.required_documents.map((doc) => (
                        <li key={doc}>{doc}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.information_still_required.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-semibold uppercase tracking-wide text-amber-600">More Info Required</p>
                    <ul className="mt-1 list-disc space-y-0.5 pl-5 text-xs text-amber-700">
                      {item.information_still_required.map((missing) => (
                        <li key={missing}>{missing}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.official_links.length > 0 && (
                  <p className="mt-2 text-xs text-slate-500">
                    Official source:{" "}
                    <a
                      href={item.official_links[0]}
                      target="_blank"
                      rel="noreferrer"
                      className="font-medium text-blue-600 hover:text-blue-700"
                    >
                      {item.official_links[0]}
                    </a>
                  </p>
                )}
              </div>
            ))}
          </div>

          {report.gst_verification && (
            <div className="mt-4 rounded-lg border border-blue-100 bg-blue-50 px-3 py-3 text-sm text-blue-900">
              <p className="font-semibold">GST Verification</p>
              <p className="mt-1 text-xs text-blue-800">{report.gst_verification.message ?? "No GST verification message."}</p>
              {report.gst_verification.checked && (
                <p className="mt-1 text-xs text-blue-800">
                  Status: {report.gst_verification.status ?? "N/A"}
                  {report.gst_verification.legal_name ? ` | Legal Name: ${report.gst_verification.legal_name}` : ""}
                </p>
              )}
            </div>
          )}

          {report.pan_verification && (
            <div className="mt-3 rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-3 text-sm text-indigo-900">
              <p className="font-semibold">PAN Verification</p>
              <p className="mt-1 text-xs text-indigo-800">
                {report.pan_verification.message ?? "No PAN verification message."}
              </p>
            </div>
          )}

          {report.data_sources && report.data_sources.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-semibold text-slate-700">Data sources used</p>
              <ul className="mt-2 space-y-1 text-xs text-slate-600">
                {report.data_sources.map((source) => (
                  <li key={`${source.source_name}-${source.status}`}>
                    <span className="font-semibold">{source.source_name}</span>: {source.status} - {source.message}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {report.action_results && report.action_results.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-semibold text-slate-700">Generated outputs</p>
              <div className="mt-2 space-y-2">
                {report.action_results.map((result) => (
                  <div key={result.name} className="rounded-md border border-slate-200 px-3 py-2">
                    <p className="text-sm font-semibold text-slate-800">{result.name}</p>
                    <p className="text-xs text-slate-600">{result.message}</p>
                    {result.artifact_content && result.artifact_filename && (
                      <button
                        type="button"
                        onClick={() =>
                          downloadTextArtifact(result.artifact_filename!, result.artifact_content!)
                        }
                        className="mt-2 cursor-pointer rounded-md bg-slate-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-slate-700"
                      >
                        Download {result.artifact_filename}
                      </button>
                    )}
                    {result.artifact_base64 && result.artifact_filename && (
                      <button
                        type="button"
                        onClick={() =>
                          downloadPdfArtifact(result.artifact_filename!, result.artifact_base64!)
                        }
                        className="mt-2 ml-2 cursor-pointer rounded-md bg-blue-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-600"
                      >
                        Download {result.artifact_filename}
                      </button>
                    )}
                    {result.artifact_url && (
                      <a
                        href={result.artifact_url}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-2 ml-2 inline-block rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                      >
                        Open Link
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {report.suggested_sequence.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-semibold text-slate-700">Suggested sequence</p>
              <ol className="mt-2 space-y-2 text-sm text-slate-600">
                {report.suggested_sequence.map((step) => (
                  <li key={step.step} className="rounded-md bg-slate-50 px-3 py-2">
                    <span className="font-semibold text-slate-800">{step.step}. {step.title}</span>
                    <p className="mt-0.5 text-xs text-slate-600">{step.detail}</p>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {report.information_still_required.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-semibold text-slate-700">Profile details still required</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
                {report.information_still_required.map((missing) => (
                  <li key={missing}>{missing}</li>
                ))}
              </ul>
            </div>
          )}

          <p className="mt-4 text-sm text-slate-500">{report.disclaimer}</p>
        </div>
      ) : (
        <p className="mt-3 max-w-md text-sm leading-relaxed text-slate-500">The Python backend returned no setup report data.</p>
      )}
      <button
        onClick={onReset}
        className="mt-8 cursor-pointer rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50"
      >
        Submit another business profile
      </button>
    </div>
  );
}
