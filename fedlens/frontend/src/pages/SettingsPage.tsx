import { useHealth } from "@/api/hooks";
import { Activity, Database, Bot, FileText, AlertTriangle, CheckCircle } from "lucide-react";

export function SettingsPage() {
  const { data: health, isLoading, error, refetch } = useHealth();

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-fed-text">Settings</h2>
          <p className="text-sm text-fed-muted mt-1">System status and configuration</p>
        </div>
        <button
          onClick={() => refetch()}
          className="rounded-md border border-fed-border px-3 py-1.5 text-xs text-fed-muted hover:text-fed-text transition"
        >
          Refresh
        </button>
      </div>

      {isLoading ? (
        <p className="text-sm text-fed-muted">Loading health data...</p>
      ) : error ? (
        <div className="rounded-lg border border-fed-red/30 bg-fed-red/5 p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-fed-red" />
            <p className="text-sm text-fed-red">
              API unreachable: {(error as Error).message}
            </p>
          </div>
          <p className="text-xs text-fed-muted mt-2">
            Make sure the API server is running: <code className="font-mono text-fed-text">fedlens serve</code>
          </p>
        </div>
      ) : health ? (
        <>
          {/* System status */}
          <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-fed-text uppercase tracking-wider">
              <Activity size={16} className="text-fed-accent" />
              System Status
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                {health.status === "ok" ? (
                  <CheckCircle size={20} className="text-fed-green" />
                ) : (
                  <AlertTriangle size={20} className="text-fed-yellow" />
                )}
                <div>
                  <p className="text-sm font-medium text-fed-text">API Status</p>
                  <p className="text-xs text-fed-muted">{health.status}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {health.ollama_available ? (
                  <CheckCircle size={20} className="text-fed-green" />
                ) : (
                  <AlertTriangle size={20} className="text-fed-yellow" />
                )}
                <div>
                  <p className="text-sm font-medium text-fed-text">Ollama</p>
                  <p className="text-xs text-fed-muted">
                    {health.ollama_available ? "Online" : "Offline — start with 'ollama serve'"}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Document counts */}
          <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-fed-text uppercase tracking-wider">
              <FileText size={16} className="text-fed-accent" />
              Document Counts ({health.total_documents} total)
            </h3>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {Object.entries(health.documents).map(([dtype, count]) => (
                <div key={dtype} className="rounded border border-fed-border bg-fed-bg/50 p-3 text-center">
                  <p className="text-xl font-bold text-fed-text">{count}</p>
                  <p className="text-xs text-fed-muted mt-1">{dtype}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Index status */}
          <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-fed-text uppercase tracking-wider">
              <Database size={16} className="text-fed-accent" />
              Vector Index
            </h3>
            <div>
              <p className="text-sm text-fed-muted">FAISS Index</p>
              <p className="text-sm font-medium text-fed-text">
                {health.index_built ? "Built" : "Not built"}
              </p>
            </div>
          </div>

          {/* Gold layer */}
          {Object.keys(health.gold_layers).length > 0 && (
            <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
              <h3 className="mb-3 text-sm font-semibold text-fed-text uppercase tracking-wider">
                Gold Layer
              </h3>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {Object.entries(health.gold_layers).map(([layer, count]) => (
                  <div key={layer} className="rounded border border-fed-border bg-fed-bg/50 p-3 text-center">
                    <p className="text-xl font-bold text-fed-text">{count}</p>
                    <p className="text-xs text-fed-muted mt-1">{layer}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* CLI reference */}
          <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-fed-text uppercase tracking-wider">
              <Bot size={16} className="text-fed-accent" />
              CLI Reference
            </h3>
            <div className="space-y-2 font-mono text-xs">
              {[
                { cmd: "fedlens init", desc: "Create data directories" },
                { cmd: "fedlens ingest --doc-type statement", desc: "Scrape Fed statements" },
                { cmd: "fedlens embed", desc: "Build FAISS index" },
                { cmd: "fedlens analyze", desc: "Run NLP pipeline" },
                { cmd: "fedlens event-study --series DGS10", desc: "Compute event studies" },
                { cmd: "fedlens brief --question '...'", desc: "Generate briefing" },
                { cmd: "fedlens serve", desc: "Start API on port 8001" },
                { cmd: "fedlens status", desc: "Show data freshness" },
              ].map(({ cmd, desc }) => (
                <div key={cmd} className="flex items-center gap-4">
                  <code className="text-fed-accent min-w-[280px]">{cmd}</code>
                  <span className="text-fed-muted">{desc}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
