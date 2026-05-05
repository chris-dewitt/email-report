import { FileText, Database, Activity, Bot } from "lucide-react";
import { useHealth, useDocuments, useSentiment } from "@/api/hooks";
import { StatCard } from "@/components/dashboard/StatCard";
import { RecentDocs } from "@/components/dashboard/RecentDocs";
import { SentimentTimeline } from "@/components/charts/SentimentTimeline";

export function DashboardPage() {
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: docs } = useDocuments();
  const { data: sentiment } = useSentiment("statement");

  const totalDocs = health?.total_documents ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-fed-text">Dashboard</h2>
        <p className="text-sm text-fed-muted mt-1">Fed Communication Intelligence Overview</p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="Documents"
          value={healthLoading ? "..." : totalDocs}
          icon={FileText}
          color="text-fed-accent"
          subtitle="Total ingested"
        />
        <StatCard
          label="FAISS Index"
          value={healthLoading ? "..." : health?.index_built ? "Built" : "Not built"}
          icon={Database}
          color="text-fed-green"
          subtitle="Vector search"
        />
        <StatCard
          label="Ollama"
          value={health?.ollama_available ? "Online" : "Offline"}
          icon={Bot}
          color={health?.ollama_available ? "text-fed-green" : "text-fed-red"}
          subtitle="Local LLM"
        />
        <StatCard
          label="Status"
          value={health?.status ?? "..."}
          icon={Activity}
          color={health?.status === "ok" ? "text-fed-green" : "text-fed-yellow"}
        />
      </div>

      {/* Document type breakdown */}
      {health && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {Object.entries(health.documents).map(([dtype, count]) => (
            <StatCard
              key={dtype}
              label={dtype}
              value={count}
              icon={FileText}
              color="text-fed-purple"
            />
          ))}
        </div>
      )}

      {/* Content row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Sentiment chart */}
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
          <SentimentTimeline data={sentiment?.data ?? []} title="Statement Sentiment" />
        </div>

        {/* Recent documents */}
        <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
          <h3 className="mb-3 text-sm font-semibold text-fed-text uppercase tracking-wider">
            Recent Documents
          </h3>
          <RecentDocs documents={docs?.documents ?? []} />
        </div>
      </div>
    </div>
  );
}
