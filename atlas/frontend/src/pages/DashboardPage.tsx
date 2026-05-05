import { RegimeBanner } from "@/components/dashboard/RegimeBanner";
import { KPIGrid } from "@/components/dashboard/KPIGrid";
import { NarrativeCard } from "@/components/dashboard/NarrativeCard";
import { HeatMap } from "@/components/charts/HeatMap";
import { useAtlasStore } from "@/store";

export function DashboardPage() {
  const mode = useAtlasStore((s) => s.mode);

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h2 className="text-xl font-bold text-atlas-text">Macro Dashboard</h2>
        <p className="text-sm text-atlas-muted">
          Real-time overview of 36 macro indicators across 6 themes
        </p>
      </div>

      {/* Regime Banner — always visible */}
      <RegimeBanner />

      {/* KPI Grid */}
      <div>
        <h3 className="mb-2 text-sm font-semibold text-atlas-muted uppercase tracking-wider">
          Key Indicators
        </h3>
        <KPIGrid />
      </div>

      {/* Two-column layout for heatmap + narrative */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <HeatMap />
        {(mode === "executive" || mode === "copilot") && <NarrativeCard />}
      </div>
    </div>
  );
}
