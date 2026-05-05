import { useFedLensStore } from "@/store";
import { useSentiment, useDrift, useUncertainty } from "@/api/hooks";
import { SentimentTimeline } from "@/components/charts/SentimentTimeline";
import { DriftChart } from "@/components/charts/DriftChart";
import { UncertaintyChart } from "@/components/charts/UncertaintyChart";
import { DOC_TYPES, DOC_TYPE_LABELS } from "@/types";

export function DriftPage() {
  const docType = useFedLensStore((s) => s.selectedDocType);
  const setDocType = useFedLensStore((s) => s.setDocType);

  const { data: sentiment, isLoading: sentLoading } = useSentiment(docType);
  const { data: drift, isLoading: driftLoading } = useDrift(docType);
  const { data: uncertainty, isLoading: uncLoading } = useUncertainty(docType);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-fed-text">Drift & Sentiment</h2>
          <p className="text-sm text-fed-muted mt-1">Track how Fed language evolves over time</p>
        </div>
        <div className="flex gap-2">
          {DOC_TYPES.map((dt) => (
            <button
              key={dt}
              onClick={() => setDocType(dt)}
              className={`rounded px-3 py-1 text-xs font-medium transition ${
                docType === dt ? "bg-fed-accent text-white" : "text-fed-muted hover:text-fed-text"
              }`}
            >
              {DOC_TYPE_LABELS[dt]}
            </button>
          ))}
        </div>
      </div>

      {/* Sentiment */}
      <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
        {sentLoading ? (
          <p className="text-sm text-fed-muted py-8 text-center">Loading sentiment...</p>
        ) : (
          <SentimentTimeline
            data={sentiment?.data ?? []}
            title={`${DOC_TYPE_LABELS[docType as keyof typeof DOC_TYPE_LABELS] ?? docType} Sentiment`}
          />
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Drift */}
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
          {driftLoading ? (
            <p className="text-sm text-fed-muted py-8 text-center">Loading drift...</p>
          ) : (
            <DriftChart data={drift?.data ?? []} />
          )}
        </div>

        {/* Uncertainty */}
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
          {uncLoading ? (
            <p className="text-sm text-fed-muted py-8 text-center">Loading uncertainty...</p>
          ) : (
            <UncertaintyChart data={uncertainty?.data ?? []} />
          )}
        </div>
      </div>

      {/* Data summary table */}
      {sentiment?.data && sentiment.data.length > 0 && (
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
          <h3 className="mb-3 text-sm font-semibold text-fed-muted uppercase tracking-wider">
            Sentiment Data ({sentiment.total} observations)
          </h3>
          <div className="max-h-64 overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-fed-border text-left text-xs text-fed-muted uppercase">
                  <th className="py-2 pr-4">Date</th>
                  <th className="py-2 pr-4">Doc ID</th>
                  <th className="py-2 pr-4">Net Score</th>
                  <th className="py-2 pr-4">Hawkish</th>
                  <th className="py-2 pr-4">Dovish</th>
                  <th className="py-2">Label</th>
                </tr>
              </thead>
              <tbody>
                {sentiment.data.map((row, i) => (
                  <tr key={i} className="border-b border-fed-border/50">
                    <td className="py-1.5 pr-4 text-fed-text">{row.date}</td>
                    <td className="py-1.5 pr-4 text-fed-muted font-mono text-xs">{row.doc_id}</td>
                    <td className="py-1.5 pr-4 font-medium" style={{ color: row.net_score > 0 ? "#ef4444" : "#3b82f6" }}>
                      {row.net_score.toFixed(3)}
                    </td>
                    <td className="py-1.5 pr-4 text-fed-hawkish">{row.hawkish_count}</td>
                    <td className="py-1.5 pr-4 text-fed-dovish">{row.dovish_count}</td>
                    <td className="py-1.5 text-fed-muted">{row.label}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
