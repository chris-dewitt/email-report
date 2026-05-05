import { cn, formatValue, zScoreColor } from "@/lib/utils";
import { SparkLine } from "@/components/charts/SparkLine";
import type { SeriesPoint } from "@/types";

interface KPICardProps {
  title: string;
  value: number | null;
  unit?: string;
  zScore?: number | null;
  change1w?: number | null;
  sparkData?: SeriesPoint[];
  onClick?: () => void;
}

export function KPICard({
  title,
  value,
  unit = "",
  zScore,
  change1w,
  sparkData,
  onClick,
}: KPICardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "rounded-lg border border-atlas-border bg-atlas-surface p-4 transition",
        onClick && "cursor-pointer hover:border-atlas-accent/40 hover:bg-atlas-accent/5"
      )}
    >
      <p className="text-xs font-medium text-atlas-muted truncate">{title}</p>

      <div className="mt-1 flex items-baseline gap-2">
        <span className="text-2xl font-bold font-mono text-atlas-text">
          {formatValue(value)}
        </span>
        {unit && <span className="text-xs text-atlas-muted">{unit}</span>}
      </div>

      {/* Z-score and change row */}
      <div className="mt-2 flex items-center gap-3 text-xs">
        {zScore != null && (
          <span className={cn("font-mono font-medium", zScoreColor(zScore))}>
            z: {zScore > 0 ? "+" : ""}
            {zScore.toFixed(2)}
          </span>
        )}
        {change1w != null && (
          <span
            className={cn(
              "font-mono",
              change1w > 0 ? "text-atlas-green" : change1w < 0 ? "text-atlas-red" : "text-atlas-muted"
            )}
          >
            1w: {change1w > 0 ? "+" : ""}
            {formatValue(change1w, 3)}
          </span>
        )}
      </div>

      {/* Sparkline */}
      {sparkData && sparkData.length > 5 && (
        <div className="mt-2 h-8">
          <SparkLine data={sparkData} />
        </div>
      )}
    </div>
  );
}
