import { useState } from "react";
import { useEventStudies } from "@/api/hooks";
import { CARBarChart } from "@/components/charts/CARBarChart";
import { formatDate, formatValue } from "@/lib/utils";

const SERIES_OPTIONS = ["DGS2", "DGS10", "DGS30", "T10Y2Y", "VIXCLS", "DFF", "SPX"];

export function EventStudyPage() {
  const [seriesId, setSeriesId] = useState("DGS10");
  const [docType, setDocType] = useState<string | undefined>(undefined);

  const { data, isLoading } = useEventStudies({
    series_id: seriesId,
    doc_type: docType,
  });

  const results = data?.results ?? [];
  const significantCount = results.filter((r) => r.significant).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-fed-text">Event Study</h2>
          <p className="text-sm text-fed-muted mt-1">Market reaction to Fed communications</p>
        </div>
        <div className="flex gap-4 items-center">
          <select
            value={seriesId}
            onChange={(e) => setSeriesId(e.target.value)}
            className="rounded-md border border-fed-border bg-fed-bg px-3 py-1.5 text-sm text-fed-text focus:border-fed-accent focus:outline-none"
          >
            {SERIES_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <select
            value={docType ?? ""}
            onChange={(e) => setDocType(e.target.value || undefined)}
            className="rounded-md border border-fed-border bg-fed-bg px-3 py-1.5 text-sm text-fed-text focus:border-fed-accent focus:outline-none"
          >
            <option value="">All Doc Types</option>
            <option value="statement">Statements</option>
            <option value="minutes">Minutes</option>
            <option value="speech">Speeches</option>
            <option value="pressconf">Press Conf</option>
          </select>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4 text-center">
          <p className="text-2xl font-bold text-fed-accent">{results.length}</p>
          <p className="text-xs text-fed-muted mt-1">Total Events</p>
        </div>
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4 text-center">
          <p className="text-2xl font-bold text-fed-yellow">{significantCount}</p>
          <p className="text-xs text-fed-muted mt-1">Significant (p &lt; 0.05)</p>
        </div>
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4 text-center">
          <p className="text-2xl font-bold text-fed-green">
            {results.length > 0
              ? formatValue(results.reduce((sum, r) => sum + Math.abs(r.car), 0) / results.length * 100)
              : "0"}
          </p>
          <p className="text-xs text-fed-muted mt-1">Avg |CAR| (bps)</p>
        </div>
      </div>

      {/* CAR chart */}
      <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
        {isLoading ? (
          <p className="text-sm text-fed-muted py-8 text-center">Loading event studies...</p>
        ) : (
          <CARBarChart data={results} title={`CAR for ${seriesId}`} />
        )}
      </div>

      {/* Results table */}
      {results.length > 0 && (
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
          <h3 className="mb-3 text-sm font-semibold text-fed-muted uppercase tracking-wider">
            Event Details
          </h3>
          <div className="max-h-80 overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-fed-border text-left text-xs text-fed-muted uppercase">
                  <th className="py-2 pr-4">Event Date</th>
                  <th className="py-2 pr-4">Doc ID</th>
                  <th className="py-2 pr-4">CAR (bps)</th>
                  <th className="py-2 pr-4">t-stat</th>
                  <th className="py-2 pr-4">p-value</th>
                  <th className="py-2">Sig.</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => (
                  <tr key={i} className="border-b border-fed-border/50">
                    <td className="py-1.5 pr-4 text-fed-text">{formatDate(r.event_date)}</td>
                    <td className="py-1.5 pr-4 text-fed-muted font-mono text-xs">{r.doc_id}</td>
                    <td
                      className="py-1.5 pr-4 font-medium"
                      style={{ color: r.car >= 0 ? "#10b981" : "#ef4444" }}
                    >
                      {(r.car * 100).toFixed(2)}
                    </td>
                    <td className="py-1.5 pr-4 text-fed-text">{r.t_stat.toFixed(2)}</td>
                    <td className="py-1.5 pr-4 text-fed-text">{r.p_value.toFixed(4)}</td>
                    <td className="py-1.5">
                      {r.significant ? (
                        <span className="text-fed-yellow font-medium">Yes</span>
                      ) : (
                        <span className="text-fed-muted">No</span>
                      )}
                    </td>
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
