import { useRegimeSnapshot } from "@/api/hooks";
import { REGIME_COLORS } from "@/types";
import { formatDate } from "@/lib/utils";
import { AlertTriangle, TrendingUp, TrendingDown, Activity, Flame } from "lucide-react";

const REGIME_ICONS: Record<string, typeof Activity> = {
  expansion: TrendingUp,
  overheating: Flame,
  slowdown: TrendingDown,
  contraction: AlertTriangle,
  financial_stress: Activity,
};

export function RegimeBanner() {
  const { data, isLoading, error } = useRegimeSnapshot();

  if (isLoading) {
    return (
      <div className="animate-pulse rounded-lg border border-atlas-border bg-atlas-surface p-4">
        <div className="h-8 w-48 rounded bg-atlas-border" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-lg border border-red-900/30 bg-red-950/20 p-4 text-red-400 text-sm">
        Regime data unavailable — run `atlas build-features` first
      </div>
    );
  }

  const color = REGIME_COLORS[data.regime] ?? "#6b7280";
  const Icon = REGIME_ICONS[data.regime] ?? Activity;

  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: `${color}40`, backgroundColor: `${color}08` }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className="flex h-10 w-10 items-center justify-center rounded-lg"
            style={{ backgroundColor: `${color}20` }}
          >
            <Icon size={22} style={{ color }} />
          </div>
          <div>
            <p className="text-xs font-medium text-atlas-muted uppercase tracking-wider">
              Current Regime
            </p>
            <p className="text-xl font-bold capitalize" style={{ color }}>
              {data.regime.replace("_", " ")}
            </p>
          </div>
        </div>

        <div className="text-right">
          <p className="text-xs text-atlas-muted">
            Confidence:{" "}
            <span className="font-mono font-semibold text-atlas-text">
              {(data.confidence * 100).toFixed(0)}%
            </span>
          </p>
          <p className="text-xs text-atlas-muted">As of {formatDate(data.as_of)}</p>
        </div>
      </div>

      {/* Drivers */}
      {data.drivers.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {data.drivers.map((d, i) => (
            <span
              key={i}
              className="rounded-full px-2.5 py-0.5 text-xs font-medium"
              style={{ backgroundColor: `${color}15`, color }}
            >
              {d}
            </span>
          ))}
        </div>
      )}

      {/* Score bars */}
      {data.all_scores && Object.keys(data.all_scores).length > 0 && (
        <div className="mt-3 grid grid-cols-5 gap-2">
          {Object.entries(data.all_scores).map(([regime, score]) => (
            <div key={regime} className="text-center">
              <div className="h-1.5 rounded-full bg-atlas-border overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${Math.max(5, Math.min(100, score * 100))}%`,
                    backgroundColor: REGIME_COLORS[regime] ?? "#6b7280",
                  }}
                />
              </div>
              <p className="mt-1 text-[10px] text-atlas-muted capitalize">
                {regime.replace("_", " ")}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
