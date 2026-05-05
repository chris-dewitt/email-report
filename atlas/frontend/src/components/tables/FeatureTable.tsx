import type { FeatureMeta } from "@/types";
import { formatValue, cn, zScoreColor } from "@/lib/utils";

interface FeatureTableProps {
  features: FeatureMeta[];
}

export function FeatureTable({ features }: FeatureTableProps) {
  return (
    <div className="overflow-auto rounded-lg border border-atlas-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-atlas-border bg-atlas-surface text-left text-xs font-medium text-atlas-muted uppercase tracking-wider">
            <th className="px-3 py-2">Series</th>
            <th className="px-3 py-2">Transform</th>
            <th className="px-3 py-2 text-right">Value</th>
            <th className="px-3 py-2 text-right">Z-Score</th>
            <th className="px-3 py-2 text-right">1W Change</th>
          </tr>
        </thead>
        <tbody>
          {features.map((f) => (
            <tr
              key={f.feature_id}
              className="border-b border-atlas-border/50 hover:bg-atlas-accent/5 transition"
            >
              <td className="px-3 py-2 font-mono text-atlas-text text-xs">
                {f.base_series}
              </td>
              <td className="px-3 py-2 text-xs text-atlas-muted">{f.transform}</td>
              <td className="px-3 py-2 text-right font-mono text-atlas-text">
                {formatValue(f.latest_value, 4)}
              </td>
              <td
                className={cn(
                  "px-3 py-2 text-right font-mono font-medium",
                  zScoreColor(f.latest_z)
                )}
              >
                {f.latest_z != null
                  ? `${f.latest_z > 0 ? "+" : ""}${f.latest_z.toFixed(2)}`
                  : "—"}
              </td>
              <td className="px-3 py-2 text-right font-mono text-xs text-atlas-muted">
                {f.change_1w != null ? formatValue(f.change_1w, 4) : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
