import { useHealth } from "@/api/hooks";
import { formatDate } from "@/lib/utils";
import { Activity, Database, AlertCircle, CheckCircle } from "lucide-react";

export function SettingsPage() {
  const { data, isLoading, error, refetch } = useHealth();

  const statusColor =
    data?.status === "ok"
      ? "text-atlas-green"
      : data?.status === "degraded"
        ? "text-atlas-yellow"
        : "text-atlas-red";

  const StatusIcon = data?.status === "ok" ? CheckCircle : AlertCircle;

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h2 className="text-xl font-bold text-atlas-text">Settings & Status</h2>
        <p className="text-sm text-atlas-muted">
          Monitor data health, API status, and system configuration
        </p>
      </div>

      {/* API Health */}
      <div className="rounded-lg border border-atlas-border bg-atlas-surface p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-atlas-accent" />
            <h3 className="font-semibold text-atlas-text">API Health</h3>
          </div>
          <button
            onClick={() => refetch()}
            className="rounded border border-atlas-border px-2.5 py-1 text-xs text-atlas-muted hover:text-atlas-text transition"
          >
            Refresh
          </button>
        </div>

        {isLoading && (
          <div className="mt-3 animate-pulse space-y-2">
            <div className="h-4 w-32 rounded bg-atlas-border" />
            <div className="h-4 w-48 rounded bg-atlas-border" />
          </div>
        )}

        {error && (
          <div className="mt-3 text-sm text-red-400">
            API unreachable — is the backend running? (`atlas serve`)
          </div>
        )}

        {data && (
          <div className="mt-3 space-y-3">
            <div className="flex items-center gap-2">
              <StatusIcon size={16} className={statusColor} />
              <span className={`font-medium capitalize ${statusColor}`}>
                {data.status}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-xs text-atlas-muted">Series Available</p>
                <p className="font-mono text-atlas-text">{data.series_count}</p>
              </div>
              <div>
                <p className="text-xs text-atlas-muted">Last Pull</p>
                <p className="font-mono text-atlas-text">
                  {data.last_pull ? formatDate(data.last_pull) : "Never"}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Data Quality */}
      {data?.data_quality && (
        <div className="rounded-lg border border-atlas-border bg-atlas-surface p-4">
          <div className="flex items-center gap-2">
            <Database size={16} className="text-atlas-accent" />
            <h3 className="font-semibold text-atlas-text">Data Quality</h3>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-xs text-atlas-muted">Total Series (Catalog)</p>
              <p className="font-mono text-atlas-text">
                {data.data_quality.total_series}
              </p>
            </div>
            <div>
              <p className="text-xs text-atlas-muted">Available (Bronze)</p>
              <p className="font-mono text-atlas-text">
                {data.data_quality.available_series}
              </p>
            </div>
          </div>

          {data.data_quality.missing_series.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-medium text-atlas-yellow">
                Missing Series ({data.data_quality.missing_series.length})
              </p>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {data.data_quality.missing_series.map((s) => (
                  <span
                    key={s}
                    className="rounded bg-atlas-yellow/10 px-2 py-0.5 text-xs font-mono text-atlas-yellow"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Configuration Reference */}
      <div className="rounded-lg border border-atlas-border bg-atlas-surface p-4">
        <h3 className="font-semibold text-atlas-text">Quick Reference</h3>
        <div className="mt-3 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-atlas-muted">Backend API</span>
            <code className="font-mono text-atlas-text">http://localhost:8000</code>
          </div>
          <div className="flex justify-between">
            <span className="text-atlas-muted">Frontend</span>
            <code className="font-mono text-atlas-text">http://localhost:5173</code>
          </div>
          <div className="flex justify-between">
            <span className="text-atlas-muted">Ollama</span>
            <code className="font-mono text-atlas-text">http://localhost:11434</code>
          </div>
        </div>
        <div className="mt-4 rounded bg-atlas-bg p-3">
          <p className="mb-1 text-xs font-medium text-atlas-muted">CLI Commands</p>
          <pre className="text-xs text-atlas-text leading-relaxed font-mono">
{`atlas pull             # Fetch fresh data from FRED + yfinance
atlas build-features   # Run bronze → silver → gold pipeline
atlas snapshot         # Print current regime classification
atlas serve            # Start API on port 8000
atlas status           # Check data freshness`}
          </pre>
        </div>
      </div>
    </div>
  );
}
