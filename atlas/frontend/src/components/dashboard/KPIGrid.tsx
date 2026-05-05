import { useFeatureGroups } from "@/api/hooks";
import { KPICard } from "./KPICard";
import { useAtlasStore } from "@/store";
import { useNavigate } from "react-router-dom";

/** Key series to highlight as KPIs on the executive dashboard. */
const KPI_SERIES = [
  { id: "CPIAUCSL", label: "CPI (All Items)", unit: "index" },
  { id: "UNRATE", label: "Unemployment Rate", unit: "%" },
  { id: "DFF", label: "Fed Funds Rate", unit: "%" },
  { id: "DGS10", label: "10Y Treasury", unit: "%" },
  { id: "T10Y2Y", label: "10Y-2Y Spread", unit: "bps" },
  { id: "VIXCLS", label: "VIX", unit: "index" },
  { id: "BAMLH0A0HYM2", label: "HY OAS", unit: "bps" },
  { id: "INDPRO", label: "Industrial Prod.", unit: "index" },
] as const;

export function KPIGrid() {
  const { data, isLoading } = useFeatureGroups();
  const selectSeries = useAtlasStore((s) => s.selectSeries);
  const navigate = useNavigate();

  // Build a lookup: series_id -> feature data
  const featureMap = new Map<
    string,
    { value: number | null; z: number | null; change: number | null }
  >();
  if (data) {
    for (const group of data.groups) {
      for (const f of group.features) {
        featureMap.set(f.base_series, {
          value: f.latest_value,
          z: f.latest_z,
          change: f.change_1w,
        });
      }
    }
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="animate-pulse rounded-lg border border-atlas-border bg-atlas-surface p-4"
          >
            <div className="h-4 w-24 rounded bg-atlas-border" />
            <div className="mt-2 h-7 w-16 rounded bg-atlas-border" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      {KPI_SERIES.map(({ id, label, unit }) => {
        const f = featureMap.get(id);
        return (
          <KPICard
            key={id}
            title={label}
            value={f?.value ?? null}
            unit={unit}
            zScore={f?.z ?? null}
            change1w={f?.change ?? null}
            onClick={() => {
              selectSeries(id);
              navigate("/series");
            }}
          />
        );
      })}
    </div>
  );
}
