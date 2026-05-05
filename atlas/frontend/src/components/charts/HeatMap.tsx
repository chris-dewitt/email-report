import { useFeatureGroups } from "@/api/hooks";
import { cn, zScoreColor } from "@/lib/utils";
import { THEME_LABELS, type Theme } from "@/types";

/**
 * Z-score heatmap — shows latest z-scores for all features grouped by theme.
 */
export function HeatMap() {
  const { data, isLoading } = useFeatureGroups();

  if (isLoading) {
    return (
      <div className="animate-pulse rounded-lg border border-atlas-border bg-atlas-surface p-4">
        <div className="h-40 rounded bg-atlas-border" />
      </div>
    );
  }

  if (!data || data.groups.length === 0) {
    return (
      <div className="rounded-lg border border-atlas-border bg-atlas-surface p-4 text-sm text-atlas-muted">
        No feature data available
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-atlas-border bg-atlas-surface p-4">
      <h3 className="mb-3 text-sm font-semibold text-atlas-text">Z-Score Heatmap</h3>
      <div className="space-y-3">
        {data.groups.map((group) => (
          <div key={group.theme}>
            <p className="mb-1 text-xs font-medium text-atlas-muted uppercase tracking-wider">
              {THEME_LABELS[group.theme as Theme] ?? group.theme}
            </p>
            <div className="flex flex-wrap gap-1.5">
              {group.features.map((f) => {
                const z = f.latest_z;
                const bgIntensity =
                  z == null
                    ? "bg-atlas-border"
                    : z > 1.5
                      ? "bg-red-900/60"
                      : z > 0.5
                        ? "bg-yellow-900/40"
                        : z < -1.5
                          ? "bg-blue-900/60"
                          : z < -0.5
                            ? "bg-cyan-900/40"
                            : "bg-atlas-border/60";

                return (
                  <div
                    key={f.feature_id}
                    className={cn(
                      "rounded px-2 py-1 text-center min-w-[70px]",
                      bgIntensity
                    )}
                    title={`${f.base_series}: z=${z?.toFixed(2) ?? "N/A"}`}
                  >
                    <p className="text-[10px] text-atlas-muted truncate">{f.base_series}</p>
                    <p className={cn("text-xs font-mono font-semibold", zScoreColor(z))}>
                      {z != null ? z.toFixed(2) : "—"}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-3 flex items-center justify-center gap-4 text-[10px] text-atlas-muted">
        <span className="flex items-center gap-1">
          <div className="h-2 w-4 rounded bg-blue-900/60" /> z &lt; -1.5
        </span>
        <span className="flex items-center gap-1">
          <div className="h-2 w-4 rounded bg-cyan-900/40" /> z &lt; -0.5
        </span>
        <span className="flex items-center gap-1">
          <div className="h-2 w-4 rounded bg-atlas-border/60" /> Normal
        </span>
        <span className="flex items-center gap-1">
          <div className="h-2 w-4 rounded bg-yellow-900/40" /> z &gt; 0.5
        </span>
        <span className="flex items-center gap-1">
          <div className="h-2 w-4 rounded bg-red-900/60" /> z &gt; 1.5
        </span>
      </div>
    </div>
  );
}
