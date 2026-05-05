import type { SeriesMeta } from "@/types";
import { THEME_LABELS, type Theme } from "@/types";
import { formatValue, formatDate } from "@/lib/utils";

interface SeriesTableProps {
  series: SeriesMeta[];
  onSelect: (id: string) => void;
  selectedId?: string | null;
}

export function SeriesTable({ series, onSelect, selectedId }: SeriesTableProps) {
  return (
    <div className="overflow-auto rounded-lg border border-atlas-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-atlas-border bg-atlas-surface text-left text-xs font-medium text-atlas-muted uppercase tracking-wider">
            <th className="px-3 py-2">Series</th>
            <th className="px-3 py-2">Theme</th>
            <th className="px-3 py-2">Freq</th>
            <th className="px-3 py-2 text-right">Latest</th>
            <th className="px-3 py-2 text-right">Updated</th>
          </tr>
        </thead>
        <tbody>
          {series.map((s) => (
            <tr
              key={s.series_id}
              onClick={() => onSelect(s.series_id)}
              className={`cursor-pointer border-b border-atlas-border/50 transition hover:bg-atlas-accent/5 ${
                selectedId === s.series_id ? "bg-atlas-accent/10" : ""
              }`}
            >
              <td className="px-3 py-2">
                <p className="font-medium text-atlas-text">{s.series_id}</p>
                <p className="text-xs text-atlas-muted truncate max-w-[250px]">{s.name}</p>
              </td>
              <td className="px-3 py-2 text-xs text-atlas-muted capitalize">
                {THEME_LABELS[s.theme as Theme] ?? s.theme}
              </td>
              <td className="px-3 py-2 text-xs text-atlas-muted capitalize">{s.frequency}</td>
              <td className="px-3 py-2 text-right font-mono text-atlas-text">
                {formatValue(s.latest_value)}
              </td>
              <td className="px-3 py-2 text-right text-xs text-atlas-muted">
                {formatDate(s.last_updated)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
